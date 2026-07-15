from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from pipeline_runtime.api import InferenceClient
from pipeline_runtime.config import ApiConfig, RequestPolicy
from pipeline_runtime.definition import load_definition
from pipeline_runtime.runner import PipelineRunner
from pipeline_runtime.thread_capture import ThreadCaptureWriter

ROOT = Path(__file__).resolve().parents[1]


class ReferencePipelineTests(unittest.TestCase):
    def test_markdown_vertical_slice_with_fake_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "reference"
            shutil.copytree(ROOT / "examples" / "markdown_repair", target)
            definition = load_definition(target / "pipeline.yaml")

            def transport(_url: str, body: bytes, *_args: object) -> tuple[int, bytes]:
                request = json.loads(body)
                rendered = request["messages"][0]["content"]
                inputs = json.loads(rendered.split("\n\nINPUTS\n", 1)[1])
                if "source_entity" in inputs and "allowed_changes" in inputs:
                    source = inputs["source_entity"]
                    if "Unrepairable ambiguity" in source:
                        result = {"status": "unable", "candidate": None, "reason": "intended meaning is unavailable"}
                    else:
                        result = {"status": "candidate", "candidate": source, "reason": None}
                elif "violations" in inputs:
                    candidate = inputs["candidate"] + ("\n```\n" if "needs a closing fence" in inputs["candidate"] else "")
                    result = {"status": "repaired", "candidate": candidate, "addressed": inputs["violations"], "unresolved": []}
                elif "candidate" in inputs:
                    result = {"verdict": "pass", "confidence": 0.9, "violations": [], "recommended_action": "accept"}
                elif "cohort_definition" in inputs:
                    result = {"cohort_id": inputs["cohort_definition"]["cohort_id"], "shared_observations": ["worker returned unable"], "counterexamples": [], "hypotheses": [{"cause": "missing intended meaning"}], "evidence_gaps": [], "confidence": 0.8}
                elif "reviewed_cohort_analysis" in inputs:
                    result = {"cohort_id": inputs["reviewed_cohort_analysis"]["cohort_id"], "observed_problem": "worker returned unable", "hypothesized_cause": "source lacks intended meaning", "proposed_change": "route this cohort to a human", "regression_fixture": "retain unrepairable.md", "sample_scope": "one entity", "retry_recommendation": "do not retry automatically", "authority": "advisory_only"}
                else:
                    result = {"observed_metrics": inputs["deterministic_run_metrics"], "calculated_metrics": {}, "hypotheses": [], "unknowns": ["false accept rate", "false reject rate"], "recommendations": ["measure the golden set"]}
                return 200, json.dumps({"message": {"content": json.dumps(result)}}).encode("utf-8")

            config = ApiConfig(Path("api.yaml"), "ollama", "http://127.0.0.1:11434", "fake", None, request=RequestPolicy(max_attempts=1))
            client = InferenceClient(config, transport=transport, thread_writer=ThreadCaptureWriter(definition.thread_root))
            runner = PipelineRunner(definition, client)
            self.assertEqual(5, runner.discover())
            result = runner.run(10, 1)
            self.assertEqual(3, result["state"]["accepted"])
            self.assertEqual(2, result["state"]["quarantined"])
            report = json.loads(Path(result["report"]).read_text(encoding="utf-8"))
            self.assertEqual(2, len(report["failure_cohorts"]))
            analysis_path = runner.analyze(result["run_id"])
            analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
            self.assertEqual("advisory_only", analysis["authority"])
            self.assertEqual(2, len(analysis["cohort_analyses"]))
            self.assertIsNotNone(analysis["performance_analysis"])
            cohort = report["failure_cohorts"][0]
            self.assertEqual(1, runner.retry_cohort(Path(result["report"]), cohort["cohort_id"]))
            self.assertIn("retry_eligible", runner.store.summary())
            runner.close()


if __name__ == "__main__":
    unittest.main()
