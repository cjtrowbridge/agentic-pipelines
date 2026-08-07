---
id: reference.performance
version: 2.0.0
kind: pipeline-running
model_role: analyzer
inputs: [deterministic_run_metrics, execution_trajectory, evaluation_metrics]
output: performance_analysis
---
Compare the first attempt with the terminal trajectory. Separate observations, calculated metrics, hypotheses, unknowns, recommendations, and a justified no-change decision. Attribute friction to the earliest responsible layer and require evidence, benefit, risk, and validation for recommendations. Return strict `performance_analysis` JSON.
