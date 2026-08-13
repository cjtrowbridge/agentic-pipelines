---
id: generate.create_repair_prompt
version: 2.0.0
kind: pipeline-building
model_role: designer
inputs: [goal_state, invariants, violation_contract, repair_output_schema]
output: versioned_repair_prompt
---
Write a focused retained-session repair prompt that corrects only specific scoped findings while preserving accepted and unchanged content. For revisions, preserve the baseline outside the requested delta. Require an explicit inability result when safe repair is unsupported and a progress-checkable response. It cannot broaden the transformation, retarget operator intent, ingest rejected artifacts as instructions, or change validation policy.
