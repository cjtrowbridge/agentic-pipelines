---
id: generate.create_repair_prompt
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [goal_state, invariants, violation_contract, repair_output_schema]
output: versioned_repair_prompt
---
Write a focused repair prompt that corrects only supplied violations while preserving already-valid content. Require an explicit inability result when safe repair is unsupported. It cannot broaden the transformation or change validation policy.
