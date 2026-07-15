# Playbook: Approve and Retry a Failure Cohort

## Use when
Applying an approved remediation and retrying a precisely identified failure cohort.

## Load
Reviewed remediation proposal, cohort membership/hash, approved repository plan, regression fixtures, pipeline/prompt diff, and operation playbook.

## Procedure
1. Confirm the approved change maps to plan items and the cohort has not drifted.
2. Add/fix regression fixtures before changing the pipeline.
3. Apply the smallest scoped change and run deterministic/lint tests.
4. Test a representative cohort sample and compare golden-set outcomes.
5. Obtain retry approval, then enqueue only the identified cohort with finite limits.
6. Verify unrelated entities were untouched and produce a comparative report.

## Stop conditions
Changed cohort identity, regression, missing approval, unbounded retry, lost evidence, or remediation requiring broader authority.
