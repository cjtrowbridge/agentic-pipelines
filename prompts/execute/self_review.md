---
id: execute.self_review
version: 1.0.0
kind: pipeline-running
model_role: self_reviewer
inputs: [goal, source_entity, candidate, invariants]
output: reviewer_verdict
---
Treat your prior output as an untrusted candidate. Check only the declared coherent goal or requested delta and its direct consequences. Identify specific repairable violations; keep broader preferences advisory. This is non-independent evidence and cannot expand scope, accept, promote, or relax an invariant. Return only the reviewer-verdict schema.
