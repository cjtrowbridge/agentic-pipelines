from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pipeline_runtime.api import InferenceClient, InferenceRequest
from pipeline_runtime.config import ApiConfig, RequestPolicy
from pipeline_runtime.thread_capture import ThreadCaptureWriter


class ApiPrimitiveTests(unittest.TestCase):
    def test_request_supports_top_level_thinking_control(self) -> None:
        payload = InferenceRequest(messages=[{"role": "user", "content": "hello"}], think=False).payload(self.config())
        self.assertIs(payload["think"], False)
        self.assertNotIn("think", payload["options"])

    def test_request_preserves_separate_context_and_completion_limits(self) -> None:
        config = ApiConfig(
            **{**self.config().__dict__, "generation": {"num_predict": 2048, "num_ctx": 20480}}
        )
        options = InferenceRequest(messages=[{"role": "user", "content": "hello"}]).payload(config)["options"]
        self.assertEqual(options["num_predict"], 2048)
        self.assertEqual(options["num_ctx"], 20480)

    def config(self) -> ApiConfig:
        return ApiConfig(
            path=Path("api.yaml"),
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="test-model",
            api_key="top-secret",
            headers={"X-Local-Key": "header-secret"},
            request=RequestPolicy(max_attempts=1),
            sensitive_values=("source-secret",),
        )

    def test_successful_call_writes_redacted_thread_capture(self) -> None:
        def transport(_url: str, _body: bytes, _headers: object, _timeout: float, _context: object) -> tuple[int, bytes]:
            return 200, b'{"message":{"content":"response source-secret"},"eval_count":4}'

        with tempfile.TemporaryDirectory() as temporary:
            client = InferenceClient(
                self.config(), transport=transport, thread_writer=ThreadCaptureWriter(Path(temporary))
            )
            response = client.invoke(
                InferenceRequest(
                    messages=[{"role": "user", "content": "request source-secret"}],
                    stage="worker",
                    run_id="run-1",
                    entity_id="entity-1",
                    entity_revision="rev-1",
                    attempt_id="attempt-1",
                )
            )
            self.assertEqual("response source-secret", response.content)
            capture = Path(temporary) / "run-1" / "entity-1" / "rev-1" / "worker" / "attempt-1.json"
            stored = json.loads(capture.read_text(encoding="utf-8"))
            self.assertEqual("request [REDACTED]", stored["request"]["messages"][0]["content"])
            self.assertEqual("response [REDACTED]", stored["response"]["message"]["content"])
            self.assertNotIn("top-secret", capture.read_text(encoding="utf-8"))
            self.assertEqual(capture, response.capture_path)


if __name__ == "__main__":
    unittest.main()
