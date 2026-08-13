# Playbook: Design a Pipeline

## Use when
Turning a user goal into an entity-oriented pipeline proposal or package.

## Load
`prompts/design/` in its README order, the pipeline-design templates, `references/deterministic_and_semantic_authority.md`, `references/run_evidence_and_continuous_improvement.md`, and only relevant repository evidence and trusted representative examples.

## Procedure
1. Separate user requirements, repository facts, inferences, and unresolved decisions. Define entity identity, source snapshot, goal, allowed changes, operator authority, and protected invariants.
2. Classify every property as representational, semantic, or human/policy. Assign only an authority that can establish that property.
3. For semantic work, define the smallest coherent decision before drawing stages. “Narrow” bounds goal and authority; it does not atomize meaning. Declare any split's observed failure, isolation/risk/context/reuse reason, cost, and evaluation evidence.
4. Inventory trusted past input/accepted-output pairs. Declare example roles, provenance, selection, whole-session budget, omissions, and why examples are sufficient or inappropriate. Never use rejected or untrusted artifacts.
5. Design one retained semantic session by default: stable context and demonstrations, candidate, scope-bound audit, and finite progress-tested repair. Fresh-session independent or claim-level review requires a consequence-based justification.
6. For revisions, use accepted baseline plus exact request and necessary factual authority. Audit the delta and direct consequences; keep broader reviewer preference advisory.
7. Declare every lossy semantic derivative, its limited authority, preservation/omission policy, cache identity, fallback, and downstream source access.
8. Put exact preparation, schema/resource/render gates, state, evidence, promotion, and rollback in deterministic code. Never provide PDFs directly to a model; supply the linked validated derived text—not the PDF.
9. Define golden fixtures and efficiency measures before adding semantic microstages. Audit the staged design and request material user decisions.

## Output and verification
A reviewable package tracing every goal to an authoritative mechanism, coherent semantic unit, example strategy, review scope, exact gates, evidence, fixtures, and escalation. Reject semantic laundering, context fragmentation, unjustified stage splits, lossy source substitution, scope escape, retry ratchets, unsafe writes, or unbounded cycles.
