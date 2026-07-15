---
id: generate.create_failure_analysis_prompt
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [cohort_contract, evidence_contract, remediation_schema]
output: versioned_failure_analysis_prompt
---
Write a cohort analysis prompt separating observations from hypotheses. Require common cause, likely ownership, feasibility, affected scope, proposed change, regression fixture, confidence, and retry/human recommendation. State that its output is advisory only.
