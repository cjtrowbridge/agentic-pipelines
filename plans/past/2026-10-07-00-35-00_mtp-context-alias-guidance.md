---
plan_id: 2026-10-07-00-35-00_mtp-context-alias-guidance
title: Preserve MTP sources in context alias guidance
summary: Correct the single-FROM assumption in reusable VS Code/Ollama guidance and alias verification.
status: past
created_at: 2026-10-07-00-35-00
---

# Preserve MTP sources in context alias guidance

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

- [x] Correct reusable guidance to inspect and preserve all model/draft sources for MTP aliases, with project/machine-specific configuration.
- [x] Remove the helper's exactly-one-FROM constraint while retaining complete source identity verification.
- [x] Verify multi-source creation/idempotency and missing/changed draft rejection; record the checkpoint.

User correction authorizes this guidance fix. No host bootstrap wiring or live deployment is in scope.

Verification: 9 alias-manager tests, 2 router tests and 16 documentation tests pass. Regression fixtures cover two FROM sources, FROM plus DRAFT, creation from the named base, repeat/check idempotency and lost/changed secondary-source rejection. These are synthetic fixtures, not live Qwen3.8 deployment evidence. No Thor/runtime/bootstrap changes were made.
