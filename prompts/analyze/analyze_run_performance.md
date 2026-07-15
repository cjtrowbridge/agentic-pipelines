---
id: analyze.analyze_run_performance
version: 1.0.0
kind: pipeline-running
model_role: analyzer
inputs: [deterministic_run_metrics, evaluation_metrics]
output: performance_analysis
---
Identify bottlenecks and improvement candidates using only supplied metrics. Label unavailable usage or quality measures unknown. For each recommendation cite evidence, confidence, expected impact, risk, and validation measurement. Return only the performance-analysis schema.
