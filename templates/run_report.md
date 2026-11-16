# Pipeline Run {{ run_id }}

- Pipeline: `{{ pipeline_id }}`
- Governance: `{{ governance_version }}`
- Execution status: `{{ execution_status }}`
- Learning status: `{{ learning_status }}`
- Started: `{{ started_at }}`
- Finished: `{{ finished_at }}`
- Machine report: `{{ machine_report_path }}`

## Outcome summary

{{ outcome_summary }}

## Attempts and retries

{{ attempt_table }}

## Semantic design trajectory

{{ semantic_unit_examples_sessions_derivatives_review_scope_and_operator_requests }}

## Rejected artifacts

{{ rejected_artifact_links }}

## Observations

{{ observations }}

## Deterministic metrics

{{ metrics }}

## Root-cause hypotheses

{{ hypotheses }}

## Recommendations

{{ recommendations_or_no_change }}

For material findings, record fix/defer/reject/no-change, rationale and governing plan or requirement. Selected improvements record baseline, expected benefit, regression checks and comparison method. After authorized execution, link comparable results, limitations and retain/revert/defer disposition. Do not report a proposed experiment as a measured improvement. Stop when acceptance and relevant budgets are met.

Observations and metrics above are recorded facts or deterministic calculations. Hypotheses and recommendations are advisory and require the normal approval workflow before changing a pipeline.
