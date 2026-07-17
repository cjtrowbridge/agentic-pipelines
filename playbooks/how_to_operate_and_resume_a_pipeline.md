# Playbook: Operate and Resume a Pipeline

## Use when
Discovering, dry-running, processing, stopping, resuming, or scheduling entities.

## Load
The host pipeline definition, local-inference playbook if preflight fails, CLI help, and current run summary. Do not load design prompts during ordinary operation.

## Procedure
1. Run bootstrap first: verify the framework is available and install declared requirements and declared local runtime dependencies only into ignored host-local directories. Then run definition/API/storage/prompt/schema preflight. Do not process source or invoke a model when bootstrap fails.
2. Discover entities and inspect counts without source mutation.
3. Confirm the runner will visibly report each material stage. Model-backed stages must show completed/remaining query counts, static-template and assembled-request sizes, elapsed time, and an elapsed-time-based ETA; discovery, skips, validation, promotion, rendering, failures, and final outcomes must also be visible without printing credentials or protected inputs.
4. Dry-run eligible selection, then invoke a bounded entity/time-limited run.
5. On Ctrl+C, require the runner to report a controlled interruption and return exit status 130. Verify durable state before resuming; do not assume leased work succeeded.
6. Keep scheduler runtime below interval and reject overlapping locks.
7. Run each entity as one bounded interactive LLM session by default: retain stable context and prior output, then append concise trusted review feedback. Record session ID, step count, and retries separately. A fresh session needs a declared compelling reason: independent review, security/isolation, or provider limits.
8. Review the persisted structured run report, summary, quarantines, and post-run report before promotion or retry. Identify every session step and retry/rejection with its concise cause and evidence path so remediation targets the root cause.
9. Run `analyze` only when deterministic cohort/metric reports need semantic interpretation; review its advisory output before any change.
10. Use `retry-cohort` only with the reviewed report and exact approved cohort ID.
11. Use `rollback-entity` only as an explicit operator action; it verifies current and backup hashes before restoring the recorded source.

## Stop conditions
Failed preflight, unexplained state migration, active conflicting runner, unsafe paths, missing evidence, or exceeded failure threshold.
