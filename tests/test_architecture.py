from pathlib import Path
import unittest


class ArchitectureTests(unittest.TestCase):
    def test_only_api_adapter_imports_provider_http(self) -> None:
        root = Path("pipeline_runtime")
        forbidden = ("urlopen", "requests.", "httpx.", "/api/chat")
        for path in root.glob("*.py"):
            if path.name == "api.py":
                continue
            text = path.read_text(encoding="utf-8")
            for term in forbidden:
                self.assertNotIn(term, text, f"{term} in {path}")


if __name__ == "__main__":
    unittest.main()
