"""Deterministic, goal-specific candidate validation with stable evidence codes."""

from __future__ import annotations

import difflib
from dataclasses import asdict, dataclass
from typing import Any

import yaml

from .definition import ValidationPolicy


@dataclass(frozen=True)
class CheckResult:
    id: str
    passed: bool
    code: str
    detail: str
    metrics: dict[str, Any]


@dataclass(frozen=True)
class ValidationEvidence:
    passed: bool
    results: tuple[CheckResult, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "results": [asdict(item) for item in self.results]}

    @property
    def failure_codes(self) -> tuple[str, ...]:
        return tuple(item.code for item in self.results if not item.passed)


def _front_matter(text: str) -> tuple[bool, object | None]:
    if not text.startswith("---\n"):
        return False, None
    end = text.find("\n---", 4)
    if end < 0:
        return True, None
    try:
        return True, yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return True, None


def validate(source: str, candidate: str, policy: ValidationPolicy) -> ValidationEvidence:
    results: list[CheckResult] = []
    nonempty = bool(candidate.strip())
    results.append(CheckResult("nonempty", nonempty, "ok" if nonempty else "empty_output", "candidate contains content" if nonempty else "candidate is empty", {}))

    if policy.require_front_matter:
        source_has, source_front = _front_matter(source)
        candidate_has, candidate_front = _front_matter(candidate)
        passed = not source_has or (candidate_has and source_front is not None and candidate_front == source_front)
        results.append(CheckResult("front_matter", passed, "ok" if passed else "front_matter_changed", "source front matter is preserved exactly" if passed else "front matter is missing, malformed, or changed", {}))

    if policy.require_balanced_fences:
        fence_count = sum(1 for line in candidate.splitlines() if line.lstrip().startswith("```"))
        passed = fence_count % 2 == 0
        results.append(CheckResult("balanced_fences", passed, "ok" if passed else "unbalanced_code_fence", f"candidate contains {fence_count} fenced-code delimiters", {"fence_count": fence_count}))

    for index, required in enumerate(policy.required_substrings):
        passed = required in candidate
        results.append(CheckResult(f"required_{index}", passed, "ok" if passed else "required_content_missing", "required content is present" if passed else f"required content is missing: {required!r}", {}))

    for index, protected in enumerate(policy.protected_substrings):
        source_count = source.count(protected)
        candidate_count = candidate.count(protected)
        passed = source_count == candidate_count
        results.append(CheckResult(f"protected_{index}", passed, "ok" if passed else "protected_content_changed", f"protected occurrence count source={source_count}, candidate={candidate_count}", {"source_count": source_count, "candidate_count": candidate_count}))

    ratio = 1 - difflib.SequenceMatcher(a=source, b=candidate).ratio()
    passed = ratio <= policy.max_change_ratio
    results.append(CheckResult("change_ratio", passed, "ok" if passed else "change_ratio_exceeded", f"change ratio {ratio:.4f}; maximum {policy.max_change_ratio:.4f}", {"change_ratio": ratio, "maximum": policy.max_change_ratio}))
    return ValidationEvidence(all(item.passed for item in results), tuple(results))
