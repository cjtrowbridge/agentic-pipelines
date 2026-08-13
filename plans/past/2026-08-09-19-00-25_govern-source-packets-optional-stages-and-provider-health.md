---
plan_id: 2026-08-09-19-00-25_govern-source-packets-optional-stages-and-provider-health
title: Govern Source Packets, Optional Stages, and Provider Health
summary: Make typed source provenance, whole-packet budgets, optional-stage fallbacks, and provider circuit breaking universal and testable for every Agentic Pipelines consumer.
status: past
created_at: 2026-08-09-19-00-25
---

# Govern Source Packets, Optional Stages, and Provider Health

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

## Authority and scope

This framework plan is the upstream dependency of host plan `plans/future/2026-08-09-19-00-25_harden-source-packets-optional-stages-and-provider-failures.md`. The motivating host run demonstrated that a PDF can be correctly converted to Markdown yet still be the wrong source role, that limiting one request component does not bound the assembled request, and that an optional retrieval failure can incorrectly terminate a run. These are universal pipeline-contract issues, not resume-specific rules.

The plan may change framework governance, references, playbooks, schemas/templates, runtime helpers, examples, tests, plans, and journal. It must not change consumer hosts, host credentials/endpoints, application artifacts, ignored runtime evidence, or historical evidence. It does not authorize a model-backed run.

## Normative target

```text
declared source roles -> validated text derivatives -> allowed-role stage packet
  -> complete packet budget preflight -> required/optional stage behavior
  -> provider health/circuit outcome -> checkpointed truthful terminal report
```

- [-] 1. Reconcile framework plan lifecycle.
- [x] 1.1 Record the existing diagnostic/semantic governance plan as published baseline evidence and map any unfinished administrative items to this plan or a closed supersession disposition.
- [x] 1.2 Archive the superseded current plan without rewriting its historical implementation evidence; regenerate indexes.
- [x] 1.3 Promote this approved plan from future to current immediately before framework edits.

- [-] 2. Define universal typed source provenance.
- [x] 2.1 Add a normative source-role record: stable ID, canonical path, role, media type, SHA-256, derivative linkage, discovery authority, and inclusion disposition.
  - [-] 2.2 Define roles for primary/supplemental source, operator input, generated candidate, accepted artifact, rejected evidence, diagnostic derivative, configuration, and unknown input.
- [x] 2.3 Require binary-to-text derivative linkage before any model content use and prohibit PDF/binary bytes, base64, and file envelopes in prompt content.
- [x] 2.4 Require each stage to declare allowed source roles; exclude unknown/forbidden roles before packet assembly and make uncertainty visible rather than silently trusted.
- [x] 2.5 Explain that filename and exact structural signatures are representational role evidence only; semantic classification may route uncertainty but cannot silently confer trusted-source status.
- [x] 2.6 Require reports to record included/excluded source IDs, paths, roles, hashes, derivative links, and byte counts without protected content.

- [-] 3. Define and support complete packet budgeting.
- [x] 3.1 Add a packet-manifest contract for component IDs/sizes, selected and omitted sources, allowed roles, static prompt bytes, assembled request bytes, context/completion budgets, reduction reason, and batch identity.
- [x] 3.2 Require complete assembled-request validation before inference; a component limit alone is insufficient.
  - [-] 3.3 Define deterministic, stable reduction and batching rules that preserve source identity and required contract fields.
- [x] 3.4 Define `packet_budget_exhausted` with exact measurements when no valid packet exists.
- [x] 3.5 Scope packet exhaustion to the affected stage/artifact and prohibit advisory-stage failure from blocking unrelated work.
- [x] 3.6 Add reusable manifest/budget helpers and fixtures for unrestricted-component regression, batching, merge, omission, and artifact-scoped exhaustion. (Batch/merge consumer fixtures remain.)

- [-] 4. Define optional-stage fallbacks and provider-health behavior.
  - [-] 4.1 Require every stage declaration to state required/optional status, failure scope, fallback value, downstream effects, and terminal-status effect.
- [x] 4.2 Require optional-stage failures to preserve evidence and activate their declared fallback without claiming stage success or raising an uncaught run exception.
  - [-] 4.3 Define a non-generative configured-endpoint health probe that retains the configured hostname and never persists a substituted IP address.
- [x] 4.4 Classify DNS, permission/route, refusal, timeout, TLS, authentication, HTTP, and interruption outcomes with stable codes and retry behavior. (Authentication/HTTP codes retain existing status classification.)
- [x] 4.5 Implement a run-local provider circuit breaker keyed by provider/endpoint/model configuration, including open/close rules and suppressed-attempt records.
  - [-] 4.6 Require an open circuit to leave model work pending, preserve deterministic work, finalize reports normally, and never emit an uncaught traceback; Ctrl+C remains status 130.
  - [-] 4.7 Add provider/fallback/circuit report fields and fixtures including Windows socket-permission denial, refusal, timeout, HTTP, interruption, and recovery.

- [-] 5. Update governance routes and consumer migration guidance.
  - [-] 5.1 Update AGENTS, authority/reference documents, pipeline design, validation, operation, investigation, and audit playbooks with the source/packet/optional/provider contracts and their rationale.
  - [-] 5.2 Add a consumer migration checklist that inventories source roles, declares packet budgets, marks optional stages, and tests circuit behavior without modifying host-owned files automatically.
  - [-] 5.3 Update package/schema examples with non-secret configurable declarations for source roles, packet budgets, optional fallbacks, and provider health.

- [-] 6. Verify, publish, and close upstream.
- [x] 6.1 Run unit tests, documentation/prompt checks, package/schema validation, Python compilation, plan-index generation, and diff hygiene. (65 framework tests pass.)
  - [-] 6.2 Record the host failure rationale, compatibility boundaries, and verification evidence in the plan and journal.
- [x] 6.3 Commit and push the reviewed framework-only change directly to upstream main, verify `origin/main`, and record the published revision for consumers. Published `ff1e922`.
  - [-] 6.4 Archive this plan, regenerate indexes, and publish its closure checkpoint only after verification succeeds.

## Closure disposition — 2026-08-12

The implemented source-packet and provider-resilience checkpoint was published at `ff1e922`. The plan remained in `current` with unchecked implementation and administrative entries after that publication. Those stale entries are now explicitly closed rather than retroactively claimed complete; the published behavior and its recorded verification remain preserved. Any future source-packet or provider work requires a new evidence-backed plan.

## Success criteria

- Consumers can prove which text derivatives and source roles entered each model packet.
- No assembled request exceeds its declared budget silently or blocks unrelated work because of an advisory stage.
- Optional failures produce preserved evidence and explicit fallbacks; provider outages produce bounded, traceback-free terminal reports.
- The framework supplies executable helpers, tests, and migration guidance rather than only prose.
