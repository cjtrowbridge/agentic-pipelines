---
id: generate.create_self_review_prompt
version: 2.0.0
kind: pipeline-building
model_role: designer
inputs: [goal_state, invariants, reviewer_output_schema]
output: versioned_self_review_prompt
---
Write a concise retained-session audit that instructs the model to treat its prior output as an untrusted candidate. Limit review to the coherent goal or exact requested delta, require specific repairable findings, and make broader preference non-blocking advice. Label the evidence non-independent; grant no policy, promotion, or scope-expansion authority; stop on inability or non-progress.
