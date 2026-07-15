# Playbook: Operate and Resume a Pipeline

## Use when
Discovering, dry-running, processing, stopping, resuming, or scheduling entities.

## Load
The host pipeline definition, local-inference playbook if preflight fails, CLI help, and current run summary. Do not load design prompts during ordinary operation.

## Procedure
1. Run definition/API/storage/prompt/schema preflight.
2. Discover entities and inspect counts without source mutation.
3. Dry-run eligible selection, then invoke a bounded entity/time-limited run.
4. On interruption, verify durable state before resuming; do not assume leased work succeeded.
5. Keep scheduler runtime below interval and reject overlapping locks.
6. Review summary, quarantines, and post-run report before promotion or retry.
7. Run `analyze` only when deterministic cohort/metric reports need semantic interpretation; review its advisory output before any change.
8. Use `retry-cohort` only with the reviewed report and exact approved cohort ID.
9. Use `rollback-entity` only as an explicit operator action; it verifies current and backup hashes before restoring the recorded source.

## Stop conditions
Failed preflight, unexplained state migration, active conflicting runner, unsafe paths, missing evidence, or exceeded failure threshold.
