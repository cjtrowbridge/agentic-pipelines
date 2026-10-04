---
plan_id: 2026-10-04-13-54-10_unicode-markdown-pdf
title: Render portable Markdown PDFs with Unicode and emoji fonts
summary: Replace xhtml2pdf with fpdf2, bundled fonts and shaping, then regenerate the host deliverables report for review.
status: current
created_at: 2026-10-04-13-54-10
---

# Render portable Markdown PDFs with Unicode and emoji fonts

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

Authority: user approved implementation and host report rendering on 2026-10-04; commit and push require subsequent review approval.

- [x] 1. Implement the approved portable renderer replacement.
  - [x] 1.1 Replace the backend with fpdf2 and HarfBuzz; retain local bootstrap, sibling output, atomic replacement and controlled interruption.
  - [x] 1.2 Bundle licensed text, code and color emoji fonts with provenance and integrity checks.
  - [x] 1.3 Preserve ordinary Markdown structure, long tables, local images and meaningful failure reporting.
  - [x] 1.4 Synchronize renderer playbook and entrypoint documentation.
- [?] 2. Verify and prepare the review checkpoint.
  - [x] 2.1 Test Unicode, compound emoji, extraction, missing glyphs/assets, bootstrap and atomic failure behavior.
  - [x] 2.2 Render the host Week 6–7 deliverables report and inspect representative pages.
  - [?] 2.3 Check syntax and relevant framework tests; record platform coverage honestly.
  - [x] 2.4 Update indexes and journal; leave changes uncommitted pending user review.

No framework ROADMAP.md exists; this scoped continuation of the archived renderer plan changes no host delivery commitments.
Windows validation occurs on CJ-Desktop. Linux execution must be recorded separately if available; otherwise it remains an explicit validation gap.

## Review checkpoint

- Windows CPython 3.12: clean bootstrap and repeat `--no-bootstrap` render succeeded; 11 renderer tests and 18 focused framework documentation/architecture tests passed. Syntax and whitespace checks passed.
- Native color font glyphs and compound sequences preserve Unicode extraction in tested PDFs. A focused fpdf2 adapter keeps ASCII-base keycaps in one shaping run; ordinary digits remain text-font glyphs. Visual inspection caught and verified this correction.
- Host output: `2026/Phase 2/Deliverables/week-6/development-week-6-7-report.pdf`, seven pages. Source report text was not edited in this checkpoint. Page previews 1–3 and a dedicated emoji fixture were inspected using PDFium in the ignored environment (inspection dependency only).
- Layout uses a documented portable profile, not browser CSS. Table-cell inline code preserves text but uses the table font; rows taller than a page fail rather than truncate. Bundled fonts do not cover all scripts or future emoji releases.
- Remaining validation: Linux and Python 3.11 execution via `.github/workflows/markdown-pdf.yml` after approval to publish. Owner: framework maintainer; target: first CI run following the user's commit/push approval. No claim of completed Linux validation.
- User review and commit/push approval are pending. Plan remains current until this verification gap is resolved or explicitly closed.
