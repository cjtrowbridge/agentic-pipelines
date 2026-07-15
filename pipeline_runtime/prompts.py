"""Versioned prompt loading, minimal-context rendering, and output validation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator


class PromptError(ValueError):
    """A prompt contract, rendering input, or model output is invalid."""


@dataclass(frozen=True)
class PromptContract:
    path: Path
    prompt_id: str
    version: str
    kind: str
    model_role: str
    inputs: tuple[str, ...]
    output: str
    body: str
    content_hash: str

    def render(self, values: Mapping[str, Any]) -> str:
        missing = [name for name in self.inputs if name not in values]
        extra = sorted(set(values) - set(self.inputs))
        if missing or extra:
            raise PromptError(f"prompt input mismatch: missing={missing}, extra={extra}")
        payload = {name: values[name] for name in self.inputs}
        return f"{self.body}\n\nINPUTS\n{json.dumps(payload, ensure_ascii=False, sort_keys=True)}"


class OutputSchemas:
    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        try:
            self.document = json.loads(self.path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(self.document)
        except (OSError, json.JSONDecodeError, Exception) as exc:
            if isinstance(exc, PromptError):
                raise
            raise PromptError(f"invalid output schema {self.path}: {exc}") from exc
        definitions = self.document.get("$defs")
        if not isinstance(definitions, dict):
            raise PromptError("output schema must define $defs")

    def has(self, name: str) -> bool:
        return name in self.document["$defs"]

    def schema_for(self, name: str) -> dict[str, Any]:
        if not self.has(name):
            raise PromptError(f"unknown output schema: {name}")
        return {"$ref": f"#/$defs/{name}", "$defs": self.document["$defs"]}

    def validate(self, name: str, text: str) -> Mapping[str, Any]:
        if not self.has(name):
            raise PromptError(f"unknown output schema: {name}")
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise PromptError(f"model output is not strict JSON: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise PromptError("model output must be a JSON object")
        schema = self.schema_for(name)
        errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda item: list(item.path))
        if errors:
            first = errors[0]
            location = ".".join(str(part) for part in first.absolute_path) or "$"
            raise PromptError(f"model output failed {name} at {location}: {first.message}")
        return value


def load_prompt(
    path: Path,
    *,
    expected_id: str | None = None,
    expected_version: str | None = None,
    expected_output: str | None = None,
) -> PromptContract:
    resolved = path.resolve()
    try:
        raw = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise PromptError(f"cannot read prompt {resolved}: {exc}") from exc
    parts = raw.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise PromptError(f"prompt {resolved} is missing YAML front matter")
    try:
        metadata = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        raise PromptError(f"invalid prompt metadata in {resolved}: {exc}") from exc
    if not isinstance(metadata, dict):
        raise PromptError(f"prompt metadata in {resolved} must be a mapping")
    required = ("id", "version", "kind", "model_role", "inputs", "output")
    missing = [key for key in required if key not in metadata]
    if missing:
        raise PromptError(f"prompt {resolved} is missing metadata: {missing}")
    inputs = metadata["inputs"]
    if not isinstance(inputs, list) or not inputs or not all(isinstance(item, str) and item for item in inputs):
        raise PromptError(f"prompt {resolved} inputs must be a nonempty list of names")
    body = parts[2].strip()
    if not body:
        raise PromptError(f"prompt {resolved} has an empty body")
    contract = PromptContract(
        path=resolved,
        prompt_id=str(metadata["id"]),
        version=str(metadata["version"]),
        kind=str(metadata["kind"]),
        model_role=str(metadata["model_role"]),
        inputs=tuple(inputs),
        output=str(metadata["output"]),
        body=body,
        content_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    )
    expected = (("id", expected_id, contract.prompt_id), ("version", expected_version, contract.version), ("output", expected_output, contract.output))
    for label, wanted, actual in expected:
        if wanted is not None and wanted != actual:
            raise PromptError(f"prompt {label} mismatch for {resolved}: expected {wanted}, found {actual}")
    return contract
