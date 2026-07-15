"""Validation for reviewable, non-running pipeline packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .definition import load_definition
from .prompts import load_prompt


class PackageError(ValueError):
    """A staged package is incomplete, unsafe, or inconsistent."""


def _inside(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    if candidate != root and root not in candidate.parents:
        raise PackageError(f"package path escapes staging root: {value}")
    if candidate.name.lower() == "api.yaml":
        raise PackageError("a staged package must not contain api.yaml or credentials")
    if not candidate.exists():
        raise PackageError(f"package file is missing: {value}")
    return candidate


def validate_package(root: Path) -> dict[str, Any]:
    package_root = root.resolve()
    manifest_path = package_root / "package.yaml"
    if not manifest_path.exists():
        raise PackageError(f"package manifest not found: {manifest_path}")
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PackageError(f"invalid package YAML: {exc}") from exc
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "pipeline_package.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(manifest), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.path) or "$"
        raise PackageError(f"package manifest failed at {location}: {error.message}")
    assert isinstance(manifest, dict)
    definition_path = _inside(package_root, manifest["pipeline_definition"])
    definition = load_definition(definition_path)
    declared_prompts = {_inside(package_root, value) for value in manifest["prompt_files"]}
    stage_prompts = {stage.prompt_path for stage in (*definition.stages.values(), *definition.analysis.values())}
    if declared_prompts != stage_prompts:
        raise PackageError("package prompt_files must exactly match pipeline stages")
    for prompt_path in declared_prompts:
        load_prompt(prompt_path)
    for key in ("fixture_manifest", "api_sample", "scheduler_example"):
        _inside(package_root, manifest[key])
    for value in manifest["validator_files"]:
        _inside(package_root, value)
    return {"pipeline_id": definition.pipeline_id, "stages": sorted(definition.stages), "analysis": sorted(definition.analysis), "prompt_count": len(declared_prompts), "traceability_count": len(manifest["goal_traceability"])}
