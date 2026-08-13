---
id: design.audit_pipeline_design
version: 3.0.0
kind: pipeline-building
model_role: designer
inputs: [proposed_pipeline_package, goal_traceability]
output: pipeline_design_audit
---
Audit the proposed coherent semantic unit, example strategy, session boundary, review scope, lossy intermediates, and every stage/gate for authority alignment. Flag semantic laundering, context fragmentation, semantic microstage proliferation, reviewer scope escape, operator-intent demotion, lossy derivatives treated as sources, exact work sent to inference, prompt accretion, retry ratchets, unjustified independent review, unsafe writes, evidence leakage, weak rollback, and unmeasured quality. Distinguish legitimate exact domain rules and risk-justified high-assurance review from ceremonial evidence machinery. For each defect identify the earliest responsible layer and whether examples, initial prompt, context, schema, scope, or stage graph should change first. Do not repair; return only `pipeline_design_audit`.
