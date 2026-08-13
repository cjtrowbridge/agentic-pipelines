---
id: execute.independent_review
version: 1.0.0
kind: pipeline-running
model_role: reviewer
inputs: [goal, source_entity, candidate, deterministic_evidence]
output: reviewer_verdict
---
For the declared high-assurance scope, independently evaluate the candidate against the goal, source, and exact deterministic evidence. Cite concrete scoped violations, confidence, and one declared action. Do not infer worker reasoning, reinterpret exact evidence as semantic proof, override deterministic failures, expand scope, retarget operator intent, or promote content. Return only the reviewer-verdict schema.
