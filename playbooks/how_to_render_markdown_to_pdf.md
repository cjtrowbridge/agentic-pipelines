# Playbook: Render Markdown to PDF

## Use when

Regenerate a trusted Markdown document's local PDF derivative. Regenerate after every source edit. This deterministic operation does not authorize PDF input to models; extract and validate text first.

## Load

- `AGENTS.md`
- `scripts/render_markdown_pdf.py`
- `requirements-markdown-pdf.txt`
- `assets/pdf-fonts/README.md`
- Source Markdown and authorizing plan item

## Contract

Run:

```powershell
python agentic-pipelines/scripts/render_markdown_pdf.py path/to/document.md
```

On Linux use `python3` if needed. Requires CPython 3.11/3.12 with venv/pip. Bootstrap installs declared versions into ignored `.markdown-pdf-renderer/`; system Python remains untouched. First installation requires package-index access or a preconfigured offline wheelhouse. No browser, Pandoc, TeX, OS package manager, or installed fonts are required. Python dependencies include platform wheels.

Uses Markdown, fpdf2, HarfBuzz and checksum-verified bundled Noto text/code/color-emoji fonts. UTF-8/BOM `.md` or `.markdown` becomes sibling `<stem>.pdf`. The PDF metadata title is the first H1 (or a readable source-filename fallback), never a generic renderer label. Promotion is atomic after PDF/page validation. Failure/interruption preserves the prior PDF; Ctrl+C exits 130. Progress is visible.

## Document profile

Supports headings, paragraphs, emphasis, links, lists, code, tables and local images. Unicode coverage follows bundled fonts; additional scripts require explicit fonts and shaping validation. Color emoji and compound sequences use a fixed font release. Missing characters fail visibly.

Layout: Letter, 0.6-inch margins, 9-point body, repeating table headers. Three-column tables use 26/28/46 percent widths; others are equal-width. Cells are left/top aligned. Table-cell inline code preserves text using the table font. Embedded CSS is replaced with this profile, visibly reported; `report-page-break` is supported. Arbitrary CSS/JavaScript, remote images and rows taller than a page are unsupported.

## Verification and failure handling

Check zero exit, nonempty sibling PDF and readable pages. Visually review tables, images, emoji and page breaks; test extraction separately. Record versions/platform and validation gaps. Correct input/environment and rerun; never report stale output as newly rendered.

`--no-bootstrap` rejects missing/outdated environments. `--bootstrap-dir PATH` selects another environment. Run `tests/test_render_markdown_pdf.py` using renderer dependencies; CI covers Windows/Linux. Byte-identical output and universal Unicode coverage are not promised.
