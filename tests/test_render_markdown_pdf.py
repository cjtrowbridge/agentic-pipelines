"""Run with the renderer virtual environment; no system fonts or browser required."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

try:
    import bs4
    import fpdf
    import uharfbuzz
    from pypdf import PdfReader
except ImportError as exc:
    raise unittest.SkipTest("Install requirements-markdown-pdf.txt to run renderer tests") from exc

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_markdown_pdf.py"
spec = importlib.util.spec_from_file_location("markdown_pdf", SCRIPT)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class RendererTests(unittest.TestCase):
    def test_unicode_color_and_compound_emoji_are_extractable(self):
        with tempfile.TemporaryDirectory(prefix="pdf Unicode space ") as directory:
            source = Path(directory) / "café report.md"
            text = "✅ ⏳ ⏸️ 🔀 😀 👩🏽‍💻 👨‍👩‍👧‍👦 🇺🇸 1️⃣"
            source.write_text(
                "# Unicode café — Δοκιμή\n\n" + text + "\n\n"
                "| Item | Status | Detail |\n|---|---|---|\n"
                "| **Ben** | ⏳ | `literal_code` |\n\n"
                "- one\n- two\n\n```python\nprint('café')\n```\n",
                encoding="utf-8-sig",
            )
            pdf = renderer.render(source)
            reader = PdfReader(pdf)
            extracted = "\n".join(page.extract_text() for page in reader.pages)
            for expected in ["café", "Δοκιμή", "literal_code", "Ben", "✅", "⏳", "🔀", "👩🏽‍💻", "👨‍👩‍👧‍👦", "🇺🇸", "1️⃣"]:
                self.assertIn(expected, extracted)
            # Color font is represented through glyph resources, not source <img> rewriting.
            resources = reader.pages[0]["/Resources"]
            self.assertIn("/Font", resources)
            self.assertTrue(any(font.get_object().get("/Subtype") == "/Type3" for font in resources["/Font"].values()))

    def test_pdf_metadata_uses_h1_or_readable_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            headed = root / "ignored-name.md"
            headed.write_text("# A deliberate report title\n", encoding="utf-8")
            self.assertEqual(
                PdfReader(renderer.render(headed)).metadata.title,
                "A deliberate report title",
            )
            unheaded = root / "week_7-status-report.md"
            unheaded.write_text("No heading here.\n", encoding="utf-8")
            self.assertEqual(
                PdfReader(renderer.render(unheaded)).metadata.title,
                "week 7 status report",
            )

    def test_long_table_repeats_headings_without_losing_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "table.md"
            rows = "\n".join(f"| Row {i:03d} | ✅ | {'wrapped detail ' * 12} |" for i in range(65))
            source.write_text("| Item | Status | Detail |\n|---|---|---|\n" + rows, encoding="utf-8")
            reader = PdfReader(renderer.render(source))
            self.assertGreater(len(reader.pages), 1)
            text = "\n".join(page.extract_text() for page in reader.pages)
            self.assertEqual(text.count("Row "), 65)
            for page in reader.pages:
                self.assertIn("Status", page.extract_text())

    def test_keycap_sequences_use_one_shaping_run_without_changing_plain_digits(self):
        pdf = renderer.create_pdf('<p>Plain 123. Keycaps 1️⃣ #️⃣ *️⃣.</p>')
        try:
            fragments = list(pdf._parse_chars('Plain 123. Keycaps 1️⃣ #️⃣ *️⃣.', False))
            for sequence in ['1️⃣', '#️⃣', '*️⃣']:
                self.assertTrue(any(sequence in ''.join(f.characters) and f.font.fontkey == 'notoemoji' for f in fragments))
            self.assertTrue(any('123' in ''.join(f.characters) and f.font.fontkey != 'notoemoji' for f in fragments))
        finally:
            for font in pdf.fonts.values():
                font.ttfont.close()

    def test_unsupported_glyph_preserves_previous_pdf_and_cleans_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.md"
            source.write_text("Missing glyph: \U00010ffff", encoding="utf-8")
            output = source.with_suffix(".pdf")
            output.write_bytes(b"previous PDF")
            with self.assertRaisesRegex(RuntimeError, "glyph|character"):
                renderer.render(source)
            self.assertEqual(output.read_bytes(), b"previous PDF")
            self.assertEqual(list(Path(directory).glob(".bad.*.pdf")), [])

    def test_missing_and_remote_images_fail_before_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "image.md"
            for uri in ["missing.png", "https://example.com/image.png"]:
                source.write_text(f"![image]({uri})", encoding="utf-8")
                with self.assertRaises((ValueError, FileNotFoundError)):
                    renderer.render(source)
                self.assertFalse(source.with_suffix(".pdf").exists())

    def test_interrupt_preserves_destination_and_removes_temporary(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "interrupt.md"
            source.write_text("hello", encoding="utf-8")
            source.with_suffix(".pdf").write_bytes(b"previous")
            with patch.object(renderer, "create_pdf", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    renderer.render(source)
            self.assertEqual(source.with_suffix(".pdf").read_bytes(), b"previous")
            self.assertEqual(list(Path(directory).glob(".interrupt.*.pdf")), [])

    def test_corrupt_or_missing_font_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(renderer, "FONT_ROOT", Path(directory)):
                with self.assertRaises(FileNotFoundError):
                    renderer.verify_fonts()
            root = Path(directory)
            (root / "manifest.json").write_text('{"broken.ttf": "wrong"}', encoding="utf-8")
            (root / "broken.ttf").write_bytes(b"broken")
            with patch.object(renderer, "FONT_ROOT", root):
                with self.assertRaisesRegex(RuntimeError, "corrupt"):
                    renderer.verify_fonts()

    def test_local_image_resolves_relative_to_source_not_working_directory(self):
        from PIL import Image

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Image.new("RGB", (20, 20), "red").save(root / "local image.png")
            source = root / "image.md"
            source.write_text('![Local](local%20image.png)', encoding="utf-8")
            reader = PdfReader(renderer.render(source))
            self.assertIn("/XObject", reader.pages[0]["/Resources"])

    def test_ready_environment_reuses_declared_dependencies_without_install(self):
        environment = Path(sys.prefix)
        with patch.object(renderer, "venv_python", return_value=Path(sys.executable)), patch.object(renderer.subprocess, "run", wraps=subprocess.run) as run:
            self.assertEqual(renderer.bootstrap(environment, False), renderer.venv_python(environment))
            self.assertEqual(run.call_count, 1)

    def test_outdated_environment_no_bootstrap_fails_without_install(self):
        with patch.object(renderer, "venv_python", return_value=Path(sys.executable)), patch.object(renderer.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)) as run:
            with self.assertRaisesRegex(RuntimeError, "outdated"):
                renderer.bootstrap(Path(sys.prefix), False)
            self.assertEqual(run.call_count, 1)

    def test_no_bootstrap_missing_environment_is_actionable(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--no-bootstrap", "--bootstrap-dir", str(Path(directory) / "missing"), "unused.md"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("renderer environment is missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
