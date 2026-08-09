---
plan_id: 2026-08-09-09-23-05_use-rejection-explanation-sidecars
title: Preserve Rejected Candidates with Explanation Sidecars
summary: Replace appended rejection diagnostics with integrity-bound Markdown explanation sidecars so rejected model output remains byte-for-byte reviewable while complete rejection evidence stays durable and machine-linked.
status: current
created_at: 2026-08-09-09-23-05
---

# Preserve Rejected Candidates with Explanation Sidecars

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

## Approval and ownership boundary

This framework plan changes the universal rejected-candidate evidence contract, shared evidence helpers and schemas, framework documentation, examples, and tests. It does not mutate any host pipeline, host application content, credentials, ignored runtime evidence, or host publication policy. Host adoption is separately governed by the linked host plan.

## Target contract

- A rejected candidate contains only the exact model/provider output bytes supplied for preservation. Framework diagnostics are never appended to it.
- Each candidate has a same-basename Markdown sidecar: `<candidate-name>.explanation.md`. The run identity replaces the illustrative numeric component rather than supplementing it: `resume.run-abc.attempt-def.rejected.md` is paired with `resume.run-abc.attempt-def.rejected.explanation.md`.
- The explanation sidecar binds itself to the candidate through its relative path and SHA-256 and contains run/entity/artifact/stage/session/attempt identity, timestamp, failure class, rejection code, authority, validator/reviewer, complete actionable explanation, retry disposition, and report/validation/thread links.
- Candidate and sidecar paths are collision-safe, immutable, ignored runtime evidence and are excluded from every source, example, prompt, semantic-evidence, rendering, and promotion consumer.
- A report may claim rejected evidence was preserved only after both candidate and sidecar exist and the recorded candidate hash matches. Partial pair creation fails visibly and may clean up only files newly created by that failed preservation operation.

## Execution checklist

- [x] 1. Revise upstream governance and executable contracts.
  - [x] 1.1 Replace the appended-diagnostic invariant in `AGENTS.md` and `references/run_evidence_and_continuous_improvement.md` with the clean-candidate and integrity-bound explanation-sidecar contract, retaining all existing evidence fields and trust boundaries.
  - [x] 1.2 Update relevant design, operation, audit, and investigation guidance so agents inspect the candidate and sidecar as a pair and never infer trust from their storage location.
  - [x] 1.3 Extend the run-evidence schema so every rejected-artifact record links both `artifact_path` and `explanation_path`, with compatibility guidance for historical appended-diagnostic evidence.
  - [x] 1.4 Update package/templates/examples that declare rejected-artifact behavior without introducing host-specific folder or filename policy.

- [x] 2. Implement shared sidecar support.
  - [x] 2.1 Replace or extend the shared rejection-record helper with deterministic Markdown sidecar rendering and explicit candidate-hash binding.
  - [x] 2.2 Provide collision-safe paired-path and guarded persistence primitives that preserve candidate bytes exactly and report success only for a complete pair.
  - [x] 2.3 Preserve safe compatibility for existing consumers long enough to produce an actionable migration error or legacy report interpretation rather than silently changing historical evidence.
  - [x] 2.4 Keep malformed structured responses, rejected Markdown, and rejected binary/render diagnostics covered by the same pairing and exclusion policy.

- [x] 3. Add adversarial and migration verification.
  - [x] 3.1 Prove rejected candidate bytes are identical to the supplied output, including trailing whitespace and content resembling framework delimiters.
  - [x] 3.2 Prove the explanation contains the correct candidate path/hash and all required diagnostic fields and that reports link both files.
  - [x] 3.3 Prove repeated attempts, resumed runs, concurrent entities, and reused provider attempt labels cannot overwrite either member of a pair; run plus pipeline-attempt identity is the collision boundary and no redundant ordinal is added.
  - [x] 3.4 Prove partial write failure cannot be reported as preserved evidence and cannot delete pre-existing/user-owned files.
  - [x] 3.5 Prove both files remain excluded from Git, discovery, retrieval, prompt assembly, semantic evidence, rendering, and promotion.
  - [x] 3.6 Run the complete upstream suite, prompt lint, compilation, and schema-v2 reference-package validation.

- [ ] 4. Publish and close the upstream change.
  - [x] 4.1 Update the plan and upstream journal with exact implementation and verification evidence and regenerate upstream plan indexes.
  - [x] 4.2 Review the submodule diff for framework scope, host safety, runtime evidence, credentials, and unrelated changes.

## Implementation checkpoint — 2026-08-09

- Replaced appended rejection trailers with exact candidate bytes and same-basename Markdown explanation sidecars bound by candidate path and SHA-256.
- Removed the redundant ordinal from shared rejected filenames; run and pipeline-attempt identity now provide the collision boundary.
- Added guarded paired persistence, schema-v3 run evidence with explicit sidecar/legacy formats, package evidence declarations, human narrative links, migration guidance, and an actionable failure for legacy append-helper callers.
- Preserved immutable historical appended evidence through the `legacy_appended` report format without rewriting it.
- Verified 56 upstream tests, 25 prompt-lint checks, Python compilation, and the schema-v2 governance-conformant reference package with no warnings.
  - [ ] 4.3 Commit and push the reviewed framework change directly to upstream `main`, verify `origin/main`, and record the published revision for host adoption.
  - [ ] 4.4 Archive this completed plan, regenerate indexes, and publish the closure checkpoint.

## Success criteria

- Rejected candidates are clean, byte-for-byte model/provider outputs.
- Every rejection explanation is a directly discoverable, integrity-bound Markdown sidecar.
- Machine reports link both members of the pair and cannot claim incomplete evidence.
- Existing security, exclusion, retry, continuous-improvement, and truthful-status governance remains at least as strong as before.
- The framework change is published before any host claims conformance with the sidecar contract.
