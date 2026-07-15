---
id: generate.compress_and_check_prompt
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [draft_prompt, required_contract]
output: reviewed_prompt
---
Remove duplicated background, filler, and instructions owned by linked artifacts. Preserve every declared input, invariant, allowed action, output requirement, and stop condition. Report each removal and confirm contract coverage; do not shorten text whose removal changes behavior.
