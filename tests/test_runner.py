from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pipeline_runtime.api import InferenceClient
from pipeline_runtime.config import ApiConfig, RequestPolicy
from pipeline_runtime.definition import load_definition
from pipeline_runtime.runner import PipelineRunner
from pipeline_runtime.thread_capture import ThreadCaptureWriter

SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "prompt_outputs.schema.json"


def ollama(content: dict[str, object]) -> bytes:
    return json.dumps({"message": {"content": json.dumps(content)}}).encode("utf-8")


def prompt(path: Path, prompt_id: str, role: str, inputs: list[str], output: str) -> None:
    path.write_text(
        "---\n"
        f"id: {prompt_id}\nversion: 1.0.0\nkind: pipeline-running\nmodel_role: {role}\n"
        f"inputs: [{', '.join(inputs)}]\noutput: {output}\n---\nPerform only this bounded job.\n",
        encoding="utf-8",
    )


def host(root: Path, *, promote: bool = False) -> Path:
    (root / "src").mkdir()
    (root / "src" / "one.md").write_text("---\ntitle: One\n---\n\n# Original\n", encoding="utf-8")
    prompt(root / "worker.md", "test.worker", "worker", ["goal", "source_entity", "allowed_changes", "protected_invariants"], "worker_result")
    prompt(root / "reviewer.md", "test.reviewer", "reviewer", ["goal", "source_entity", "candidate", "deterministic_evidence"], "reviewer_verdict")
    (root / "pipeline.yaml").write_text(
        f"""schema_version: 2
pipeline_id: test
contract:
  goal: Repair the heading.
  allowed_changes: [heading]
  protected_invariants: [front matter]
source: {{root: src, glob: '*.md'}}
paths:
  state: state/pipeline.sqlite
  artifacts: artifacts
  threads: threads
  reports: reports
  output_schema: {SCHEMA.as_posix()}
stages:
  worker: {{prompt: worker.md, id: test.worker, version: 1.0.0, output: worker_result, llm_justification: semantic heading repair}}
  reviewer: {{prompt: reviewer.md, id: test.reviewer, version: 1.0.0, output: reviewer_verdict, llm_justification: meaning preservation review}}
validation:
  required_substrings: ['title: One']
  protected_substrings: []
  max_change_ratio: 0.5
  require_front_matter: true
  require_balanced_fences: true
runtime: {{lease_seconds: 60, lock_stale_seconds: 60, max_repairs: 0}}
promotion: {{enabled: {str(promote).lower()}, backup_root: artifacts/backups}}
""",
        encoding="utf-8",
    )
    return root / "pipeline.yaml"


def config() -> ApiConfig:
    return ApiConfig(Path("api.yaml"), "ollama", "http://127.0.0.1:11434", "test", None, request=RequestPolicy(max_attempts=1))


class RunnerTests(unittest.TestCase):
    def test_structured_worker_review_validation_and_evidence(self) -> None:
        responses = iter(
            [
                ollama({"status": "candidate", "candidate": "---\ntitle: One\n---\n\n# Fixed\n", "reason": None}),
                ollama({"verdict": "pass", "confidence": 0.9, "violations": [], "recommended_action": "accept"}),
            ]
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            definition = load_definition(host(root))
            client = InferenceClient(config(), transport=lambda *_args: (200, next(responses)), thread_writer=ThreadCaptureWriter(definition.thread_root))
            runner = PipelineRunner(definition, client)
            self.assertEqual(1, runner.discover())
            result = runner.run(1, 1)
            self.assertEqual(1, result["state"]["accepted"])
            entity = next(iter(runner.store.eligible(1)), None)
            self.assertIsNone(entity)
            self.assertEqual(2, len(list((root / "threads").rglob("*.json"))))
            self.assertTrue(list((root / "artifacts" / "evidence").rglob("*.json")))
            self.assertTrue(Path(result["report"]).exists())
            runner.close()

    def test_promotion_refuses_a_changed_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            definition = load_definition(host(root, promote=True))
            source = root / "src" / "one.md"
            calls = 0

            def transport(*_args: object) -> tuple[int, bytes]:
                nonlocal calls
                calls += 1
                if calls == 1:
                    return 200, ollama({"status": "candidate", "candidate": "---\ntitle: One\n---\n\n# Fixed\n", "reason": None})
                source.write_text("human changed this\n", encoding="utf-8")
                return 200, ollama({"verdict": "pass", "confidence": 0.9, "violations": [], "recommended_action": "accept"})

            client = InferenceClient(config(), transport=transport, thread_writer=ThreadCaptureWriter(definition.thread_root))
            runner = PipelineRunner(definition, client)
            runner.discover()
            result = runner.run(1, 1)
            self.assertEqual(1, result["state"]["quarantined"])
            self.assertEqual("human changed this\n", source.read_text(encoding="utf-8"))
            runner.close()

    def test_changed_prompt_contract_requeues_same_source(self) -> None:
        responses = iter([
            ollama({"status": "candidate", "candidate": "---\ntitle: One\n---\n\n# Fixed\n", "reason": None}),
            ollama({"verdict": "pass", "confidence": 0.9, "violations": [], "recommended_action": "accept"}),
        ])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            definition_path = host(root)
            definition = load_definition(definition_path)
            runner = PipelineRunner(definition, InferenceClient(config(), transport=lambda *_args: (200, next(responses)), thread_writer=ThreadCaptureWriter(definition.thread_root)))
            runner.discover()
            runner.run(1, 1)
            runner.close()
            worker = root / "worker.md"
            worker.write_text(worker.read_text(encoding="utf-8") + "Narrow clarification.\n", encoding="utf-8")
            changed = PipelineRunner(load_definition(definition_path))
            self.assertEqual(1, changed.discover())
            self.assertEqual(1, changed.store.summary()["discovered"])
            changed.close()

    def test_successful_promotion_has_explicit_rollback(self) -> None:
        responses = iter([
            ollama({"status": "candidate", "candidate": "---\ntitle: One\n---\n\n# Fixed\n", "reason": None}),
            ollama({"verdict": "pass", "confidence": 0.9, "violations": [], "recommended_action": "accept"}),
        ])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            definition = load_definition(host(root, promote=True))
            client = InferenceClient(config(), transport=lambda *_args: (200, next(responses)), thread_writer=ThreadCaptureWriter(definition.thread_root))
            runner = PipelineRunner(definition, client)
            runner.discover()
            result = runner.run(1, 1)
            self.assertEqual(1, result["state"]["promoted"])
            entity = next(iter(runner.store.connection.execute("SELECT id FROM entities")))[0]
            runner.rollback_entity(entity)
            self.assertIn("# Original", (root / "src" / "one.md").read_text(encoding="utf-8"))
            self.assertEqual("rolled_back", runner.store.latest_promotion(entity)["status"])
            runner.close()


if __name__ == "__main__":
    unittest.main()
