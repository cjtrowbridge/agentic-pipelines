"""Exercise the non-installable host bootstrap example in an isolated directory."""

from contextlib import redirect_stdout
from importlib.util import module_from_spec, spec_from_file_location
from io import StringIO
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


EXAMPLE = Path("templates/bootstrap")


class HostBootstrapExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in ("bootstrap.py", "bootstrap-v1.py"):
            shutil.copy2(EXAMPLE / name, scripts / name)
        self.entrypoint = scripts / "bootstrap.py"
        self.marker = self.root / ".agentic-pipelines" / "bootstrap-example.ready"

    def invoke(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(self.entrypoint), *args],
            capture_output=True,
            text=True,
            timeout=15,
        )

    def load_implementation(self):
        path = self.root / "scripts" / "bootstrap-v1.py"
        spec = spec_from_file_location("host_bootstrap_example", path)
        assert spec is not None and spec.loader is not None
        module = module_from_spec(spec)
        with patch.dict(sys.modules, {spec.name: module}):
            spec.loader.exec_module(module)
        return module

    def test_check_is_read_only_and_reports_failure_then_success(self) -> None:
        missing = self.invoke("--check")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("FAIL example local state", missing.stdout)
        self.assertIn("TOTAL pass=0 fail=1", missing.stdout)
        self.assertFalse(self.marker.exists())

        applied = self.invoke()
        self.assertEqual(applied.returncode, 0)
        self.assertIn("(repaired)", applied.stdout)
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "ready\n")
        timestamp = self.marker.stat().st_mtime_ns

        repeated = self.invoke()
        self.assertEqual(repeated.returncode, 0)
        self.assertNotIn("(repaired)", repeated.stdout)
        self.assertEqual(self.marker.stat().st_mtime_ns, timestamp)

        healthy = self.invoke("--check")
        self.assertEqual(healthy.returncode, 0)
        self.assertIn("TOTAL pass=1 fail=0", healthy.stdout)
        self.assertEqual(self.marker.stat().st_mtime_ns, timestamp)

    def test_corrupt_state_is_repaired_only_in_normal_mode(self) -> None:
        self.marker.parent.mkdir()
        self.marker.write_text("broken\n", encoding="utf-8")
        failure = self.invoke("--check")
        self.assertEqual(failure.returncode, 1)
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "broken\n")
        repaired = self.invoke()
        self.assertEqual(repaired.returncode, 0)
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "ready\n")

    def test_independent_checks_report_totals_and_failed_repairs(self) -> None:
        module = self.load_implementation()
        actions: list[str] = []

        def failed_repair() -> None:
            actions.append("repair")
            raise RuntimeError("repair unavailable")

        checks = [
            module.Requirement("healthy service", lambda: (True, "ready")),
            module.Requirement("unhealthy service", lambda: (False, "not ready"), failed_repair),
        ]
        output = StringIO()
        with redirect_stdout(output):
            status = module.run(checks, check_only=True)
        self.assertEqual(status, 1)
        self.assertEqual(actions, [])
        self.assertIn("TOTAL pass=1 fail=1", output.getvalue())

        output = StringIO()
        with redirect_stdout(output):
            status = module.run(checks, check_only=False)
        self.assertEqual(status, 1)
        self.assertEqual(actions, ["repair"])
        self.assertIn("FAIL unhealthy service: RuntimeError: repair unavailable", output.getvalue())

    def test_empty_inventory_fails(self) -> None:
        module = self.load_implementation()
        output = StringIO()
        with redirect_stdout(output):
            status = module.run([], check_only=True)
        self.assertEqual(status, 1)
        self.assertIn("TOTAL pass=0 fail=1", output.getvalue())

    def test_interrupt_returns_130(self) -> None:
        module = self.load_implementation()

        def interrupt() -> tuple[bool, str]:
            raise KeyboardInterrupt

        with patch.object(module, "requirements", return_value=[module.Requirement("interrupted", interrupt)]), patch.object(sys, "argv", ["bootstrap-v1.py"]):
            with redirect_stdout(StringIO()):
                self.assertEqual(module.main(), 130)


if __name__ == "__main__":
    unittest.main()
