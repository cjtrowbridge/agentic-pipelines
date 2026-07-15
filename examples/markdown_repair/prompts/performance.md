---
id: reference.performance
version: 1.0.0
kind: pipeline-running
model_role: analyzer
inputs: [deterministic_run_metrics, evaluation_metrics]
output: performance_analysis
---
Interpret supplied metrics without changing them. Separate observed and calculated metrics, hypotheses, unknowns, and bounded recommendations. Label unavailable quality measurements unknown; return strict `performance_analysis` JSON.
