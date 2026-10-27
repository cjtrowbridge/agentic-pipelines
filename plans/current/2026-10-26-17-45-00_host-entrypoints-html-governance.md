---
plan_id: 2026-10-26-17-45-00_host-entrypoints-html-governance
title: Preserve governed host entrypoints and parse HTML comments
summary: Narrow R11 repair for explicitly declared root launchers and HTML source accounting without weakening limits or inventories.
status: current
created_at: 2026-10-26-17-45-00
---

# Host entrypoints and HTML governance

Authorized by runtime operator October 26: repair in owning framework repo,
publish dependency before advancing runtime pointer; preserve all enforcement.
Host root bootstrap.sh is a documented stable dispatcher. Framework host
preservation instructions conflict with the checker rejecting every root file.
HTML is included in SOURCE_SUFFIXES but no available adapter recognizes HTML
comments. Confirmed using bounded valid-header and undeclared-launcher cases.

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

- [x] Confirm defects against host contract and existing checker.
- [x] Add exact root-entrypoint declaration with purpose/delegate, normal language/size checks and root README inventory; reject wildcards, traversal, undeclared files and invalid targets.
- [x] Add HTML-aware comment accounting; retain executable/data/attribute content, inspect embedded script/style and refuse unsupported inline executable attributes.
- [x] Test worktree/staged checks, valid cases and genuine size/inventory/layout failures, and build refusal.
- [x] Update framework policy/README/config documentation; run focused and full tests and source gate.
- [x] Commit/publish dependency; verify remote receipt before runtime pin advances (`6256777`).

No host entrypoint, model policy, data or live service is changed here.

Verification: 78 focused tests passed (1 skip); canonical source check 68 files,
zero failures. Full suite: 165 tests, one existing failure and two skips;
Cerebras playbook is 363 words at unchanged upstream HEAD `9847070`, exceeding
the pre-existing test's <350 rule. No unrelated guidance changed.
Publication is authorized by the runtime operator; receipt follows push.

## R11 continuation: Go syntax compatibility

The authorized host source migration exposed generic C-style false positives
for Go composite literals and for-clause grammar. Extend only language parsing,
using the installed Go parser; preserve size, headers, inventories and rejection
of compressed executable statements. Runtime/operator R11 authorization covers
this prerequisite repair; no root or language exemption is introduced.

- [x] Add Go parser-backed layout/counting adapter; inspected code is parsed, never executed.
- [x] Guard compilation of the trusted helper with the framework's own source gate; host source cannot choose helper paths or commands.
- [x] Regress valid composites/loop grammar, real inline actions, raw literals, header/size limits and staged checks.
- [ ] Publish tested dependency before host mapping/pointer advancement.

Go continuation verification: 96 focused source tests pass; framework source
gate passes (72 files). Full suite before final guard regression: 184 tests,
one unchanged Cerebras playbook word-count failure, two skips. Parser uses
physical source lines despite //line directives; local-only module-free helper
compilation is preceded by the framework source gate. No inspected code runs.

### Multiline initializer enforcement

- [x] Reject if/switch initializer actions even when the header spans lines;
  physical-line uniqueness alone must not permit a condition-assignment bypass.
- [x] Regress multiline headers (98 focused tests pass); publication receipt follows.
