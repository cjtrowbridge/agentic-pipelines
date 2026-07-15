---
id: generate.create_self_review_prompt
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [goal_state, invariants, reviewer_output_schema]
output: versioned_self_review_prompt
---
Write a concise worker self-check prompt for goal/invariant violations and submit-versus-repair recommendation. Label its evidence non-independent and grant no acceptance, promotion, or policy authority.
