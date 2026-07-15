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

    def __init__(self, message: str, *, retryable: bool, status_code: int | None = None) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code
        self.capture_path: Path | None = None


@dataclass(frozen=True)
class InferenceRequest:
    messages: Sequence[Mapping[str, str]]
    model: str | None = None
    generation: Mapping[str, Any] = field(default_factory=dict)
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
    capture_path: Path | None = None


Transport = Callable[[str, bytes, Mapping[str, str], float, ssl.SSLContext | None], tuple[int, bytes]]
Sleeper = Callable[[float], None]


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
        raise InferenceError(f"local inference connection failed: {exc.reason}", retryable=True) from exc
    except TimeoutError as exc:
        raise InferenceError("local inference request timed out", retryable=True) from exc


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

    def invoke(self, inference_request: InferenceRequest) -> InferenceResponse:
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
                capture = self._capture(inference_request, payload, response=response, error=None)
                return InferenceResponse(response.content, response.raw, response.elapsed_seconds, response.attempts, response.usage, capture)
            except InferenceError as exc:
                last_error = exc
                if not exc.retryable or attempt == self._config.request.max_attempts:
                    break
                delay = min(
                    self._config.request.max_backoff_seconds,
                    self._config.request.initial_backoff_seconds * (2 ** (attempt - 1)),
                )
                delay *= 0.75 + (self._random() * 0.5)
                LOGGER.warning("Retrying local inference stage=%s attempt=%s after %.2fs: %s", inference_request.stage, attempt, delay, self._safe_message(exc))
                self._sleeper(delay)
        assert last_error is not None
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
            raise InferenceError("local inference returned non-JSON response", retryable=status >= 500, status_code=status) from exc
        if not isinstance(raw, dict):
            raise InferenceError("local inference returned a non-object JSON response", retryable=False, status_code=status)
        if status < 200 or status >= 300:
            message = raw.get("error") if isinstance(raw.get("error"), str) else f"HTTP {status}"
            raise InferenceError(f"local inference request failed: {message}", retryable=status in {408, 429} or status >= 500, status_code=status)
        message = raw.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise InferenceError("local inference response is missing message.content", retryable=False, status_code=status)
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
            error={
                "message": self._safe_message(error),
                "retryable": error.retryable,
                "status_code": error.status_code,
            } if error else None,
            provider=self._config.provider,
            endpoint=self._config.endpoint,
            model=(inference_request.model or self._config.model),
            sensitive_values=self._config.redaction_values,
        )
