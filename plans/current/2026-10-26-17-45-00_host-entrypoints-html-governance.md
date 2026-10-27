---
plan_id: 2026-10-26-17-45-00_host-entrypoints-html-governance
title: Host source governance compatibility and bounded migration
summary: R11 exact entrypoints, language-aware enforcement and guarded source-preserving migration without weakening limits or inventories.
status: current
created_at: 2026-10-26-17-45-00
---

# Host source governance compatibility and bounded migration

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

### Authorized R11 host source migration support

- [x] Supply a parse-only Go edit-proposal helper for scoped initializer and
  whitespace repairs; no automatic checker mutations or source execution.
- [x] Verify lexical scope, nested else/switch, comment refusal and retained
  tokens; gate the helper's own compilation before use.
- [ ] Publish the tested helper before host migration use.

Migration verification: five focused regressions pass, including a governed
compiled synthetic fixture preserving shadowing, nested else, switch/type-switch
and continue targets. Full framework suite: 194 tests, only the previously
recorded unrelated Cerebras 363-word failure, two skips. Canonical framework
source gate: 75 files, zero failures. No inspected host code executed.

### Select clause grammar correction

- [x] Distinguish select send/receive/binding grammar from clause body actions
  in checker and migration proposals; inline clause bodies must still fail.
- [x] Regress both valid communications and real inline violations before
  publishing and advancing runtime dependency.

Select correction:100 focused source tests and6 migration tests pass; valid
channel clauses pass, inline bodies still fail. Source gates pass before commit.

### Parser-backed declaration inventory

- [x] Expose physical function spans and receiver identities for authorized
  host decomposition; retain declaration comments and ignore string lookalikes.
- [x] Regress spans and existing source/migration contracts before publication.

Declaration inventory:101 source tests and6 migration tests pass. Physical
byte spans retain docs and exclude function-like raw string content; no host
source executed. Publication follows owning source-gated commit.

### JavaScript grammar correction (authorized R11 continuation)

Confirmed host defects: regex quantifiers mistaken for blocks, regex semicolons
as actions, template interpolation read as code and arrow comparison as assignment.
- [x] Add explicit parser-backed JavaScript adapter with declared GJS/esprima dependencies.
- [x] Regress real actions, embedded assignments, literals, physical size and no execution.
- [ ] Publish owning dependency before runtime mapping/pin advancement.

JavaScript verification:110 source tests pass, including9 dedicated JS cases.
Missing dependencies, malformed syntax and real embedded actions fail closed;
regex/template/arrow/object syntax passes. No application source executed.

- [x] Parse native ES-module imports/exports without resolving or executing dependencies; covered by unavailable-import regression.

### Exact third-party distribution identity

Host already retains Bootstrap5.3.8 and Chart.js4.5.1 manifests with upstream
version/source/license and hashes. First-party formatting must not rewrite those
locked distributions. Add exact-manifest recognition, retaining source inventory
and all checks for unlisted/changed files; no vendor-directory exclusion.
- [x] Regress matching, changed, unlisted, unsafe and staged dependency identity.
- [ ] Publish owning dependency before host adoption.

Dependency verification:118 focused source tests pass, including seven exact
manifest identity/inventory/unlisted/staged/BOM/provenance cases. No broad exclusions.

## R11 continuation: shell literal boundaries

Host shell contracts use heredocs for literal help, Python input and rendered
configuration. The generic adapter misclassified Python shifts and semicolons
inside those bodies and rejected standalone case terminators. Operator R11
continuation authorization covers narrow parsing repairs without exclusions.

- [x] Parse simple heredoc declarations and queued/tab-stripped bodies; retain every payload row in size enforcement.
- [x] Retain fail-closed complex delimiters and unquoted executable substitution; distinguish here-strings.
- [x] Accept standalone case grammar while rejecting combined commands.
- [x] Verify nine new regressions; all 127 focused source cases and 81-file framework gate pass.
- [ ] Publish exact tested tree and verify host receipt before runtime pin advancement.
