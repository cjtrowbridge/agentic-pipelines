"""Strict schema-v2 loading for a host-owned pipeline definition."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


class DefinitionError(ValueError):
    """The pipeline definition is missing, unsafe, or internally inconsistent."""


@dataclass(frozen=True)
class PromptStage:
    name: str
    prompt_path: Path
    prompt_id: str
    prompt_version: str
    output_schema: str
    llm_justification: str
    max_attempts: int = 1


@dataclass(frozen=True)
class ValidationPolicy:
    required_substrings: tuple[str, ...]
    protected_substrings: tuple[str, ...]
    max_change_ratio: float
    require_front_matter: bool
    require_balanced_fences: bool


@dataclass(frozen=True)
class RuntimePolicy:
    lease_seconds: int
    max_repairs: int
    lock_stale_seconds: int
    max_source_bytes: int
    max_candidate_bytes: int


@dataclass(frozen=True)
class PromotionPolicy:
    enabled: bool
    backup_root: Path


@dataclass(frozen=True)
class PipelineDefinition:
    path: Path
    root: Path
    pipeline_id: str
    goal: str
    allowed_changes: tuple[str, ...]
    protected_invariants: tuple[str, ...]
    source_root: Path
    source_glob: str
    state_path: Path
    artifact_root: Path
    thread_root: Path
    report_root: Path
    output_schema_path: Path
    stages: Mapping[str, PromptStage]
    analysis: Mapping[str, PromptStage]
    validation: ValidationPolicy
    runtime: RuntimePolicy
    promotion: PromotionPolicy


def _mapping(value: Any, name: str, *, default: bool = False) -> Mapping[str, Any]:
    if value is None and default:
        return {}
    if not isinstance(value, dict):
        raise DefinitionError(f"{name} must be a mapping")
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DefinitionError(f"{name} must be a nonempty string")
    return value.strip()


def _string_list(value: Any, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise DefinitionError(f"{name} must be a list of nonempty strings")
    return tuple(value)


def _boolean(value: Any, name: str, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise DefinitionError(f"{name} must be a boolean")
    return value


def _integer(value: Any, name: str, default: int, minimum: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise DefinitionError(f"{name} must be an integer >= {minimum}")
    return value


def _path(root: Path, value: Any, name: str) -> Path:
    text = _string(value, name)
    candidate = (root / text).resolve()
    if candidate != root and root not in candidate.parents:
        raise DefinitionError(f"{name} escapes the host root")
    return candidate


def _schema_path(root: Path, value: Any, name: str) -> Path:
    framework_root = Path(__file__).resolve().parents[1]
    text = _string(value, name)
    candidate = (framework_root / text.removeprefix("@framework/")).resolve() if text.startswith("@framework/") else (root / text).resolve()
    if candidate != root and root not in candidate.parents and candidate != framework_root and framework_root not in candidate.parents:
        raise DefinitionError(f"{name} must remain in the host or Pipelines framework root")
    return candidate


def _stage(root: Path, name: str, value: Any) -> PromptStage:
    data = _mapping(value, f"stages.{name}")
    return PromptStage(
        name=name,
        prompt_path=_path(root, data.get("prompt"), f"stages.{name}.prompt"),
        prompt_id=_string(data.get("id"), f"stages.{name}.id"),
        prompt_version=_string(data.get("version"), f"stages.{name}.version"),
        output_schema=_string(data.get("output"), f"stages.{name}.output"),
        llm_justification=_string(data.get("llm_justification"), f"stages.{name}.llm_justification"),
        max_attempts=_integer(data.get("max_attempts"), f"stages.{name}.max_attempts", 1, 1),
    )


def load_definition(path: Path | str) -> PipelineDefinition:
    definition_path = Path(path).resolve()
    root = definition_path.parent
    if not definition_path.exists():
        raise DefinitionError(f"pipeline definition not found: {definition_path}")
    try:
        raw = yaml.safe_load(definition_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise DefinitionError(f"invalid pipeline YAML: {exc}") from exc
    data = _mapping(raw, "pipeline definition")
    if data.get("schema_version") != 2:
        raise DefinitionError("schema_version must be 2; schema v1 was a non-contract prototype")
    pipeline_id = _string(data.get("pipeline_id"), "pipeline_id")
    if not pipeline_id.replace("-", "").replace("_", "").isalnum():
        raise DefinitionError("pipeline_id must be alphanumeric with hyphens/underscores")
    contract = _mapping(data.get("contract"), "contract")
    source = _mapping(data.get("source"), "source")
    paths = _mapping(data.get("paths"), "paths")
    stage_data = _mapping(data.get("stages"), "stages")
    unknown_stages = set(stage_data) - {"worker", "self_review", "reviewer", "repair", "adjudicator"}
    if unknown_stages:
        raise DefinitionError(f"unknown stages: {sorted(unknown_stages)}")
    if "worker" not in stage_data:
        raise DefinitionError("stages.worker is required")
    stages = {name: _stage(root, name, value) for name, value in stage_data.items()}
    analysis_data = _mapping(data.get("analysis"), "analysis", default=True)
    unknown_analysis = set(analysis_data) - {"failure", "performance", "remediation"}
    if unknown_analysis:
        raise DefinitionError(f"unknown analysis stages: {sorted(unknown_analysis)}")
    analysis = {name: _stage(root, name, value) for name, value in analysis_data.items()}
    validation_data = _mapping(data.get("validation"), "validation", default=True)
    ratio = validation_data.get("max_change_ratio", 1.0)
    if isinstance(ratio, bool) or not isinstance(ratio, (int, float)) or not 0 <= ratio <= 1:
        raise DefinitionError("validation.max_change_ratio must be between 0 and 1")
    runtime_data = _mapping(data.get("runtime"), "runtime", default=True)
    promotion_data = _mapping(data.get("promotion"), "promotion", default=True)
    source_glob = source.get("glob", "**/*.md")
    if not isinstance(source_glob, str) or not source_glob:
        raise DefinitionError("source.glob must be a nonempty string")
    definition = PipelineDefinition(
        path=definition_path,
        root=root,
        pipeline_id=pipeline_id,
        goal=_string(contract.get("goal"), "contract.goal"),
        allowed_changes=_string_list(contract.get("allowed_changes", []), "contract.allowed_changes"),
        protected_invariants=_string_list(contract.get("protected_invariants", []), "contract.protected_invariants"),
        source_root=_path(root, source.get("root"), "source.root"),
        source_glob=source_glob,
        state_path=_path(root, paths.get("state", "state/pipeline.sqlite"), "paths.state"),
        artifact_root=_path(root, paths.get("artifacts", "artifacts"), "paths.artifacts"),
        thread_root=_path(root, paths.get("threads", "threads"), "paths.threads"),
        report_root=_path(root, paths.get("reports", "reports"), "paths.reports"),
        output_schema_path=_schema_path(root, paths.get("output_schema"), "paths.output_schema"),
        stages=stages,
        analysis=analysis,
        validation=ValidationPolicy(
            required_substrings=_string_list(validation_data.get("required_substrings", []), "validation.required_substrings"),
            protected_substrings=_string_list(validation_data.get("protected_substrings", []), "validation.protected_substrings"),
            max_change_ratio=float(ratio),
            require_front_matter=_boolean(validation_data.get("require_front_matter"), "validation.require_front_matter", True),
            require_balanced_fences=_boolean(validation_data.get("require_balanced_fences"), "validation.require_balanced_fences", True),
        ),
        runtime=RuntimePolicy(
            lease_seconds=_integer(runtime_data.get("lease_seconds"), "runtime.lease_seconds", 900, 30),
            max_repairs=_integer(runtime_data.get("max_repairs"), "runtime.max_repairs", 1),
            lock_stale_seconds=_integer(runtime_data.get("lock_stale_seconds"), "runtime.lock_stale_seconds", 3600, 60),
            max_source_bytes=_integer(runtime_data.get("max_source_bytes"), "runtime.max_source_bytes", 1_000_000, 1),
            max_candidate_bytes=_integer(runtime_data.get("max_candidate_bytes"), "runtime.max_candidate_bytes", 1_000_000, 1),
        ),
        promotion=PromotionPolicy(
            enabled=_boolean(promotion_data.get("enabled"), "promotion.enabled", False),
            backup_root=_path(root, promotion_data.get("backup_root", "artifacts/backups"), "promotion.backup_root"),
        ),
    )
    for stage in (*definition.stages.values(), *definition.analysis.values()):
        if not stage.prompt_path.exists():
            raise DefinitionError(f"stage prompt not found: {stage.prompt_path}")
    if not definition.output_schema_path.exists():
        raise DefinitionError(f"output schema not found: {definition.output_schema_path}")
    if not definition.source_root.is_dir():
        raise DefinitionError(f"source root not found: {definition.source_root}")
    return definition
