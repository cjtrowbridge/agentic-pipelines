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


REQUIRED_REJECTED_EXCLUSIONS = {
    "git",
    "source_discovery",
    "example_retrieval",
    "prompt_assembly",
    "rendering",
    "promotion",
    "semantic_evidence",
}


def _validate_authority_matrix(rows: list[dict[str, Any]]) -> None:
    """Reject authority assignments that claim more than their mechanism proves."""
    for index, row in enumerate(rows):
        location = f"authority_matrix[{index}] ({row.get('id', 'unknown')})"
        property_class = row["property_class"]
        mechanism = row["mechanism"]
        authority = row["authority"]
        proof_basis = row["proof_basis"]
        heuristic_role = row["heuristic_role"]
        if property_class == "semantic" and authority not in {"semantic_model", "human", "none"}:
            raise PackageError(f"{location}: semantic verdicts require semantic_model or human authority")
        if property_class == "semantic" and authority == "none" and mechanism != "heuristic":
            raise PackageError(f"{location}: no-authority semantic mechanisms must be declared as routing heuristics")
        if property_class == "representational" and authority != "deterministic":
            raise PackageError(f"{location}: representational properties require deterministic authority")
        if property_class == "human_policy" and authority != "human":
            raise PackageError(f"{location}: human/policy properties require human authority")
        if mechanism == "heuristic":
            if authority != "none" or heuristic_role == "none":
                raise PackageError(f"{location}: heuristics must declare no verdict authority and a routing role")
        elif heuristic_role != "none":
            raise PackageError(f"{location}: only heuristic mechanisms may declare a heuristic role")
        if proof_basis == "exact_domain_rule" and not (property_class == "representational" and authority == "deterministic"):
            raise PackageError(f"{location}: exact domain rules may establish only representational properties deterministically")
        if authority == "semantic_model" and mechanism != "llm":
            raise PackageError(f"{location}: semantic_model authority requires an llm mechanism")
        if authority == "human" and mechanism != "human":
            raise PackageError(f"{location}: human authority requires a human mechanism")
        if authority == "deterministic" and mechanism in {"llm", "human"}:
            raise PackageError(f"{location}: llm/human mechanisms cannot claim deterministic authority")


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
    warnings: list[str] = []
    if manifest["schema_version"] == 1:
        warnings.append(
            "legacy package schema 1 has no enforceable authority/evidence declarations; migrate to schema 2 before claiming current governance conformance"
        )
    else:
        _validate_authority_matrix(manifest["authority_matrix"])
        exclusions = set(manifest["evidence_policy"]["excluded_from"])
        missing = sorted(REQUIRED_REJECTED_EXCLUSIONS - exclusions)
        if missing:
            raise PackageError(f"evidence_policy.excluded_from is missing required rejected-artifact boundaries: {missing}")
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
    return {
        "pipeline_id": definition.pipeline_id,
        "package_schema_version": manifest["schema_version"],
        "governance_conformant": manifest["schema_version"] == 2,
        "warnings": warnings,
        "stages": sorted(definition.stages),
        "analysis": sorted(definition.analysis),
        "prompt_count": len(declared_prompts),
        "traceability_count": len(manifest["goal_traceability"]),
    }
