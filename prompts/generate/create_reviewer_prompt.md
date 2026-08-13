---
id: generate.create_reviewer_prompt
version: 2.0.0
kind: pipeline-building
model_role: designer
inputs: [goal_state, invariants, validation_evidence_schema, reviewer_output_schema]
output: versioned_reviewer_prompt
---
Write a concise reviewer prompt only after receiving its risk justification and exact review scope. For routine reversible work, create a retained-session audit that treats prior output as an untrusted candidate. For justified high-assurance independence, use a fresh session receiving source, candidate, goal, and exact evidence—not hidden reasoning. A revision reviewer judges only the requested delta and direct consequences; supported operator intent is blocking within policy and broader preference is advice. Require actionable scoped findings and stop behavior. It cannot relax policy, retarget accepted work, or promote output.
