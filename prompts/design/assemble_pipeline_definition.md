---
id: design.assemble_pipeline_definition
version: 3.0.0
kind: pipeline-building
model_role: designer
inputs: [approved_goal, entity_contract, invariant_catalog, validation_matrix, prompt_manifest]
output: staged_pipeline_package
---
Assemble a reviewable package containing governance version; coherent semantic-unit declaration; example roles/selection/budget; retained-session and review scope; blocking authority and risk tier; stage-split justification; lossy-intermediate policy; pipeline definition; authority matrix; prompts; exact validators; golden fixtures; non-secret API sample; reports and rejected-evidence contract; rollback; exceptions; and goal traceability. Every declared field must have a validator, runtime/reporting consumer, or explicit design-audit consumer. Do not start the pipeline, write credentials, or mutate host runtime data. Report missing inputs instead of inventing them.
