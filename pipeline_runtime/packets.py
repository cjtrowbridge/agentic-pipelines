"""Deterministic source provenance and complete model-packet accounting."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class SourceRecord:
    """One discoverable input/output with a declared representational role."""

    source_id: str
    path: str
    role: str
    media_type: str
    sha256: str
    derivative_path: str | None = None
    derivative_sha256: str | None = None
    discovery_authority: str = "deterministic"
    disposition: str = "included"

    @classmethod
    def from_path(
        cls, path: Path, *, source_id: str, role: str, media_type: str,
        derivative: Path | None = None, disposition: str = "included",
    ) -> "SourceRecord":
        raw = path.read_bytes()
        derivative_raw = derivative.read_bytes() if derivative and derivative.is_file() else None
        return cls(
            source_id=source_id, path=str(path), role=role, media_type=media_type,
            sha256=hashlib.sha256(raw).hexdigest(), derivative_path=str(derivative) if derivative else None,
            derivative_sha256=hashlib.sha256(derivative_raw).hexdigest() if derivative_raw is not None else None,
            disposition=disposition,
        )


@dataclass(frozen=True)
class PacketManifest:
    """Non-secret accounting for one complete model request before transport."""

    stage: str
    allowed_roles: tuple[str, ...]
    component_bytes: Mapping[str, int]
    selected_source_ids: tuple[str, ...]
    omitted_source_ids: tuple[str, ...]
    static_prompt_bytes: int
    assembled_request_bytes: int
    context_limit: int
    completion_limit: int
    reduction_reason: str | None = None
    batch_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage, "allowed_roles": list(self.allowed_roles),
            "component_bytes": dict(self.component_bytes),
            "selected_source_ids": list(self.selected_source_ids),
            "omitted_source_ids": list(self.omitted_source_ids),
            "static_prompt_bytes": self.static_prompt_bytes,
            "assembled_request_bytes": self.assembled_request_bytes,
            "context_limit": self.context_limit, "completion_limit": self.completion_limit,
            "reduction_reason": self.reduction_reason, "batch_id": self.batch_id,
        }


class PacketBudgetError(ValueError):
    """No complete, declared request fits the stage budget."""


def utf8_size(value: object) -> int:
    """Measure the exact UTF-8 representation used in a JSON packet."""
    return len(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def bounded_records(
    records: Iterable[SourceRecord], *, allowed_roles: set[str], max_bytes: int,
) -> tuple[list[SourceRecord], list[SourceRecord]]:
    """Keep source order, roles, and whole records; never truncate a record invisibly."""
    selected: list[SourceRecord] = []
    omitted: list[SourceRecord] = []
    used = 0
    for record in records:
        if record.role not in allowed_roles or record.disposition != "included":
            omitted.append(record)
            continue
        size = utf8_size(record.__dict__)
        if selected and used + size > max_bytes:
            omitted.append(record)
            continue
        selected.append(record)
        used += size
    return selected, omitted


def require_packet_budget(manifest: PacketManifest, *, max_request_bytes: int) -> None:
    """Reject an oversized complete request before any provider transport occurs."""
    if manifest.assembled_request_bytes > max_request_bytes:
        raise PacketBudgetError(
            f"packet_budget_exhausted: {manifest.stage} assembled {manifest.assembled_request_bytes} bytes "
            f"above declared {max_request_bytes} bytes"
        )
