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

Observations and metrics above are recorded facts or deterministic calculations. Hypotheses and recommendations are advisory and require the normal approval workflow before changing a pipeline.
