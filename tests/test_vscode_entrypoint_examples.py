import json
from pathlib import Path
import unittest


ROOT = Path("templates/vscode")


class VSCodeEntrypointExampleTests(unittest.TestCase):
    def test_tasks_are_visible_process_tasks_with_platform_native_dispatch(self) -> None:
        data = json.loads((ROOT / "tasks.example.json").read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "2.0.0")
        self.assertEqual(len(data["tasks"]), 2)
        self.assertEqual(len({task["label"] for task in data["tasks"]}), 2)
        for task in data["tasks"]:
            self.assertEqual(task["type"], "process")
            self.assertEqual(task["command"], "bash")
            self.assertTrue(task["args"][0].endswith("PATH_TO_HOST_BOOTSTRAP.sh"))
            self.assertEqual(task["windows"]["command"], "powershell.exe")
            self.assertIn("${workspaceFolder}\\PATH_TO_HOST_BOOTSTRAP.ps1", task["windows"]["args"])
            self.assertEqual(task["presentation"]["reveal"], "always")
            self.assertEqual(task["presentation"]["panel"], "dedicated")
            self.assertEqual(task["problemMatcher"], [])

    def test_launch_invokes_one_platform_wrapper_once(self) -> None:
        data = json.loads((ROOT / "launch.example.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["configurations"]), 1)
        launch = data["configurations"][0]
        self.assertEqual(launch["type"], "node-terminal")
        self.assertEqual(launch["request"], "launch")
        self.assertNotIn("preLaunchTask", launch)
        self.assertEqual(launch["command"].count("PATH_TO_HOST_BOOTSTRAP.sh"), 1)
        self.assertEqual(launch["windows"]["command"].count("PATH_TO_HOST_BOOTSTRAP.ps1"), 1)

    def test_examples_are_placeholders_without_installers_or_direct_python(self) -> None:
        paths = list(ROOT.iterdir())
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
        for forbidden in ("winget install", "apt-get install", "dnf install", "brew install", "sudo ", "pip install"):
            self.assertNotIn(forbidden, combined)
        tasks = (ROOT / "tasks.example.json").read_text(encoding="utf-8").lower()
        launch = (ROOT / "launch.example.json").read_text(encoding="utf-8").lower()
        self.assertNotIn("python", tasks)
        self.assertNotIn("python", launch)
        self.assertIn("replace_", combined)
        self.assertIn("not installable framework defaults", combined)

    def test_native_examples_check_then_delegate(self) -> None:
        powershell = (ROOT / "bootstrap.example.ps1").read_text(encoding="utf-8")
        bash = (ROOT / "bootstrap.example.sh").read_text(encoding="utf-8")
        self.assertLess(powershell.index("Get-Command REPLACE_PREREQUISITE_COMMAND"), powershell.index("& REPLACE_PIPELINE_COMMAND"))
        self.assertLess(bash.index("command -v REPLACE_PREREQUISITE_COMMAND"), bash.index("exec REPLACE_PIPELINE_COMMAND"))
        self.assertIn("exit 130", powershell)
        self.assertIn("exit 130", bash)


if __name__ == "__main__":
    unittest.main()
