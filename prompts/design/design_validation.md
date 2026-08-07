---
id: design.design_validation
version: 2.0.0
kind: pipeline-building
model_role: designer
inputs: [entity_contract, invariant_catalog, representative_entities]
output: validation_matrix
---
Map every goal and invariant to an authority record declaring property class, mechanism, verdict authority, proof basis, heuristic role, exact acceptance, evidence, materiality, repair owner, escalation, and stable failure code. Deterministic rejection requires an explicit representation or traceable exact domain rule. Similarity, overlap, embeddings, keywords, confidence, and handcrafted matching may route semantic review but cannot prove meaning. Use bounded semantic or human judgment for entailment, equivalence, relevance, faithful restatement, and quality. Declare rejected-candidate persistence and report evidence for every failure path. Include malformed/disagreement routing, finite repair/retry, quarantine, and adversarial golden fixtures. Return only `validation_matrix`.
