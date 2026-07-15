---
id: design.design_validation
version: 1.1.0
kind: pipeline-building
model_role: designer
inputs: [entity_contract, invariant_catalog, representative_entities]
output: validation_matrix
---
Map every goal and invariant to a specific deterministic validator, narrowly justified semantic review, or explicit human decision. Generic similarity, nonempty output, and model confidence are signals, not sufficient acceptance. Define stable codes, evidence, calibrated thresholds, malformed-output and disagreement routing, finite repair/retry, quarantine, and golden fixtures. Return only `validation_matrix`.
