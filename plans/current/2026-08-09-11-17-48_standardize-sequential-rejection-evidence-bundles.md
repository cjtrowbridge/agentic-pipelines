---
plan_id: 2026-08-09-11-17-48_standardize-sequential-rejection-evidence-bundles
title: Standardize Sequential Rejection Evidence Bundles
summary: Replace opaque run-and-attempt filenames with sortable entity-local rejection bundles that preserve parent candidates, truthfully typed precursor evidence, explanation sidecars, and durably checkpointed traceability.
status: current
created_at: 2026-08-09-11-17-48
---

# Standardize Sequential Rejection Evidence Bundles

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

## Approval and ownership boundary

This upstream plan governs universal evidence policy, shared runtime helpers, schemas, templates, examples, playbooks, references, tests, plan indexes, and publication in `agentic-pipelines`. It does not alter any host pipeline, host application content, credentials, ignored runtime evidence, or historical rejection files. Host adoption begins only after this framework plan is implemented, verified, committed, and pushed, and is governed by the separately linked host plan.

## Normative target contract

- Every rejected attempt is a human-browsable entity-local evidence bundle. Its primary generated candidate is `<artifact>.<sequence>.rejected.<ext>` and its integrity-bound sidecar is `<artifact>.<sequence>.rejected.explanation.md`.
- Associated precursor evidence keeps the same artifact and sequence before its subtype: `<artifact>.<sequence>.rejected.<stage>.<ext>` and `<artifact>.<sequence>.rejected.<stage>.explanation.md`. Thus a bundle may contain `resume.1.rejected.md`, `resume.1.rejected.explanation.md`, `resume.1.rejected.claim_review.json`, and `resume.1.rejected.claim_review.explanation.md`; the next rejected trajectory uses `resume.2...`. A filename contains exactly one dot between components.
- The sequence is the next unused positive integer in the entity/artifact evidence namespace. It is allocated with exclusive creation and collision retry, is never replaced by a hash or UUID, and is never reused after a complete bundle is published. Consumers parse it numerically and present it in natural numeric order.
- Run, session, attempt, revision, thread, timestamp, and content-hash identities belong in sidecars and machine reports, not human-facing filenames.
- File extensions state the preserved representation: generated Markdown uses `.md`; syntactically valid structured JSON uses `.json` even when schema or post-parse validation rejects it; malformed, truncated, or unknown text uses `.txt`; binary render evidence keeps its binary extension.
- If a downstream reviewer, validator, repairer, renderer, or promoter prevents publication, the parent candidate is rejected evidence and must be present in the same bundle even when its worker contract passed. It may never exist only inside a thread envelope. Every rejected child response is preserved and linked to that parent bundle.
- Reports checkpoint every material event and every completed candidate/sidecar pair. Interruption recovery reconciles persisted evidence so a stale `running` report cannot claim zero attempts or rejections after evidence exists.
- Byte-identical retry responses are recorded as non-progress and may not consume another unchanged retry without a declared strategy change or escalation.
- Deterministic citation checks prove only exact representation or stable-ID resolution. Multi-passage support uses separately resolvable excerpts or source IDs; formatting mismatches may not impersonate semantic factual verdicts.
- Historical run/attempt-named and appended-diagnostic evidence remains immutable legacy evidence. New executions use the sequential bundle contract.

## Execution checklist

- [x] 1. Publish the normative rejection-bundle governance model.
  - [x] 1.1 Replace the run/attempt filename requirement in `AGENTS.md` and `references/run_evidence_and_continuous_improvement.md` with the sequential bundle grammar, truthful-extension rules, parent/child preservation, and metadata-only trace identities.
  - [x] 1.2 Update design, operation, investigation, audit, and post-run-analysis playbooks so agents reconstruct a bundle, distinguish primary and precursor evidence, verify every hash/link, and recognize stale-report reconciliation and non-progress retries.
  - [x] 1.3 Extend deterministic/semantic authority guidance for exact citations so schemas permit multiple exact source references and deterministic formatting checks cannot issue semantic verdicts.
  - [x] 1.4 Document legacy interpretation and an explicit no-rewrite migration boundary for existing run/attempt and appended-diagnostic evidence.

- [x] 2. Define executable schemas and templates.
  - [x] 2.1 Advance the run-evidence schema with bundle sequence, artifact role, content format, parent candidate, child evidence, legacy format, and checkpoint/reconciliation fields while retaining readable schema-v2/v3 evidence.
  - [x] 2.2 Update the rejection explanation template so its filename, candidate path/hash, bundle sequence, parent/child relationships, run/session/attempt identities, authority, rejection, disposition, and evidence links are unambiguous.
  - [x] 2.3 Update pipeline-package declarations and validation to require sequential candidate and precursor patterns without prescribing a host-specific directory name.
  - [x] 2.4 Update reference examples and documentation to use syntactically consistent names with no doubled dots, hidden UUID components, or falsely typed extensions.

- [x] 3. Implement shared sequential bundle persistence.
  - [x] 3.1 Add a numeric sequence parser and allocator that finds the next unused artifact-local integer, uses atomic exclusive creation with collision retry, and never overwrites a complete or partial pre-existing pair.
  - [x] 3.2 Replace run/attempt path construction with candidate and stage-evidence path helpers implementing `<artifact>.<sequence>.rejected[.<stage>].<ext>` and paired `.explanation.md` names.
  - [x] 3.3 Add content-format classification that preserves original bytes while selecting `.json` only after syntactic JSON parse success, `.txt` for unparseable text, and native extensions for Markdown and binary candidates.
  - [x] 3.4 Provide a guarded bundle transaction that publishes the parent candidate, its sidecar, each precursor, and each precursor sidecar without reporting incomplete evidence as complete or deleting pre-existing files.
  - [x] 3.5 Add parent/child relationship recording and require orchestration callers to preserve the parent whenever a downstream terminal or retry verdict rejects it.
  - [x] 3.6 Add atomic run-report checkpoints after material events plus deterministic restart reconciliation for evidence written after the last checkpoint.
  - [x] 3.7 Add repeated-content detection that records byte-identical retries as non-progress and requires changed feedback, changed strategy, or escalation before another model call.

- [x] 4. Verify the universal contract adversarially.
  - [x] 4.1 Prove natural numeric discovery and grouping for candidates 1 through 12, associated claim/coverage/render evidence, same-basename sidecars, and filenames containing neither hashes nor doubled separators.
  - [x] 4.2 Prove concurrent allocation, interrupted pair creation, resumed runs, partial directories, and user-created collisions cannot overwrite evidence, reuse a published sequence, or misassociate a precursor with another candidate.
  - [x] 4.3 Prove valid-but-rejected JSON uses `.json`, malformed JSON uses `.txt`, rejected Markdown uses `.md`, binary evidence remains byte-identical, and every explanation hash matches its candidate.
  - [x] 4.4 Prove downstream contract exhaustion preserves both the parent candidate and all precursor responses in linked bundles and that none enters trusted iteration, retrieval, prompt, rendering, recovery, or promotion paths.
  - [x] 4.5 Prove interruption after evidence persistence yields a reconciled non-running report with truthful attempt/rejection counts and links.
  - [x] 4.6 Prove identical retries are visible and bounded, multi-excerpt citation contracts accept independently exact evidence, and formatting-only differences cannot become semantic rejection authority.
  - [x] 4.7 Run the complete upstream suite, prompt lint, package validation, schema fixtures, compilation, plan-index generation, and diff hygiene checks.

- [ ] 5. Publish and close the upstream change.
  - [x] 5.1 Update this plan and the upstream journal with implementation, migration, verification, and compatibility evidence; regenerate upstream plan indexes.
  - [x] 5.2 Review the submodule diff for framework scope, host safety, ignored runtime evidence, credentials, and unrelated work.
  - [ ] 5.3 Commit and push the reviewed framework change directly to upstream `main`, verify `origin/main`, and record the published revision for consumers.
  - [ ] 5.4 Archive this completed plan, regenerate indexes, and publish the closure checkpoint before any host claims conformance.

## Success criteria

- Operators can understand and naturally sort rejection evidence without decoding hashes.
- Every downstream failure leaves a reviewable primary candidate and correctly typed, linked precursor evidence.
- Sidecars and reports retain complete machine traceability without polluting filenames or candidate content.
- Interrupted and repeated attempts remain truthful, durable, and actionable for continuous improvement.
- The published framework contract is reusable by every consuming pipeline.
