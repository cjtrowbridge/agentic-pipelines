---
id: design.identify_invariants
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [pipeline_goal_report, entity_contract, representative_entities]
output: invariant_catalog
---
List what must be preserved, what may change, and what must never appear. For each invariant, name deterministic evidence when possible; otherwise label the needed semantic or human judgment. Include promotion and rollback safety. Output the invariant catalog schema.
