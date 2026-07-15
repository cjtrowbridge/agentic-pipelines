"""Atomic, redacted evidence records for each local-inference call."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from .redaction import redact_value

_SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ThreadCaptureError(ValueError):
    """Raised when a caller supplies an unsafe evidence path component."""


def _safe_segment(value: str, name: str) -> str:
    if not _SAFE_SEGMENT.fullmatch(value):
        raise ThreadCaptureError(f"{name} must use only letters, digits, dot, underscore, or hyphen")
    return value


class ThreadCaptureWriter:
    """Writes captures under run/entity/stage/attempt paths without path traversal."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()

    def write(
        self,
        *,
        run_id: str,
        entity_id: str,
        entity_revision: str,
        stage: str,
        attempt_id: str,
        prompt_template_id: str,
        prompt_template_hash: str,
        request_payload: Mapping[str, Any],
        response_payload: Mapping[str, Any] | None,
        elapsed_seconds: float | None,
        usage: Mapping[str, int | float] | None,
        error: Mapping[str, Any] | None,
        provider: str,
        endpoint: str,
        model: str,
        sensitive_values: tuple[str, ...],
    ) -> Path:
        run_id = _safe_segment(run_id, "run_id")
        entity_id = _safe_segment(entity_id, "entity_id")
        entity_revision = _safe_segment(entity_revision, "entity_revision")
        stage = _safe_segment(stage, "stage")
        attempt_id = _safe_segment(attempt_id, "attempt_id")
        prompt_template_id = _safe_segment(prompt_template_id, "prompt_template_id")
        prompt_template_hash = _safe_segment(prompt_template_hash, "prompt_template_hash")
        payload: dict[str, Any] = {
            "schema_version": 1,
            "captured_at": datetime.now(UTC).isoformat(),
            "run_id": run_id,
            "entity_id": entity_id,
            "entity_revision": entity_revision,
            "stage": stage,
            "attempt_id": attempt_id,
            "prompt_template": {"id": prompt_template_id, "hash": prompt_template_hash},
            "provider": provider,
            "endpoint": endpoint,
            "model": model,
            "request": request_payload,
            "response": response_payload,
            "elapsed_seconds": elapsed_seconds,
            "usage": usage or {},
            "error": error,
            "redaction": {"configured_sensitive_value_count": len(tuple(value for value in sensitive_values if value))},
        }
        redacted = redact_value(payload, sensitive_values)
        encoded = (json.dumps(redacted, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        capture_hash = hashlib.sha256(encoded).hexdigest()
        target_dir = self.root / run_id / entity_id / entity_revision / stage
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{attempt_id}.json"
        if target.exists():
            existing_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            if existing_hash == capture_hash:
                return target
            raise ThreadCaptureError(f"capture already exists with different contents: {target}")
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{attempt_id}.", suffix=".tmp", dir=target_dir)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            Path(temporary_name).replace(target)
        finally:
            temporary = Path(temporary_name)
            if temporary.exists():
                temporary.unlink()
        return target
