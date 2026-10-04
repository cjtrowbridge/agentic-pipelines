#!/usr/bin/env python3
"""Render a Markdown file to a sibling PDF using a local, self-bootstrapped environment.

The renderer deliberately supports a portable Markdown and CSS subset.  It has no
browser, Pandoc, TeX, or system package dependency; the first run creates an
ignored virtual environment beside this script and installs the declared Python
packages into it.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import logging
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unicodedata
from urllib.parse import unquote, urlparse


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = SCRIPT_ROOT / "requirements-markdown-pdf.txt"
DEFAULT_BOOTSTRAP_DIR = SCRIPT_ROOT / ".markdown-pdf-renderer"
BOOTSTRAPPED = "MARKDOWN_PDF_RENDERER_BOOTSTRAPPED"
FONT_ROOT = SCRIPT_ROOT / "assets" / "pdf-fonts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a Markdown file to a PDF in the same directory."
    )
    parser.add_argument("markdown", type=Path, help="Markdown source file (.md or .markdown)")
    parser.add_argument(
        "--bootstrap-dir",
        type=Path,
        default=DEFAULT_BOOTSTRAP_DIR,
        help="ignored local virtual-environment directory (default: beside this script)",
    )
    parser.add_argument(
        "--no-bootstrap",
        action="store_true",
        help="fail instead of creating or updating the local renderer environment",
    )
    return parser.parse_args()


def venv_python(bootstrap_dir: Path) -> Path:
    return bootstrap_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def bootstrap(bootstrap_dir: Path, allow_bootstrap: bool) -> Path:
    python = venv_python(bootstrap_dir)
    if not python.is_file():
        if not allow_bootstrap:
            raise RuntimeError(f"renderer environment is missing: {bootstrap_dir}")
        print(f"bootstrap: creating local environment at {bootstrap_dir}", flush=True)
        subprocess.run([sys.executable, "-m", "venv", str(bootstrap_dir)], check=True)

    # Check declared versions as well as imports, including upgrades from the old backend.
    check = """import importlib.metadata, pathlib, sys
requirements = pathlib.Path(sys.argv[1]).read_text().splitlines()
for line in requirements:
    if not line.strip() or line.startswith('#'):
        continue
    name, version = line.split('==')
    assert importlib.metadata.version(name) == version, name
import markdown, fpdf, uharfbuzz, bs4, pypdf
"""
    available = subprocess.run(
        [str(python), "-c", check, str(REQUIREMENTS)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    if available:
        print("bootstrap: declared renderer dependencies are ready", flush=True)
        return python
    if not allow_bootstrap:
        raise RuntimeError("renderer dependencies are missing or outdated; rerun without --no-bootstrap")
    print("bootstrap: installing declared Markdown-to-PDF dependencies", flush=True)
    subprocess.run(
        [
            str(python), "-m", "pip", "install", "--disable-pip-version-check",
            "--only-binary=:all:", "--upgrade", "-r", str(REQUIREMENTS),
        ],
        check=True,
    )
    return python


def restart_in_environment(args: argparse.Namespace) -> int:
    bootstrap_dir = args.bootstrap_dir.resolve()
    python = bootstrap(bootstrap_dir, not args.no_bootstrap)
    environment = os.environ.copy()
    environment[BOOTSTRAPPED] = "1"
    command = [str(python), str(Path(__file__).resolve()), str(args.markdown)]
    command.extend(["--bootstrap-dir", str(bootstrap_dir), "--no-bootstrap"])
    print("render: starting isolated renderer", flush=True)
    return subprocess.run(command, env=environment).returncode


def document_html(markdown_text: str) -> str:
    import markdown

    body = markdown.markdown(
        markdown_text,
        extensions=["extra", "sane_lists", "toc"],
        output_format="xhtml",
    )
    return body


def verify_fonts() -> None:
    manifest = json.loads((FONT_ROOT / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest.items():
        path = FONT_ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(f"bundled font is missing or corrupt: {name}")


def prepare_html(body: str, source_dir: Path) -> str:
    """Use an explicit HTML subset; external styles never select system fonts."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(body, "html.parser")
    if soup.find("style"):
        print("render: using portable document styling instead of embedded CSS", flush=True)
    for element in soup.find_all(["style", "script", "head"]):
        element.decompose()
    for element in soup.find_all(True):
        element.attrs.pop("style", None)
        if "report-page-break" in element.get("class", []):
            element["style"] = "break-before: page"
    for cell in soup.find_all(["td", "th"]):
        cell["align"] = "left"
    for paragraph in soup.find_all("p"):
        paragraph["align"] = "left"
    for table in soup.find_all("table"):
        table["border"] = "1"
        table["cellpadding"] = "3"
        table["width"] = "100%"
        # Report tables give the description column more room; others are equal-width.
        first = table.find("tr")
        cells = first.find_all(["th", "td"], recursive=False) if first else []
        widths = [26, 28, 46] if len(cells) == 3 else [100 / len(cells)] * len(cells)
        for cell, width in zip(cells, widths):
            cell["width"] = f"{width}%"
            cell["align"] = "left"
            cell["bgcolor"] = "#e2e8f0"
        # fpdf2's supported table markup does not need row-group wrappers.
        for group in table.find_all(["thead", "tbody", "tfoot"]):
            group.unwrap()
        # fpdf2 cannot switch to a code font inside its HTML table cells.
        # Preserve literal code text rather than dropping it or rejecting ordinary tables.
        for code in table.find_all("code"):
            code.unwrap()
    for image in soup.find_all("img"):
        uri = str(image.get("src", ""))
        # Absolute Windows paths are not URI schemes.
        path = Path(unquote(uri))
        if not path.is_absolute() and urlparse(uri).scheme:
            raise ValueError(f"only local image paths are supported: {uri}")
        if not path.is_absolute():
            path = source_dir / path
        if not path.is_file():
            raise FileNotFoundError(f"local image is missing: {path}")
        image["src"] = str(path.resolve())
    return str(soup)


def document_title(html: str, markdown_path: Path) -> str:
    """Derive the PDF metadata title from the rendered document, never a generic label."""
    from bs4 import BeautifulSoup

    heading = BeautifulSoup(html, "html.parser").find("h1")
    if heading:
        title = " ".join(heading.get_text(" ", strip=True).split())
        if title:
            return title
    return markdown_path.stem.replace("_", " ").replace("-", " ")


def create_pdf(html: str, title: str = "Markdown document"):
    from bs4 import BeautifulSoup
    from fpdf import FPDF
    from fpdf.html import HTML2FPDF
    from fpdf.enums import VAlign
    from fpdf.line_break import Fragment
    from fpdf.fonts import TextStyle
    from fontTools.ttLib import TTFont

    verify_fonts()
    coverage = set()
    for path in FONT_ROOT.glob("*.ttf"):
        with TTFont(path) as font:
            coverage.update(font.getBestCmap())
    displayed = BeautifulSoup(html, "html.parser").get_text()
    missing = sorted({
        ord(char) for char in displayed
        if ord(char) not in coverage and not char.isspace()
        and unicodedata.category(char) != "Cf"
        and not (0xFE00 <= ord(char) <= 0xFE0F or 0xE0100 <= ord(char) <= 0xE01EF)
    })
    if missing:
        raise RuntimeError("bundled fonts lack required characters: " + ", ".join(f"U+{point:04X}" for point in missing))
    class PortableHTML(HTML2FPDF):
        def handle_starttag(self, tag, attrs):
            super().handle_starttag(tag, attrs)
            if tag == "table":
                # Pinned fpdf2 HTML adapter does not expose table vertical alignment.
                self.table._v_align = VAlign.T

    class PortablePDF(FPDF):
        def _parse_chars(self, text, markdown, **kwargs):
            # fpdf2 selects fallback fonts per character. Keep ASCII-base keycaps
            # in one emoji-font shaping run instead of splitting their digits off.
            if not re.search(r"[#*0-9]\ufe0f?\u20e3", text):
                yield from super()._parse_chars(text, markdown, **kwargs)
                return
            fragments = list(super()._parse_chars(text, markdown, **kwargs))
            chars = [(char, fragment) for fragment in fragments for char in fragment.characters]
            displayed = "".join(char for char, _ in chars)
            sequences = {match.start(): match.end() for match in re.finditer(r"[#*0-9]\ufe0f?\u20e3", displayed)}
            index = 0
            while index < len(chars):
                original = chars[index][1]
                if index in sequences:
                    end = sequences[index]
                    state = copy.copy(original.graphics_state)
                    state.current_font = self.fonts["notoemoji"]
                    state.font_family = "notoemoji"
                    state.font_style = ""
                    yield Fragment(displayed[index:end], state, original.k, original.link)
                else:
                    end = index + 1
                    while end < len(chars) and end not in sequences and chars[end][1] is original:
                        end += 1
                    yield Fragment(displayed[index:end], original.graphics_state, original.k, original.link)
                index = end

    pdf = PortablePDF(unit="pt", format="letter")
    pdf.HTML2FPDF_CLASS = PortableHTML
    pdf.set_margins(43.2, 43.2, 43.2)
    pdf.set_auto_page_break(True, 43.2)
    pdf.set_title(title)
    pdf.set_creator("Agentic Pipelines portable Markdown renderer")
    emoji = TTFont(FONT_ROOT / "Noto-COLRv1.ttf")
    emoji_points = {cp for cp in emoji.getBestCmap() if cp >= 0x2000}
    emoji.close()
    for style, name in [("", "Regular"), ("B", "Bold"), ("I", "Italic"), ("BI", "BoldItalic")]:
        font = TTFont(FONT_ROOT / f"NotoSans-{name}.ttf")
        text_points = set(font.getBestCmap()) - emoji_points
        font.close()
        pdf.add_font("NotoSans", style, FONT_ROOT / f"NotoSans-{name}.ttf", unicode_range=list(text_points))
    pdf.add_font("NotoMono", fname=FONT_ROOT / "NotoSansMono-Regular.ttf")
    pdf.add_font("NotoEmoji", fname=FONT_ROOT / "Noto-COLRv1.ttf")
    pdf.set_fallback_fonts(["NotoEmoji", "NotoSans"], exact_match=False)
    pdf.set_text_shaping(True)
    pdf.set_font("NotoSans", size=9)
    pdf.set_text_color(31, 41, 55)
    pdf.set_draw_color(148, 163, 184)
    pdf.add_page()
    pdf.write_html(
        html, table_line_separators=True,
        tag_styles={
            "h1": TextStyle(font_size_pt=18, font_style="B", b_margin=0.15),
            "h2": TextStyle(font_size_pt=13, font_style="B", t_margin=3, b_margin=0.15),
            "h3": TextStyle(font_size_pt=11, font_style="B", t_margin=3, b_margin=0.15),
            "p": TextStyle(t_margin=1.4, b_margin=1.4),
            "code": TextStyle(font_family="NotoMono"),
            "pre": TextStyle(font_family="NotoMono", font_size_pt=8),
        },
    )
    return pdf


class RenderWarnings(logging.Handler):
    """A PDF with discarded glyphs or unsupported content is not a successful derivative."""

    def __init__(self):
        super().__init__(logging.WARNING)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def render(markdown_path: Path) -> Path:
    from pypdf import PdfReader

    if not markdown_path.is_file():
        raise FileNotFoundError(f"Markdown source is not a file: {markdown_path}")
    if markdown_path.suffix.lower() not in {".md", ".markdown"}:
        raise ValueError("Markdown source must use a .md or .markdown extension")

    output = markdown_path.with_suffix(".pdf")
    html = prepare_html(document_html(markdown_path.read_text(encoding="utf-8-sig")), markdown_path.parent)
    title = document_title(html, markdown_path)

    print(f"render: {markdown_path.name} -> {output.name}", flush=True)
    with tempfile.NamedTemporaryFile(
        mode="w+b", suffix=".pdf", prefix=f".{output.stem}.", dir=output.parent, delete=False
    ) as temporary:
        temp_path = Path(temporary.name)
    warnings = RenderWarnings()
    logger = logging.getLogger("fpdf")
    logger.addHandler(warnings)
    pdf = None
    try:
        pdf = create_pdf(html, title)
        pdf.output(temp_path)
        if warnings.messages:
            raise RuntimeError("PDF rendering warnings: " + "; ".join(dict.fromkeys(warnings.messages)))
        payload = temp_path.read_bytes()
        if len(payload) < 5 or not payload.startswith(b"%PDF-"):
            raise RuntimeError("renderer did not produce a valid PDF header")
        reader = PdfReader(temp_path, strict=True)
        if not reader.pages:
            raise RuntimeError("renderer produced no PDF pages")
        for page in reader.pages:
            page.extract_text()
        page_count = len(reader.pages)
        print(f"validate: {page_count} readable PDF pages; bundled fonts and shaping used", flush=True)
        # Close any reader-owned handles before replacing on Windows.
        reader.close()
        temp_path.replace(output)
    finally:
        logger.removeHandler(warnings)
        if pdf is not None:
            for font in pdf.fonts.values():
                if hasattr(font, "ttfont"):
                    font.ttfont.close()
        temp_path.unlink(missing_ok=True)
    print(f"complete: wrote {output} ({output.stat().st_size} bytes)", flush=True)
    return output


def main() -> int:
    args = parse_args()
    try:
        if os.environ.get(BOOTSTRAPPED) != "1":
            return restart_in_environment(args)
        render(args.markdown.resolve())
        return 0
    except KeyboardInterrupt:
        print("interrupted: no successful render reported", file=sys.stderr, flush=True)
        return 130
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
