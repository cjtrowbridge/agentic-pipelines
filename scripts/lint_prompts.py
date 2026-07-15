#!/usr/bin/env python3
"""Validate prompt identity, metadata, contracts, and narrow authority."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

VERSION = re.compile(r"^\d+\.\d+\.\d+$")
ID = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
FORBIDDEN_RUNTIME_AUTHORITY = (
    "change the pipeline",
    "modify the pipeline",
    "write credentials",
    "change validation",
    "enqueue retries",
    "select any file",
)


def parse(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("missing YAML front matter")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError("front matter must be a mapping")
    return data, parts[2].strip()


def _substantive_schema(definition: object) -> bool:
    if not isinstance(definition, dict):
        return False
    if "$ref" in definition:
        return True
    return bool(definition.get("required")) and isinstance(definition.get("properties"), dict)


def lint(root: Path) -> list[str]:
    manifest = yaml.safe_load((root / "manifest.yaml").read_text(encoding="utf-8"))
    required = manifest["required_metadata"]
    allowed_kinds = set(manifest["allowed_kinds"])
    allowed_roles = set(manifest["allowed_model_roles"])
    schema_path = (root / manifest["output_schema"]).resolve()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    outputs = schema["$defs"]
    errors: list[str] = []
    seen: dict[str, Path] = {}
    for path in sorted(root.glob("*/*.md")):
        if path.name == "README.md":
            continue
        try:
            data, body = parse(path)
        except Exception as exc:
            errors.append(f"{path}: {exc}")
            continue
        missing = [key for key in required if key not in data]
        if missing:
            errors.append(f"{path}: missing metadata {missing}")
            continue
        prompt_id = str(data["id"])
        version = str(data["version"])
        output = str(data["output"])
        inputs = data["inputs"]
        if not ID.fullmatch(prompt_id):
            errors.append(f"{path}: invalid id {prompt_id}")
        if prompt_id in seen:
            errors.append(f"{path}: duplicate id also in {seen[prompt_id]}")
        seen[prompt_id] = path
        if not VERSION.fullmatch(version):
            errors.append(f"{path}: invalid semantic version {version}")
        if data["kind"] not in allowed_kinds:
            errors.append(f"{path}: invalid kind {data['kind']}")
        if data["model_role"] not in allowed_roles:
            errors.append(f"{path}: invalid model_role {data['model_role']}")
        if not isinstance(inputs, list) or not inputs or not all(isinstance(item, str) and item for item in inputs):
            errors.append(f"{path}: inputs must be a nonempty YAML list")
        elif len(inputs) != len(set(inputs)):
            errors.append(f"{path}: duplicate input names")
        if output not in outputs:
            errors.append(f"{path}: unknown output contract {output}")
        elif not _substantive_schema(outputs[output]):
            errors.append(f"{path}: output contract {output} is only a placeholder")
        if not body:
            errors.append(f"{path}: empty prompt body")
        if "{{" in body or "}}" in body:
            errors.append(f"{path}: unresolved inline placeholder; inputs are rendered structurally")
        if data["kind"] == "pipeline-running":
            lowered = body.lower()
            for phrase in FORBIDDEN_RUNTIME_AUTHORITY:
                if phrase in lowered and "cannot" not in lowered and "do not" not in lowered:
                    errors.append(f"{path}: forbidden runtime authority phrase: {phrase}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("prompts"))
    args = parser.parse_args()
    errors = lint(args.root)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    count = len([path for path in args.root.glob("*/*.md") if path.name != "README.md"])
    print(f"Prompt catalog valid: {count} prompts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
