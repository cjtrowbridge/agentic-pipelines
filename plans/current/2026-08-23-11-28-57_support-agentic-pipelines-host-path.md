---
plan_id: 2026-08-23-11-28-57_support-agentic-pipelines-host-path
title: Support the Agentic Pipelines Host Path
summary: Remove the legacy requirement that hosts mount the framework at ./pipelines and make ./agentic-pipelines the documented and tested canonical path.
status: current
created_at: 2026-08-23-11-28-57
---

# Support the Agentic Pipelines Host Path

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

- [x] 1. Correct the active host-mount contract.
  - [x] 1.1 Replace active documentation, migration guidance, playbooks, templates, examples, and commands that require `./pipelines` with `./agentic-pipelines`.
  - [x] 1.2 Update tests to enforce the canonical `./agentic-pipelines/AGENTS.md` entrypoint and migration path.
  - [x] 1.3 Preserve generic pipeline terminology, Python module/package names, schema identifiers, historical plan/journal text, and the `.agentic-pipelines/` ignored dependency directory.
  - [x] 1.4 Remove the duplicate `worker.max_attempts` key from `pipeline.sample.yaml`, retaining the effective value of `1`.

- [x] 2. Verify and publish the correction.
  - [x] 2.1 Confirm no active product file or test still requires the `./pipelines` host path.
  - [x] 2.2 Run the complete framework test suite successfully.
  - [ ] 2.3 Update the framework journal, archive this plan, regenerate indexes, review the final diff, commit, and push the correction to `origin/main`.

## Completion condition

Hosts may mount the framework at the product-identical `./agentic-pipelines` path using only documented commands, all active path-contract tests enforce that location, all framework tests pass, and the published main branch contains the fix.
