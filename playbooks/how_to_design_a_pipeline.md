# Playbook: Design a Pipeline

## Use when
Turning a user goal into an entity-oriented pipeline proposal or package.

## Load
`prompts/design/` in this order: understand goal, define entity contract, identify invariants, design stages/validation, audit design, assemble definition. Load the pipeline-design output template, `references/deterministic_and_semantic_authority.md`, `references/run_evidence_and_continuous_improvement.md`, and only repository evidence relevant to the target data.

## Procedure
1. Separate stated requirements, discovered facts, inferences, and unresolved user decisions.
2. Define entity identity, source snapshot, goal state, allowed changes, and protected invariants.
3. For every transformation, decision, gate, and repair, declare the property, property class, mechanism, verdict authority, proof basis, heuristic role, evidence, repair owner, and escalation. A deterministic mechanism is sufficient only when it establishes the actual property exactly.
4. Permit an LLM stage only for bounded semantic work that exact mechanisms cannot perform. Heuristics may route or escalate but may not accept or reject semantic correctness. Convert PDF sources to linked Markdown/text derivatives deterministically before the stage, and make the derived text—not the PDF—the declared prompt input.
5. Put safe fact-preserving canonicalization before inference. Define exact gates around semantic stages, then finite semantic repair, quarantine, and human-decision paths. Never compensate for uncertain behavior with broad proxies or return exact formatting defects to a model unnecessarily.
6. Order preconditions and validators so impossible or unsafe entities fail before consuming inference, while valid entities pass only with requirement-specific evidence.
7. Define machine and human run reports, rejected-candidate naming/trailers/exclusions/retention, evidence links, truthful execution and learning statuses, promotion, rollback, scheduling, and post-run analysis.
8. Produce a staged package and trace every goal/invariant to a stage and verification.
9. Audit the design; request user decisions for material unresolved choices before integration.

## Output and verification
A reviewable pipeline package and design traceability report. Reject unnecessary model calls, deterministic semantic overreach, exact repairs sent to inference, unmapped goals, destructive unvalidated writes, missing terminal evidence, discardable rejected candidates, or undeclared authority.
