# Playbook: Bootstrap Agentic Pipelines into a Host Repository

## Use when
Adding this framework to a host for the first time.

## Load
`AGENTS.md`, host ownership guidance in `docs/prompt_first_product_model.md`, the framework `api.sample.yaml`, `pipeline.sample.yaml`, and the host's existing instruction/configuration files.

## Procedure
1. Inspect the host and obtain approval for the submodule, target path, and planned host files.
2. Add/initialize the framework at `./pipelines`.
3. Create only missing non-secret host scaffolding: root shim, `TODO.md`, pipeline definition, prompts, plans/journal, ignored runtime directories, and a tracked root `api.sample.yaml` copied from the framework sample. Do not create `api.yaml` or infer its values.
4. If a target exists, produce synthesis decisions; never overwrite host-owned content.
5. Point host shims to `./pipelines/AGENTS.md` while retaining host-specific routing context.
6. Ensure `.gitignore` excludes `api.yaml`, state, artifacts, threads, failures, runs, and generated reports.
7. Ask the operator to copy the host-root `api.sample.yaml` to ignored `api.yaml` and configure local values through the local-inference playbook; do not create or infer them.
8. Validate paths, router resolution, the staged package with `scripts/validate_pipeline_package.py`, API/pipeline preflight, plan indexes, and Git exclusions. Do not start processing.

## Outputs and stop conditions
A non-running host scaffold plus synthesis/verification report. The host root contains a tracked `api.sample.yaml`; only `api.yaml` is ignored. Stop on unapproved overwrite, dirty conflict, credential exposure, unsafe runtime path, or ambiguous host ownership.


