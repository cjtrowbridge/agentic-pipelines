# Playbook: Design Pipeline Validation

## Use when
Defining exact runtime gates, bounded semantic review, human decisions, evaluation fixtures, or reviewer contracts.

## Load
Entity/goal contract, semantic-unit and example strategy, protected invariants, `prompts/design/design_validation.md`, validator evidence schema, `references/deterministic_and_semantic_authority.md`, and prompt-authoring guidance when inference is required.

## Procedure
1. Classify each property as representational, semantic, or human/policy. State what the mechanism actually proves.
2. Use deterministic rejection only for exact declared representations or traceable exact domain rules. IDs, typed labels, free-text classes, similarity, overlap, embeddings, confidence, and handcrafted matching cannot prove meaning.
3. Flag semantic laundering whenever exact control flow converts one of those proxies into a verdict over entailment, relevance, equivalence, materiality, or quality.
4. Apply the cheapest authoritative exact gates before bounded semantic review. Safe representation repair belongs in code; meaning-changing repair belongs in the scoped semantic session.
5. Choose retained self-audit for routine reversible work. Require a consequence or empirical justification for independent or claim-level high-assurance review.
6. For revisions, review the requested delta and direct consequences. Unchanged accepted content is non-blocking unless the delta creates a contradiction or exact violation.
7. Define malformed output, disagreement, finite repair, quarantine, escalation, promotion and rejected-evidence behavior. Review redundant gates and failure ownership using `references/deliverable_driven_simplicity.md`; checks protect requirements, not reviewer preferences.
8. Build versioned golden cases for examples, unsupported content, omission, low-overlap equivalence, high-overlap contradiction, scope escape, operator intent, context reduction, lossy intermediates, and high-assurance exceptions. Measure false accepts/rejects and retry cost.

## Output and verification
An authority matrix plus runtime and offline-evaluation plan. Every gate names property, authority, proof, materiality, evidence, repair owner, and escalation. Reject semantic proxies as verdicts, decorative blocking fields, unmeasured stage proliferation, or weakened criteria.

## Mandatory source and build governance

Follow `playbooks/how_to_govern_source_and_builds.md`: source rules govern maintained
code; failing build gates apply to actual host software builds. Map host actions to
VS Code tasks and the canonical pipeline to launch.json. Do not create hosted workflows.
