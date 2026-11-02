---
plan_id: 2026-11-02-12-30-00_remove-api-file-commit-dependency
title: Remove API configuration dependency from source commit checks
summary: User-authorized independent source policy and documentation-only commit checks.
status: past
created_at: 2026-11-02-12-30-00
---

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

User explicitly removed the API-file requirement after it blocked the November 2 checkpoint. No runtime API configuration or credentials should be needed for a commit.

- [x] Support independent source-governance.yaml; retain legacy public sample compatibility without reading local api.yaml.
- [x] Allow documentation/gitlink-only staged commits without a source-policy file; source/config changes still require source validation.
- [x] Verify behavior, synchronize policy, commit/push framework and remaining parent/runtime checkpoints.

Verified 15 source repository tests and five applicable hook tests; framework source gate: 81 files, zero failures. Existing Go hook test blocked by absent Go compiler on this host, not a tested Go regression. Source/API configuration decoupled; publication follows this checkpoint.
