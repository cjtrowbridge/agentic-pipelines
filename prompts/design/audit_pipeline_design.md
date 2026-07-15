---
id: design.audit_pipeline_design
version: 1.1.0
kind: pipeline-building
model_role: designer
inputs: [proposed_pipeline_package, goal_traceability]
output: pipeline_design_audit
---
Audit for unnecessary LLM calls, excessive model context or authority, broad proxy acceptance, unmapped goals, unsafe writes, missing evidence, circular review, unbounded retry, non-idempotent stages, weak rollback, missing terminal states, and unmeasured quality. Separate defects, risks, inferences, and user decisions. Do not repair; return only `pipeline_design_audit`.
