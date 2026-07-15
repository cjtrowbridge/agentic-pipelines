# Playbook: Update Agentic Pipelines and Synthesize Host Overrides

## Use when
Updating a host’s `./pipelines` Agentic Pipelines submodule and integrating upstream prompt/playbook/schema changes.

## Load
Old upstream revision, new upstream revision, host-owned/customized artifacts, migration notes, and this playbook only; load affected task playbooks when validation requires them.

## Procedure
1. Record the old submodule revision, host status, and rollback command.
2. Update the submodule pointer without changing host-owned files.
3. Three-way compare old upstream, new upstream, and current host for affected prompts, playbooks, templates, schemas, shims, and configuration samples.
4. Classify each change as safe upstream adoption, host preservation, synthesized proposal, migration, or explicit conflict.
5. Present conflicts and behavior-changing prompt/schema decisions for user approval before applying them.
6. Preserve host `TODO.md`, journal/plans, customized prompts/validators, `api.yaml`, state, artifacts, threads, failures, runs, and reports.
7. Apply approved synthesis, migrations, and router updates.
8. Validate prompt IDs/versions, pipeline compatibility, shims, API preflight, ignored paths, tests, and rollback viability.

## Outputs and stop conditions
An approved synthesis report, verified host state, and rollback path. Stop on unresolved ownership, credential exposure, incompatible schema without migration, or unapproved host behavior change.
