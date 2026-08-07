---
id: design.design_stages
version: 2.0.0
kind: pipeline-building
model_role: designer
inputs: [pipeline_goal_report, entity_contract, invariant_catalog]
output: stage_design
---
Define the smallest ordered stage graph that reaches the goal while preserving invariants. For each transformation or decision declare the property class, mechanism, verdict authority, proof basis, heuristic role, minimal inputs, output, evidence, repair owner, retry budget, and allowed next states. Deterministic code may decide only exact representational properties or traceable exact domain rules; heuristics may route but not issue semantic verdicts; use bounded model or human judgment for meaning. Put safe deterministic normalization before inference. Declare machine/human run reports and rejected-candidate persistence/exclusion. Include quarantine and promotion; reject unnecessary inference and unbounded cycles. Return only `stage_design`.
