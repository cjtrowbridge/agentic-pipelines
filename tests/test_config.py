import tempfile
import unittest
from pathlib import Path

from pipeline_runtime.config import ConfigError, load_api_config


class ConfigTests(unittest.TestCase):
    def test_remote_endpoint_requires_explicit_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "api.yaml"
            path.write_text("schema_version: 1\nprovider: ollama\nendpoint: https://example.com\nmodel: x\n", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_api_config(path)


if __name__ == "__main__":
    unittest.main()
