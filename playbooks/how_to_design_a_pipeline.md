# Playbook: Design a Pipeline

## Use when
Turning a user goal into an entity-oriented pipeline proposal or package.

## Load
`prompts/design/` in this order: understand goal, define entity contract, identify invariants, design stages/validation, audit design, assemble definition. Load the pipeline-design output template and only repository evidence relevant to the target data.

## Procedure
1. Separate stated requirements, discovered facts, inferences, and unresolved user decisions.
2. Define entity identity, source snapshot, goal state, allowed changes, and protected invariants.
3. For every transformation or decision, try a trusted tool, parser/query/script, and deterministic routing rule before proposing inference.
4. Permit an LLM stage only when its required semantic work cannot be performed reliably by deterministic logic; record that justification and minimize its inputs and authority.
5. Define specific deterministic gates around inference, then finite repair, quarantine, and human-decision paths. Never compensate for uncertain model behavior with broad acceptance criteria.
6. Order preconditions and validators so impossible or unsafe entities fail before consuming inference, while valid entities pass only with requirement-specific evidence.
7. Define evidence, retention, promotion, rollback, scheduling, and post-run analysis.
8. Produce a staged package and trace every goal/invariant to a stage and verification.
9. Audit the design; request user decisions for material unresolved choices before integration.

## Output and verification
A reviewable pipeline package and design traceability report. Reject unnecessary model calls, unmapped goals, broad proxy acceptance, destructive unvalidated writes, missing terminal states, or undeclared model authority.
