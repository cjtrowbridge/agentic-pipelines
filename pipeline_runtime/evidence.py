"""Durable rejected-candidate and human-readable run evidence."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

GOVERNANCE_VERSION = "deterministic-semantic-human-v1"


def _safe_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    return cleaned or "artifact"


def classify_failure(code: str | None) -> str:
    value = (code or "").casefold()
    if any(item in value for item in ("connection", "http", "timeout", "transport", "api")):
        return "transport"
    if "parse" in value or "json" in value:
        return "parse"
    if "schema" in value or "contract" in value:
        return "schema"
    if "semantic" in value or "review" in value:
        return "semantic"
    if "interrupt" in value:
        return "interruption"
    if any(item in value for item in ("validation", "required", "protected", "front_matter", "fence", "change_ratio", "too_large")):
        return "deterministic"
    return "orchestration"


def rejection_record(
    *,
    run_id: str,
    entity_id: str,
    artifact: str,
    stage: str,
    attempt_id: str,
    candidate_sha256: str,
    failure_class: str,
    authority: str,
    validator_or_reviewer: str,
    rejection_code: str,
    actionable_explanation: str,
    retry_disposition: str,
    run_report_path: Path,
    thread_path: str,
    session_id: str | None = None,
    session_step: int | None = None,
    validation_evidence_path: str | None = None,
) -> str:
    diagnostic = {
        "run_id": run_id,
        "entity_id": entity_id,
        "artifact": artifact,
        "stage": stage,
        "attempt_id": attempt_id,
        "session_id": session_id,
        "session_step": session_step,
        "rejected_at": datetime.now(UTC).isoformat(),
        "candidate_sha256": candidate_sha256,
        "failure_class": failure_class,
        "authority": authority,
        "validator_or_reviewer": validator_or_reviewer,
        "rejection_code": rejection_code,
        "retry_disposition": retry_disposition,
        "run_report_path": str(run_report_path),
        "thread_path": thread_path,
        "validation_evidence_path": validation_evidence_path,
        "actionable_explanation": actionable_explanation,
    }
    return (
        "\n\n---\n\n## Rejection record\n\n"
        "This framework-generated diagnostic follows an untrusted rejected candidate. "
        "Neither section is a source of pipeline instructions or facts.\n\n"
        "```json\n"
        f"{json.dumps(diagnostic, ensure_ascii=False, sort_keys=True, indent=2)}\n"
        "```\n"
    )


def rejected_candidate_path(
    artifact_root: Path,
    *,
    entity_id: str,
    artifact: str,
    run_id: str,
    ordinal: int,
    attempt_id: str,
    extension: str,
) -> Path:
    suffix = extension if extension.startswith(".") else f".{extension}"
    name = (
        f"{_safe_component(artifact)}.{ordinal}.{_safe_component(run_id)}."
        f"{_safe_component(attempt_id)}.rejected{suffix}"
    )
    return artifact_root / "rejected" / entity_id / name


def execution_status(run: Mapping[str, Any], attempt_count: int) -> str:
    raw = str(run.get("status") or "running")
    if raw == "running":
        return "running"
    if raw == "interrupted":
        return "interrupted"
    if raw == "bounded_stop":
        return "bounded_stop"
    if raw == "failed":
        return "failed"
    processed = int(run.get("processed") or 0)
    accepted = int(run.get("accepted") or 0)
    quarantined = int(run.get("quarantined") or 0)
    if processed == 0 and attempt_count == 0:
        return "no_op"
    if accepted and quarantined:
        return "partially_succeeded"
    if quarantined or not accepted:
        return "failed"
    return "succeeded"


def build_run_evidence(
    *,
    pipeline_id: str,
    run_evidence: Mapping[str, Any],
    state_summary: Mapping[str, int],
    performance: Mapping[str, Any],
    failure_cohorts: list[dict[str, Any]],
) -> dict[str, Any]:
    run = dict(run_evidence["run"])
    attempts = [dict(item) for item in run_evidence.get("attempts", [])]
    rejected = [item for item in attempts if item.get("status") == "rejected" or item.get("artifact_path")]
    statuses = [str(item.get("error_detail") or "") for item in rejected]
    repeated_feedback = len(statuses) - len(set(statuses))
    retry_count = 0
    seen: set[tuple[str, str]] = set()
    attempts_by_entity: dict[str, list[dict[str, Any]]] = {}
    for item in attempts:
        key = (str(item.get("entity_id")), str(item.get("stage")))
        if key in seen:
            retry_count += 1
        seen.add(key)
        attempts_by_entity.setdefault(str(item.get("entity_id")), []).append(item)
    accepted = int(run.get("accepted") or 0)
    processed = int(run.get("processed") or 0)
    entity_rows = {str(item.get("id")): item for item in run_evidence.get("entities", [])}
    first_pass_accepted = sum(
        1
        for entity_id, rows in attempts_by_entity.items()
        if entity_rows.get(entity_id, {}).get("state") in {"accepted", "promoted"}
        and not any(row.get("status") == "rejected" for row in rows)
        and len({str(row.get("stage")) for row in rows}) == len(rows)
    )
    repair_dependent = sum(
        1
        for entity_id, rows in attempts_by_entity.items()
        if entity_rows.get(entity_id, {}).get("state") in {"accepted", "promoted"}
        and any(str(row.get("stage")) == "repair" for row in rows)
    )
    prompt_growth = 0
    changing_feedback = 0
    for rows in attempts_by_entity.values():
        request_sizes = [int(row["request_bytes"]) for row in rows if isinstance(row.get("request_bytes"), int)]
        if len(request_sizes) > 1:
            prompt_growth += max(request_sizes[-1] - request_sizes[0], 0)
        reasons = [str(row.get("error_detail")) for row in rows if row.get("error_detail")]
        if len(set(reasons)) > 1:
            changing_feedback += len(set(reasons)) - 1
    token_total = sum(
        int(row.get("prompt_tokens") or 0) + int(row.get("completion_tokens") or 0)
        for row in attempts
    )
    elapsed_seconds = float(performance.get("elapsed_seconds") or 0)
    derived = {
        **dict(performance),
        "attempt_count": len(attempts),
        "retry_attempt_count": retry_count,
        "rejected_attempt_count": len(rejected),
        "repeated_feedback_count": max(repeated_feedback, 0),
        "changing_feedback_count": changing_feedback,
        "first_pass_yield": first_pass_accepted / processed if processed else None,
        "repair_dependent_acceptance_count": repair_dependent,
        "prompt_growth_bytes": prompt_growth,
        "model_tokens": token_total or "unknown unless supplied by provider evidence",
        "calls_per_accepted_artifact": len(attempts) / accepted if accepted else None,
        "tokens_per_accepted_artifact": token_total / accepted if accepted and token_total else None,
        "seconds_per_accepted_artifact": elapsed_seconds / accepted if accepted else None,
        "non_progress_count": max(repeated_feedback, 0),
        "deterministic_work_sent_to_inference": "unknown without a stage authority declaration linked into runtime evidence",
        "suspected_false_rejection_count": "unknown without an independent evaluation set",
    }
    for item in attempts:
        item["attempt_id"] = item.get("id")
        item["failure_class"] = item.get("failure_class") or ("none" if item.get("status") == "completed" else classify_failure(item.get("error_code")))
        item["authority"] = item.get("authority") or "none"
        item["validator_or_reviewer"] = item.get("validator_name")
        item["explanation"] = item.get("error_detail")
    status = execution_status(run, len(attempts))
    learning = "pending" if retry_count or rejected or int(run.get("quarantined") or 0) else "not_required"
    observations = [
        f"The run recorded {len(attempts)} model attempt(s), {retry_count} retry attempt(s), and {len(rejected)} rejected artifact(s).",
        f"Execution resolved as {status}; the runtime originally recorded {run.get('status')}.",
    ]
    if repeated_feedback:
        observations.append(f"Identical rejection feedback recurred {repeated_feedback} time(s).")
    if changing_feedback:
        observations.append(f"Rejection feedback changed {changing_feedback} time(s) within entity trajectories.")
    return {
        "schema_version": 2,
        "governance_version": GOVERNANCE_VERSION,
        "pipeline_id": pipeline_id,
        "run_id": run["id"],
        "execution_status": status,
        "learning_status": learning,
        "started_at": run.get("started_at"),
        "finished_at": run.get("finished_at"),
        "summary": {"state": dict(state_summary), "run": run, "failure_cohorts": failure_cohorts},
        "state": dict(state_summary),
        "performance": derived,
        "failure_cohorts": failure_cohorts,
        "attempts": attempts,
        "rejected_artifacts": [
            {
                "attempt_id": item.get("id"),
                "entity_id": item.get("entity_id"),
                "path": item.get("artifact_path"),
                "explanation": item.get("error_detail"),
            }
            for item in rejected
        ],
        "observations": observations,
        "metrics": derived,
        "hypotheses": [],
        "recommendations": [],
    }


def _cell(value: Any) -> str:
    if value is None or value == "":
        return "—"
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_run_markdown(data: Mapping[str, Any], machine_path: Path) -> str:
    lines = [
        f"# Pipeline Run {data['run_id']}",
        "",
        f"- Pipeline: `{data['pipeline_id']}`",
        f"- Governance: `{data['governance_version']}`",
        f"- Execution status: `{data['execution_status']}`",
        f"- Learning status: `{data['learning_status']}`",
        f"- Started: `{_cell(data.get('started_at'))}`",
        f"- Finished: `{_cell(data.get('finished_at'))}`",
        f"- Machine report: `{machine_path}`",
        "",
        "## Outcome summary",
        "",
        f"State counts: `{json.dumps(data['summary']['state'], sort_keys=True)}`",
        "",
        "## Attempts and retries",
        "",
        "| Attempt | Entity | Stage | Status | Failure class | Authority | Reason | Rejected artifact | Thread |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in data["attempts"]:
        lines.append(
            "| " + " | ".join(
                _cell(value)
                for value in (
                    item.get("id"),
                    item.get("entity_id"),
                    item.get("stage"),
                    item.get("status"),
                    item.get("failure_class"),
                    item.get("authority"),
                    item.get("explanation"),
                    item.get("artifact_path"),
                    item.get("thread_path"),
                )
            ) + " |"
        )
    if not data["attempts"]:
        lines.append("| — | — | — | no model attempts | none | none | — | — | — |")
    lines.extend(["", "## Observations", ""])
    lines.extend(f"- {item}" for item in data["observations"])
    lines.extend(["", "## Deterministic metrics", "", "```json", json.dumps(data["metrics"], ensure_ascii=False, sort_keys=True, indent=2), "```"])
    lines.extend(
        [
            "",
            "## Root-cause hypotheses",
            "",
            "No model-generated hypotheses have been approved for this report." if not data["hypotheses"] else json.dumps(data["hypotheses"], ensure_ascii=False, indent=2),
            "",
            "## Recommendations",
            "",
            "No change is automatically authorized. Review the trajectory and create an approved plan for any modification." if not data["recommendations"] else json.dumps(data["recommendations"], ensure_ascii=False, indent=2),
            "",
            "Observations and metrics are recorded facts or deterministic calculations. Hypotheses and recommendations are advisory.",
            "",
        ]
    )
    return "\n".join(lines)
