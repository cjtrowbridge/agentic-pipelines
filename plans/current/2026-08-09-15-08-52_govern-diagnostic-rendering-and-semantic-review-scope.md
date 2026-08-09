---
plan_id: 2026-08-09-15-08-52_govern-diagnostic-rendering-and-semantic-review-scope
title: Govern Diagnostic Rendering and Semantic Review Scope
summary: Establish universal governance, schemas, evidence contracts, and conformance tests for diagnostic rendering of rejected candidates and correctly scoped semantic claim and coverage review.
status: current
created_at: 2026-08-09-15-08-52
---

# Govern Diagnostic Rendering and Semantic Review Scope

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

## Authority, dependency, and preservation boundary

This upstream framework plan must be executed and published before the linked host plan `plans/future/2026-08-09-15-08-53_adopt-diagnostic-rendering-and-correct-cover-letter-review.md` may begin implementation. It may change universal governance, references, playbooks, templates, schemas, shared evidence helpers, reference implementations, fixtures, tests, indexes, and the upstream journal. It must not change any consuming host, application content, host prompt, host renderer, credential, ignored runtime evidence, or historical rejection bundle. Existing schema-v1 through schema-v4 reports and legacy evidence remain immutable and readable. No model-backed host run is authorized by this plan.

## Evidence motivating the change

The host run `run-26abe031f7c2` exposed three generalized defects. First, governance says rejected evidence must not enter final rendering, but operational language collapses that prohibition into a ban on all rendering, so a rejected Markdown candidate has no visual diagnostic PDF. Second, semantic claim review can be applied outside its domain—for example to a required salutation or closing—creating false rejection and destructive repair pressure. Third, a nonessential metadata field and unsupported coverage gaps can exhaust repair budgets even when the candidate body is usable. This plan must preserve those reasons in durable governance and executable fixtures rather than relying on transient agent context.

## Normative target behavior

```text
untrusted rejected Markdown candidate
  -> exact byte-preserving candidate + explanation sidecar
  -> isolated deterministic diagnostic render
  -> typed render child + its own explanation sidecar
  -> report checkpoint

accepted candidate
  -> ordinary validated rendering
  -> promotion eligibility
```

Diagnostic rendering is evidence production, not acceptance, repair, ordinary rendering, or promotion. A canonical bundle is:

```text
cover_letter.1.rejected.md
cover_letter.1.rejected.explanation.md
cover_letter.1.rejected.claim_review.json
cover_letter.1.rejected.claim_review.explanation.md
cover_letter.1.rejected.render.pdf
cover_letter.1.rejected.render.explanation.md
```

- [ ] 1. Resolve the diagnostic-versus-final-rendering governance contradiction.
  - [ ] 1.1 Amend `AGENTS.md` to define ordinary/final rendering as a trusted promotion-path operation and diagnostic rendering as an isolated evidence-only transformation of an already rejected candidate.
  - [ ] 1.2 State normatively that every newly rejected renderable Markdown candidate must receive a diagnostic render when the declared deterministic renderer is available.
  - [ ] 1.3 Retain the prohibition against rejected evidence entering ordinary rendering, promotion, recovery, source discovery, semantic evidence, example retrieval, prompt assembly, freshness decisions, or accepted manifests.
  - [ ] 1.4 Require diagnostic rendering to read the exact persisted candidate bytes, make no content repair or normalization, and record the source path and SHA-256 used.
  - [ ] 1.5 Require the render child name `<artifact>.<sequence>.rejected.render.pdf` and sidecar `<artifact>.<sequence>.rejected.render.explanation.md` so Markdown and PDF explanations cannot collide.
  - [ ] 1.6 Require the render child to share the parent sequence and link bidirectionally through sidecar and run-report metadata without becoming another primary candidate.
  - [ ] 1.7 Require diagnostic-render metadata to state renderer/profile identity, command/configuration identity without secrets, start/finish time, page count, overflow and readability measurements when available, source hash, PDF hash, and outcome.
  - [ ] 1.8 Define diagnostic-render failure as evidence failure local to the derivative: retain the original rejection, preserve a typed `.render.txt` or other truthful failure child plus sidecar, checkpoint it, and never relabel the original semantic verdict.
  - [ ] 1.9 Define interruption behavior so a safely persisted parent remains truthful even if diagnostic rendering is interrupted; reconciliation must identify the absent or partial derivative without claiming success.
  - [ ] 1.10 Define idempotency and collision behavior: an existing verified render child is reused, an incomplete child is reconciled safely, and a conflicting child never overwrites evidence or consumes a different candidate sequence.
  - [ ] 1.11 Explicitly prohibit model calls, semantic repair, promotion gates, and retry loops within diagnostic rendering; it is a bounded deterministic representation step.
  - [ ] 1.12 Add an immutable-legacy boundary: do not backfill or rename historical rejected candidates unless a separately authorized migration requests it.

- [ ] 2. Correct universal semantic claim-review scope.
  - [ ] 2.1 Amend deterministic/semantic authority guidance to distinguish factual propositions from structural, performative, prospective, polite, and conventional document language.
  - [ ] 2.2 Permit deterministic artifact parsers to identify exact structural zones—headers, contact blocks, salutations, closings, signatures, and declared section types—without claiming semantic factual authority.
  - [ ] 2.3 Require semantic reviewers to classify any submitted non-factual unit as `not_factual` or an equivalent declared status rather than `unsupported`.
  - [ ] 2.4 State that `not_factual` findings are non-repairing and non-blocking unless a separate exact structural validator rejects the text.
  - [ ] 2.5 Require factual-review schemas to distinguish unsupported assertions from text outside the factual-review domain.
  - [ ] 2.6 Require correction feedback to identify the exact proposition and semantic defect; it may not tell a repairer to delete required document structure.
  - [ ] 2.7 Require disagreement between a structural validator and semantic reviewer to route to authority correction or human review rather than blindly privileging the reviewer.
  - [ ] 2.8 Add cover-letter, resume-objective, salutation, closing, signature, expression-of-interest, and thank-you examples to the authority reference.

- [ ] 3. Correct universal semantic coverage and repairability rules.
  - [ ] 3.1 Define `repairable_missing` as a material omission for which trusted source evidence exists and can be added without invention.
  - [ ] 3.2 Require every `repairable_missing` finding to cite independently resolvable exact source excerpts or stable source IDs.
  - [ ] 3.3 Require deterministic validation that those citations resolve before the finding may trigger repair.
  - [ ] 3.4 Define unsupported qualifications as `unsupported_gap` and legitimately selective omissions as `optional_omitted`; neither status may instruct a model to invent coverage.
  - [ ] 3.5 Require artifact-specific coverage policy: a cover letter selects the strongest material alignments and is not presumed to enumerate every posting requirement.
  - [ ] 3.6 Require coverage reviewers to distinguish mandatory application instructions, high-value qualifications, optional preferences, and unsupported qualifications before assigning materiality.
  - [ ] 3.7 Require repair feedback to include only findings whose declared repair owner is semantic transformation and whose trusted evidence is present.
  - [ ] 3.8 Route materially ambiguous coverage decisions to human review rather than manufacturing a deterministic threshold or repeated repair loop.

- [ ] 4. Govern output-contract minimality and schema-driven non-progress.
  - [ ] 4.1 Add guidance that every output field must have a declared consumer and material consequence; remove decorative or duplicate metadata fields from model contracts.
  - [ ] 4.2 Require prompts, JSON schemas, deterministic validators, examples, and consumers to agree on each field’s type, nullability, optionality, and cardinality.
  - [ ] 4.3 State that a nonessential field must not be allowed to discard an otherwise usable candidate unless the field is explicitly part of the acceptance invariant.
  - [ ] 4.4 Prohibit silently deleting or coercing an invalid field after inference unless a predeclared, meaning-preserving canonicalization rule makes that normalization authoritative and visible.
  - [ ] 4.5 Extend non-progress guidance beyond byte identity: repeated rejection of the same schema path and constraint after corrective feedback must stop, change strategy, or escalate within a finite budget.
  - [ ] 4.6 Require reports to distinguish content rejection, contract/schema rejection, diagnostic-render failure, and ordinary render/promotion failure.
  - [ ] 4.7 Require retry telemetry to record rejection path/code, feedback delta, response delta, and whether the retry changed the responsible property.

- [ ] 5. Update shared evidence contracts, schemas, templates, and runtime helpers.
  - [ ] 5.1 Extend the run-evidence schema with a diagnostic-render artifact role and explicit source-candidate path/hash, child path/hash, renderer metadata, metrics, and outcome fields.
  - [ ] 5.2 Extend rejection-sidecar templates for typed diagnostic-render children and render-failure children without reusing the primary candidate sidecar.
  - [ ] 5.3 Extend pipeline-package declarations with optional diagnostic-render capability, renderer availability policy, supported input/output representations, and failure behavior.
  - [ ] 5.4 Add shared path helpers for `<artifact>.<sequence>.rejected.render.<ext>` and its same-stage explanation sidecar.
  - [ ] 5.5 Add guarded shared persistence for a diagnostic derivative that verifies the persisted parent hash before publishing the child pair.
  - [ ] 5.6 Add shared report-link helpers that checkpoint diagnostic-render start, success, failure, interruption, reuse, and reconciliation events.
  - [ ] 5.7 Ensure shared discovery and trust classifiers continue excluding all diagnostic children from trusted pipeline inputs and accepted outputs.
  - [ ] 5.8 Update reference runner behavior or a renderer-agnostic example to demonstrate the evidence callback without prescribing host commands or rendering engines.

- [ ] 6. Update framework routing, investigation, audit, and design documentation.
  - [ ] 6.1 Update pipeline-design guidance to require an explicit diagnostic-artifact policy for every generated human-readable artifact.
  - [ ] 6.2 Update validation-design guidance and authority-matrix templates with factual-domain scope, `not_factual`, evidence-backed repairability, diagnostic rendering, and escalation rows.
  - [ ] 6.3 Update operation guidance to allow diagnostic rendering while continuing to prohibit ordinary rendering and promotion of rejected evidence.
  - [ ] 6.4 Update investigation guidance so agents compare rejected Markdown and its diagnostic PDF, verify source/render hashes, and keep render observations separate from semantic verdicts.
  - [ ] 6.5 Update audit guidance to flag absent diagnostic renders, diagnostic PDFs entering trusted paths, structural language treated as factual claims, unsupported gaps marked repairable, and nonessential schema fields causing terminal failure.
  - [ ] 6.6 Update post-run analysis guidance to identify the earliest responsible layer and quantify retries caused by claim-scope, coverage-scope, schema, and renderer defects.
  - [ ] 6.7 Update package examples, naming examples, and README language to use the typed `.render.pdf` child grammar consistently.

- [ ] 7. Verify the upstream contract adversarially.
  - [ ] 7.1 Add a fixture proving a rejected Markdown candidate produces an exact-hash-linked `.render.pdf` child while no ordinary/final render or promotion occurs.
  - [ ] 7.2 Add a fixture proving Markdown and diagnostic PDF sidecars do not collide and both hashes validate.
  - [ ] 7.3 Add a fixture proving diagnostic-render failure preserves the original candidate and writes a truthful failure child without changing the semantic verdict.
  - [ ] 7.4 Add fixtures for interruption between parent persistence, render start, PDF persistence, sidecar persistence, and report checkpoint, followed by truthful reconciliation.
  - [ ] 7.5 Add collision and concurrency fixtures proving no existing candidate, render child, or sidecar is overwritten or misassociated.
  - [ ] 7.6 Add authority fixtures proving salutations, closings, signatures, objectives, expressions of interest, and polite conclusions are not rejected as unsupported CV facts.
  - [ ] 7.7 Add coverage fixtures proving a source-backed material omission is repairable while an unsupported qualification and selective optional omission are not.
  - [ ] 7.8 Add schema fixtures proving prompt/schema/consumer agreement and repeated same-path rejection causes bounded strategy change or escalation.
  - [ ] 7.9 Prove diagnostic children remain excluded from discovery, retrieval, semantic evidence, prompt assembly, accepted manifests, freshness decisions, ordinary rendering, recovery, and promotion.
  - [ ] 7.10 Validate backward readability of schema-v1 through schema-v4 reports and legacy rejection names without rewriting fixtures.
  - [ ] 7.11 Run the complete upstream test suite, prompt lint, package validation, schema fixtures, Python compilation, plan-index generation, and diff hygiene checks.

- [ ] 8. Publish and close the upstream change.
  - [ ] 8.1 Update the upstream journal with the motivating Malibu trajectory, normative decisions, compatibility boundary, implementation evidence, and verification results.
  - [ ] 8.2 Review the complete diff for framework-only scope, host safety, ignored evidence, credentials, and unrelated changes.
  - [ ] 8.3 Commit and push the reviewed framework implementation directly to upstream `main` under the consuming host’s direct-publication policy.
  - [ ] 8.4 Verify upstream `origin/main`, record the implementation revision in this plan, and expose it as the exact dependency for the host plan.
  - [ ] 8.5 Archive this plan, regenerate upstream indexes, commit and push the closure checkpoint, and record the final upstream revision.

## Success criteria

- Rejected renderable Markdown always has an isolated visual diagnostic when a renderer is available, without becoming trusted or promotable.
- Structural and non-factual document language cannot be rejected as an unsupported source fact.
- Coverage repair is triggered only by material, source-backed omissions.
- Nonessential output metadata and repeated same-path schema mistakes cannot consume an unproductive repair trajectory.
- Consuming pipelines receive executable schemas, helpers, playbooks, examples, and tests—not merely prose—to adopt the behavior consistently.
