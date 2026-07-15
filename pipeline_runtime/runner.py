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

from .api import InferenceClient, InferenceError, InferenceRequest
from .definition import PipelineDefinition, PromptStage
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
        for path in sorted(self.definition.source_root.glob(self.definition.source_glob)):
            if path.is_file() and self.store.upsert_discovered(entity_id(path, self.definition.source_root), str(path), digest(path), self.contract_hash):
                changed += 1
        return changed

    def _write_artifact(self, kind: str, entity: str, name: str, content: str | bytes) -> Path:
        path = self.definition.artifact_root / kind / entity / name
        encoded = content.encode("utf-8") if isinstance(content, str) else content
        _atomic_write(path, encoded)
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
        self.store.begin_attempt(attempt_id, run_id, entity, stage.name, prompt.prompt_id, prompt.version, prompt.content_hash)
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
            self.store.finish_attempt(attempt_id, "completed", thread=thread or None)
            return result, attempt_id, thread
        except (InferenceError, PromptError) as exc:
            thread_path = getattr(exc, "capture_path", None)
            safe = self.client.redact(str(exc))
            self.store.finish_attempt(attempt_id, "failed", thread=str(thread_path) if thread_path else None, error=("stage_error", safe))
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
                self.store.set_outcome(entity, "quarantined", error=("worker_unable", str(result.get("reason") or "worker returned unable")), thread=last_thread, prompt_hash=self.contract_hash, evidence=str(snapshot))
                return
            candidate = str(result["candidate"])
            if len(candidate.encode("utf-8")) > self.definition.runtime.max_candidate_bytes:
                self.store.set_outcome(entity, "quarantined", error=("candidate_too_large", f"candidate exceeds {self.definition.runtime.max_candidate_bytes} bytes"), thread=last_thread, prompt_hash=self.contract_hash)
                return
            staged = self._write_artifact("staged", entity, f"{attempt}.md", candidate)
            evidence, evidence_path = self._validate_candidate(run_id, entity, attempt, source, candidate)
            if not evidence.passed:
                repaired, repair_attempt, repair_thread = self._repair(source, candidate, list(evidence.failure_codes), run_id=run_id, entity=entity, revision=revision)
                if repaired is None:
                    self.store.set_outcome(entity, "quarantined", candidate=str(staged), error=(evidence.failure_codes[0], ", ".join(evidence.failure_codes)), thread=repair_thread or last_thread, prompt_hash=self.contract_hash, evidence=str(evidence_path))
                    return
                candidate = repaired
                attempt = repair_attempt
                last_thread = repair_thread or last_thread
                staged = self._write_artifact("staged", entity, f"{attempt}.md", candidate)
                evidence, evidence_path = self._validate_candidate(run_id, entity, attempt, source, candidate)
                if not evidence.passed:
                    self.store.set_outcome(entity, "quarantined", candidate=str(staged), error=(evidence.failure_codes[0], ", ".join(evidence.failure_codes)), thread=last_thread, evidence=str(evidence_path))
                    return
            review_passed, violations, review_thread = self._semantic_review(source, candidate, evidence, run_id=run_id, entity=entity, revision=revision)
            if not review_passed:
                action, adjudication_thread = self._adjudicate(source, candidate, evidence, violations, run_id=run_id, entity=entity, revision=revision)
                if action != "repair":
                    self.store.set_outcome(entity, "quarantined", candidate=str(staged), error=("semantic_review_failed", f"adjudication={action}; {json.dumps(violations, ensure_ascii=False)}"), thread=adjudication_thread or review_thread or last_thread, evidence=str(evidence_path))
                    return
                repaired, repair_attempt, repair_thread = self._repair(source, candidate, violations, run_id=run_id, entity=entity, revision=revision)
                if repaired is None:
                    self.store.set_outcome(entity, "quarantined", candidate=str(staged), error=("semantic_review_failed", json.dumps(violations, ensure_ascii=False)), thread=review_thread or last_thread, evidence=str(evidence_path))
                    return
                candidate = repaired
                attempt = repair_attempt
                last_thread = repair_thread or review_thread or last_thread
                staged = self._write_artifact("staged", entity, f"{attempt}.md", candidate)
                evidence, evidence_path = self._validate_candidate(run_id, entity, attempt, source, candidate)
                review_passed, violations, review_thread = self._semantic_review(source, candidate, evidence, run_id=run_id, entity=entity, revision=revision) if evidence.passed else (False, list(evidence.failure_codes), "")
                if not evidence.passed or not review_passed:
                    self.store.set_outcome(entity, "quarantined", candidate=str(staged), error=("repair_not_accepted", json.dumps(violations, ensure_ascii=False)), thread=review_thread or last_thread, evidence=str(evidence_path))
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
            return {"eligible": len(eligible), "entity_ids": [row["id"] for row in eligible], "state": self.store.summary()}
        run_id = f"run-{uuid.uuid4().hex[:16]}"
        owner = f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        lock_seconds = max(self.definition.runtime.lock_stale_seconds, int(runtime_minutes * 60) + 60)
        self.store.acquire_lock(owner, run_id, lock_seconds)
        self.store.recover_expired_leases()
        eligible = self.store.eligible(maximum)
        self.store.start_run(run_id)
        started = time.monotonic()
        status = "completed"
        try:
            for row in eligible:
                if time.monotonic() - started >= runtime_minutes * 60:
                    status = "bounded_stop"
                    break
                self._process(row, run_id, owner)
        except KeyboardInterrupt:
            status = "interrupted"
        finally:
            self.store.finish_run(run_id, status)
            self.store.release_lock(owner, run_id)
        report = self.report(run_id)
        return {"run_id": run_id, "status": status, "state": self.store.summary(), "report": str(report)}

    def inspect(self, entity: str) -> dict[str, Any] | None:
        return self.store.entity(entity)

    def report(self, run_id: str | None = None) -> Path:
        self.definition.report_root.mkdir(parents=True, exist_ok=True)
        data = {"schema_version": 1, "pipeline_id": self.definition.pipeline_id, "run_id": run_id, "state": self.store.summary(), "performance": self.store.run_metrics(run_id), "failure_cohorts": self.store.failure_cohorts()}
        path = self.definition.report_root / (f"{run_id}.json" if run_id else "current-summary.json")
        _atomic_write(path, (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
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
                {"deterministic_run_metrics": deterministic["performance"], "evaluation_metrics": {"false_accept_rate": "unknown", "false_reject_rate": "unknown"}},
                str(actual_run_id),
                "performance",
            )
            output["performance_analysis"] = {"analysis": analysis, "thread": thread}
        path = self.definition.report_root / f"{actual_run_id}.post-run.json"
        _atomic_write(path, (json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
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
