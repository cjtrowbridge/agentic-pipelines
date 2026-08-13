---
plan_id: 2026-08-12-21-10-22_articulate-few-shot-semantic-pipeline-governance
title: Articulate Few-Shot Semantic Pipeline Governance
summary: Make coherent few-shot semantic transformations the framework default while preventing semantic laundering, context fragmentation, and unbounded reviewer authority.
status: past
created_at: 2026-08-12-21-10-22
---

# Articulate Few-Shot Semantic Pipeline Governance

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

## Authority and scope

This is an upstream Agentic Pipelines framework plan. Its motivating evidence comes from the host application-materials V1 and V2 implementations and their preserved run reports, but its requirements must apply to summarization, classification, ranking, extraction, document generation, document repair, code transformation, and other semantic pipelines without importing resume-specific policy.

The plan may change upstream governance, references, playbooks, design and generation prompts, architecture documentation, templates, schemas where needed, conformance-audit contracts, general examples, tests, plans, and journal checkpoints. It must not modify a consumer host, automatically rewrite an existing consumer pipeline, change host credentials or runtime state, or declare a consumer conformant without a separate evidence-backed host audit and approved host plan.

## Problem statement

The framework correctly prohibits deterministic mechanisms from claiming semantic authority, but its positive design guidance still presents atomized claims, typed evidence, independent semantic review, and repair as a common default. Agents can therefore construct a chain in which semantic properties are converted into hand-built classifications or model labels and then rejected by exact validators operating on those non-authoritative representations. This plan names that failure mode **semantic laundering** and replaces the default with a smaller positive architecture based on coherent semantic units, bounded representative demonstrations, retained sessions, risk-based review, exact deterministic envelopes, and explicit human escalation.

The framework currently mentions representative examples mainly as a reason to disable unnecessary reasoning. It does not yet state the broader design implication that LLMs are few-shot learners and that trusted demonstrations can be the most direct specification of a semantic transformation's ontology, selection behavior, abstraction level, relationships among outputs, tone, and boundary behavior.

## Normative target

```text
trusted sources and demonstrations
  -> deterministic preparation, provenance, bounds, and exact preconditions
  -> one smallest coherent semantic transformation in a retained session
  -> scope-bound semantic audit and at most bounded evidence-driven repair
  -> deterministic schema/resource/render/promotion gates
  -> explicit human decision only for unresolved intent, material ambiguity, or risk
```

The concise framework doctrine will be:

> Code governs exactness. Models govern meaning. Humans govern unresolved intent and risk. Examples specify behavior.

The canonical governance reference must also preserve this exact sentence and its immediate practical explanation:

> **LLMs are few-shot learners.** For semantic transformations, the best outputs will come from giving the model representative examples of past inputs and their accepted outputs, followed by the new input, so the model can learn the demonstrated transformation rather than forcing agents to approximate that behavior with an expanding collection of handcrafted semantic rules.

The surrounding guidance must explain that this is the default design pattern when trusted representative examples exist, not permission to send unbounded examples, treat examples as undeclared factual authority, or use an LLM for exact work.

- “Narrow” means bounded authority and a specific coherent outcome; it does not mean decomposing meaning into the smallest individually nameable claim.
- “Minimum context” means the minimum sufficient context for correct performance, including bounded representative demonstrations when they materially specify the task; it does not mean the fewest bytes irrespective of lost coherence.
- Deterministic validation may prove properties of authoritative exact representations. It may not make a lexical, structural, statistical, model-generated, or hand-typed proxy authoritative for the meaning it approximates.
- A reviewer may judge only the declared decision scope. For a requested revision, previously accepted content remains outside blocking review unless the requested delta directly changes or contradicts it.
- Independent semantic review and claim-level provenance are optional high-assurance patterns justified by material risk, not universal default stages.
- Semantic quality is evaluated across representative golden fixtures as well as bounded runtime review; a production entity must not traverse pseudo-exact semantic proof machinery merely to make an unmeasured design appear rigorous.

## Plan

- [x] 1. Reconcile plan lifecycle and establish the evidence baseline.
  - [x] 1.1 Review the existing upstream current plan and its published/unfinished items; complete, explicitly close, or separately preserve every item before promoting this plan.
  - [x] 1.2 Promote this approved plan from `plans/future/` to `plans/current/` immediately before the first non-trivial framework edit and regenerate plan indexes.
  - [x] 1.3 Record the framework revision, affected routes, and representative host evidence used for design without copying protected entity content into upstream fixtures.
  - [x] 1.4 Preserve as a sanitized regression trajectory the V1 pattern in which a semantically supported result is rejected because deterministic free-text classification permits the wrong evidence kind.
  - [x] 1.5 Preserve as sanitized regression trajectories the V2 broad-review retry loop and the focused request-aware two-call success, including prompt-growth and reviewer-scope observations.

- [x] 2. Define the positive semantic-stage design doctrine.
  - [x] 2.1 Add the four-part authority rule: deterministic mechanisms govern exact state and representation; models govern meaning; humans govern unresolved intent and material risk; examples specify behavior.
  - [x] 2.2 Define the **smallest coherent semantic unit** and distinguish it from the smallest individually nameable subproblem.
  - [x] 2.3 Require every semantic-stage split to declare its observed failure, isolation/risk/context/reuse justification, added context/schema/retry cost, and evaluation evidence.
  - [x] 2.4 Define **semantic laundering** and prohibit exact validators from promoting a heuristic, inferred free-text class, model label, typed proxy, similarity score, or lexical relation into authority over the underlying semantic property.
  - [x] 2.5 Clarify that exact code may validate schema shape, stable IDs, source availability, hashes, protected literals, limits, renders, and transactions without deciding entailment, relevance, equivalence, materiality, or qualitative fitness.
  - [x] 2.6 Clarify that independently resolvable evidence IDs provide provenance and integrity, not semantic support by themselves.
  - [x] 2.7 Recast claim-level evidence review and fresh-session independent review as optional high-assurance patterns selected through a documented risk analysis.
  - [x] 2.8 Define human authority for unresolved material facts, policy exceptions, intent conflicts, risk acceptance, and publication decisions without routing ordinary model uncertainty automatically to a user.

- [x] 3. Make bounded few-shot examples a first-class specification mechanism.
  - [x] 3.1 Put the exact sentence **“LLMs are few-shot learners.”** in the canonical governance reference and follow it immediately with a brief explanation that the best semantic-transformation outputs come from representative past input/accepted-output pairs plus the new input.
  - [x] 3.2 Require the same canonical passage to explain that demonstrations let the model learn the desired ontology, selection behavior, abstraction level, output relationships, tone, and boundary behavior instead of forcing agents to approximate those properties through expanding handcrafted semantic rules.
  - [x] 3.3 Require each example set to declare whether each item is authoritative for facts, behavior, style/format, ontology, boundary behavior, or negative behavior.
  - [x] 3.4 Prohibit rejected, quarantined, diagnostic, unknown, or otherwise untrusted artifacts from becoming examples; retain existing source-role and provenance controls.
  - [x] 3.5 Require deterministic candidate eligibility and provenance checks where possible while reserving semantic relevance, comparability, ranking, and diversity selection for bounded model or human judgment.
  - [x] 3.6 Require a bounded example budget based on measured complete-session context, completion reserve, relevance, diversity, recency where applicable, and whole-example preservation.
  - [x] 3.7 Require example omission and context-reduction decisions to be visible in packet manifests and run evidence.
  - [x] 3.8 Define when examples are insufficient or inappropriate, including exact tasks, contaminated or conflicting examples, privacy restrictions, unstable policy, adversarial content, unacceptable anchoring risk, and high-assurance domains requiring additional review.
  - [x] 3.9 Distinguish concise invariant/exception prose from attempts to reimplement demonstrated semantic behavior as exhaustive natural-language rules.

- [x] 4. Govern retained sessions, review scope, and revisions.
  - [x] 4.1 Make one retained session containing stable entity context, demonstrations, candidate, bounded feedback, and repair the default for one coherent semantic decision.
  - [x] 4.2 Require a declared reason for a fresh session, such as independent high-risk review, security/isolation, provider limitations, or empirically demonstrated self-review failure.
  - [x] 4.3 Define self-audit framing that treats prior model output as an untrusted candidate rather than protected authorship and separates hidden reasoning from review evidence.
  - [x] 4.4 Require reviewer authority to be no broader than the goal, entity, artifact set, and decision currently under review.
  - [x] 4.5 Define delta-oriented revision as the default: accepted baseline plus exact request plus necessary factual authority produces a focused change and request-aware audit.
  - [x] 4.6 Require supported explicit operator requests to remain authoritative within policy; reviewer preference may be recorded as non-blocking advice but may not silently retarget, optimize, or remove the requested result.
  - [x] 4.7 Require revision audits to ignore unchanged accepted content unless the requested delta creates a direct contradiction, invalidates an exact invariant, or expands the declared review scope through an explicit policy decision.
  - [x] 4.8 Require every audit/repair loop to have a finite session-step budget, a specific repairable issue, a progress test, and a truthful unable/human branch rather than a changing-feedback retry ratchet.

- [x] 5. Govern semantic intermediates and end-to-end coherence.
  - [x] 5.1 Require every semantic intermediate that filters, summarizes, simplifies, extracts, or classifies source material to declare whether it is lossy and what downstream authority it may hold.
  - [x] 5.2 Prohibit a lossy semantic derivative from silently becoming an exact substitute for its source; require an omission policy, preservation rubric, fallback, audit path, or retained-source access proportional to consequence.
  - [x] 5.3 Require a stage that generates interdependent outputs to consider them together when selection, factual consistency, division of content, or user intent crosses artifact boundaries.
  - [x] 5.4 Require deterministic caching and invalidation for expensive semantic derivatives using source, prompt, model/configuration, and output-contract identity.
  - [x] 5.5 Require run evidence to expose semantic derivative reuse, regeneration, omitted source/example units, and downstream reliance without logging protected contents unnecessarily.

- [x] 6. Separate runtime acceptance from semantic-system evaluation.
  - [x] 6.1 Define the cheapest authoritative runtime gates for exact properties and a bounded semantic review appropriate to the entity's risk.
  - [x] 6.2 Prohibit adding live semantic microstages merely to compensate for missing representative evaluation or an underspecified initial prompt.
  - [x] 6.3 Require versioned golden sets to evaluate first-attempt quality, unsupported content, omission, equivalence, contradiction, reviewer scope, operator-intent preservation, self-review progress, context reduction, and high-assurance exceptions.
  - [x] 6.4 Measure semantic stage designs by first-pass acceptance, calls and tokens per accepted outcome, repair dependence, repeated/changing feedback, prompt growth, false rejection, false acceptance, and human-escalation quality.
  - [x] 6.5 Require post-run recommendations to prefer improving the initial examples, prompt, context, schema, or scope before adding another model stage or validator.
  - [x] 6.6 Require a no-change conclusion when added ceremony lacks evidence of improved outcomes.

- [x] 7. Refactor upstream guidance without creating another mandatory documentation layer.
  - [x] 7.1 Keep `AGENTS.md` concise by adding only universal rules for coherent semantic units, few-shot examples, semantic laundering, scope-bound review, and risk-based independence.
  - [x] 7.2 Revise `references/deterministic_and_semantic_authority.md` to lead with the positive default architecture and label its current claim/citation/independent-review sequence as an optional high-assurance pattern.
  - [x] 7.3 Generalize or relocate resume-specific examples in the universal authority reference so host-remediation history does not masquerade as framework-wide default policy.
  - [x] 7.4 Revise `references/prompt_authoring.md` so one prompt owns one coherent semantic decision and receives minimum sufficient—not merely smallest possible—context.
  - [x] 7.5 Revise the pipeline-design playbook to require semantic-unit, example-strategy, stage-split, lossy-intermediate, review-risk, and operator-authority decisions before stage generation.
  - [x] 7.6 Revise the prompt-building playbook to treat representative demonstrations as a primary design mechanism and to distinguish self-audit, request-aware review, and independent high-assurance review.
  - [x] 7.7 Revise the validation playbook to distinguish exact runtime validation, bounded semantic runtime review, human authority, and offline golden-set evaluation.
  - [x] 7.8 Revise the architecture document and lifecycle so independent semantic review is conditional rather than a universal required state.
  - [x] 7.9 Revise design/generation prompts and package templates with `semantic_unit`, `example_roles`, `example_selection`, `session_boundary`, `review_scope`, `blocking_authority`, `stage_split_justification`, `lossy_intermediate_policy`, and `risk_tier` where each field has a real consumer.
  - [x] 7.10 Preserve a single canonical owner for each normative rule and replace duplicate explanations with routed links.

- [x] 8. Strengthen conformance review and design auditing.
  - [x] 8.1 Require audits to flag semantic laundering, context fragmentation, semantic microstage proliferation, reviewer scope escape, operator-intent demotion, lossy-intermediate authority, prompt accretion, and retry ratchets.
  - [x] 8.2 Require each finding to identify the actual property, claimed verdict, real authority, proxy representation, earliest responsible layer, observed outcome cost, and smallest architectural correction.
  - [x] 8.3 Require audits to distinguish legitimate exact domain rules and justified high-assurance review from ceremonial evidence machinery.
  - [x] 8.4 Require consumer remediation proposals to prefer a coherent few-shot redesign only when representative trusted examples exist and measured risk supports it; do not prescribe LLM use for exact work.
  - [x] 8.5 Keep consumer audits read-only and require an approved host plan before modifying prompts, validators, stages, or runtime behavior.

- [x] 9. Add framework-wide positive and adversarial fixtures.
  - [x] 9.1 Add a sanitized semantic-laundering fixture in which a valid semantic conclusion is rejected because deterministic code misclassifies free-text structure or evidence kind; require the design auditor to reject the architecture rather than broaden the classifier.
  - [x] 9.2 Add a context-fragmentation fixture in which a bounded evidence projection omits supporting material and causes a false unsupported verdict.
  - [x] 9.3 Add a broad-review fixture in which a reviewer overrides a supported requested change and oscillates across repairs; require request-aware scope and non-blocking advice.
  - [x] 9.4 Add a coherent few-shot document-transformation fixture that learns selection, structure, and tone from trusted paired examples while deterministic code validates only exact contracts.
  - [x] 9.5 Add non-document fixtures for semantic classification, summarization, extraction, retrieval/ranking, repair, and code transformation.
  - [x] 9.6 Add high-assurance fixtures proving that independent review and claim-level evidence remain available when justified by consequence and that their deterministic validators do not overclaim semantic proof.
  - [x] 9.7 Add fixtures for contaminated examples, conflicting demonstrations, oversized example sets, lossy summaries, unchanged-baseline revisions, direct contradictions, and unresolved human decisions.
  - [x] 9.8 Verify that prompt lint, routing tests, package/schema validation, and conformance-audit tests load the new doctrine through the smallest canonical context set.

- [x] 10. Publish upstream and enable deliberate consumer adoption.
  - [x] 10.1 Run the complete relevant upstream unit tests, prompt/documentation checks, package/schema validation, Python compilation, plan-index verification, and diff hygiene review.
  - [x] 10.2 Record compatibility effects: existing consumers are not automatically rewritten or failed, but governance-changing adoption should offer a read-only conformance audit and a separate host remediation plan.
  - [x] 10.3 Record verification evidence and a framework journal checkpoint without copying private host content.
  - [x] 10.4 Review and commit the approved framework-only changes directly to upstream `main`, push without a pull request, verify `origin/main`, and record the published revision.
  - [x] 10.5 Archive the completed upstream plan and regenerate plan indexes after all planned work is complete or explicitly closed.
  - [x] 10.6 Document the consumer sequence: update submodule, synthesize without overwrite, audit the existing pipeline, inspect run evidence, create and approve a host remediation plan, implement, evaluate against representative fixtures, and publish host changes separately.

## Success criteria

- An agent designing a semantic pipeline naturally proposes deterministic preparation, one coherent bounded few-shot transformation, scope-bound review/repair, exact deterministic gates, and explicit human escalation instead of a default chain of semantic microservices.
- The exact sentence **“LLMs are few-shot learners.”** appears in canonical governance and is immediately connected to the default pattern of representative past inputs and accepted outputs followed by the new input.
- The upstream design auditor rejects V1-style evidence-kind regex expansion as semantic laundering and recommends correcting the authority boundary rather than enlarging the proxy.
- The upstream design auditor rejects V2-style broad revision review when it overrides an explicit supported request, while accepting a request-aware delta audit with non-blocking broader advice.
- Few-shot demonstrations are first-class, bounded, provenance-aware specifications with declared authority roles and visible omission decisions.
- Independent review, claim-level provenance, and adjudication remain available for justified high-assurance domains without being required for routine reversible transformations.
- Lossy semantic intermediates cannot silently become exact source substitutes.
- Framework-wide fixtures cover document and non-document semantic pipelines and distinguish semantic design quality from exact runtime correctness.
- Existing consumers receive a preservation-safe audit and planning path; no upstream update silently rewrites host-owned pipelines.

## Risks and tradeoffs

- “Few-shot first” could be misread as “use an LLM for everything”; exact-work prohibitions and mechanism-selection fixtures must remain explicit.
- A coherent semantic unit can become too broad; context budgets, declared outputs, review scope, and stage-split criteria must keep it bounded.
- Same-session review can share model blind spots; risk-tier rules must preserve justified independent review.
- Demonstrations can anchor stale or unsupported behavior; example authority, provenance, diversity, invalidation, and evaluation must be explicit.
- Simplifying universal guidance may hide high-assurance needs; optional patterns must remain discoverable without controlling the default route.

## Explicit non-goals

- Do not encode resume, cover-letter, job-posting, title, one-page, or supplemental-question policy as universal framework behavior.
- Do not automatically replace existing consumer pipelines with a V2-style implementation.
- Do not claim few-shot learning guarantees correctness, factuality, independence, or generalization.
- Do not make examples factual authority unless their declared source contract grants that role.
- Do not remove exact security, provenance, schema, resource, render, state, or transactional promotion gates.
- Do not remove independent semantic review or claim-level evidence from domains where a documented risk analysis justifies them.
- Do not treat a model's semantic verdict as deterministic or infallible.
- Do not perform a live consumer model run as part of the upstream governance change without separate host authority.

## Implementation checkpoint — 2026-08-12

- Reconciled the stale source-packet plan without rewriting its published history and promoted this approved plan.
- Added the exact sentence **“LLMs are few-shot learners.”** to `AGENTS.md`, `README.md`, and the canonical authority reference, with the representative past-input/accepted-output plus new-input pattern.
- Replaced the default atomized-review architecture with coherent semantic units, bounded examples, retained sessions, scope-bound revision review, risk-justified independence, explicit lossy-intermediate authority, and golden-set evaluation.
- Added package schema 5 and `coherent-semantic-units-v3`; schemas 1–4 remain compatible legacy inputs but do not claim current governance conformance.
- Added sanitized cross-domain fixtures for semantic laundering, context fragmentation, scope escape, coherent few-shot transformation, contaminated examples, lossy derivatives, code transformation, and justified high-assurance review.
- Verification: 71 upstream unit tests pass; 25 prompts lint; the schema-5 Markdown reference package validates; changed Python compiles. No live model run was performed.
- Published implementation revision: `ab3e1052720b73360998f2f89a39a7e7debee557`, verified on upstream `origin/main` before plan closure.
