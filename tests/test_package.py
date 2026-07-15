from pathlib import Path
import unittest

from pipeline_runtime.package import validate_package


class PackageTests(unittest.TestCase):
    def test_reference_package_is_complete_and_non_running(self) -> None:
        root = Path(__file__).resolve().parents[1] / "examples" / "markdown_repair"
        result = validate_package(root)
        self.assertEqual("markdown-reference", result["pipeline_id"])
        self.assertEqual(6, result["prompt_count"])


if __name__ == "__main__":
    unittest.main()
