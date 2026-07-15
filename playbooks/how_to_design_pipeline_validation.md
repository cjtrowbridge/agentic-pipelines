# Playbook: Design Pipeline Validation

## Use when
Defining acceptance gates, evaluation fixtures, or reviewer/adjudicator contracts.

## Load
Entity/goal contract, protected invariants, `prompts/design/design_validation.md`, validator evidence schema, and prompt-authoring reference when semantic review is required.

## Procedure
1. Convert structural and preservation requirements into deterministic validators with stable codes.
2. Use semantic review only for judgments deterministic code cannot make.
3. Define acceptance per goal/invariant. Treat generic similarity, nonempty output, model confidence, and “looks reasonable” as signals, never sufficient acceptance criteria.
4. Make uncertainty fail closed into repair, quarantine, or human review; do not broaden thresholds merely to improve pass rate.
5. Define disagreement, malformed-review, repair, retry, quarantine, and promotion behavior.
6. Build a golden set covering valid, invalid, ambiguous, adversarial, and unrepairable cases.
7. Measure false accepts and false rejects; label unmeasured quality unknown.

## Output and verification
A validation matrix mapping every invariant to code, semantic review, or explicit human decision, with fixtures and acceptance thresholds.
