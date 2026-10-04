#!/usr/bin/env python3
"""Render a Markdown file to a sibling PDF using a local, self-bootstrapped environment.

The renderer deliberately supports a portable Markdown and CSS subset.  It has no
browser, Pandoc, TeX, or system package dependency; the first run creates an
ignored virtual environment beside this script and installs the declared Python
packages into it.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = SCRIPT_ROOT / "requirements-markdown-pdf.txt"
DEFAULT_BOOTSTRAP_DIR = SCRIPT_ROOT / ".markdown-pdf-renderer"
BOOTSTRAPPED = "MARKDOWN_PDF_RENDERER_BOOTSTRAPPED"


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

    if not allow_bootstrap:
        return python
    available = subprocess.run(
        [str(python), "-c", "import markdown; import xhtml2pdf"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    if available:
        print("bootstrap: declared renderer dependencies are ready", flush=True)
        return python
    print("bootstrap: installing declared Markdown-to-PDF dependencies", flush=True)
    subprocess.run(
        [
            str(python), "-m", "pip", "install", "--disable-pip-version-check",
            "--upgrade", "-r", str(REQUIREMENTS),
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
    return f"""<!doctype html>
<html><head><meta charset=\"utf-8\"><style>
@page {{ size: letter; margin: 0.75in; }}
body {{ font-family: Helvetica, sans-serif; font-size: 10pt; line-height: 1.35; }}
h1, h2, h3 {{ color: #1f2937; }}
h1 {{ font-size: 20pt; }} h2 {{ font-size: 15pt; }} h3 {{ font-size: 12pt; }}
pre {{ background: #f3f4f6; border: 1px solid #d1d5db; padding: 6pt; }}
code {{ font-family: Courier, monospace; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #9ca3af; padding: 4pt; vertical-align: top; }}
th {{ background: #e5e7eb; }}
img {{ max-width: 100%; }}
</style></head><body>{body}</body></html>"""


def render(markdown_path: Path) -> Path:
    from xhtml2pdf import pisa

    if not markdown_path.is_file():
        raise FileNotFoundError(f"Markdown source is not a file: {markdown_path}")
    if markdown_path.suffix.lower() not in {".md", ".markdown"}:
        raise ValueError("Markdown source must use a .md or .markdown extension")

    output = markdown_path.with_suffix(".pdf")
    html = document_html(markdown_path.read_text(encoding="utf-8-sig"))
    def resolve_asset(uri: str, _relative: str) -> str:
        candidate = Path(uri)
        if not candidate.is_absolute():
            candidate = markdown_path.parent / candidate
        return str(candidate.resolve())

    print(f"render: {markdown_path.name} -> {output.name}", flush=True)
    with tempfile.NamedTemporaryFile(
        mode="w+b", suffix=".pdf", prefix=f".{output.stem}.", dir=output.parent, delete=False
    ) as temporary:
        temp_path = Path(temporary.name)
        result = pisa.CreatePDF(
            html, dest=temporary, encoding="utf-8", link_callback=resolve_asset
        )
    try:
        if result.err:
            raise RuntimeError(f"xhtml2pdf reported {result.err} rendering error(s)")
        payload = temp_path.read_bytes()
        if len(payload) < 5 or not payload.startswith(b"%PDF-"):
            raise RuntimeError("renderer did not produce a valid PDF header")
        temp_path.replace(output)
    finally:
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
    except (FileNotFoundError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
