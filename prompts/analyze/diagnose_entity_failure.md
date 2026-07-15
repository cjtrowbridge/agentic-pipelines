---
id: analyze.diagnose_entity_failure
version: 1.0.0
kind: pipeline-running
model_role: analyzer
inputs: [entity_evidence_summary]
output: entity_failure_analysis
---
Identify the first failing stage and separate observed facts from hypotheses. Classify likely ownership, cite evidence, state confidence/unknowns, and recommend one declared next action. Do not change state or retry the entity. Return only the entity-failure-analysis schema.
