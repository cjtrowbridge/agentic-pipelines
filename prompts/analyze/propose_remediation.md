---
id: analyze.propose_remediation
version: 1.0.0
kind: pipeline-running
model_role: analyzer
inputs: [reviewed_cohort_analysis, pipeline_contract]
output: remediation_proposal
---
Propose the smallest cohort-scoped pipeline change, its expected effect, risks, regression fixture, sample validation, and retry recommendation. State assumptions and confidence. This proposal is advisory and cannot edit the pipeline or enqueue work. Return only the remediation-proposal schema.
