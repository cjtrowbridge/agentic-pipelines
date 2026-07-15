---
id: reference.remediation
version: 1.0.0
kind: pipeline-running
model_role: analyzer
inputs: [reviewed_cohort_analysis, pipeline_contract]
output: remediation_proposal
---
Propose the smallest cohort-safe change, regression fixture, sample scope, and retry recommendation. Separate the observed problem from the hypothesized cause. Set authority to `advisory_only`; return strict `remediation_proposal` JSON.
