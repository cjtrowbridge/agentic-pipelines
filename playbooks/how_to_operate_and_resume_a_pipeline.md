# Playbook: Operate and Resume a Pipeline

## Use when
Discovering, dry-running, processing, stopping, resuming, or scheduling entities.

## Load
The host pipeline definition, local-inference playbook if preflight fails, CLI help, and current run summary. Do not load design prompts during ordinary operation.

## Procedure
1. For interactive work, select the applicable host-owned VS Code task or primary play action; it must enter the host's native bootstrap. Automation may call the equivalent direct interface.
2. Run bootstrap first: verify the framework, prepare declared dependencies only in ignored host-local directories, then run definition/API/storage/prompt/schema preflight. Do not process source or invoke a model when bootstrap fails.
3. Discover entities and inspect counts without source mutation.
4. Confirm visible reporting for each material stage, including required model query counts, prompt sizes, elapsed time/ETA, discovery, skips, validation, promotion, rendering, failures, and final outcomes without protected inputs.
5. Dry-run eligible selection, then invoke a bounded entity/time-limited run.
6. On Ctrl+C, require the runner to report a controlled interruption and return exit status 130. Verify durable state before resuming; do not assume leased work succeeded.
7. Keep scheduler runtime below interval and reject overlapping locks.
8. Run each entity as one bounded interactive LLM session by default: retain stable context and prior output, then append concise trusted review feedback. Record session ID, step count, and retries separately. A fresh session needs a declared compelling reason: independent review, security/isolation, or provider limits.
9. Review the persisted structured run report, summary, quarantines, and post-run report before promotion or retry. Identify every session step and retry/rejection with its concise cause and evidence path so remediation targets the root cause.
10. Run `analyze` only when deterministic cohort/metric reports need semantic interpretation; review its advisory output before any change.
11. Use `retry-cohort` only with the reviewed report and exact approved cohort ID.
12. Use `rollback-entity` only as an explicit operator action; it verifies current and backup hashes before restoring the recorded source.

## Stop conditions
Failed preflight, unexplained state migration, active conflicting runner, unsafe paths, missing evidence, or exceeded failure threshold.
