"""Bounded, resumable execution of prompt-defined entity stages."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from .api import InferenceClient, InferenceError, InferenceRequest
from .definition import PipelineDefinition, PromptStage
from .evidence import (
    build_run_evidence,
    classify_failure,
    persist_rejected_pair,
    rejected_candidate_path,
    rejection_explanation,
    render_run_markdown,
)
from .prompts import OutputSchemas, PromptContract, PromptError, load_prompt
from .state import StateError, StateStore
from .validators import ValidationEvidence, validate


def entity_id(path: Path, root: Path) -> str:
    return hashlib.sha256(path.relative_to(root).as_posix().encode("utf-8")).hexdigest()[:24]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        Path(temporary_name).replace(path)
    finally:
        temporary = Path(temporary_name)
        if temporary.exists():
            temporary.unlink()


class PipelineRunner:
    def __init__(self, definition: PipelineDefinition, client: InferenceClient | None = None) -> None:
        self.definition = definition
        self.client = client
        self.store = StateStore(definition.state_path)
        self.schemas = OutputSchemas(definition.output_schema_path)
        self.prompts: dict[str, PromptContract] = {}
        self._stage_counts: dict[tuple[str, str, str], int] = {}
        self._session_steps: dict[tuple[str, str, str], int] = {}
        for name, stage in {**definition.stages, **definition.analysis}.items():
            prompt = load_prompt(
                stage.prompt_path,
                expected_id=stage.prompt_id,
                expected_version=stage.prompt_version,
                expected_output=stage.output_schema,
            )
            if prompt.kind != "pipeline-running":
                raise PromptError(f"stage {name} must use a pipeline-running prompt")
            if not self.schemas.has(prompt.output):
                raise PromptError(f"stage {name} references unknown output {prompt.output}")
            self.prompts[name] = prompt
        contract_material = definition.path.read_bytes() + "".join(sorted(prompt.content_hash for prompt in self.prompts.values())).encode("ascii")
        self.contract_hash = hashlib.sha256(contract_material).hexdigest()

    def close(self) -> None:
        self.store.close()

    def discover(self) -> int:
        changed = 0
        excluded_roots = tuple(
            root.resolve()
            for root in (
                self.definition.artifact_root,
                self.definition.thread_root,
                self.definition.report_root,
                self.definition.state_path.parent,
            )
        )
        for path in sorted(self.definition.source_root.glob(self.definition.source_glob)):
            resolved = path.resolve()
            if ".rejected." in path.name or any(resolved == root or root in resolved.parents for root in excluded_roots):
                continue
            if path.is_file() and self.store.upsert_discovered(entity_id(path, self.definition.source_root), str(path), digest(path), self.contract_hash):
                changed += 1
        return changed

    def _write_artifact(self, kind: str, entity: str, name: str, content: str | bytes) -> Path:
        path = self.definition.artifact_root / kind / entity / name
        encoded = content.encode("utf-8") if isinstance(content, str) else content
        _atomic_write(path, encoded)
        return path

    def _write_rejected_candidate(
        self,
        content: str,
        *,
        run_id: str,
        entity: str,
        artifact: str,
        stage: str,
        attempt_id: str,
        extension: str,
        failure_class: str,
        authority: str,
        validator_or_reviewer: str,
        rejection_code: str,
        explanation: str,
        retry_disposition: str,
        thread: str,
    ) -> Path:
        encoded = content.encode("utf-8")
        attempt_evidence = self.store.attempt_evidence(attempt_id)
        attempt_row = attempt_evidence["attempt"]
        path = rejected_candidate_path(
            self.definition.artifact_root,
            entity_id=entity,
            artifact=artifact,
            run_id=run_id,
            attempt_id=attempt_id,
            extension=extension,
        )
        candidate_sha256 = hashlib.sha256(encoded).hexdigest()
        explanation_markdown = rejection_explanation(
            run_id=run_id,
            entity_id=entity,
            artifact=artifact,
            stage=stage,
            attempt_id=attempt_id,
            candidate_path=path,
            candidate_sha256=candidate_sha256,
            failure_class=failure_class,
            authority=authority,
            validator_or_reviewer=validator_or_reviewer,
            rejection_code=rejection_code,
            actionable_explanation=explanation,
            retry_disposition=retry_disposition,
            run_report_path=self.definition.report_root / f"{run_id}.md",
            thread_path=thread,
            session_id=attempt_row.get("session_id"),
            session_step=attempt_row.get("session_step"),
            validation_evidence_path=attempt_evidence.get("validation_evidence_path"),
        )
        try:
            persist_rejected_pair(
                path,
                encoded,
                explanation_markdown,
                candidate_sha256=candidate_sha256,
            )
        except (FileExistsError, OSError, ValueError) as exc:
            raise StateError(f"failed to preserve rejected evidence pair: {path}: {exc}") from exc
        self.store.finish_attempt(
            attempt_id,
            "rejected",
            thread=thread or None,
            artifact=str(path),
            error=(rejection_code, explanation),
            response_bytes=len(encoded),
            failure_class=failure_class,
            authority=authority,
            validator_name=validator_or_reviewer,
            retry_disposition=retry_disposition,
        )
        return path

    def _invoke(
        self,
        stage: PromptStage,
        context: Mapping[str, Any],
        *,
        run_id: str,
        entity: str,
        revision: str,
    ) -> tuple[Mapping[str, Any], str, str]:
        prompt = self.prompts[stage.name]
        if self.client is None:
            raise StateError("this operation requires configured local inference")
        count_key = (run_id, entity, stage.name)
        count = self._stage_counts.get(count_key, 0) + 1
        if count > stage.max_attempts:
            raise StateError(f"stage attempt budget exceeded: {stage.name}")
        self._stage_counts[count_key] = count
        inputs = {name: context[name] for name in prompt.inputs if name in context}
        rendered = prompt.render(inputs)
        attempt_id = f"a-{uuid.uuid4().hex[:16]}"
        lane = "independent-review" if stage.name in {"self_review", "reviewer", "adjudicator"} else "worker"
        session_key = (run_id, entity, lane)
        session_step = self._session_steps.get(session_key, 0) + 1
        self._session_steps[session_key] = session_step
        generation = dict(self.client.config.generation)
        self.store.begin_attempt(
            attempt_id,
            run_id,
            entity,
            stage.name,
            prompt.prompt_id,
            prompt.version,
            prompt.content_hash,
            request_bytes=len(rendered.encode("utf-8")),
            prompt_template_bytes=len(prompt.body.encode("utf-8")),
            context_limit=generation.get("num_ctx") if isinstance(generation.get("num_ctx"), int) else None,
            completion_limit=generation.get("num_predict") if isinstance(generation.get("num_predict"), int) else None,
            reasoning_mode=str(generation.get("think", "unspecified")),
            provider=self.client.config.provider,
            model=self.client.config.model,
            generation_config=generation,
            session_id=f"{run_id}-{entity}-{lane}",
            session_step=session_step,
        )
        response = None
        try:
            response = self.client.invoke(
                InferenceRequest(
                    messages=[{"role": "user", "content": rendered}],
                    response_format=self.schemas.schema_for(prompt.output),
                    stage=stage.name,
                    run_id=run_id,
                    entity_id=entity,
                    entity_revision=revision,
                    attempt_id=attempt_id,
                    prompt_template_id=prompt.prompt_id,
                    prompt_template_hash=prompt.content_hash,
                )
            )
            result = self.schemas.validate(prompt.output, response.content)
            thread = str(response.capture_path) if response.capture_path else ""
            self.store.finish_attempt(
                attempt_id,
                "completed",
                thread=thread or None,
                response_bytes=len(response.content.encode("utf-8")),
                failure_class="none",
                authority="semantic_model",
                validator_name=prompt.output,
                retry_disposition="continue_stage",
                transport_attempts=response.attempts,
                transport_retry_events=[dict(item) for item in response.retry_events],
                prompt_tokens=int(response.usage["prompt_eval_count"]) if isinstance(response.usage.get("prompt_eval_count"), int) else None,
                completion_tokens=int(response.usage["eval_count"]) if isinstance(response.usage.get("eval_count"), int) else None,
            )
            return result, attempt_id, thread
        except (InferenceError, PromptError) as exc:
            thread_path = getattr(exc, "capture_path", None)
            safe = self.client.redact(str(exc))
            thread = str(thread_path or (response.capture_path if response and response.capture_path else ""))
            raw_failure = getattr(exc, "raw_content", None)
            if response is not None or raw_failure is not None:
                code = "schema_or_parse_rejection"
                failure_class = "schema" if isinstance(exc, PromptError) else classify_failure(code)
                self._write_rejected_candidate(
                    self.client.redact(response.content if response is not None else str(raw_failure)),
                    run_id=run_id,
                    entity=entity,
                    artifact=stage.name,
                    stage=stage.name,
                    attempt_id=attempt_id,
                    extension="txt",
                    failure_class=failure_class,
                    authority="deterministic",
                    validator_or_reviewer=prompt.output,
                    rejection_code=code,
                    explanation=safe,
                    retry_disposition="stage_retry_or_terminal",
                    thread=thread,
                )
            else:
                self.store.finish_attempt(
                    attempt_id,
                    "failed",
                    thread=thread or None,
                    error=("stage_error", safe),
                    failure_class=classify_failure(str(exc)),
                    authority="none",
                    validator_name="inference_transport",
                    retry_disposition="transport_policy_or_terminal",
                    transport_attempts=getattr(exc, "attempts", None),
                    transport_retry_events=list(getattr(exc, "retry_events", [])),
                )
            raise

    def _context(self, source: str, candidate: str | None = None, evidence: Mapping[str, Any] | None = None, violations: list[Any] | None = None) -> dict[str, Any]:
        return {
            "goal": self.definition.goal,
            "source_entity": source,
            "candidate": candidate,
            "allowed_changes": list(self.definition.allowed_changes),
            "protected_invariants": list(self.definition.protected_invariants),
            "invariants": list(self.definition.protected_invariants),
            "deterministic_evidence": evidence or {},
            "violations": violations or [],
            "review_verdicts": [],
            "allowed_actions": ["repair", "quarantine", "human_required"],
        }

    def _adjudicate(self, source: str, candidate: str, evidence: ValidationEvidence, violations: list[Any], *, run_id: str, entity: str, revision: str) -> tuple[str, str]:
        stage = self.definition.stages.get("adjudicator")
        if stage is None:
            return "repair", ""
        context = self._context(source, candidate, evidence.as_dict(), violations)
        context["review_verdicts"] = [{"violations": violations, "verdict": "fail"}]
        result, _attempt, thread = self._invoke(stage, context, run_id=run_id, entity=entity, revision=revision)
        action = str(result["action"])
        if action == "accept":
            return "quarantine", thread
        return action, thread

    def _validate_candidate(self, run_id: str, entity: str, attempt_id: str, source: str, candidate: str) -> tuple[ValidationEvidence, Path]:
        evidence = validate(source, candidate, self.definition.validation)
        path = self._write_artifact("evidence", entity, f"{attempt_id}.validation.json", json.dumps(evidence.as_dict(), ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        self.store.record_validation(run_id, entity, attempt_id, evidence.passed, evidence.as_dict(), str(path))
        return evidence, path

    def _invoke_analysis(self, stage: PromptStage, context: Mapping[str, Any], run_id: str, subject: str) -> tuple[Mapping[str, Any], str]:
        if self.client is None:
            raise StateError("analysis requires configured local inference")
        prompt = self.prompts[stage.name]
        inputs = {name: context[name] for name in prompt.inputs if name in context}
        rendered = prompt.render(inputs)
        attempt_id = f"a-{uuid.uuid4().hex[:16]}"
        response = self.client.invoke(
            InferenceRequest(
                messages=[{"role": "user", "content": rendered}],
                response_format=self.schemas.schema_for(prompt.output),
                stage=f"analysis-{stage.name}",
                run_id=run_id,
                entity_id=subject,
                entity_revision="post-run",
                attempt_id=attempt_id,
                prompt_template_id=prompt.prompt_id,
                prompt_template_hash=prompt.content_hash,
            )
        )
        return self.schemas.validate(prompt.output, response.content), str(response.capture_path) if response.capture_path else ""

    def _repair(
        self,
        source: str,
        candidate: str,
        violations: list[Any],
        *,
        run_id: str,
        entity: str,
        revision: str,
    ) -> tuple[str | None, str, str]:
        stage = self.definition.stages.get("repair")
        if stage is None or self.definition.runtime.max_repairs < 1:
            return None, "", ""
        result, attempt, thread = self._invoke(stage, self._context(source, candidate, violations=violations), run_id=run_id, entity=entity, revision=revision)
        if result["status"] != "repaired" or result.get("unresolved") or not isinstance(result.get("candidate"), str):
            return None, attempt, thread
        return str(result["candidate"]), attempt, thread

    def _semantic_review(self, source: str, candidate: str, evidence: ValidationEvidence, *, run_id: str, entity: str, revision: str) -> tuple[bool, list[Any], str]:
        threads: list[str] = []
        for name in ("self_review", "reviewer"):
            stage = self.definition.stages.get(name)
            if stage is None:
                continue
            result, _attempt, thread = self._invoke(stage, self._context(source, candidate, evidence.as_dict()), run_id=run_id, entity=entity, revision=revision)
            if thread:
                threads.append(thread)
            if result["verdict"] != "pass" or result.get("violations"):
                return False, list(result.get("violations", [])), threads[-1] if threads else ""
        return True, [], threads[-1] if threads else ""

    def _promote(self, entity: str, source_path: Path, expected_hash: str, accepted_path: Path) -> str:
        if digest(source_path) != expected_hash:
            raise StateError("source changed after discovery; refusing promotion")
        backup = self.definition.promotion.backup_root / entity / f"{expected_hash}.bak"
        if not backup.exists():
            _atomic_write(backup, source_path.read_bytes())
        candidate = accepted_path.read_bytes()
        candidate_hash = hashlib.sha256(candidate).hexdigest()
        promotion_id = f"promotion-{uuid.uuid4().hex[:16]}"
        self.store.prepare_promotion(promotion_id, entity, expected_hash, candidate_hash, str(backup))
        temporary = source_path.parent / f".{source_path.name}.{uuid.uuid4().hex}.promote"
        try:
            _atomic_write(temporary, candidate)
            temporary.replace(source_path)
            self.store.finish_promotion(promotion_id, "completed")
            return candidate_hash
        except OSError:
            self.store.finish_promotion(promotion_id, "failed")
            raise

    def _process(self, row: Any, run_id: str, owner: str) -> None:
        entity = row["id"]
        source_path = Path(row["source_path"])
        expected_hash = row["source_hash"]
        if source_path.stat().st_size > self.definition.runtime.max_source_bytes:
            self.store.set_outcome(entity, "quarantined", error=("source_too_large", f"source exceeds {self.definition.runtime.max_source_bytes} bytes"))
            return
        if digest(source_path) != expected_hash:
            self.store.set_outcome(entity, "quarantined", error=("source_changed", "source changed after discovery"))
            return
        source = source_path.read_text(encoding="utf-8")
        revision = expected_hash[:16]
        self.store.lease(entity, run_id, owner, self.definition.runtime.lease_seconds)
        snapshot = self._write_artifact("source", entity, f"{revision}.md", source)
        worker = self.definition.stages["worker"]
        last_thread = ""
        try:
            result, attempt, last_thread = self._invoke(worker, self._context(source), run_id=run_id, entity=entity, revision=revision)
            if result["status"] != "candidate" or not isinstance(result.get("candidate"), str):
                explanation = str(result.get("reason") or "worker returned unable")
                rejected = self._write_rejected_candidate(
                    json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    run_id=run_id,
                    entity=entity,
                    artifact=worker.name,
                    stage=worker.name,
                    attempt_id=attempt,
                    extension="json",
                    failure_class="semantic",
                    authority="semantic_model",
                    validator_or_reviewer="worker_result_contract",
                    rejection_code="worker_unable",
                    explanation=explanation,
                    retry_disposition="quarantine",
                    thread=last_thread,
                )
                self.store.set_outcome(entity, "quarantined", candidate=str(rejected), error=("worker_unable", explanation), thread=last_thread, prompt_hash=self.contract_hash, evidence=str(snapshot))
                return
            candidate = str(result["candidate"])
            if len(candidate.encode("utf-8")) > self.definition.runtime.max_candidate_bytes:
                explanation = f"candidate exceeds {self.definition.runtime.max_candidate_bytes} bytes"
                rejected = self._write_rejected_candidate(
                    candidate,
                    run_id=run_id,
                    entity=entity,
                    artifact="worker",
                    stage="candidate_size_validation",
                    attempt_id=attempt,
                    extension="md",
                    failure_class="deterministic",
                    authority="deterministic",
                    validator_or_reviewer="max_candidate_bytes",
                    rejection_code="candidate_too_large",
                    explanation=explanation,
                    retry_disposition="quarantine",
                    thread=last_thread,
                )
                self.store.set_outcome(entity, "quarantined", candidate=str(rejected), error=("candidate_too_large", explanation), thread=last_thread, prompt_hash=self.contract_hash)
                return
            staged = self._write_artifact("staged", entity, f"{attempt}.md", candidate)
            evidence, evidence_path = self._validate_candidate(run_id, entity, attempt, source, candidate)
            if not evidence.passed:
                explanation = ", ".join(evidence.failure_codes)
                rejected = self._write_rejected_candidate(
                    candidate,
                    run_id=run_id,
                    entity=entity,
                    artifact=worker.name,
                    stage="deterministic_validation",
                    attempt_id=attempt,
                    extension="md",
                    failure_class="deterministic",
                    authority="deterministic",
                    validator_or_reviewer="pipeline_validation",
                    rejection_code=evidence.failure_codes[0],
                    explanation=explanation,
                    retry_disposition="semantic_repair" if self.definition.stages.get("repair") else "quarantine",
                    thread=last_thread,
                )
                repaired, repair_attempt, repair_thread = self._repair(source, candidate, list(evidence.failure_codes), run_id=run_id, entity=entity, revision=revision)
                if repaired is None:
                    self.store.set_outcome(entity, "quarantined", candidate=str(rejected), error=(evidence.failure_codes[0], explanation), thread=repair_thread or last_thread, prompt_hash=self.contract_hash, evidence=str(evidence_path))
                    return
                candidate = repaired
                attempt = repair_attempt
                last_thread = repair_thread or last_thread
                staged = self._write_artifact("staged", entity, f"{attempt}.md", candidate)
                evidence, evidence_path = self._validate_candidate(run_id, entity, attempt, source, candidate)
                if not evidence.passed:
                    explanation = ", ".join(evidence.failure_codes)
                    rejected = self._write_rejected_candidate(
                        candidate,
                        run_id=run_id,
                        entity=entity,
                        artifact="repair",
                        stage="deterministic_validation",
                        attempt_id=attempt,
                        extension="md",
                        failure_class="deterministic",
                        authority="deterministic",
                        validator_or_reviewer="pipeline_validation",
                        rejection_code=evidence.failure_codes[0],
                        explanation=explanation,
                        retry_disposition="quarantine",
                        thread=last_thread,
                    )
                    self.store.set_outcome(entity, "quarantined", candidate=str(rejected), error=(evidence.failure_codes[0], explanation), thread=last_thread, evidence=str(evidence_path))
                    return
            review_passed, violations, review_thread = self._semantic_review(source, candidate, evidence, run_id=run_id, entity=entity, revision=revision)
            if not review_passed:
                explanation = json.dumps(violations, ensure_ascii=False)
                rejected = self._write_rejected_candidate(
                    candidate,
                    run_id=run_id,
                    entity=entity,
                    artifact=f"{worker.name}-semantic-review" if attempt.startswith("a-") else "semantic-review",
                    stage="semantic_review",
                    attempt_id=attempt,
                    extension="md",
                    failure_class="semantic",
                    authority="semantic_model",
                    validator_or_reviewer="independent_semantic_review",
                    rejection_code="semantic_review_failed",
                    explanation=explanation,
                    retry_disposition="adjudicate_then_repair_or_quarantine",
                    thread=review_thread or last_thread,
                )
                action, adjudication_thread = self._adjudicate(source, candidate, evidence, violations, run_id=run_id, entity=entity, revision=revision)
                if action != "repair":
                    self.store.set_outcome(entity, "quarantined", candidate=str(rejected), error=("semantic_review_failed", f"adjudication={action}; {explanation}"), thread=adjudication_thread or review_thread or last_thread, evidence=str(evidence_path))
                    return
                repaired, repair_attempt, repair_thread = self._repair(source, candidate, violations, run_id=run_id, entity=entity, revision=revision)
                if repaired is None:
                    self.store.set_outcome(entity, "quarantined", candidate=str(rejected), error=("semantic_review_failed", explanation), thread=review_thread or last_thread, evidence=str(evidence_path))
                    return
                candidate = repaired
                attempt = repair_attempt
                last_thread = repair_thread or review_thread or last_thread
                staged = self._write_artifact("staged", entity, f"{attempt}.md", candidate)
                evidence, evidence_path = self._validate_candidate(run_id, entity, attempt, source, candidate)
                review_passed, violations, review_thread = self._semantic_review(source, candidate, evidence, run_id=run_id, entity=entity, revision=revision) if evidence.passed else (False, list(evidence.failure_codes), "")
                if not evidence.passed or not review_passed:
                    explanation = json.dumps(violations, ensure_ascii=False)
                    failure_class = "deterministic" if not evidence.passed else "semantic"
                    authority = "deterministic" if not evidence.passed else "semantic_model"
                    rejected = self._write_rejected_candidate(
                        candidate,
                        run_id=run_id,
                        entity=entity,
                        artifact="repair",
                        stage="repair_validation" if not evidence.passed else "semantic_review",
                        attempt_id=attempt,
                        extension="md",
                        failure_class=failure_class,
                        authority=authority,
                        validator_or_reviewer="pipeline_validation" if not evidence.passed else "independent_semantic_review",
                        rejection_code="repair_not_accepted",
                        explanation=explanation,
                        retry_disposition="quarantine",
                        thread=review_thread or last_thread,
                    )
                    self.store.set_outcome(entity, "quarantined", candidate=str(rejected), error=("repair_not_accepted", explanation), thread=review_thread or last_thread, evidence=str(evidence_path))
                    return
            accepted = self._write_artifact("accepted", entity, f"{attempt}.md", candidate)
            state = "accepted"
            new_source_hash = None
            if self.definition.promotion.enabled:
                new_source_hash = self._promote(entity, source_path, expected_hash, accepted)
                state = "promoted"
            self.store.set_outcome(entity, state, candidate=str(staged), accepted=str(accepted), thread=review_thread or last_thread, prompt_hash=self.contract_hash, source_hash=new_source_hash, evidence=str(evidence_path))
        except (InferenceError, PromptError, StateError, OSError) as exc:
            safe = self.client.redact(str(exc)) if self.client is not None else str(exc)
            self.store.set_outcome(entity, "quarantined", error=("processing_error", safe), thread=last_thread or None)

    def run(self, maximum: int, runtime_minutes: float, dry_run: bool = False) -> dict[str, Any]:
        if maximum < 1 or runtime_minutes <= 0:
            raise ValueError("run bounds must be positive")
        if dry_run:
            eligible = self.store.eligible(maximum)
            run_id = f"run-{uuid.uuid4().hex[:16]}"
            self.store.start_run(run_id)
            self.store.finish_run(run_id, "completed")
            report = self.report(run_id)
            return {
                "run_id": run_id,
                "status": "dry_run",
                "eligible": len(eligible),
                "entity_ids": [row["id"] for row in eligible],
                "state": self.store.summary(),
                "report": str(report),
                "human_report": str(report.with_suffix(".md")),
            }
        run_id = f"run-{uuid.uuid4().hex[:16]}"
        owner = f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        lock_seconds = max(self.definition.runtime.lock_stale_seconds, int(runtime_minutes * 60) + 60)
        self.store.acquire_lock(owner, run_id, lock_seconds)
        self.store.recover_expired_leases()
        eligible = self.store.eligible(maximum)
        self.store.start_run(run_id)
        started = time.monotonic()
        status = "completed"
        initial_report: Path | None = None
        failure: Exception | None = None
        try:
            # Evidence persistence is a precondition for material work.
            initial_report = self.report(run_id)
            for row in eligible:
                if time.monotonic() - started >= runtime_minutes * 60:
                    status = "bounded_stop"
                    break
                self._process(row, run_id, owner)
        except KeyboardInterrupt:
            status = "interrupted"
        except Exception as exc:
            status = "failed"
            failure = exc
        finally:
            self.store.finish_run(run_id, status)
            self.store.release_lock(owner, run_id)
        report = self.report(run_id)
        if failure is not None:
            raise failure
        narrative = report.with_suffix(".md")
        return {
            "run_id": run_id,
            "status": status,
            "state": self.store.summary(),
            "report": str(report),
            "human_report": str(narrative),
            "initial_report": str(initial_report) if initial_report else None,
        }

    def inspect(self, entity: str) -> dict[str, Any] | None:
        return self.store.entity(entity)

    def report(self, run_id: str | None = None, *, learning_status: str | None = None) -> Path:
        self.definition.report_root.mkdir(parents=True, exist_ok=True)
        performance = self.store.run_metrics(run_id)
        actual_run_id = performance.get("run_id")
        if not actual_run_id:
            data = {
                "schema_version": 3,
                "governance_version": "deterministic-semantic-human-v1",
                "pipeline_id": self.definition.pipeline_id,
                "run_id": run_id or "current-summary",
                "execution_status": "no_op",
                "learning_status": "not_required",
                "started_at": None,
                "finished_at": None,
                "summary": {"state": self.store.summary(), "run": {}, "failure_cohorts": self.store.failure_cohorts()},
                "state": self.store.summary(),
                "performance": performance,
                "failure_cohorts": self.store.failure_cohorts(),
                "attempts": [],
                "rejected_artifacts": [],
                "observations": ["No recorded run exists; this is a deterministic current-state summary."],
                "metrics": performance,
                "hypotheses": [],
                "recommendations": [],
            }
            path = self.definition.report_root / "current-summary.json"
        else:
            data = build_run_evidence(
                pipeline_id=self.definition.pipeline_id,
                run_evidence=self.store.run_evidence(str(actual_run_id)),
                state_summary=self.store.summary(),
                performance=performance,
                failure_cohorts=self.store.failure_cohorts(),
            )
            if learning_status is not None:
                data["learning_status"] = learning_status
            path = self.definition.report_root / f"{actual_run_id}.json"
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "run_evidence.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda error: list(error.path))
        if errors:
            location = ".".join(str(part) for part in errors[0].path) or "$"
            raise StateError(f"run evidence failed at {location}: {errors[0].message}")
        _atomic_write(path, (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
        narrative = path.with_suffix(".md")
        _atomic_write(narrative, render_run_markdown(data, path).encode("utf-8"))
        return path

    def analyze(self, run_id: str | None = None) -> Path:
        deterministic_path = self.report(run_id)
        deterministic = json.loads(deterministic_path.read_text(encoding="utf-8"))
        actual_run_id = deterministic["performance"].get("run_id") or run_id or "run-analysis"
        output: dict[str, Any] = {
            "schema_version": 1,
            "authority": "advisory_only",
            "deterministic_report": str(deterministic_path),
            "observations": deterministic,
            "cohort_analyses": [],
            "performance_analysis": None,
        }
        failure_stage = self.definition.analysis.get("failure")
        remediation_stage = self.definition.analysis.get("remediation")
        if failure_stage:
            for cohort in deterministic["failure_cohorts"]:
                representatives = []
                for entity in cohort["entity_ids"][:3]:
                    evidence = self.store.entity(entity)
                    if evidence:
                        representatives.append({"entity_id": entity, "state": evidence["entity"]["state"], "error_code": evidence["entity"]["error_code"], "transitions": [{"to_state": item["to_state"], "reason": item["reason"]} for item in evidence["transitions"]]})
                analysis, thread = self._invoke_analysis(
                    failure_stage,
                    {"cohort_definition": cohort, "representative_evidence": representatives, "run_context": deterministic["performance"]},
                    str(actual_run_id),
                    cohort["cohort_id"],
                )
                item: dict[str, Any] = {"cohort": cohort, "analysis": analysis, "thread": thread}
                if remediation_stage:
                    proposal, proposal_thread = self._invoke_analysis(
                        remediation_stage,
                        {"reviewed_cohort_analysis": analysis, "pipeline_contract": {"goal": self.definition.goal, "allowed_changes": self.definition.allowed_changes, "protected_invariants": self.definition.protected_invariants}},
                        str(actual_run_id),
                        cohort["cohort_id"],
                    )
                    item["remediation_proposal"] = proposal
                    item["remediation_thread"] = proposal_thread
                output["cohort_analyses"].append(item)
        performance_stage = self.definition.analysis.get("performance")
        if performance_stage:
            analysis, thread = self._invoke_analysis(
                performance_stage,
                {
                    "deterministic_run_metrics": deterministic["performance"],
                    "execution_trajectory": deterministic.get("attempts", []),
                    "evaluation_metrics": {"false_accept_rate": "unknown", "false_reject_rate": "unknown"},
                },
                str(actual_run_id),
                "performance",
            )
            output["performance_analysis"] = {"analysis": analysis, "thread": thread}
        path = self.definition.report_root / f"{actual_run_id}.post-run.json"
        _atomic_write(path, (json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
        if deterministic.get("run_id"):
            self.report(str(deterministic["run_id"]), learning_status="completed")
        return path

    def retry_cohort(self, report_path: Path, cohort_id: str) -> int:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        cohort = next((item for item in report.get("failure_cohorts", []) if item.get("cohort_id") == cohort_id), None)
        if cohort is None or not isinstance(cohort.get("entity_ids"), list):
            raise ValueError(f"cohort not found: {cohort_id}")
        return self.store.retry_entities([str(item) for item in cohort["entity_ids"]])

    def rollback_entity(self, entity: str) -> Path:
        evidence = self.store.entity(entity)
        if not evidence or evidence["entity"]["state"] != "promoted":
            raise StateError("only a promoted entity can be rolled back")
        promotion = self.store.latest_promotion(entity)
        if not promotion or promotion["status"] != "completed":
            raise StateError("completed promotion evidence is missing")
        source_path = Path(evidence["entity"]["source_path"])
        if digest(source_path) != promotion["candidate_hash"]:
            raise StateError("promoted source changed; refusing rollback")
        backup = Path(promotion["backup_path"])
        if not backup.exists() or digest(backup) != promotion["original_hash"]:
            raise StateError("promotion backup is missing or corrupt")
        _atomic_write(source_path, backup.read_bytes())
        self.store.finish_promotion(promotion["id"], "rolled_back")
        self.store.set_outcome(
            entity,
            "quarantined",
            candidate=evidence["entity"]["candidate_path"],
            accepted=evidence["entity"]["accepted_path"],
            error=("operator_rollback", "promotion was explicitly rolled back"),
            source_hash=promotion["original_hash"],
            evidence=str(backup),
        )
        return source_path
