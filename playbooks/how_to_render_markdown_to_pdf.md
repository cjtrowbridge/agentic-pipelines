# Playbook: Render Markdown to PDF

## Use when

You need a repeatable, local PDF derivative of a trusted Markdown document on Windows or Linux. This is a deterministic rendering operation; it is not a model stage and does not authorize a PDF as model input. If a pipeline needs a PDF source, first extract and validate a linked Markdown/text derivative, then provide only that derivative to prompts.

## Load

- `AGENTS.md`
- `scripts/render_markdown_pdf.py`
- `requirements-markdown-pdf.txt`
- The source Markdown document and the active plan item that authorizes its rendering

## Renderer contract

Use `scripts/render_markdown_pdf.py`. On its first run it creates an ignored local virtual environment at `agentic-pipelines/.markdown-pdf-renderer/`, installs only the packages in `requirements-markdown-pdf.txt`, and restarts itself in that environment. It requires no browser, Pandoc, TeX distribution, or OS package manager.

The renderer reads UTF-8 or UTF-8-with-BOM Markdown and writes `<source-stem>.pdf` in the same directory. It atomically replaces the destination only after `xhtml2pdf` reports no errors and the temporary file begins with a PDF header. It emits visible bootstrap, rendering, completion, and failure messages; Ctrl+C returns status 130.

The dependency path is Python-package based and portable across supported CPython releases on Windows and Linux. Its packages may use platform wheels; “portable” means it has no separate browser, TeX, Pandoc, or OS-level renderer prerequisite. It is not a promise of pixel-identical output across all platforms: PDF library versions and available fonts can affect typography. Keep the dependency ranges declared and test the target platform for release-critical documents.

## Supported document profile

Use ordinary Markdown: headings, paragraphs, emphasis, links, lists, fenced code blocks, tables, and local images. The renderer uses a deliberately small embedded stylesheet and the `extra`, `sane_lists`, and `toc` Markdown extensions.

Avoid browser-dependent JavaScript, remote assets, arbitrary CSS, SVGs that need browser layout, advanced page floats, and Unicode glyphs not covered by the available PDF fonts. For multilingual or brand-critical output, supply and test a licensed Unicode font as an explicit renderer enhancement; do not silently substitute or claim fidelity without visual review.

## Procedure

1. Confirm an approved plan item authorizes the derivative and that the Markdown input is trusted. Do not render rejected evidence as an ordinary/final artifact; use the isolated diagnostic-rendering contract instead.
2. Run the renderer from the host root or any directory:

   ```powershell
   python agentic-pipelines/scripts/render_markdown_pdf.py path/to/document.md
   ```

   ```bash
   python3 agentic-pipelines/scripts/render_markdown_pdf.py path/to/document.md
   ```

3. On the first invocation, allow the visible local bootstrap to complete. It downloads packages through the configured Python package index. For an offline/reproducible environment, pre-populate the local environment using an approved package mirror; do not add an undeclared system renderer as a fallback.
4. Confirm that `path/to/document.pdf` exists, is nonempty, and begins with `%PDF-`. Open it for a human visual check whenever layout, tables, images, or non-ASCII text are material.
5. Treat a rendering failure as a failed derivative. Preserve the Markdown source and report the command/error; do not mislabel a partial PDF as success.

## Options and examples

Use `--no-bootstrap` in a controlled environment to fail if the renderer environment is not already ready:

```powershell
python agentic-pipelines/scripts/render_markdown_pdf.py --no-bootstrap docs/report.md
```

Place the local environment elsewhere only when the default ignored directory is unsuitable:

```bash
python3 agentic-pipelines/scripts/render_markdown_pdf.py --bootstrap-dir /tmp/markdown-pdf-env docs/report.md
```

## Verification

- Confirm the source path ends in `.md` or `.markdown` and the sibling output is `<stem>.pdf`.
- Confirm a zero exit code, a nonempty PDF, and a `%PDF-` header.
- Visually inspect representative tables, lists, code blocks, images, page breaks, and required characters for a release-critical document.
- Record the source/output paths, renderer dependency versions, platform, and any visual-review result in the applicable run evidence or checkpoint.

## Failure handling

- A missing Python `venv`/`pip`, package-install failure, unreadable source, or renderer error is a visible failure. Correct the environment or input and rerun; do not replace this renderer with an unreviewed platform-specific tool.
- If the PDF is invalid, the temporary file is removed and the prior sibling PDF remains untouched.
- If a local image cannot resolve, simplify or correct the Markdown path and verify the output visually. Remote images are intentionally not a reliable publication dependency.
