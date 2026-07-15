---
id: generate.create_reviewer_prompt
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [goal_state, invariants, validation_evidence_schema, reviewer_output_schema]
output: versioned_reviewer_prompt
---
Write a concise independent reviewer prompt receiving source, candidate, goal, and deterministic evidence—not worker hidden reasoning. Require verdict, confidence, violations, evidence, and recommended action. It cannot relax policy or promote output.
