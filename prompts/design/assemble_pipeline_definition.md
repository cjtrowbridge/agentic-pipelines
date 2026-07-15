---
id: design.assemble_pipeline_definition
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [approved_goal, entity_contract, invariant_catalog, validation_matrix, prompt_manifest]
output: staged_pipeline_package
---
Assemble a reviewable package containing the versioned pipeline definition, prompt manifest/files, validators, evaluation fixtures, non-secret API sample linkage, scheduler example, evidence/retention policy, rollback notes, and goal traceability. Do not start the pipeline or write credentials. Report missing required inputs instead of inventing them.
