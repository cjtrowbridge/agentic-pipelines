from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from pipeline_runtime.evidence import execution_status, rejected_candidate_path, rejection_record
from pipeline_runtime.package import PackageError, _validate_authority_matrix, validate_package
from pipeline_runtime.runner import _atomic_write_new
from pipeline_runtime.state import StateError


ROOT = Path(__file__).resolve().parents[1]


def matrix_row(case: dict[str, object]) -> dict[str, object]:
    property_class = str(case["property_class"])
    mechanism = str(case["mechanism"])
    authority = str(case["authority"])
    proof = {
        "representational": "explicit_representation",
        "semantic": "semantic_rubric",
        "human_policy": "human_policy",
    }[property_class]
    return {
        "id": case["id"],
        "property": case["property"],
        "property_class": property_class,
        "mechanism": mechanism,
        "authority": authority,
        "proof_basis": proof,
        "heuristic_role": case.get("heuristic_role", "none"),
        "evidence": "governance regression fixture",
        "repair_owner": "none",
        "escalation": "quarantine or explicit human review",
    }


class GovernanceEvidenceTests(unittest.TestCase):
    def test_cross_domain_authority_fixtures_enforce_expected_decisions(self) -> None:
        fixture = yaml.safe_load((ROOT / "examples" / "governance" / "authority_cases.yaml").read_text(encoding="utf-8"))
        domains = {case["domain"] for case in fixture["cases"]}
        self.assertTrue({"summarization", "classification", "factual_transformation", "retrieval_ranking", "document_repair"} <= domains)
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                if case["expected"] == "allowed":
                    _validate_authority_matrix([matrix_row(case)])
                else:
                    with self.assertRaises(PackageError):
                        _validate_authority_matrix([matrix_row(case)])

    def test_schema_one_package_is_compatible_but_not_governance_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "package"
            shutil.copytree(ROOT / "examples" / "markdown_repair", target)
            manifest_path = target / "package.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["schema_version"] = 1
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            result = validate_package(target)
            self.assertFalse(result["governance_conformant"])
            self.assertTrue(result["warnings"])

    def test_rejected_candidate_paths_are_collision_safe_and_records_are_actionable(self) -> None:
        root = Path("artifacts")
        first = rejected_candidate_path(root, entity_id="entity", artifact="resume", run_id="run-1", ordinal=2, attempt_id="a-1", extension="md")
        second = rejected_candidate_path(root, entity_id="entity", artifact="resume", run_id="run-1", ordinal=2, attempt_id="a-2", extension="md")
        self.assertNotEqual(first, second)
        self.assertIn("resume.2.run-1.a-1.rejected.md", first.as_posix())
        trailer = rejection_record(
            run_id="run-1",
            entity_id="entity",
            artifact="resume",
            stage="validation",
            attempt_id="a-1",
            candidate_sha256="0" * 64,
            failure_class="deterministic",
            authority="deterministic",
            validator_or_reviewer="page_count",
            rejection_code="too_long",
            actionable_explanation="Rendered output is one line over the limit.",
            retry_disposition="semantic_repair",
            run_report_path=Path("reports/run-1.md"),
            thread_path="threads/run-1/a-1.json",
        )
        self.assertIn("## Rejection record", trailer)
        self.assertIn("one line over", trailer)
        self.assertIn('"authority": "deterministic"', trailer)

    def test_rejected_evidence_cannot_be_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.2.rejected.md"
            _atomic_write_new(path, b"first")
            with self.assertRaises(StateError):
                _atomic_write_new(path, b"second")
            self.assertEqual(b"first", path.read_bytes())

    def test_concurrent_rejected_evidence_writers_cannot_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.2.rejected.md"

            def write(value: bytes) -> str:
                try:
                    _atomic_write_new(path, value)
                    return "created"
                except StateError:
                    return "rejected"

            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = sorted(pool.map(write, (b"first", b"second")))
            self.assertEqual(["created", "rejected"], outcomes)
            self.assertIn(path.read_bytes(), {b"first", b"second"})

    def test_execution_status_never_confuses_process_exit_with_artifact_success(self) -> None:
        self.assertEqual("failed", execution_status({"status": "failed", "processed": 0, "accepted": 0, "quarantined": 0}, 0))
        self.assertEqual("interrupted", execution_status({"status": "interrupted"}, 1))
        self.assertEqual("bounded_stop", execution_status({"status": "bounded_stop"}, 1))
        self.assertEqual("no_op", execution_status({"status": "completed", "processed": 0}, 0))
        self.assertEqual("partially_succeeded", execution_status({"status": "completed", "processed": 2, "accepted": 1, "quarantined": 1}, 2))
        self.assertEqual("succeeded", execution_status({"status": "completed", "processed": 1, "accepted": 1, "quarantined": 0}, 1))

    def test_schema_two_requires_all_rejected_artifact_exclusions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "package"
            shutil.copytree(ROOT / "examples" / "markdown_repair", target)
            manifest_path = target / "package.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["evidence_policy"]["excluded_from"].remove("semantic_evidence")
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(PackageError, "semantic_evidence"):
                validate_package(target)

    def test_rejected_artifacts_are_ignored_by_default(self) -> None:
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in ("*.rejected.md", "*.rejected.json", "*.rejected.txt"):
            self.assertIn(pattern, ignore)


if __name__ == "__main__":
    unittest.main()
