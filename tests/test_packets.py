from __future__ import annotations

import unittest

from pipeline_runtime.packets import PacketBudgetError, PacketManifest, SourceRecord, bounded_records, require_packet_budget


class PacketTests(unittest.TestCase):
    def test_forbidden_roles_and_over_budget_records_are_omitted(self) -> None:
        records = [
            SourceRecord("posting", "posting.md", "primary_source", "text/markdown", "a"),
            SourceRecord("resume", "resume.md", "accepted_artifact", "text/markdown", "b"),
            SourceRecord("flyer", "flyer.md", "supplemental_source", "text/markdown", "c"),
        ]
        selected, omitted = bounded_records(records, allowed_roles={"primary_source"}, max_bytes=1000)
        self.assertEqual(["posting"], [record.source_id for record in selected])
        self.assertEqual(["resume", "flyer"], [record.source_id for record in omitted])

    def test_complete_assembled_budget_is_enforced(self) -> None:
        manifest = PacketManifest(
            stage="review", allowed_roles=("primary_source",), component_bytes={"posting": 10, "cv": 10},
            selected_source_ids=("posting",), omitted_source_ids=(), static_prompt_bytes=10,
            assembled_request_bytes=101, context_limit=1024, completion_limit=128,
        )
        with self.assertRaisesRegex(PacketBudgetError, "packet_budget_exhausted"):
            require_packet_budget(manifest, max_request_bytes=100)


if __name__ == "__main__":
    unittest.main()
