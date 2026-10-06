# Playbook: Create and Maintain a Host Bootstrap

## Use when

Creating, reviewing, checking, or repairing an importing project's setup entrypoint.

## Load

`AGENTS.md`, the host README and dependency/service declarations, existing setup scripts, and `references/host_bootstrap_contract.md`. Load `playbooks/how_to_set_up_pipeline_entrypoints_in_vscode.md` only when wiring interactive entrypoints. `templates/bootstrap/` is a non-installable example.

## Procedure

1. Inventory every declared dependency, configuration prerequisite, and required service in dependency order. Inspect host-owned files and preserve existing setup logic.
2. Keep `scripts/bootstrap.py` as the stable dispatcher to the user-selected `scripts/bootstrap-vN.py`. Add each requirement's read-only probe and authorized idempotent repair to the selected implementation. Follow the linked contract for versioning, external changes, service health, failures, and interruption.
3. Run `python scripts/bootstrap.py --check` on healthy and controlled unhealthy states. Confirm per-check PASS/FAIL, totals, nonzero failure exit, and no changes. Run normal mode twice; verify the second run repairs nothing. Test failed repair and interruption.
4. Route the host's tasks, primary launch action, and automation through the same bootstrap boundary before pipeline work. Record supported platforms, external targets, privileges, and verification in the host README.
5. When a new failure is diagnosed, add its bounded probe and safe repair to the current version, test both modes, and apply through the stable entrypoint. Create a new version only when the user chooses.

## Outputs and stop conditions

Produce the host-owned entrypoint, current versioned implementation, requirement inventory, and check/apply evidence. Stop on absent host plan authority, uncertain repair scope, host-data overwrite, unapproved privilege or machine-wide changes, or a check mode that mutates state.
