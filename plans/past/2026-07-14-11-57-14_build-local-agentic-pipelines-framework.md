---
plan_id: 2026-07-14-11-57-14_build-local-agentic-pipelines-framework
title: Build the local agentic pipelines framework
summary: Convert this repository from agent-governance-first scaffolding into a submodule-ready framework for resumable local-inference pipelines with traceable review, recovery, and post-run analysis.
status: past
created_at: 2026-07-14-11-57-14
---

# Build the Local Agentic Pipelines Framework

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

> Superseded on 2026-07-14 by `plans/current/2026-07-14-13-12-31_reorient-pipelines-around-prompts-and-playbooks.md`. Checked work is retained as provisional infrastructure; all formerly open items below are intentionally closed here and transferred according to `docs/plan_reconciliation_2026-07-14.md`.

## Outcome and boundaries

The framework will let a host repository define a large entity-oriented transformation, use cloud assistance to engineer the pipeline, and use local inference (initially an Ollama-compatible API) to execute it in bounded, resumable batches. Each result will be deterministic-validated, optionally semantically reviewed, staged before promotion, and preserved with enough evidence to diagnose both individual failures and cohort-level failures after a run.

The framework's own journal remains the append-only human/agent metaconversation about pipeline design and changes. Machine activity is recorded separately in state, run manifests, per-call thread captures, and post-run reports. Root `TODO.md` is the human-facing checklist; it is never the execution queue for entities.

This plan deliberately does not implement a provider other than the initial Ollama-compatible adapter, a web UI, distributed workers, unrestricted automatic pipeline rewriting, or a complete production pipeline for every content type. Those are later expansion candidates once the reference pipeline works.

## Plan lineage and durable handoffs

- [-] 0. Retire superseded governance backlog work and preserve its useful operating ideas here.
  - [x] 0.1 Delete the superseded `framework-known-opportunities-backlog` future plan at the user's direction after incorporating its only distinct requirement below.
  - [x] 0.2 Define durable multi-checkpoint handoff fields: active plan path, checklist deltas, approved/open decisions, evidence and report links, material risks, and the exact next approved action.
  - [-] 0.3 Add the handoff fields to the journal/checkpoint template and relevant execution playbooks, then verify them with a simulated handoff.

## Decision records to settle before implementation

- [x] 1. Establish the target architecture and compatibility boundary.
  - [x] 1.1 Inspect the current framework, identify every agent/kanban/downtime assumption, and document its proposed pipelines-era replacement or retained role.
  - [x] 1.2 Write an architecture document defining the framework/submodule boundary and host-owned runtime boundary.
  - [x] 1.3 Specify the canonical host layout, including root `TODO.md`, `pipeline.yaml`, prompt directories, state, run evidence, artifacts, failure cohorts, reports, and local-only configuration.
  - [x] 1.4 Define ownership and update-synthesis rules for `TODO.md`: the framework has a template; a host's root checklist remains host-owned and is never blindly overwritten.
  - [x] 1.5 Define a versioned pipeline-definition schema, including entity discovery, stages, prompt contracts, validators, retry policy, promotion policy, retention policy, and post-run analysis policy.
  - [x] 1.6 Define the entity state machine, allowed transitions, terminal states, recovery of abandoned leases, and the distinction between retryable and quarantined work.
  - [x] 1.7 Decide the initial implementation packaging, Python version/dependency policy, CLI surface, and how the host invokes framework scripts without copying or modifying runtime source unnecessarily.
  - [x] 1.8 Record explicit non-goals and deferred decisions: multi-provider support, multi-machine scheduling, UI, automated remediation application, and non-Ollama authentication schemes.

## Runtime state, reproducibility, and artifact safety

- [x] 2. Design the durable execution record.
  - [x] 2.1 Select SQLite as the initial local state store and document why it is sufficient for single-host bounded runners.
  - [x] 2.2 Define migrations and tables for entities, state transitions, attempts, stage outcomes, validation evidence, leases, retries, and run membership.
  - [x] 2.3 Define a stable entity identity, input snapshot/hash policy, and idempotency rule so a resumed invocation cannot duplicate completed work or confuse revised inputs with previous inputs.
  - [x] 2.4 Define run manifests that record pipeline schema/version, source revision, runtime and dependency versions, configuration identity with secrets redacted, and aggregate counters.
  - [x] 2.5 Define artifact paths and retention policy for originals, staged outputs, accepted outputs, superseded outputs, quarantined entities, and compact metadata.
  - [x] 2.6 Define atomic promotion and rollback behavior: a worker must never overwrite the source directly; only accepted staged content may be promoted, with a reversible provenance link.
  - [x] 2.7 Define file locking/lease behavior, lock-loss handling, stale-run recovery, and safe bounded-run shutdown behavior for cron execution.
  - [x] 2.8 Define sensitive-data handling and redaction rules for source content, prompts, responses, headers, credentials, logs, reports, and retained thread captures.

## Shared local API primitive and configuration

- [x] 3. Build one reusable, observable inference boundary instead of allowing ad hoc HTTP calls.
  - [x] 3.1 Define the provider-neutral request and response interfaces used by all workers, reviewers, repair stages, and failure-analysis stages.
  - [x] 3.2 Implement the initial Ollama-compatible adapter with configurable base URL, model, request timeout, connect/read timeout, optional API key/header settings, generation parameters, and TLS verification settings.
  - [x] 3.3 Create `api.sample.yaml` with documented non-secret example values and comments explaining each supported setting.
  - [x] 3.4 Add a local `api.yaml` convention, a `.gitignore` rule that prevents it from being committed, and an explicit validation that rejects a missing or malformed configuration before processing entities.
  - [x] 3.5 Implement a bootstrap/preflight command that detects absent local API configuration, points to `api.sample.yaml`, and asks the operator to supply local endpoint/credential details before a run can start.
  - [x] 3.6 Ensure config loading validates types and allowed values, resolves paths predictably, redacts secrets in all diagnostics, and does not fall back silently to cloud endpoints.
  - [x] 3.7 Add retry classification, exponential backoff with jitter, bounded attempt limits, cancellation, and actionable errors to the shared primitive.
  - [x] 3.8 Add structured request timing and token/usage capture where the local endpoint supplies it, while treating unavailable metrics as explicitly unknown rather than fabricated.
  - [-] 3.9 Prohibit direct provider calls outside the primitive through architecture tests/code review rules and usage documentation.

## Thread capture, observability, and audit evidence

- [-] 4. Preserve explainable evidence for every API interaction.
  - [x] 4.1 Define a per-call thread-capture schema containing run ID, entity ID, attempt, stage, prompt template version/hash, rendered request, normalized response, provider metadata, timings, errors, and redaction metadata.
  - [x] 4.2 Define a stable folder layout for thread captures that permits lookup by run, entity, stage, and attempt without making the state database dependent on filenames.
  - [x] 4.3 Implement capture writing atomically before each result is considered by downstream stages, including partial/error captures for failed calls.
  - [x] 4.4 Implement automatic redaction of API keys and configured sensitive patterns before thread records, logs, or reports are written.
  - [-] 4.5 Add reference IDs and hashes linking database records, artifacts, thread captures, validator outputs, and run manifests.
  - [-] 4.6 Provide a CLI/report query path that retrieves a problematic entity's complete evidence trail without exposing unrelated entities.
  - [-] 4.7 Define retention, compression, and opt-out controls so valuable review evidence does not consume unbounded disk space or violate project data constraints.

## Pipeline stages and quality controls

- [-] 5. Implement the minimum complete entity-processing lifecycle.
  - [-] 5.1 Implement discovery and staging interfaces that enumerate entities deterministically, record source evidence, and do not mutate source material.
  - [-] 5.2 Implement a worker stage that renders a versioned prompt template, invokes only the shared API primitive, and writes output to a unique staged location.
  - [-] 5.3 Implement deterministic validator interfaces and an initial reusable validation library for existence, parsing, schema/front-matter preservation, required content, protected ranges, forbidden changes, and edit-distance or content-diff bounds.
  - [-] 5.4 Define validator evidence schema so failures have machine-readable codes and human-readable explanations suitable for cohort grouping.
  - [-] 5.5 Implement optional worker self-check as a low-cost gate, clearly labeled as non-independent evidence.
  - [-] 5.6 Implement independent semantic review with a distinct prompt contract that receives source, candidate, task goal, and deterministic evidence but not hidden worker reasoning.
  - [-] 5.7 Define structured reviewer verdicts, confidence, violations, and recommended actions; validate that reviewer output conforms before acting on it.
  - [-] 5.8 Implement an adjudication/repair routing interface for disagreement, explicit repair prompts, retry of the original worker, and escalation.
  - [-] 5.9 Implement a quarantine terminal state with reason code, evidence links, recommended next action, and a guarantee that retry limits cannot create infinite loops.
  - [-] 5.10 Implement acceptance promotion only after configured required gates pass, and retain sufficient provenance to reverse a promotion.

## Runner, scheduling, and operator experience

- [-] 6. Make the framework safe to invoke repeatedly from cron or a task scheduler.
  - [-] 6.1 Implement a preflight command that validates repository layout, pipeline definition, API configuration, storage availability, write permissions, and pending migration compatibility.
  - [-] 6.2 Implement a bounded `run` command accepting entity-count and wall-clock limits, resume mode, explicit pipeline selection, and safe dry-run mode.
  - [-] 6.3 Implement runner lock acquisition, recovery of abandoned in-progress work, eligible-work selection, transactional state persistence, graceful interruption, and final lock release.
  - [-] 6.4 Implement separate commands for discovery, processing, review, retrying an approved cohort, inspecting an entity, and generating a report so operators can diagnose without reprocessing data.
  - [-] 6.5 Add machine-readable and human-readable run summaries showing discovered, processed, accepted, rejected, quarantined, retried, and unfinished entity counts.
  - [-] 6.6 Document scheduler examples and operational constraints, including no overlapping runs, expected time limit below scheduler interval, exit codes, log locations, and restart behavior.
  - [-] 6.7 Add a first-run host onboarding flow that creates only safe scaffolding, presents required local API setup, and never silently writes credentials or starts processing.

## Post-run failure and performance analysis

- [-] 7. Replace generic runtime downtime review with a first-class post-run analysis phase while retaining framework-level reflective maintenance.
  - [-] 7.1 Define the post-run analysis trigger, minimum completed-run threshold, report location, and distinction between per-run reports and framework-maintenance reports.
  - [-] 7.2 Define deterministic cohort grouping by failed stage, validator code, reviewer verdict, file/content type, input size, prompt/model version, error class, retry pattern, and edit-distance or output-shape signals.
  - [-] 7.3 Implement cohort generation with representative entity selection and privacy-aware evidence references.
  - [-] 7.4 Create a failure-analysis prompt template that asks for common cause, likely ownership (input/prompt/model/validator/orchestrator), feasibility, safe cohort-specific remedy, required regression test, and retry-versus-human recommendation.
  - [-] 7.5 Route failure-analysis prompts through the same shared API primitive and preserve their thread captures with the cohort report.
  - [-] 7.6 Define a remediation-proposal schema that is explicitly advisory: it may suggest a pipeline revision but cannot edit pipeline code/configuration or relaunch all failures automatically.
  - [-] 7.7 Implement performance analysis for throughput, time per stage, queue/lease delays, request failures, retry rates, acceptance/rejection/quarantine rates, local model usage metrics when available, and estimated remaining duration.
  - [-] 7.8 Include false-accept and false-reject signals from a curated evaluation set; distinguish unknown quality from measured quality.
  - [-] 7.9 Implement report output linking cohorts to individual evidence trails and separating confirmed observations from model-generated hypotheses.
  - [-] 7.10 Define the approved recovery path: review proposal, modify pipeline through normal plan governance, validate on a representative sample, then retry only the intended affected cohort.

## Evaluation, security, and reliability gates

- [-] 8. Establish safeguards before broad local execution.
  - [-] 8.1 Define a versioned golden evaluation-set format with source fixtures, expected invariants, known acceptable outcomes, and labeled edge cases.
  - [-] 8.2 Add test fixtures for malformed inputs, giant entities, API timeouts, malformed model output, invalid reviewer JSON, interrupted runs, stale leases, duplicate invocation, and promotion failure.
  - [-] 8.3 Add unit tests for pipeline schema validation, configuration redaction, API primitive behavior, state transitions, idempotency, retry limits, capture integrity, deterministic validators, and report grouping.
  - [-] 8.4 Add integration tests using a fake Ollama-compatible server to verify complete success, validation failure, semantic disagreement, repair, quarantine, resume, and post-run analysis paths without real credentials.
  - [-] 8.5 Add a controlled real-local-model smoke-test procedure that is opt-in, does not require committing credentials, and records environment limits.
  - [-] 8.6 Define prompt-injection and untrusted-content rules: source text can influence the requested transformation but cannot instruct the runner, alter configuration, execute tools, or bypass validation.
  - [-] 8.7 Ensure all file writes remain scoped to declared artifact/state directories and validate paths to prevent an entity identifier or model output from escaping them.
  - [-] 8.8 Establish release acceptance criteria: schema validation, unit/integration tests, evaluation-set thresholds, dry run, resume test, redaction inspection, and documentation review must pass before recommending operational use.

## Documentation, templates, journal, and migration

- [-] 9. Convert the framework's policy surface without losing its design-memory function.
  - [-] 9.1 Rewrite the root README around the pipelines purpose, architecture, host bootstrap, local API configuration, lifecycle, scheduling, observability, recovery, and migration from `agents`.
  - [-] 9.2 Rewrite RULES.md so repository-change governance remains plan-bound, while runtime execution authority is the validated pipeline definition; replace kanban operational policy with root-checklist policy.
  - [-] 9.3 Preserve and adapt journal policy so it records the metaconversation and approved framework-design checkpoints, not per-entity machine events.
  - [-] 9.4 Replace kanban board artifacts and instructions with a canonical root `TODO.md` template and migration guidance that preserves host-owned task text.
  - [-] 9.5 Replace or adapt downtime task catalog and report template into framework-maintenance reviews plus post-run failure/performance report templates.
  - [-] 9.6 Add templates for pipeline definitions, API config sample, prompt contracts, worker/reviewer/repair outputs, validator evidence, run manifests, entity evidence summaries, cohort analysis, remediation proposals, and evaluation fixtures.
  - [-] 9.7 Add playbooks for designing a pipeline, onboarding a host, configuring/testing local inference, operating a bounded run, investigating an entity, reviewing a post-run report, and approving a cohort retry.
  - [-] 9.8 Add reusable references covering prompt separation, deterministic versus semantic validation, artifact provenance, local API security, cohort analysis, and evaluation-set calibration.
  - [-] 9.9 Update all root LLM shims and host bootstrap/update-synthesis instructions to use `pipelines` paths and preserve host-owned state/configuration.
  - [-] 9.10 Update indexes in RULES.md for every added, removed, or renamed playbook, template, reference, and post-run/framework-maintenance task.
  - [-] 9.11 Add a migration guide from an existing `agents` submodule, including a pre-migration backup, kanban-to-TODO decision, retained journal history, downtime-report disposition, local config creation, verification, and rollback steps.

## Reference pipeline and staged delivery

- [-] 10. Prove the design with one intentionally narrow reference pipeline before generalizing.
  - [-] 10.1 Choose and document a non-destructive Markdown repair reference pipeline with a small fixture corpus and protected-content invariants.
  - [-] 10.2 Configure discovery, worker prompt, deterministic Markdown validation, optional reviewer, staging/promotion, and quarantine handling for the fixture corpus.
  - [-] 10.3 Run the reference pipeline against the fake provider and fixture corpus; inspect accepted, rejected, quarantined, and thread-capture outputs.
  - [-] 10.4 Run an opt-in local Ollama smoke test using `api.yaml`, verify redaction and report generation, and preserve no credentials in repository state.
  - [-] 10.5 Intentionally exercise failure cohorts and verify that post-run analysis produces advisory remediation proposals with evidence links.
  - [-] 10.6 Test an approved, cohort-scoped retry after a controlled pipeline revision; confirm unrelated entities are untouched and reruns remain idempotent.
  - [-] 10.7 Capture findings in the journal as a framework-design checkpoint, distinguishing human decisions from machine run evidence.

## Delivery checkpoints and verification

- [-] 11. Deliver in reviewable checkpoints rather than one unbounded conversion.
  - [-] 11.1 Checkpoint A: approve architecture, data/state contracts, host ownership rules, and documentation/template/playbook migration plan before writing runtime code.
  - [-] 11.2 Checkpoint B: deliver configuration, shared API primitive, thread capture, redaction, and fake-provider tests; review the evidence format before building stages.
  - [-] 11.3 Checkpoint C: deliver state store, bounded runner, worker/staging/validator lifecycle, and resume/lock tests.
  - [-] 11.4 Checkpoint D: deliver reviewer/repair/quarantine, post-run failure/performance analysis, remediation-proposal boundary, and evaluation-set tests.
  - [-] 11.5 Checkpoint E: deliver complete documentation, submodule/bootstrap migration, reference pipeline, end-to-end verification, and rollout recommendation.
  - [-] 11.6 At each checkpoint, update this plan, regenerate plan indexes, review status/diff, update affected documentation, append the approved journal work log, and request explicit commit approval under the repository policy.
  - [-] 11.7 Before declaring operational readiness, verify all release acceptance criteria in item 8.8, review generated reports and redaction behavior manually, and document known limitations and rollback procedures.

## Expected file groups

Implementation will determine exact names only after Checkpoint A approves the contracts. Expected affected groups are: root policy/shim files; `README.md`; `docs/`; `playbooks/`; `references/`; `templates/`; `scripts/` or a Python package; test fixtures; `downtime/` or renamed framework-maintenance/post-run task directories; `.gitignore`; root `TODO.md` template; and `plans/` indexes. Host-generated `api.yaml`, SQLite state, artifacts, runs, thread captures, and reports will be ignored and never committed by the framework.
