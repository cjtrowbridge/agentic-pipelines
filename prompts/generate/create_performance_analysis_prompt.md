---
id: generate.create_performance_analysis_prompt
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [run_metrics_contract, performance_report_schema]
output: versioned_performance_analysis_prompt
---
Write a performance analysis prompt that interprets supplied deterministic metrics without fabricating unavailable usage or quality data. Require bottlenecks, evidence, confidence, expected impact, risks, and measurement needed to validate each recommendation.
