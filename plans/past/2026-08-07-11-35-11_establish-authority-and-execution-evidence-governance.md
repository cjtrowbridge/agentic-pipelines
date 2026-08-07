---
plan_id: 2026-08-07-11-35-11_establish-authority-and-execution-evidence-governance
title: Establish Authority and Execution-Evidence Governance
summary: Define and enforce deterministic, semantic, and human authority boundaries; require inspectable run and rejected-candidate evidence; and equip consuming hosts to audit and plan conformance migrations.
status: past
created_at: 2026-08-07-11-35-11
---

# Establish Authority and Execution-Evidence Governance

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

This is the canonical upstream execution plan derived from the approved host program plan `2026-08-08-00-00-00_fix-stochastic-vs-deterministic-decisioning`. Resume-pipeline failures are motivating evidence and regression fixtures, not the scope boundary. All implemented contracts must generalize to every Agentic Pipelines consumer.

## Adopted Decisions

- Deterministic mechanisms have authoritative acceptance/rejection power only for properties exactly computable from declared representations or traceable exact domain rules.
- Meaning, entailment, equivalence, relevance, faithful transformation, and qualitative fitness require bounded semantic or explicit human judgment. Heuristics may route or escalate but may not masquerade as semantic proof.
- Safely repairable representational defects belong in deterministic normalization; model retries are reserved for corrections requiring semantic or editorial judgment.
- Every execution must preserve a machine-readable report, a human-readable run narrative, and each rejected candidate with an appended actionable rejection record.
- Runtime evidence is durable institutional memory: it must expose complete attempt trajectories and reasons so future agents can remove avoidable loops at the earliest responsible layer.
- Rejected artifacts are inspectable but untrusted, ignored runtime evidence. They may never be promoted, rendered as final output, retrieved as examples, treated as factual sources, or automatically assembled into prompts.
- Analysis is advisory and must distinguish observations, metrics, hypotheses, and recommendations. It may recommend no change and may not mutate a framework or host without an approved plan.
- Framework updates provide a preservation-safe conformance audit and remediation-plan proposal; hosts retain ownership and separately approve migrations.

## Checklist

- [x] 1. Establish canonical governance and rationale.
  - [x] 1.1 Add the inverse deterministic-first authority invariant and mandatory execution-evidence invariant to `AGENTS.md` without expanding it into a procedural manual.
  - [x] 1.2 Add `references/deterministic_and_semantic_authority.md` defining property classes, sufficiency, exact domain rules, heuristic limits, authority laundering, mixed gates, deterministic repair, semantic review, ambiguity, and human escalation.
  - [x] 1.3 Add `references/run_evidence_and_continuous_improvement.md` preserving the detailed reasons for complete run trajectories, rejected-candidate retention, first-pass learning, causal analysis, prompt-accretion controls, privacy, retention, and trust boundaries.
  - [x] 1.4 Update the prompt-first product model and prompt-authoring reference to use the new sufficiency definition and avoid categorically assigning semantic comparison, extraction, matching, or selection to deterministic code.
  - [x] 1.5 Update reference indexes and cross-links while preserving progressive disclosure and canonical information ownership.

- [x] 2. Make authority and evidence requirements enforceable in pipeline design.
  - [x] 2.1 Update pipeline-design and validation-design playbooks to require an authority matrix for every stage, gate, repair, and escalation.
  - [x] 2.2 Extend pipeline package schemas/templates with property class, mechanism, authority, proof basis, heuristic role, evidence, materiality, repair owner, escalation, governance version, and evidence-path/retention declarations.
  - [x] 2.3 Update design prompts to emit the declared authority and evidence contracts.
  - [x] 2.4 Update the design auditor to flag semantic properties assigned to deterministic proxies, heuristics used as verdicts, untraceable exact-domain rules, unbounded semantic authority, deterministic repairs sent to inference, misleading validator language, discardable rejected candidates, and missing terminal run reports.
  - [x] 2.5 Update package validation so executable contracts reject invalid authority assignments and missing evidence declarations without misclassifying legitimate exact rules or bounded semantic stages.

- [x] 3. Add a reusable consumer conformance-review workflow.
  - [x] 3.1 Add a routed playbook for reviewing an existing host pipeline against the current governance revision.
  - [x] 3.2 Add a structured conformance report template/schema and audit prompt that inventory stages and gates, cite host evidence, classify authority, identify overclaims and missing evidence, and recommend the smallest correction.
  - [x] 3.3 Require the review to inspect definitions, prompts, validators, schemas, retries, repairs, promotion, run reports, rejected candidates, thread evidence, and tests.
  - [x] 3.4 Require a proposed host remediation plan, accepted-exception and no-change outcomes, and no automatic host mutation.
  - [x] 3.5 Integrate the audit into the submodule update/synthesis playbook after governance-changing updates while preserving host ownership.

- [x] 4. Define reusable runtime execution-evidence contracts.
  - [x] 4.1 Add versioned schemas/templates for the machine run report, human-readable run narrative, attempt/rejection events, and rejected-artifact diagnostic trailer.
  - [x] 4.2 Require initialization before material work and guarded finalization for success, failure, interruption, partial success, resume, and no-op paths; evidence-persistence failure must be visible and terminal.
  - [x] 4.3 Record entity/artifact/stage/session/attempt identity, model/configuration, prompt sizes and limits, timing, outcome, failure class, authority, validator/reviewer, explanation, feedback, retry disposition, and evidence links.
  - [x] 4.4 Define a shared rejected-candidate persistence primitive or reference implementation with atomic collision-safe writes, content hashes, names such as `resume.2.rejected.md`, appended rejection records, raw malformed-output retention, and no overwrite.
  - [x] 4.5 Define default Git-ignore, discovery-exclusion, retrieval-exclusion, prompt-exclusion, render-exclusion, and promotion-exclusion behavior for rejected artifacts.
  - [x] 4.6 Separate truthful `execution_status` from `learning_status` and prevent ordinary process exit from masquerading as artifact success.
  - [x] 4.7 Generate the factual human-readable narrative deterministically and link it from the terminal summary; retrospective inference may enrich analysis but is not required for basic reconstruction.

- [x] 5. Add governed continuous-improvement analysis.
  - [x] 5.1 Update operation, entity-investigation, and post-run-review playbooks to consume the canonical run narrative and rejected artifacts first.
  - [x] 5.2 Compute first-pass yield, repair dependence, repeated/changing feedback, non-progress, prompt growth, deterministic work sent to inference, suspected false rejection, calls/tokens/time per accepted artifact, and root-cause cohorts before optional model analysis.
  - [x] 5.3 Update analysis prompts/contracts to compare the first attempt with the accepted or terminal trajectory and identify the earliest responsible layer.
  - [x] 5.4 Require observations, derived metrics, hypotheses, recommendations, expected benefit, regression risk, and required fixtures to remain distinct.
  - [x] 5.5 Prevent prompt accretion through evidence thresholds, compression/generalization, successful-case regression checks, and explicit no-change conclusions.

- [x] 6. Verify framework-wide behavior.
  - [x] 6.1 Add documentation/routing tests for the new references, conformance route, and minimum-context behavior.
  - [x] 6.2 Add authority fixtures for low-overlap equivalence, high-overlap contradiction, false numeric units, exact typed facts, deterministic formatting repair, and human escalation.
  - [x] 6.3 Add non-resume fixtures for summarization, classification, factual transformation, retrieval/ranking, and document repair.
  - [x] 6.4 Test every terminal path for both run reports and truthful statuses.
  - [x] 6.5 Test rejected-artifact naming, integrity, diagnostic trailers, malformed outputs, concurrency/restart collision safety, and no-overwrite behavior.
  - [x] 6.6 Test that rejected evidence cannot enter Git, source discovery, example retrieval, prompt assembly, rendering, promotion, or semantic evidence.
  - [x] 6.7 Test redaction and cross-entity isolation and document compatibility/migration behavior for older hosts.
  - [x] 6.8 Run the complete upstream suite and record exact results.

- [x] 7. Document, publish, and hand off downstream adoption.
  - [x] 7.1 Update README/index documentation and release/migration guidance with the governance revision and repeatable update → synthesize → audit → plan → approve → remediate sequence.
  - [x] 7.2 Update this plan, regenerate plan indexes, and record the journal checkpoint with rationale and verification evidence.
  - [x] 7.3 Review the scoped upstream diff for internal consistency, ownership safety, generated evidence, and unrelated changes.
  - [x] 7.4 Commit the approved framework changes and push directly to `origin/main`.
  - [x] 7.5 Verify the remote revision and provide it to the host as the minimum conformance-governance revision.

## Completion Evidence

- Framework implementation commit: `9397f4f5691a1fbbb94326e0ab3de2d9b138d6f4`.
- `origin/main` was verified at the same revision after push.
- Verification: 53 unit tests passed; 25 prompts linted; Python compiled; the reference package validated as schema 2 and governance conformant.
- Downstream minimum governance revision: `9397f4f5691a1fbbb94326e0ab3de2d9b138d6f4`.
