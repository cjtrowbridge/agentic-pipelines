# Playbook: Design Pipeline Validation

## Use when
Defining acceptance gates, evaluation fixtures, or reviewer/adjudicator contracts.

## Load
Entity/goal contract, protected invariants, `prompts/design/design_validation.md`, validator evidence schema, `references/deterministic_and_semantic_authority.md`, and prompt-authoring reference when semantic review is required.

## Procedure
1. Classify each required property as representational, semantic, or explicit human/policy judgment.
2. Build an authority matrix declaring mechanism, verdict authority, proof basis, heuristic role, evidence, materiality, repair owner, escalation, and stable code.
3. Use deterministic validators only when failure follows exactly from declared representations or a traceable exact domain rule. Use safe deterministic normalization before model repair.
4. Use bounded semantic review for meaning, entailment, equivalence, relevance, faithful restatement, and qualitative fitness. Treat generic similarity, overlap, embeddings, nonempty output, and model confidence as signals, never proof.
5. Make uncertainty fail closed into semantic repair, quarantine, or human review; do not broaden thresholds merely to improve pass rate.
6. Define disagreement, malformed-review, rejected-candidate persistence, repair, retry, quarantine, and promotion behavior.
7. Build a golden set covering valid, invalid, ambiguous, adversarial, unrepairable, low-overlap-equivalent, and high-overlap-contradictory cases.
8. Measure false accepts and false rejects; label unmeasured quality unknown.

## Output and verification
A machine-checkable authority matrix mapping every invariant to exact code, bounded semantic review, or explicit human decision, with evidence, fixtures, acceptance thresholds, and rejected-artifact behavior.
