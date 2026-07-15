from pathlib import Path
import unittest


class RouterTests(unittest.TestCase):
    def test_agents_is_the_only_root_instruction_file(self) -> None:
        text = Path("AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Pipelines is a prompt-first framework", text)
        self.assertIn("## Task routing", text)
        self.assertIn("## Universal invariants", text)
        self.assertIn("./pipelines/AGENTS.md", text)
        for name in ("RULES.md", "CODEX.md", "CLAUDE.md", "GEMINI.md", "OPENCODE.md"):
            self.assertFalse(Path(name).exists(), name)

    def test_every_agent_route_exists(self) -> None:
        text = Path("AGENTS.md").read_text(encoding="utf-8")
        for value in text.split("`")[1::2]:
            if value.startswith("playbooks/"):
                self.assertTrue(Path(value).exists(), value)


if __name__ == "__main__":
    unittest.main()
