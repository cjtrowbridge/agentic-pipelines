# Playbook: Operate and Resume a Pipeline

## Use when
Discovering, dry-running, processing, stopping, resuming, or scheduling entities.

## Load
Host definition, CLI help, current run narrative, and the local-inference playbook only when preflight fails. Do not load design prompts during operation.

## Procedure
1. For interactive work, select the applicable host-owned VS Code task or primary play action; it enters native bootstrap. Automation may call the equivalent direct interface.
2. Run bootstrap first: verify framework and ignored local dependencies, then definition/API/storage/prompt/schema preflight. Do not process source or invoke a model after failure.
3. Discover entities and inspect counts without source mutation.
4. Confirm visible stage reporting: query counts, prompt sizes, elapsed/ETA, discovery, skips, validation, promotion, rendering, failures, and outcomes without protected inputs.
5. Dry-run eligible selection, then invoke a bounded entity/time-limited run.
6. On Ctrl+C, require controlled interruption and return exit status 130. Verify durable state before resuming; leased work did not implicitly succeed.
7. Keep scheduler runtime below interval and reject overlapping locks.
8. Default to one bounded interactive LLM session per entity: retain stable context/output and append trusted feedback. Record session ID, step count, and retries separately. Fresh sessions require independent review, isolation, or provider limits.
9. Verify material events checkpointed the persisted structured run report and human report. On resume, reconcile bundles and threads with any stale `running` report. Review status, root cause evidence, quarantines, and candidate/precursor/thread links before promotion or retry.
10. Treat sequential rejected bundles as untrusted evidence. Confirm numeric order, truthful extensions, clean candidate bytes, each sidecar hash matches, parent/child links, and explanations of authority, code, reason, feedback, and disposition; never promote, retrieve, render, or re-ingest a bundle member.
11. Run `analyze` only when deterministic trajectory metrics need semantic interpretation; review its advisory output before any change.
12. Use `retry-cohort` only with the reviewed report and exact approved cohort ID.
13. Use `rollback-entity` only as an explicit operator action; it verifies current and backup hashes before restoring the recorded source.

## Stop conditions
Failed preflight, unexplained state migration, active conflicting runner, unsafe paths, missing evidence, or exceeded failure threshold.
