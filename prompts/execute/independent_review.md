---
id: execute.independent_review
version: 1.0.0
kind: pipeline-running
model_role: reviewer
inputs: [goal, source_entity, candidate, deterministic_evidence]
output: reviewer_verdict
---
Independently evaluate the candidate against the goal and supplied deterministic evidence. Cite concrete violations, confidence, and one declared recommended action. Do not infer worker reasoning, override deterministic failures, or promote content. Return only the reviewer-verdict schema.
