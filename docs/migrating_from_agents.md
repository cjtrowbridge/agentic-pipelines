# Migrating from Agents to Pipelines

Use this only for an existing host that mounted the former framework.

1. Record the current submodule revision, host status, customized files, and rollback command.
2. Replace the old submodule path with `./pipelines`; point the host's concise `AGENTS.md` entrypoint to `./pipelines/AGENTS.md`.
3. Preserve the host's journal and plans. Replace legacy boards with one host-owned root `TODO.md`; do not copy machine events into it.
4. Stage, compare, and explicitly approve generated `pipeline.yaml`, prompts, validators, fixtures, or schemas. Never overwrite customized host artifacts.
5. Remove old downtime tasks. Runtime failures now produce deterministic cohorts, performance reports, and advisory remediation proposals.
6. Copy only `api.sample.yaml`; keep host `api.yaml`, state, artifacts, threads, runs, failures, and reports ignored and local.
7. Convert definitions to schema version 2 with prompt IDs, versions, output contracts, LLM justifications, deterministic validation, finite repair, and safe promotion policy.
8. Run prompt lint, package validation, complete preflight, fake-provider fixtures, and a bounded opt-in Ollama smoke test before processing valuable sources.
9. Roll back by restoring the prior submodule revision and host files; archive schema-v2 evidence rather than opening it with an older prototype.

Manual decisions are required for host prompt synthesis, acceptance criteria, whether each LLM stage is genuinely necessary, promotion enablement, and retrying any failure cohort.
