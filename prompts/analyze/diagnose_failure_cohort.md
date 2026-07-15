---
id: analyze.diagnose_failure_cohort
version: 1.0.0
kind: pipeline-running
model_role: analyzer
inputs: [cohort_definition, representative_evidence, run_context]
output: cohort_failure_analysis
---
Explain what the cohort shares, likely cause/ownership, feasibility, confidence, counterexamples, and evidence gaps. Distinguish deterministic observations from hypotheses. Recommend no execution; return only the cohort-failure-analysis schema.
