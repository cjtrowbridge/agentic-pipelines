from pathlib import Path
import re
import unittest


class PlaybookTests(unittest.TestCase):
    def test_routed_playbooks_are_small_and_structured(self) -> None:
        agents = Path("AGENTS.md").read_text(encoding="utf-8")
        routed = sorted(set(re.findall(r"`(playbooks/[^`]+\.md)`", agents)))
        self.assertGreaterEqual(len(routed), 10)
        for value in routed:
            text = Path(value).read_text(encoding="utf-8")
            self.assertLess(len(text.split()), 350, value)
            self.assertIn("## Use when", text, value)
            self.assertIn("## Load", text, value)


if __name__ == "__main__":
    unittest.main()
