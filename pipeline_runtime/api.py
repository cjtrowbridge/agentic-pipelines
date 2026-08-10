"""The sole Ollama-compatible inference boundary for pipeline stages."""

from __future__ import annotations

import json
import logging
import random
import ssl
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib import error, request

from .config import ApiConfig
from .redaction import redact_text
from .thread_capture import ThreadCaptureWriter

LOGGER = logging.getLogger(__name__)


class InferenceError(RuntimeError):
    """Normalized failure from the shared local inference boundary."""

    def __init__(self, message: str, *, retryable: bool, status_code: int | None = None, failure_code: str = "unknown") -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code
        self.failure_code = failure_code
        self.capture_path: Path | None = None
        self.raw_content: str | None = None
        self.attempts = 0
        self.retry_events: list[dict[str, Any]] = []


@dataclass(frozen=True)
class InferenceRequest:
    messages: Sequence[Mapping[str, str]]
    model: str | None = None
    generation: Mapping[str, Any] = field(default_factory=dict)
    think: bool | str | None = None
    response_format: str | Mapping[str, Any] | None = None
    stage: str = "unspecified"
    run_id: str = "unassigned"
    entity_id: str = "unassigned"
    entity_revision: str = "unassigned"
    attempt_id: str = "unassigned"
    prompt_template_id: str = "unassigned"
    prompt_template_hash: str = "unassigned"

    def payload(self, config: ApiConfig) -> dict[str, Any]:
        if not self.messages:
            raise ValueError("InferenceRequest.messages must not be empty")
        normalized_messages: list[dict[str, str]] = []
        for index, message in enumerate(self.messages):
            role = message.get("role")
            content = message.get("content")
            if not isinstance(role, str) or not role.strip() or not isinstance(content, str):
                raise ValueError(f"messages[{index}] must contain non-empty string role and string content")
            normalized_messages.append({"role": role, "content": content})
        payload: dict[str, Any] = {
            "model": self.model or config.model,
            "messages": normalized_messages,
            "stream": False,
            "options": {**config.generation, **self.generation},
        }
        if self.think is not None:
            if not isinstance(self.think, (bool, str)):
                raise ValueError("InferenceRequest.think must be a boolean, thinking level, or None")
            payload["think"] = self.think
        if self.response_format is not None:
            payload["format"] = self.response_format
        return payload


@dataclass(frozen=True)
class InferenceResponse:
    content: str
    raw: Mapping[str, Any]
    elapsed_seconds: float
    attempts: int
    usage: Mapping[str, int | float] = field(default_factory=dict)
    retry_events: tuple[Mapping[str, Any], ...] = ()
    capture_path: Path | None = None


Transport = Callable[[str, bytes, Mapping[str, str], float, ssl.SSLContext | None], tuple[int, bytes]]
Sleeper = Callable[[float], None]


def transport_failure_code(reason: object) -> str:
    """Classify transport evidence without changing the configured endpoint."""
    text = str(reason).casefold()
    if "10013" in text or "permission" in text or "forbidden" in text:
        return "socket_permission_denied"
    if "name or service not known" in text or "getaddrinfo" in text or "nodename" in text:
        return "dns_failure"
    if "refused" in text:
        return "connection_refused"
    if "timed out" in text or "timeout" in text:
        return "timeout"
    if "ssl" in text or "tls" in text or "certificate" in text:
        return "tls_failure"
    return "transport_failure"


@dataclass
class ProviderCircuitBreaker:
    """Run-local breaker that prevents equivalent doomed calls from multiplying."""

    identity: str
    open_code: str | None = None
    suppressed_attempts: int = 0

    def permit(self) -> None:
        if self.open_code:
            self.suppressed_attempts += 1
            raise InferenceError(
                f"provider circuit is open ({self.open_code})", retryable=False,
                failure_code="provider_circuit_open",
            )

    def record_failure(self, failure: InferenceError) -> None:
        if failure.failure_code in {"socket_permission_denied", "dns_failure", "connection_refused"}:
            self.open_code = failure.failure_code


def _default_transport(
    url: str, body: bytes, headers: Mapping[str, str], timeout: float, ssl_context: ssl.SSLContext | None
) -> tuple[int, bytes]:
    http_request = request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with request.urlopen(http_request, timeout=timeout, context=ssl_context) as response:
            return response.status, response.read()
    except error.HTTPError as exc:
        return exc.code, exc.read()
    except error.URLError as exc:
        code = transport_failure_code(exc.reason)
        raise InferenceError(
            f"local inference connection failed: {exc.reason}",
            retryable=code not in {"socket_permission_denied", "dns_failure", "connection_refused"},
            failure_code=code,
        ) from exc
    except TimeoutError as exc:
        raise InferenceError("local inference request timed out", retryable=True, failure_code="timeout") from exc


def _usage(raw: Mapping[str, Any]) -> dict[str, int | float]:
    keys = ("prompt_eval_count", "eval_count", "prompt_eval_duration", "eval_duration", "total_duration", "load_duration")
    return {key: raw[key] for key in keys if isinstance(raw.get(key), (int, float)) and not isinstance(raw[key], bool)}


class InferenceClient:
    """Synchronous, bounded client for Ollama's `/api/chat` endpoint."""

    def __init__(
        self,
        config: ApiConfig,
        *,
        transport: Transport = _default_transport,
        sleeper: Sleeper = time.sleep,
        random_source: Callable[[], float] = random.random,
        thread_writer: ThreadCaptureWriter | None = None,
        is_cancelled: Callable[[], bool] | None = None,
    ) -> None:
        self._config = config
        self._transport = transport
        self._sleeper = sleeper
        self._random = random_source
        self._thread_writer = thread_writer
        self._is_cancelled = is_cancelled or (lambda: False)
        self._circuit = ProviderCircuitBreaker(f"{config.provider}|{config.endpoint}|{config.model}")

    @property
    def config(self) -> ApiConfig:
        """Expose non-secret request policy/generation metadata for run evidence."""
        return self._config

    def invoke(self, inference_request: InferenceRequest) -> InferenceResponse:
        self._circuit.permit()
        payload = inference_request.payload(self._config)
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json", **self._config.headers}
        if self._config.api_key:
            headers.setdefault("Authorization", f"Bearer {self._config.api_key}")
        ssl_context = None
        if self._config.endpoint.startswith("https://") and not self._config.request.tls_verify:
            ssl_context = ssl._create_unverified_context()  # noqa: SLF001 - explicit local opt-out
        endpoint = f"{self._config.endpoint}/api/chat"
        started = time.monotonic()
        last_error: InferenceError | None = None
        retry_events: list[dict[str, Any]] = []
        for attempt in range(1, self._config.request.max_attempts + 1):
            if self._is_cancelled():
                last_error = InferenceError("local inference request cancelled", retryable=False)
                break
            if time.monotonic() - started >= self._config.request.total_timeout_seconds:
                last_error = InferenceError("local inference total timeout exceeded", retryable=False)
                break
            try:
                elapsed = time.monotonic() - started
                remaining = max(0.1, self._config.request.total_timeout_seconds - elapsed)
                status, response_body = self._transport(
                    endpoint,
                    body,
                    headers,
                    min(self._config.request.read_timeout_seconds, remaining),
                    ssl_context,
                )
                response = self._parse_response(status, response_body, started, attempt)
                response = InferenceResponse(
                    response.content,
                    response.raw,
                    response.elapsed_seconds,
                    response.attempts,
                    response.usage,
                    tuple(retry_events),
                )
                capture = self._capture(inference_request, payload, response=response, error=None)
                return InferenceResponse(
                    response.content,
                    response.raw,
                    response.elapsed_seconds,
                    response.attempts,
                    response.usage,
                    response.retry_events,
                    capture,
                )
            except InferenceError as exc:
                self._circuit.record_failure(exc)
                last_error = exc
                exc.attempts = attempt
                event: dict[str, Any] = {
                    "attempt": attempt,
                    "failure": self._safe_message(exc),
                "status_code": exc.status_code,
                "failure_code": exc.failure_code,
                    "retryable": exc.retryable,
                }
                if not exc.retryable or attempt == self._config.request.max_attempts:
                    event["disposition"] = "terminal"
                    retry_events.append(event)
                    break
                delay = min(
                    self._config.request.max_backoff_seconds,
                    self._config.request.initial_backoff_seconds * (2 ** (attempt - 1)),
                )
                delay *= 0.75 + (self._random() * 0.5)
                event["disposition"] = "retry"
                event["delay_seconds"] = delay
                retry_events.append(event)
                LOGGER.warning("Retrying local inference stage=%s attempt=%s after %.2fs: %s", inference_request.stage, attempt, delay, self._safe_message(exc))
                self._sleeper(delay)
        assert last_error is not None
        last_error.retry_events = retry_events
        last_error.capture_path = self._capture(inference_request, payload, response=None, error=last_error)
        raise last_error

    def redact(self, value: str) -> str:
        """Redact configured secrets before callers persist an error."""
        return redact_text(value, self._config.redaction_values)

    def _parse_response(self, status: int, response_body: bytes, started: float, attempt: int) -> InferenceResponse:
        text = response_body.decode("utf-8", errors="replace")
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            failure = InferenceError("local inference returned non-JSON response", retryable=status >= 500, status_code=status)
            failure.raw_content = text
            raise failure from exc
        if not isinstance(raw, dict):
            failure = InferenceError("local inference returned a non-object JSON response", retryable=False, status_code=status)
            failure.raw_content = text
            raise failure
        if status < 200 or status >= 300:
            message = raw.get("error") if isinstance(raw.get("error"), str) else f"HTTP {status}"
            failure = InferenceError(f"local inference request failed: {message}", retryable=status in {408, 429} or status >= 500, status_code=status)
            failure.raw_content = text
            raise failure
        message = raw.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            failure = InferenceError("local inference response is missing message.content", retryable=False, status_code=status)
            failure.raw_content = text
            raise failure
        return InferenceResponse(
            content=content,
            raw=raw,
            elapsed_seconds=time.monotonic() - started,
            attempts=attempt,
            usage=_usage(raw),
        )

    def _safe_message(self, exc: Exception) -> str:
        return redact_text(str(exc), self._config.redaction_values)

    def _capture(
        self,
        inference_request: InferenceRequest,
        payload: Mapping[str, Any],
        *,
        response: InferenceResponse | None,
        error: InferenceError | None,
    ) -> Path | None:
        if self._thread_writer is None:
            return None
        return self._thread_writer.write(
            run_id=inference_request.run_id,
            entity_id=inference_request.entity_id,
            entity_revision=inference_request.entity_revision,
            stage=inference_request.stage,
            attempt_id=inference_request.attempt_id,
            prompt_template_id=inference_request.prompt_template_id,
            prompt_template_hash=inference_request.prompt_template_hash,
            request_payload=payload,
            response_payload=response.raw if response else None,
            elapsed_seconds=response.elapsed_seconds if response else None,
            usage=response.usage if response else None,
            retry_events=response.retry_events if response else error.retry_events if error else (),
            error={
                "message": self._safe_message(error),
                "retryable": error.retryable,
                "status_code": error.status_code,
                "failure_code": error.failure_code,
                "attempts": error.attempts,
                "raw_content": error.raw_content,
            } if error else None,
            provider=self._config.provider,
            endpoint=self._config.endpoint,
            model=(inference_request.model or self._config.model),
            sensitive_values=self._config.redaction_values,
        )
