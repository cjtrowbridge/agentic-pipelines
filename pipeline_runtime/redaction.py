"""Redact configured literal secrets before evidence leaves process memory."""

from __future__ import annotations

from typing import Any


REDACTED = "[REDACTED]"


def redact_text(value: str, sensitive_values: tuple[str, ...]) -> str:
    result = value
    for sensitive in sensitive_values:
        if sensitive:
            result = result.replace(sensitive, REDACTED)
    return result


def redact_value(value: Any, sensitive_values: tuple[str, ...]) -> Any:
    if isinstance(value, str):
        return redact_text(value, sensitive_values)
    if isinstance(value, list):
        return [redact_value(item, sensitive_values) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_value(item, sensitive_values) for item in value)
    if isinstance(value, dict):
        return {str(key): redact_value(item, sensitive_values) for key, item in value.items()}
    return value

