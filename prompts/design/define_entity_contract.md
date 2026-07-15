---
id: design.define_entity_contract
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [pipeline_goal_report, source_evidence]
output: entity_contract
---
Define one stable unit of work: identity key, discovery rule, immutable source snapshot, revision trigger, goal state, allowed outputs, terminal dispositions, and sensitive-data classification. Flag identities that can collide or change silently. Output only the entity contract schema.
