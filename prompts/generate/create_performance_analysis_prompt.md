---
id: generate.create_performance_analysis_prompt
version: 2.0.0
kind: pipeline-building
model_role: designer
inputs: [run_metrics_contract, execution_trajectory_contract, performance_report_schema]
output: versioned_performance_analysis_prompt
---
Write a performance analysis prompt that compares first attempts with accepted or terminal trajectories without fabricating unavailable usage or quality data. Require repeated/changing feedback, non-progress, prompt growth, authority mismatches, exact work sent to inference, earliest responsible layer, evidence, expected impact, regression risk, and a fixture or measurement for each recommendation. Require compression/generalization and an explicit no-change option.
