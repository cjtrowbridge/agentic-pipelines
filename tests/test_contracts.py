from __future__ import annotations

import json
import unittest
from pathlib import Path

from pipeline_runtime.prompts import OutputSchemas, PromptError, load_prompt

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_every_catalog_prompt_loads_and_has_a_real_schema(self) -> None:
        schemas = OutputSchemas(ROOT / "schemas" / "prompt_outputs.schema.json")
        for path in (ROOT / "prompts").glob("*/*.md"):
            if path.name == "README.md":
                continue
            contract = load_prompt(path)
            self.assertTrue(schemas.has(contract.output), path)

    def test_worker_output_fails_closed(self) -> None:
        schemas = OutputSchemas(ROOT / "schemas" / "prompt_outputs.schema.json")
        with self.assertRaises(PromptError):
            schemas.validate("worker_result", "not JSON")
        with self.assertRaises(PromptError):
            schemas.validate("worker_result", json.dumps({"status": "candidate", "candidate": None, "reason": None}))

    def test_prompt_rejects_missing_and_extra_context(self) -> None:
        contract = load_prompt(ROOT / "prompts" / "execute" / "worker.md")
        with self.assertRaises(PromptError):
            contract.render({"goal": "x"})
        values = {name: "x" for name in contract.inputs}
        values["unrelated_repository_context"] = "must not load"
        with self.assertRaises(PromptError):
            contract.render(values)


if __name__ == "__main__":
    unittest.main()
