---
plan_id: 2026-07-14-13-12-31_reorient-pipelines-around-prompts-and-playbooks
title: Reorient Agentic Pipelines Around Prompts and Playbooks
summary: Make concise prompts and task-specific playbooks the primary product while retaining the local runtime as shared supporting infrastructure.
status: current
created_at: 2026-07-14-13-12-31
---

# Reorient Agentic Pipelines Around Prompts and Playbooks

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

## Outcome

Agentic Pipelines will become a progressively disclosed prompt-and-playbook framework. Root instructions will explain the universal project model and route agents to the one playbook relevant to their current task. Playbooks will load only the prompts, templates, references, and commands needed for that task. The existing Python runtime, API primitive, SQLite state, thread capture, validators, and reports will remain reusable execution infrastructure beneath this prompt-first product surface.

Agentic Pipelines are deterministic programs first. Agents must use trusted tools, parsers, queries, shell commands, and small programs for every step they can perform reliably. An LLM is permitted only for a narrowly justified semantic transformation or judgment, receives the minimum necessary context, and is bounded by exact schemas, requirement-specific validation, finite attempts, evidence, and fail-closed routing. Broad acceptance criteria may not substitute for proof of the declared goal and invariants.

## Supersession

This plan supersedes `2026-07-14-11-57-14_build-local-agentic-pipelines-framework`. The predecessor is archived in `plans/past/`; its verified API, thread-capture, SQLite prototype, validator, and bounded-run work is retained as provisional infrastructure. Its unfinished work is closed there and dispositioned into this plan by `docs/plan_reconciliation_2026-07-14.md`.

## Non-goals

- Do not discard working runtime code merely because it was implemented before the prompt architecture.
- Do not require every agent to learn every pipeline lifecycle or governance workflow.
- Do not duplicate detailed instructions across `AGENTS.md`, playbooks, prompts, and references.
- Do not make generated host prompts silently inherit framework-development policy.
- Do not add cloud-provider fallbacks, distributed scheduling, or a graphical interface during this reorientation.
- Do not use an LLM for work that deterministic logic can reliably perform or weaken acceptance criteria to increase pass rates.

## 0. Reconcile governing plans and preserve completed work

- [x] 0. Reconcile this reorientation with the active runtime plan before implementation begins.
  - [x] 0.1 Audit the active plan against repository evidence.
    - [x] 0.1.1 Map every checked item in the predecessor plan to its implementing file or verification evidence.
      - [x] 0.1.1.1 Record inaccurate or only partially implemented checked items as corrections rather than preserving optimistic status.
    - [x] 0.1.2 Map every open item in the predecessor plan to this plan, a retained follow-up plan, or explicit closure.
      - [x] 0.1.2.1 Produce a one-to-one disposition table with `absorbed`, `retained`, `completed`, or `closed` for each open workstream.
  - [x] 0.2 Preserve runtime work as an infrastructure baseline.
    - [x] 0.2.1 Inventory `pipeline_runtime/`, `scripts/pipeline.py`, configuration samples, schemas, and tests.
      - [x] 0.2.1.1 Identify correctness, readability, and test gaps that must be fixed before the runtime is treated as stable.
    - [x] 0.2.2 Document which runtime interfaces prompt/playbook work may rely on.
      - [x] 0.2.2.1 Freeze provisional interfaces for API invocation, prompt path resolution, thread capture, entity inspection, and bounded runs.
  - [x] 0.3 Perform the approved plan lifecycle transition.
    - [x] 0.3.1 Update the old active plan with honest final checklist states and a pointer to this successor plan.
      - [x] 0.3.1.1 Mark absorbed unfinished items `[-]` with the successor plan ID instead of marking them completed.
    - [x] 0.3.2 Archive the reconciled old plan and promote this plan immediately before its first implementation edit.
      - [x] 0.3.2.1 Regenerate all plan indexes and verify status-directory/front-matter consistency.

## 1. Establish the prompt-first product model

- [x] 1. Make the repository's product hierarchy explicit and testable.
  - [x] 1.1 Define the project north star.
    - [x] 1.1.1 Write a concise statement distinguishing product assets from supporting infrastructure.
      - [x] 1.1.1.1 State that prompts and playbooks are primary, templates/references are supporting knowledge, and runtime code is the execution substrate.
    - [x] 1.1.2 Define progressive disclosure as an architectural requirement.
      - [x] 1.1.2.1 Require that an agent can perform one supported task without reading instructions for unrelated tasks.
  - [x] 1.2 Define the two prompt classes.
    - [x] 1.2.1 Specify pipeline-building prompts used by cloud or high-capability design agents.
      - [x] 1.2.1.1 Define their inputs, expected design artifacts, approval boundaries, and host-output locations.
    - [x] 1.2.2 Specify pipeline-running prompts used repeatedly by local inference.
      - [x] 1.2.2.1 Define their per-entity/per-cohort inputs, structured outputs, versioning, and thread-capture requirements.
  - [x] 1.3 Define information ownership.
    - [x] 1.3.1 Assign universal invariants to `AGENTS.md`, procedures to playbooks, reusable concepts to references, output shapes to templates/schemas, and executable instructions to prompts.
      - [x] 1.3.1.1 Create a duplication-resolution rule identifying the canonical owner when the same instruction appears in multiple layers.
    - [x] 1.3.2 Define host versus framework ownership for generated prompts and pipeline packages.
      - [x] 1.3.2.1 Specify how upstream prompt improvements are proposed without overwriting host-customized prompts.
  - [x] 1.4 Add architectural acceptance criteria.
    - [x] 1.4.1 Define maximum expected entrypoint scope and task-loading behavior without relying on a fragile word-count-only rule.
      - [x] 1.4.1.1 Add a verification scenario in which agents select tasks and enumerate exactly which files must be loaded.

## 2. Replace the universal manual with a concise entrypoint router

- [x] 2. Make root instructions a small universal kernel and task router.
  - [x] 2.1 Rewrite `AGENTS.md` around universally applicable behavior.
    - [x] 2.1.1 Retain only project purpose, task routing, source/config safety, progressive disclosure, plan authority for repository mutations, and missing-playbook behavior.
      - [x] 2.1.1.1 Move journaling, commits, host bootstrap, pipeline operation, failure analysis, and framework maintenance details to their owning playbooks.
    - [x] 2.1.2 Add a task-to-playbook routing table with unambiguous task signals.
      - [x] 2.1.2.1 Include routes for pipeline design, prompt creation, local API configuration, operation/resume, entity investigation, post-run analysis, cohort retry, host integration, and framework changes.
    - [x] 2.1.3 Define behavior when more than one task type applies.
      - [x] 2.1.3.1 Require loading the minimum ordered playbook set and prohibit speculative loading of the entire catalog.
  - [x] 2.2 Remove redundant model-specific root shims.
    - [x] 2.2.1 Retain `AGENTS.md` as the sole canonical root instruction file and remove ignored model-specific shims.
      - [x] 2.2.1.1 Preserve the prompt-first intention and correct `./pipelines/AGENTS.md` host path in the canonical entrypoint.
    - [x] 2.2.2 Verify that no redundant shim or separate root rules file remains.
      - [x] 2.2.2.1 Add a focused test for canonical `AGENTS.md`, routed playbooks, removed files, and host path behavior.
  - [x] 2.3 Remove global mandatory reading of unrelated detail.
    - [x] 2.3.1 Replace “read all of RULES and all indexed materials” behavior with explicit routing.
      - [x] 2.3.1.1 Test the router against at least six representative user requests and record the minimal file set selected for each.
  - [x] 2.4 Consolidate all root instruction authority into `AGENTS.md`.
    - [x] 2.4.1 Merge the concise router, task table, universal invariants, framework-change boundary, host resolution, and information ownership map into `AGENTS.md`.
      - [x] 2.4.1.1 Keep the merged entrypoint concise and require task-specific detail to remain in playbooks, prompts, templates, and references.
    - [x] 2.4.2 Remove the separate rules file and the ignored model-specific root shims (`CODEX.md`, `CLAUDE.md`, `GEMINI.md`, and `OPENCODE.md`).
      - [x] 2.4.2.1 Update active root, documentation, playbook, template, reference, test, and host-bootstrap references to `AGENTS.md` and `./pipelines/AGENTS.md`.
    - [x] 2.4.3 Verify the single-entrypoint contract.
      - [x] 2.4.3.1 Confirm `AGENTS.md` routes every supported task, no active file requires the removed rules file, and no removed shim remains in the working tree.

## 3. Create the task taxonomy and playbook system

- [x] 3. Give each recurring agent task one clear operational playbook.
  - [x] 3.1 Define a canonical playbook contract.
    - [x] 3.1.1 Require each playbook to state applicability signals, files to load, prerequisites, procedure, outputs, verification, and stopping/escalation conditions.
      - [x] 3.1.1.1 Update `templates/playbook_proposal.md` and the playbook-authoring playbook to enforce the contract.
    - [x] 3.1.2 Require playbooks to reference shared material instead of copying it.
      - [x] 3.1.2.1 Add an audit check for routed playbook size/structure and remove competing repeated legacy procedures.
  - [x] 3.2 Create pipeline-construction playbooks.
    - [x] 3.2.1 Add `playbooks/how_to_design_a_pipeline.md`.
      - [x] 3.2.1.1 Route goal interpretation, entity definition, invariants, stages, acceptance, recovery, and pipeline-package assembly through named design prompts.
    - [x] 3.2.2 Add `playbooks/how_to_build_pipeline_prompts.md`.
      - [x] 3.2.2.1 Cover worker, self-review, independent review, repair, adjudication, and analysis prompt generation and calibration.
    - [x] 3.2.3 Add `playbooks/how_to_design_pipeline_validation.md`.
      - [x] 3.2.3.1 Separate deterministic invariants from semantic judgments and require a golden evaluation set.
  - [x] 3.3 Create operation and diagnosis playbooks.
    - [x] 3.3.1 Add `playbooks/how_to_configure_local_inference.md`.
      - [x] 3.3.1.1 Cover `api.sample.yaml`, ignored `api.yaml`, preflight, secret handling, connectivity verification, and safe failure behavior.
    - [x] 3.3.2 Add `playbooks/how_to_operate_and_resume_a_pipeline.md`.
      - [x] 3.3.2.1 Cover discovery, dry run, bounded run, scheduler locking, interruption, resume, summaries, and rollback boundaries.
    - [x] 3.3.3 Add `playbooks/how_to_investigate_a_pipeline_entity.md`.
      - [x] 3.3.3.1 Cover state transitions, source/candidate evidence, validator results, thread capture, and disposition decisions without exposing unrelated entities.
    - [x] 3.3.4 Add `playbooks/how_to_review_post_run_analysis.md`.
      - [x] 3.3.4.1 Cover failure cohorts, performance findings, hypothesis labeling, remediation review, and regression requirements.
    - [x] 3.3.5 Add `playbooks/how_to_approve_and_retry_a_failure_cohort.md`.
      - [x] 3.3.5.1 Require approved pipeline revision, sample validation, explicit cohort identity, bounded retry, and unaffected-entity verification.
  - [x] 3.4 Create framework and host lifecycle playbooks.
    - [x] 3.4.1 Adapt host bootstrap and update-synthesis playbooks from `agents` paths to `pipelines` paths.
      - [x] 3.4.1.1 Preserve host-owned prompts, `TODO.md`, `api.yaml`, state, artifacts, threads, and reports during updates.
    - [x] 3.4.2 Add or adapt `playbooks/how_to_change_the_pipelines_framework.md`.
      - [x] 3.4.2.1 Keep plan/journal/verification requirements specific to framework mutation rather than loading them for ordinary pipeline runs.
  - [x] 3.5 Retire or adapt legacy playbooks.
    - [x] 3.5.1 Retain routed Agentic Pipelines procedures and remove unrelated agent, assimilation, downtime, tool-wrapper, roadmap, kickoff, and duplicate commit/review playbooks.
      - [x] 3.5.1.1 Remove legacy multi-board/HUD/agents-only routes from the active catalog after preserving reusable checklist principles in the root `TODO.md` and checkpoint guidance.

## 4. Build the canonical prompt library

- [x] 4. Make prompts the primary reusable intelligence of the repository.
  - [x] 4.1 Create the prompt directory taxonomy.
    - [x] 4.1.1 Create `prompts/design/`, `prompts/generate/`, `prompts/execute/`, and `prompts/analyze/` with concise index files.
      - [x] 4.1.1.1 Document which prompts are framework meta-prompts versus host-customizable runtime prompts.
  - [x] 4.2 Add pipeline-design prompts.
    - [x] 4.2.1 Add prompts to interpret the goal, define entities, identify invariants, design stages, design validation, and assemble a pipeline definition.
      - [x] 4.2.1.1 Give every prompt explicit inputs, one decision/output objective, required output schema, and uncertainty/escalation behavior.
    - [x] 4.2.2 Add a prompt that audits a proposed pipeline for missing stages and unsafe assumptions.
      - [x] 4.2.2.1 Require the audit to distinguish deterministic evidence, inference, and unresolved user decisions.
  - [x] 4.3 Add prompt-generation prompts.
    - [x] 4.3.1 Add generators for worker, self-review, independent reviewer, repair, adjudicator, failure-analysis, and performance-analysis prompts.
      - [x] 4.3.1.1 Require generated prompts to declare protected inputs, allowed transformations, structured output, and non-authority boundaries.
    - [x] 4.3.2 Add a prompt compression and completeness review.
      - [x] 4.3.2.1 Remove repeated background while verifying that no critical constraint or output field was lost.
  - [x] 4.4 Add reusable execution prompts.
    - [x] 4.4.1 Add canonical local worker, self-review, independent review, repair, and adjudication prompt templates.
      - [x] 4.4.1.1 Use placeholders that map directly to validated pipeline runtime fields and reject undeclared inputs.
    - [x] 4.4.2 Keep reviewer independence explicit.
      - [x] 4.4.2.1 Ensure reviewer prompts receive source, candidate, goal, and evidence but not worker hidden reasoning or an instruction to rationalize acceptance.
  - [x] 4.5 Add analysis prompts.
    - [x] 4.5.1 Add entity-failure, cohort-failure, remediation-proposal, and performance-analysis prompts.
      - [x] 4.5.1.1 Require observed facts, hypotheses, confidence, affected cohort, proposed change, regression test, and retry recommendation as separate fields.
    - [x] 4.5.2 Prevent analysis prompts from becoming execution authority.
      - [x] 4.5.2.1 State in each output contract that recommendations cannot edit the pipeline or relaunch entities without approved plan/playbook flow.

## 5. Define prompt quality, versioning, and output contracts

- [x] 5. Make “terse but complete” enforceable rather than aesthetic.
  - [x] 5.1 Create a prompt authoring reference.
    - [x] 5.1.1 Define one-job scope, minimum context, explicit inputs, invariants, output contract, and stop conditions.
      - [x] 5.1.1.1 Include paired examples showing verbosity removal without loss of operational meaning.
    - [x] 5.1.2 Define when content belongs in a prompt, playbook, reference, template, schema, or runtime validator.
      - [x] 5.1.2.1 Add a decision table usable during prompt review.
  - [x] 5.2 Create prompt metadata and manifests.
    - [x] 5.2.1 Define stable prompt IDs, semantic versions, content hashes, compatible input/output schemas, and intended model roles.
      - [x] 5.2.1.1 Extend schema-v2 `pipeline.yaml` so stages reference prompt IDs, versions, files, output contracts, attempt budgets, and LLM justifications.
    - [x] 5.2.2 Record resolved prompt identity in thread captures and attempt/run evidence.
      - [x] 5.2.2.1 Requeue an unchanged entity when its combined definition/prompt contract hash changes; cover this with a regression test.
  - [x] 5.3 Create structured output templates and schemas.
    - [x] 5.3.1 Add substantive schemas for pipeline design, worker result, reviewer verdict, repair, adjudication, validator evidence, failure analysis/cohorts, remediation, and performance.
      - [x] 5.3.1.1 Parse strict JSON and validate the declared schema before any model result changes entity state.
  - [x] 5.4 Add prompt linting and quality tests.
    - [x] 5.4.1 Check required metadata, schema substance, input lists, unresolved placeholders, duplicate IDs, broken references, roles, and forbidden authority language.
      - [x] 5.4.1.1 Add the lint command to verification with actionable failures.
    - [x] 5.4.2 Add scenario tests for contract completeness and irrelevant-context rejection.
      - [x] 5.4.2.1 Verify missing, extra, malformed, and schema-invalid inputs/outputs fail closed.

## 6. Create the goal-to-pipeline generation workflow

- [x] 6. Turn a user description into a reviewable host pipeline package.
  - [x] 6.1 Define the pipeline-design intake.
    - [x] 6.1.1 Capture goal, source, scale, allowed changes, protected content, constraints, acceptance, and escalation policy.
      - [x] 6.1.1.1 Separate discovered facts, inferences, and unresolved decisions.
  - [x] 6.2 Generate a proposed pipeline package.
    - [x] 6.2.1 Produce a schema-v2 definition, justified prompts, deterministic validation, fixtures, API sample, scheduler example, and rollback notes.
      - [x] 6.2.1.1 Keep generated content under a staged package root.
    - [x] 6.2.2 Produce requirement-to-stage verification traceability.
      - [x] 6.2.2.1 Reject missing traceability, unsafe paths, missing files, credentials, undeclared prompts, or invalid definitions.
  - [x] 6.3 Review and approve the package.
    - [x] 6.3.1 Run prompt/schema/package validation and retain an independent design audit artifact.
      - [x] 6.3.1.1 Record unresolved local-model calibration and promotion decisions before activation.
  - [x] 6.4 Bootstrap local execution safely.
    - [x] 6.4.1 Create non-secret samples and validate packages without creating credentials or starting work.
      - [x] 6.4.1.1 Validate config, definition, storage paths, prompts, schemas, and fixtures before processing.

## 7. Reposition and complete the shared runtime substrate

- [?] 7. Make the runtime faithfully execute prompt-defined contracts; execution and recovery are implemented, while retention/compression remains open below.
  - [x] 7.1 Refactor provisional runtime code for maintainability and contract fidelity.
    - [x] 7.1.1 Replace compressed implementations with clear typed modules, transactional migrations, and bounded error handling.
      - [x] 7.1.1.1 Preserve existing behavior and expand regression coverage during the rewrite.
    - [x] 7.1.2 Enforce that all model calls use the shared API primitive.
      - [x] 7.1.2.1 Add an architecture test rejecting provider HTTP access outside the adapter.
  - [x] 7.2 Connect prompt manifests to the runner.
    - [x] 7.2.1 Resolve, validate, minimally render, hash, constrain, and capture each declared entity/analysis prompt.
      - [x] 7.2.1.1 Abort before invocation on input, identity, version, output-schema, or path mismatch.
  - [x] 7.3 Complete entity quality stages.
    - [x] 7.3.1 Implement deterministic validation, optional self-review, independent review, repair, adjudication, quarantine, atomic promotion, and explicit rollback.
      - [x] 7.3.1.1 Enforce stage attempt and source/candidate size budgets with terminal reasons.
  - [x] 7.4 Complete scheduler-safe operation.
    - [x] 7.4.1 Add run IDs, locks, leases, stale recovery, bounded selection, interruption state, resume, changed-contract discovery, and cohort retry.
      - [x] 7.4.1.1 Test lock overlap, stale recovery, duplicate discovery, changed source/prompt safety, promotion rollback, and cohort isolation.
  - [ ] 7.5 Complete evidence linking and retention.
    - [x] 7.5.1 Link source hash, contract/prompt hash, thread capture, candidate, validation, attempt, transition, promotion, cohort, and report through stable IDs.
      - [ ] 7.5.1.1 Implement configured redaction, retention, compression, cleanup audit, and evidence-integrity verification.

## 8. Make post-run learning a prompt-driven pipeline phase

- [x] 8. Convert run evidence into safe improvement proposals.
  - [x] 8.1 Build deterministic cohort formation.
    - [x] 8.1.1 Group failures by stage, stable code, content type, size, contract revision, and attempt pattern; retain output/diff failures as stable codes.
      - [x] 8.1.1.1 Store exact membership, grouping data, and representative selection without copying source content.
  - [x] 8.2 Run prompt-based failure and performance analysis.
    - [x] 8.2.1 Invoke configured failure, remediation, and performance prompts through the shared primitive and capture their threads.
      - [x] 8.2.1.1 Nest model analysis beneath deterministic observations and keep hypotheses/unknowns schema-separated.
    - [x] 8.2.2 Calculate throughput, stage time, attempt failures, acceptance/quarantine rates, remaining work, and estimated duration; label unavailable usage unknown.
      - [x] 8.2.2.1 Supply false-accept/false-reject fields as unknown until a real golden-set run measures them.
  - [x] 8.3 Enforce the remediation boundary.
    - [x] 8.3.1 Mark proposals `advisory_only`; analysis has no code/configuration or retry mutation path.
      - [x] 8.3.1.1 Keep cohort retry a separate explicit command requiring a reviewed report and exact cohort ID.

## 9. Preserve the journal and simplify human-facing project state

- [x] 9. Keep design memory separate from machine evidence.
  - [x] 9.1 Adapt the journal to the prompt-first framework.
    - [x] 9.1.1 Retain user-only intentions/reflections and agent-managed design/checkpoint history.
      - [x] 9.1.1.1 Add plan, checklist, decision, evidence, risk, and next-action handoff fields.
    - [x] 9.1.2 Keep per-entity runtime events out of the journal.
      - [x] 9.1.2.1 Link reports/evidence rather than duplicating machine records.
  - [x] 9.2 Make root `TODO.md` the sole human-facing checklist.
    - [x] 9.2.1 Define framework-template versus host-owned checklist behavior.
      - [x] 9.2.1.1 Delete the legacy multi-board files, template, reference, and move playbook at the user's explicit direction; update active checkpoint/bootstrap documentation to use only root `TODO.md`.
  - [x] 9.3 Separate framework maintenance from post-run analysis.
    - [x] 9.3.1 Remove inherited downtime materials; framework maintenance uses approved plans and runtime learning uses post-run reports.
      - [x] 9.3.1.1 Keep failure/performance analysis in runtime reports and routed review/retry playbooks.

## 10. Migrate documentation and host integration

- [x] 10. Make documentation reflect the prompt-first operating model.
  - [x] 10.1 Rewrite `README.md` as the public project explanation.
    - [x] 10.1.1 Explain the cloud-design/local-execution model, prompt taxonomy, playbook routing, runtime substrate, host layout, and first pipeline workflow.
      - [x] 10.1.1.1 Link details to playbooks/docs instead of reproducing full procedures.
  - [x] 10.2 Update framework catalogs and architecture references.
    - [x] 10.2.1 Use `AGENTS.md` for routing and small directory READMEs/manifests for catalogs.
      - [x] 10.2.1.1 Verify routed playbooks and canonical catalog paths through structural tests.
    - [x] 10.2.2 Reframe runtime architecture as supporting contract documentation.
      - [x] 10.2.2.1 Make deterministic-first prompts/playbooks primary while preserving runtime safety contracts.
  - [x] 10.3 Create an `agents`-to-`pipelines` migration guide.
    - [x] 10.3.1 Cover submodule/router changes, host synthesis, journal/TODO retention, old maintenance removal, API/state setup, verification, and rollback.
      - [x] 10.3.1.1 Add documentation tests for required migration boundaries and explicit manual decisions.
  - [x] 10.4 Rename project-identity references from Pipelines to Agentic Pipelines.
    - [x] 10.4.1 Update documentation titles and self-references while preserving generic pipeline terminology, stable plan identifiers, and the `./pipelines` submodule path.
  - [x] 10.5 Establish and demonstrate the README entry-point documentation convention.
    - [x] 10.5.1 Require every pipeline README to place a concise pipeline explanation before an explanation of every supported pipeline entry point.
      - [x] 10.5.1.1 Add the convention to the framework README and verify the documented catalog stays present.
  - [x] 10.6 Require host deployments to retain a root API configuration sample.
    - [x] 10.6.1 Make bootstrap copy the framework's non-secret `api.sample.yaml` to the host root, keep the sample tracked, and reserve ignored `api.yaml` for operator-local values.
      - [x] 10.6.1.1 Document and test the host API-sample requirement in the deployment instructions.

## 11. Prove the complete paradigm with a Markdown repair pipeline

- [?] 11. Validate the product from user goal through post-run learning; the fake-provider vertical slice passes and operator-local calibration remains.
  - [x] 11.1 Create a representative fixture corpus.
    - [x] 11.1.1 Include valid, malformed-front-matter, broken-fence, protected, size-bound, prompt-injection, and unrepairable cases.
      - [x] 11.1.1.1 Label required invariants and acceptable outcome classes without overfitting prose.
  - [x] 11.2 Use only the documented design route to produce the staged package.
    - [x] 11.2.1 Record loaded artifacts, deterministic/LLM placement decisions, package outputs, traceability, and design audit.
      - [x] 11.2.1.1 Confirm no operation, migration, maintenance, or retry playbook is needed during design.
  - [?] 11.3 Execute with a fake provider; acceptance, repair, quarantine, analysis, retry, locking, stale recovery, and rollback pass, while full process interruption and configured adjudication need integration coverage.
    - [?] 11.3.1 Cover accepted, rejected, repaired, quarantined, recovered, and cohort-retried paths; configured adjudication and process interruption remain release gates.
      - [x] 11.3.1.1 Inspect source safety, state/attempt evidence, prompt hashes, threads, reports, promotion records, and cohort isolation.
  - [?] 11.4 Execute an opt-in local Ollama smoke test; blocked only on operator-local model/configuration.
    - [ ] 11.4.1 Use ignored credentials/configuration and a bounded fixture batch.
      - [ ] 11.4.1.1 Verify redaction, structured outputs, runtime compatibility, throughput, quality, and clean Git exclusions against the real model.
  - [?] 11.5 Exercise post-run improvement; cohort analysis, advisory proposal, and scoped retry work, but measured improvement after an approved change remains.
    - [?] 11.5.1 Generate deterministic cohorts, advisory remediation, and retry only the selected cohort; apply one reviewed change after real-model evidence exists.
      - [ ] 11.5.1.1 Confirm improved outcomes without golden-set regression or unrelated-entity changes.

## 12. Verification, release, and plan closure

- [?] 12. Demonstrate that the reorientation is complete and internally consistent; automated verification passes and operator-local gates keep the plan current.
  - [x] 12.1 Run structural verification.
    - [x] 12.1.1 Validate prompt/package schemas, imports, playbook routes, root authority, catalogs, provider boundary, migration references, and ignored paths.
      - [x] 12.1.1.1 Fail on removed-system references in active product files, missing prompts, duplicate IDs, placeholder schemas, or provider calls outside the adapter.
  - [?] 12.2 Run behavioral verification; all available automated tests pass, with real Ollama and process-interruption gates outstanding.
    - [?] 12.2.1 Run unit/integration coverage for redaction, contract invalidation, cohorts, reference flow, locks, stale recovery, source safety, and rollback.
      - [x] 12.2.1.1 Record commands, coverage, and remaining gates in `docs/release_readiness.md`.
  - [x] 12.3 Run progressive-disclosure verification.
    - [x] 12.3.1 Verify routed playbooks are concise/structured and prompts reject undeclared context.
      - [x] 12.3.1.1 Confirm tasks resolve from the root router to the minimum owning catalog/playbook.
  - [x] 12.4 Review documentation and repository state.
    - [x] 12.4.1 Document implemented behavior, explicit limitations, local-only config, and ignored runtime evidence.
      - [x] 12.4.1.1 Review status, removed maintenance material, journal linkage, migration rollback, and lack of baseline commit.
  - [ ] 12.5 Close the implementation plan.
    - [ ] 12.5.1 Mark every item completed, validated, or intentionally closed with evidence.
      - [ ] 12.5.1.1 Archive this plan, regenerate indexes, append the final journal checkpoint, and present the user with a commit/push proposal.

## Delivery checkpoints

- [x] A. Approve Sections 0-1: plan reconciliation and prompt-first product contract.
- [x] B. Deliver Sections 2-5: concise router, task playbooks, prompt library, and prompt contracts.
- [?] C. Deliver Sections 6-8: generation, execution, and learning are delivered; retention/compression remains.
- [x] D. Deliver Sections 9-10: journal/TODO/maintenance migration and host documentation.
- [?] E. Deliver Sections 11-12: fake-provider reference and release report are delivered; local calibration and final closure remain.

## Expected file groups

Expected changes include the root `AGENTS.md` entrypoint, `README.md`, `TODO.md`, `.gitignore`, the old and successor plan files/indexes, `prompts/`, `playbooks/`, `references/`, `templates/`, `docs/`, `journal/`, framework-maintenance materials, `pipeline_runtime/`, `scripts/`, schemas, fixtures, and tests. Exact new filenames must be fixed during Sections 1-5 before broad runtime refactoring begins.

