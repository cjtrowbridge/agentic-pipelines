---
id: execute.self_review
version: 1.0.0
kind: pipeline-running
model_role: self_reviewer
inputs: [goal, source_entity, candidate, invariants]
output: reviewer_verdict
---
Check your candidate against the goal and invariants. Identify specific violations and recommend submit or repair. This is non-independent evidence and cannot accept, promote, or relax an invariant. Return only the reviewer-verdict schema.
