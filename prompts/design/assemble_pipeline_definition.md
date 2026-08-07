---
id: design.assemble_pipeline_definition
version: 2.0.0
kind: pipeline-building
model_role: designer
inputs: [approved_goal, entity_contract, invariant_catalog, validation_matrix, prompt_manifest]
output: staged_pipeline_package
---
Assemble a reviewable package containing the governance version, versioned pipeline definition, authority matrix, prompt manifest/files, validators, evaluation fixtures, non-secret API sample linkage, scheduler example, machine/human run-report contract, rejected-candidate naming/trailer/retention/exclusions, rollback notes, accepted exceptions, and goal traceability. Do not start the pipeline, write credentials, or mutate host runtime data. Report missing required inputs instead of inventing them.
