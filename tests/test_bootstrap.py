import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.bootstrap_pipeline_environment import bootstrap, fingerprint, within


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_installs_declared_requirements_then_reuses_a_matching_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            requirement = root / "requirements.txt"
            requirement.write_text("example==1\n", encoding="utf-8")
            target = root / ".agentic-pipelines" / "dependencies"
            with patch("scripts.bootstrap_pipeline_environment.dependencies_available", return_value=True) as available, patch("scripts.bootstrap_pipeline_environment.subprocess.run") as run:
                self.assertTrue(bootstrap(root, target, [requirement], ["example"]))

            run.assert_called_once()
            recorded = json.loads((target.parent / "bootstrap.json").read_text(encoding="utf-8"))
            self.assertEqual(recorded["fingerprint"], fingerprint([requirement]))
            self.assertEqual(available.call_count, 1)

            with patch("scripts.bootstrap_pipeline_environment.dependencies_available", return_value=True), patch("scripts.bootstrap_pipeline_environment.subprocess.run") as run:
                self.assertFalse(bootstrap(root, target, [requirement], ["example"]))
            run.assert_not_called()

    def test_bootstrap_rejects_paths_outside_the_host(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                within(root, root.parent / "outside")


if __name__ == "__main__":
    unittest.main()
