"""Deterministic checks for Docker Ollama alias provisioning without Ollama."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import subprocess
import unittest
from unittest.mock import patch
from urllib import error

from scripts import ensure_ollama_context_aliases as aliases


BASE_SOURCE = "/root/.ollama/models/blobs/sha256-base"


class FakeOllama:
    def __init__(self) -> None:
        self.models: dict[str, dict] = {
            "qwen3.8:27b": {
                "modelfile": f"FROM {BASE_SOURCE}\n",
                "parameters": "temperature 0.8",
                "model_info": {"general.architecture": "qwen3", "qwen3.context_length": 262144},
            },
        }
        self.creates: list[dict] = []

    def api(self, endpoint: str, path: str, payload: dict | None, *, timeout: int) -> dict:
        assert endpoint == "http://127.0.0.1:11434"
        assert timeout == 15
        if path == "/api/tags":
            return {"models": [{"name": name} for name in self.models]}
        if path == "/api/show":
            assert payload is not None
            return self.models[payload["model"]]
        if path == "/api/create":
            assert payload is not None
            self.creates.append(payload)
            self.models[payload["model"]] = {
                "modelfile": f"FROM {BASE_SOURCE}\nPARAMETER num_ctx {payload['parameters']['num_ctx']}\n",
                "parameters": f"num_ctx {payload['parameters']['num_ctx']}",
            }
            return {"status": "success"}
        raise AssertionError(path)


class OllamaContextAliasTests(unittest.TestCase):
    def test_names_preserve_model_tag_and_normalize_context(self) -> None:
        self.assertEqual(aliases.alias_name("CJ-Desktop", "96k", "qwen3.8:27b"), "cj-desktop-96k-qwen3.8:27b")
        self.assertEqual(aliases.parse_context("98304"), ("96k", 98304))
        self.assertEqual(aliases.parse_context("98305"), ("98305t", 98305))
        self.assertEqual(aliases.canonical_name("cj-desktop-96k-qwen3.8"), "cj-desktop-96k-qwen3.8:latest")
        with self.assertRaises(aliases.AliasError):
            aliases.parse_context("0k")
        with self.assertRaises(aliases.AliasError):
            aliases.alias_name("CJ", "1k", "bad model")
        with self.assertRaises(aliases.AliasError):
            aliases.alias_name("CJ", "1k", "qwen3.8:")

    def test_docker_container_and_local_port_are_checked(self) -> None:
        responses = [
            subprocess.CompletedProcess([], 0, '"npipe:////./pipe/docker_engine"\n', ""),
            subprocess.CompletedProcess([], 0, "true\n", ""),
            subprocess.CompletedProcess([], 0, "0.0.0.0:11434\n", ""),
        ]
        with patch.dict(aliases.os.environ, {"DOCKER_HOST": ""}), patch.object(aliases.subprocess, "run", side_effect=responses) as run:
            self.assertEqual(aliases.docker_endpoint("ollama", timeout=15), "http://127.0.0.1:11434")
        self.assertEqual(run.call_args_list[0].args[0][:2], ["docker", "context"])
        self.assertEqual(run.call_args_list[1].args[0][:2], ["docker", "inspect"])
        self.assertEqual(run.call_args_list[2].args[0][:2], ["docker", "port"])
        responses = [
            subprocess.CompletedProcess([], 0, '"unix:///var/run/docker.sock"\n', ""),
            subprocess.CompletedProcess([], 0, "true\n", ""),
            subprocess.CompletedProcess([], 0, "192.0.2.10:11434\n", ""),
        ]
        with patch.dict(aliases.os.environ, {"DOCKER_HOST": ""}), patch.object(aliases.subprocess, "run", side_effect=responses):
            with self.assertRaisesRegex(aliases.AliasError, "no usable local"):
                aliases.docker_endpoint("ollama", timeout=15)
        with patch.dict(aliases.os.environ, {"DOCKER_HOST": "ssh://example.com"}):
            with self.assertRaisesRegex(aliases.AliasError, "nonlocal"):
                aliases.docker_endpoint("ollama", timeout=15)

    def test_check_only_reports_missing_then_normal_mode_creates_once(self) -> None:
        fake = FakeOllama()
        with patch.object(aliases, "docker_endpoint", return_value="http://127.0.0.1:11434"), patch.object(aliases, "api_json", side_effect=fake.api):
            output = StringIO()
            with redirect_stdout(output):
                status = aliases.ensure_aliases("ollama", "qwen3.8:27b", ["1k", "96k"], check_only=True, timeout=15, hostname="CJ-Desktop")
            self.assertEqual(status, 1)
            self.assertEqual(fake.creates, [])
            self.assertIn("TOTAL pass=0 fail=2 created=0", output.getvalue())

            output = StringIO()
            with redirect_stdout(output):
                status = aliases.ensure_aliases("ollama", "qwen3.8:27b", ["1k", "96k"], check_only=False, timeout=15, hostname="CJ-Desktop")
            self.assertEqual(status, 0)
            self.assertEqual(len(fake.creates), 2)
            self.assertEqual(fake.creates[1]["parameters"], {"num_ctx": 98304})
            self.assertIn("TOTAL pass=2 fail=0 created=2", output.getvalue())

            output = StringIO()
            with redirect_stdout(output):
                status = aliases.ensure_aliases("ollama", "qwen3.8:27b", ["1k", "96k"], check_only=False, timeout=15, hostname="CJ-Desktop")
            self.assertEqual(status, 0)
            self.assertEqual(len(fake.creates), 2)
            self.assertIn("TOTAL pass=2 fail=0 created=0", output.getvalue())

    def test_conflicting_existing_alias_is_not_replaced(self) -> None:
        fake = FakeOllama()
        fake.models["cj-desktop-1k-qwen3.8:27b"] = {"modelfile": f"FROM {BASE_SOURCE}\n", "parameters": "num_ctx 2048"}
        with patch.object(aliases, "docker_endpoint", return_value="http://127.0.0.1:11434"), patch.object(aliases, "api_json", side_effect=fake.api):
            output = StringIO()
            with redirect_stdout(output):
                status = aliases.ensure_aliases("ollama", "qwen3.8:27b", ["1k"], check_only=False, timeout=15, hostname="CJ-Desktop")
        self.assertEqual(status, 1)
        self.assertEqual(fake.creates, [])
        self.assertIn("context mismatch", output.getvalue())

    def test_wrong_base_and_unverifiable_alias_fail(self) -> None:
        fake = FakeOllama()
        alias = "cj-desktop-1k-qwen3.8:27b"
        fake.models[alias] = {"modelfile": "FROM /other/blob\n", "parameters": "num_ctx 1024"}
        with patch.object(aliases, "docker_endpoint", return_value="http://127.0.0.1:11434"), patch.object(aliases, "api_json", side_effect=fake.api):
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(aliases.ensure_aliases("ollama", "qwen3.8:27b", ["1k"], check_only=False, timeout=15, hostname="CJ-Desktop"), 1)
            self.assertIn("source does not match", output.getvalue())
            fake.models[alias] = {"parameters": "num_ctx 1024"}
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(aliases.ensure_aliases("ollama", "qwen3.8:27b", ["1k"], check_only=False, timeout=15, hostname="CJ-Desktop"), 1)
            self.assertIn("cannot be verified", output.getvalue())
        self.assertEqual(fake.creates, [])

    def test_missing_base_and_oversize_context_fail_before_create(self) -> None:
        fake = FakeOllama()
        with patch.object(aliases, "docker_endpoint", return_value="http://127.0.0.1:11434"), patch.object(aliases, "api_json", side_effect=fake.api):
            with self.assertRaisesRegex(aliases.AliasError, "base model .* missing"):
                aliases.ensure_aliases("ollama", "missing:1b", ["1k"], check_only=False, timeout=15, hostname="CJ-Desktop")
            with self.assertRaisesRegex(aliases.AliasError, "exceeds base model limit"):
                aliases.ensure_aliases("ollama", "qwen3.8:27b", ["257k"], check_only=False, timeout=15, hostname="CJ-Desktop")
        self.assertEqual(fake.creates, [])

    def test_api_failure_and_interrupt_are_controlled(self) -> None:
        with patch.object(aliases.LOCAL_OPENER, "open", side_effect=error.URLError("connection refused")):
            with self.assertRaisesRegex(aliases.AliasError, "Ollama /api/tags request failed"):
                aliases.api_json("http://127.0.0.1:11434", "/api/tags", None, timeout=15)
        with patch.object(aliases, "docker_endpoint", side_effect=aliases.AliasError("Docker unavailable")):
            err = StringIO()
            with redirect_stderr(err):
                self.assertEqual(aliases.main(["--model", "qwen3.8:27b", "--context", "1k"]), 1)
            self.assertIn("Docker unavailable", err.getvalue())
        with patch.object(aliases, "ensure_aliases", side_effect=KeyboardInterrupt):
            err = StringIO()
            with redirect_stderr(err):
                self.assertEqual(aliases.main(["--model", "qwen3.8:27b", "--context", "1k"]), 130)
            self.assertIn("interrupted", err.getvalue())


if __name__ == "__main__":
    unittest.main()
