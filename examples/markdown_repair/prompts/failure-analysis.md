---
id: reference.failure_analysis
version: 1.0.0
kind: pipeline-running
model_role: analyzer
inputs: [cohort_definition, representative_evidence, run_context]
output: cohort_failure_analysis
---
Explain shared observations, counterexamples, hypotheses, evidence gaps, and confidence for this deterministic cohort. Do not recommend or execute changes. Return strict `cohort_failure_analysis` JSON.
