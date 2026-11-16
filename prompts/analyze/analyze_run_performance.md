---
id: analyze.analyze_run_performance
version: 2.1.0
kind: pipeline-running
model_role: analyzer
inputs: [deterministic_run_metrics, execution_trajectory, evaluation_metrics]
output: performance_analysis
---
Compare the first attempt with the accepted or terminal trajectory. Identify repeated or changing feedback, non-progress, prompt growth, exact work sent to inference, suspected false deterministic rejection, and repair-dependent acceptance. Attribute each hypothesis to the earliest responsible input, prompt, context, schema, normalizer, validator-authority, semantic-review, provider, orchestration, or goal layer. Separate observations, calculated metrics, hypotheses, unknowns, and recommendations. Each recommendation must cite evidence, expected impact, regression risk, and a fixture or validation measurement; generalize and compress rather than accreting one-off prompt rules. Permit an explicit no-change conclusion. Consider eliminating work before accelerating it. Recommendations should name relevant budgets, comparable workload/environment, measurement limits, expected benefit and regression checks, with a proposed fix/defer/reject/no-change disposition. Use existing recommendation objects; do not invent measured results. After authorized iteration, distinguish measured benefit from noise and recommend retain/revert/stop. Recommendations remain advisory and grant no execution authority. Return only `performance_analysis`.
