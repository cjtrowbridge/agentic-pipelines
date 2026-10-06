# Playbook: Set Up Host VS Code Pipeline Entrypoints

## Use when

Creating or reviewing an importing project's host-owned interactive VS Code entrypoints.

## Load

`AGENTS.md`; host README, pipeline definition, CLI help, VS Code files, native scripts, `scripts/bootstrap.py`, its selected version, and dependencies. Load `playbooks/how_to_create_and_maintain_host_bootstrap.md` if bootstrap is absent or unhealthy; load `templates/vscode/` as needed.

Do not infer the host's entrypoints from the framework reference CLI. Inventory and configuration checks are deterministic; do not use an LLM.

## Procedure

1. Record every host-declared interactive entrypoint, its required inputs, and whether it is ordinary, mutating, or recovery-oriented.
2. Preserve existing VS Code files and native scripts. If the inventory or main action is ambiguous, obtain a host decision.
3. Select exactly one ordinary, non-recovery entrypoint as the primary play action.
4. Each supported platform needs a native wrapper that locates Python, calls `scripts/bootstrap.py` once, then runs the pipeline only on success and preserves its exit status. The versioned bootstrap owns requirements. Do not invent a package manager, silently elevate, alter system Python, or assume dependency layouts.
5. Map every entrypoint to one visible `tasks.json` task. Prefer process commands and argument arrays, prompt for required operator values, use platform overrides where needed, and run visibly in the foreground terminal.
6. Configure the primary `launch.json` action to enter the same native wrapper, run `scripts/bootstrap.py` once, and execute the main operation exactly once. Never pair a full-operation pre-launch task with a launch command that repeats it.
7. Create missing files only from reviewed host-specific inputs. For existing files, propose an explicit merge; never replace the file from a framework example.
8. Validate syntax, task coverage, inputs, arguments, platform dispatch, foreground visibility, one primary action, bootstrap-before-pipeline order, and smoke checks on claimed platforms. Verify read-only `--check` and that wrapper failures prevent pipeline execution.

Direct CLI, CI, scheduler, and other automation entrypoints remain supported.

## Outputs and stop conditions

Produce the reviewed inventory, host-owned task mapping, selected primary action, native-script mapping, and validation evidence. Stop for ambiguity, unsupported platforms, unsafe prerequisite behavior, unapproved privilege or machine-wide installation, uncertain paths, credentials, conflicts, or proposed host-file overwrite.
