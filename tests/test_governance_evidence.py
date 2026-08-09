from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import yaml

from pipeline_runtime import evidence as evidence_module
from pipeline_runtime.evidence import (
    execution_status,
    is_non_progress,
    persist_rejected_pair,
    persist_rejection_bundle,
    persist_sequential_rejected_pair,
    rejected_candidate_path,
    rejected_content_extension,
    rejected_sequence,
    rejection_explanation,
    rejection_explanation_path,
)
from pipeline_runtime.package import PackageError, _validate_authority_matrix, validate_package


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

    def test_rejected_candidate_paths_are_collision_safe_and_explanations_are_actionable(self) -> None:
        root = Path("artifacts")
        first = rejected_candidate_path(root, entity_id="entity", artifact="resume", sequence=1, extension="md")
        second = rejected_candidate_path(root, entity_id="entity", artifact="resume", sequence=2, extension="md")
        self.assertNotEqual(first, second)
        self.assertIn("resume.1.rejected.md", first.as_posix())
        self.assertIn("resume.2.rejected.md", second.as_posix())
        self.assertEqual(1, rejected_sequence(first))
        self.assertNotIn("run-1", first.as_posix())
        explanation = rejection_explanation(
            run_id="run-1",
            entity_id="entity",
            artifact="resume",
            stage="validation",
            attempt_id="a-1",
            candidate_path=first,
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
        self.assertIn("# Rejection explanation", explanation)
        self.assertIn(str(first), explanation)
        self.assertIn("one line over", explanation)
        self.assertIn('"authority": "deterministic"', explanation)

    def test_sequential_pairs_are_atomic_naturally_ordered_and_truthfully_typed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def write(value: bytes) -> tuple[Path, int]:
                candidate, _sidecar, sequence = persist_sequential_rejected_pair(
                    root,
                    entity_id="entity",
                    artifact="resume",
                    candidate=value,
                    extension=".md",
                    explanation_builder=lambda path, number, digest: f"{path}\n{number}\n{digest}\n",
                )
                return candidate, sequence

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(write, (b"first", b"second")))
            self.assertEqual([1, 2], sorted(sequence for _path, sequence in results))
            self.assertEqual(
                ["resume.1.rejected.md", "resume.2.rejected.md"],
                sorted(path.name for path, _sequence in results),
            )
            self.assertTrue(all(rejection_explanation_path(path).is_file() for path, _sequence in results))
            self.assertEqual(".json", rejected_content_extension(b'{"valid": true}'))
            self.assertEqual(".txt", rejected_content_extension(b'{not json'))
            self.assertEqual(".md", rejected_content_extension(b"# Resume", intended_format="markdown"))

    def test_precursor_name_keeps_parent_sequence_before_stage(self) -> None:
        path = rejected_candidate_path(
            Path("artifacts"), entity_id="entity", artifact="resume", sequence=2,
            stage="claim_review", extension="json",
        )
        self.assertEqual("resume.2.rejected.claim_review.json", path.name)
        self.assertEqual("resume.2.rejected.claim_review.explanation.md", rejection_explanation_path(path).name)
        self.assertNotIn("..", path.name)
        self.assertTrue(is_non_progress(b"same", "same reason", b"same", "same reason"))
        self.assertFalse(is_non_progress(b"before", "same reason", b"after", "same reason"))
        paths = [
            rejected_candidate_path(Path("artifacts"), entity_id="entity", artifact="resume", sequence=number, extension="md")
            for number in range(12, 0, -1)
        ]
        self.assertEqual(list(range(1, 13)), [rejected_sequence(item) for item in sorted(paths, key=lambda item: rejected_sequence(item) or 0)])

    def test_guarded_bundle_publishes_parent_and_typed_precursor_together(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = persist_rejection_bundle(
                Path(temporary),
                entity_id="entity",
                artifact="resume",
                candidate=b"# Resume\n",
                extension=".md",
                explanation_builder=lambda path, sequence, digest: f"parent {path} {sequence} {digest}",
                precursors=[{
                    "stage": "claim_review",
                    "candidate": b'{"claims": []}',
                    "extension": ".json",
                    "explanation_builder": lambda path, sequence, digest: f"child {path} {sequence} {digest}",
                }],
            )
            self.assertEqual(1, result["sequence"])
            self.assertEqual("resume.1.rejected.md", result["path"].name)
            self.assertEqual("resume.1.rejected.claim_review.json", result["children"][0]["path"].name)
            self.assertTrue(result["explanation_path"].is_file())
            self.assertTrue(result["children"][0]["explanation_path"].is_file())

    def test_rejected_pair_preserves_candidate_bytes_and_cannot_be_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.run-1.a-1.rejected.md"
            candidate = b"# Resume\n\nExact trailing spaces  \n\n---\nframework-looking text\n"
            digest = hashlib.sha256(candidate).hexdigest()
            explanation = f"Candidate SHA-256: `{digest}`\n"
            sidecar = persist_rejected_pair(path, candidate, explanation, candidate_sha256=digest)
            self.assertEqual(candidate, path.read_bytes())
            self.assertEqual(rejection_explanation_path(path), sidecar)
            self.assertEqual(explanation, sidecar.read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                persist_rejected_pair(path, b"second", "other", candidate_sha256=hashlib.sha256(b"second").hexdigest())
            self.assertEqual(candidate, path.read_bytes())

    def test_concurrent_rejected_pair_writers_cannot_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.run-1.a-1.rejected.md"

            def write(value: bytes) -> str:
                try:
                    persist_rejected_pair(
                        path, value, value.decode("utf-8"), candidate_sha256=hashlib.sha256(value).hexdigest(),
                    )
                    return "created"
                except FileExistsError:
                    return "rejected"

            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = sorted(pool.map(write, (b"first", b"second")))
            self.assertEqual(["created", "rejected"], outcomes)
            self.assertIn(path.read_bytes(), {b"first", b"second"})
            self.assertTrue(rejection_explanation_path(path).is_file())

    def test_partial_pair_failure_removes_only_the_new_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.run-1.a-1.rejected.md"
            original_create = evidence_module._atomic_create
            calls = 0

            def fail_second(target: Path, data: bytes) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated sidecar failure")
                original_create(target, data)

            with patch.object(evidence_module, "_atomic_create", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "simulated"):
                    persist_rejected_pair(
                        path, b"candidate", "explanation", candidate_sha256=hashlib.sha256(b"candidate").hexdigest(),
                    )
            self.assertFalse(path.exists())
            self.assertFalse(rejection_explanation_path(path).exists())

    def test_incomplete_pair_refuses_and_preserves_a_preexisting_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.run-1.a-1.rejected.md"
            sidecar = rejection_explanation_path(path)
            sidecar.write_text("user-owned evidence", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                persist_rejected_pair(
                    path, b"candidate", "new explanation", candidate_sha256=hashlib.sha256(b"candidate").hexdigest(),
                )
            self.assertFalse(path.exists())
            self.assertEqual("user-owned evidence", sidecar.read_text(encoding="utf-8"))

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

    def test_schema_three_requires_rejected_stage_and_explanation_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "package"
            shutil.copytree(ROOT / "examples" / "markdown_repair", target)
            manifest_path = target / "package.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            del manifest["evidence_policy"]["rejected_explanation_pattern"]
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(PackageError, "rejected_explanation_pattern"):
                validate_package(target)

            manifest = yaml.safe_load((ROOT / "examples" / "markdown_repair" / "package.yaml").read_text(encoding="utf-8"))
            del manifest["evidence_policy"]["rejected_stage_pattern"]
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(PackageError, "rejected_stage_pattern"):
                validate_package(target)

    def test_rejected_artifacts_are_ignored_by_default(self) -> None:
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in ("*.rejected.md", "*.rejected.json", "*.rejected.txt", "*.rejected.*"):
            self.assertIn(pattern, ignore)


if __name__ == "__main__":
    unittest.main()
