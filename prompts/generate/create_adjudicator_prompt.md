---
id: generate.create_adjudicator_prompt
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [goal_state, stage_evidence, adjudication_output_schema]
output: versioned_adjudicator_prompt
---
Write an adjudicator prompt that selects only declared actions from conflicting validated evidence. Require reason, cited evidence, confidence, and action. It cannot invent a new action, bypass a failed deterministic invariant, or promote content directly.
