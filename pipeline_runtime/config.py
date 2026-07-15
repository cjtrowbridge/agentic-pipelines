"""Validated, local-only configuration for the shared inference primitive."""

from __future__ import annotations

from dataclasses import dataclass, field
import ipaddress
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

import yaml


class ConfigError(ValueError):
    """Raised when local API configuration is absent or unsafe."""


@dataclass(frozen=True)
class RequestPolicy:
    connect_timeout_seconds: float = 10.0
    read_timeout_seconds: float = 600.0
    total_timeout_seconds: float = 660.0
    max_attempts: int = 3
    initial_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 20.0
    tls_verify: bool = True


@dataclass(frozen=True)
class ApiConfig:
    path: Path
    provider: str
    endpoint: str
    model: str
    api_key: str | None = field(repr=False)
    headers: Mapping[str, str] = field(default_factory=dict, repr=False)
    request: RequestPolicy = field(default_factory=RequestPolicy)
    generation: Mapping[str, Any] = field(default_factory=dict)
    sensitive_values: tuple[str, ...] = field(default_factory=tuple, repr=False)
    allow_remote_endpoint: bool = False

    @property
    def redaction_values(self) -> tuple[str, ...]:
        values = [value for value in self.sensitive_values if value]
        if self.api_key:
            values.append(self.api_key)
        values.extend(value for value in self.headers.values() if value)
        return tuple(dict.fromkeys(values))


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a mapping")
    return value


def _number(value: Any, name: str, *, minimum: float, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < minimum:
        raise ConfigError(f"{name} must be a number >= {minimum}")
    return float(value)


def _integer(value: Any, name: str, *, minimum: int, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigError(f"{name} must be an integer >= {minimum}")
    return value


def _string(value: Any, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ConfigError(f"{name} must be a non-empty string")
    return value.strip()


def _validate_endpoint(endpoint: str, tls_verify: bool, allow_remote: bool) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConfigError("endpoint must be an absolute http:// or https:// URL")
    if parsed.username or parsed.password:
        raise ConfigError("endpoint must not embed credentials")
    hostname = parsed.hostname or ""
    local = hostname == "localhost"
    try:
        address = ipaddress.ip_address(hostname)
        local = address.is_loopback or address.is_private or address.is_link_local
    except ValueError:
        pass
    if not local and not allow_remote:
        raise ConfigError("endpoint must be loopback/private; set allow_remote_endpoint: true only for an explicitly approved gateway")
    if parsed.scheme == "http" and tls_verify is False:
        # It is not an error; this makes the intentional local plaintext choice explicit.
        return


def load_api_config(path: Path | str = "api.yaml") -> ApiConfig:
    """Load and validate an ignored local API configuration file."""

    config_path = Path(path).expanduser().resolve()
    if not config_path.exists():
        raise ConfigError(
            f"Local API configuration is missing: {config_path}. "
            "Copy api.sample.yaml to api.yaml, then enter the local endpoint, model, and any required credential."
        )
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {config_path}: {exc}") from exc
    data = _mapping(raw, "root configuration")
    if data.get("schema_version") != 1:
        raise ConfigError("schema_version must be 1")
    provider = _string(data.get("provider"), "provider")
    if provider != "ollama":
        raise ConfigError("provider must be 'ollama' in the initial runtime")
    request_raw = _mapping(data.get("request"), "request")
    tls_verify = request_raw.get("tls_verify", True)
    if not isinstance(tls_verify, bool):
        raise ConfigError("request.tls_verify must be a boolean")
    request = RequestPolicy(
        connect_timeout_seconds=_number(
            request_raw.get("connect_timeout_seconds"), "request.connect_timeout_seconds", minimum=0.1, default=10.0
        ),
        read_timeout_seconds=_number(
            request_raw.get("read_timeout_seconds"), "request.read_timeout_seconds", minimum=0.1, default=600.0
        ),
        total_timeout_seconds=_number(
            request_raw.get("total_timeout_seconds"), "request.total_timeout_seconds", minimum=0.1, default=660.0
        ),
        max_attempts=_integer(request_raw.get("max_attempts"), "request.max_attempts", minimum=1, default=3),
        initial_backoff_seconds=_number(
            request_raw.get("initial_backoff_seconds"), "request.initial_backoff_seconds", minimum=0.0, default=1.0
        ),
        max_backoff_seconds=_number(
            request_raw.get("max_backoff_seconds"), "request.max_backoff_seconds", minimum=0.0, default=20.0
        ),
        tls_verify=tls_verify,
    )
    if request.total_timeout_seconds < request.connect_timeout_seconds:
        raise ConfigError("request.total_timeout_seconds must be at least request.connect_timeout_seconds")
    if request.max_backoff_seconds < request.initial_backoff_seconds:
        raise ConfigError("request.max_backoff_seconds must be at least request.initial_backoff_seconds")
    allow_remote_endpoint = data.get("allow_remote_endpoint", False)
    if not isinstance(allow_remote_endpoint, bool):
        raise ConfigError("allow_remote_endpoint must be a boolean")
    endpoint = _string(data.get("endpoint"), "endpoint").rstrip("/")
    _validate_endpoint(endpoint, request.tls_verify, allow_remote_endpoint)
    authentication = _mapping(data.get("authentication"), "authentication")
    api_key = authentication.get("api_key")
    if api_key is not None and not isinstance(api_key, str):
        raise ConfigError("authentication.api_key must be a string or null")
    headers_raw = _mapping(authentication.get("headers"), "authentication.headers")
    headers = {_string(key, "authentication.headers key"): _string(value, f"authentication.headers[{key!r}]") for key, value in headers_raw.items()}
    generation = _mapping(data.get("generation"), "generation")
    redaction = _mapping(data.get("redaction"), "redaction")
    sensitive_values = redaction.get("sensitive_values", [])
    if not isinstance(sensitive_values, list) or not all(isinstance(value, str) for value in sensitive_values):
        raise ConfigError("redaction.sensitive_values must be a list of strings")
    return ApiConfig(
        path=config_path,
        provider=provider,
        endpoint=endpoint,
        model=_string(data.get("model"), "model"),
        api_key=api_key or None,
        headers=headers,
        request=request,
        generation=generation,
        sensitive_values=tuple(value for value in sensitive_values if value),
        allow_remote_endpoint=allow_remote_endpoint,
    )
