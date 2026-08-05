---
plan_id: 2026-08-04-18-11-42_vscode-pipeline-entrypoints
title: Establish Bootstrap-Backed VS Code Pipeline Entrypoints
summary: Require every pipeline entrypoint to be a visible VS Code task, expose the designated main entrypoint through the Run/Debug play button, and route every invocation through a platform-native bootstrap wrapper into Python.
status: future
created_at: 2026-08-04-18-11-42
---

# Establish Bootstrap-Backed VS Code Pipeline Entrypoints

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

## Outcome

Every host pipeline has an intentionally maintained, cross-platform interactive operator surface:

```text
every declared pipeline entrypoint
  -> named .vscode/tasks.json task
  -> platform-native bootstrap wrapper (.ps1 on Windows; .sh on Linux/macOS)
  -> visible prerequisite verification/setup and host-local dependency preparation
  -> the selected Python pipeline entrypoint, using the prepared environment

designated main entrypoint
  -> its required named task
  -> exactly one primary .vscode/launch.json configuration
  -> VS Code Run/Debug play button without executing the operation twice
```

The framework will provide the policy, playbook, templates, wrappers, integration mechanism, and tests needed to make that contract real. The task and launch files are host-owned after creation; framework bootstrap or update must never overwrite customized VS Code configuration, credentials, state, artifacts, threads, reports, prompts, plans, journal, or `TODO.md`.

## Decisions and acceptance constraints

- An entrypoint is every pipeline operation exposed to an operator by the applicable Python CLI, including standard operations (`preflight`, `discover`, `run`, `inspect-entity`, `report`, `analyze`, `retry-cohort`, and `rollback-entity`) plus any host-declared operation. No entrypoint may exist only as undocumented flags or a README command.
- Every entrypoint has one visible, accurately named task. Tasks with required identifiers or paths use VS Code inputs rather than requiring the user to edit JSON or reconstruct CLI syntax.
- One host-designated main entrypoint is both a task and the only primary launch configuration. It is the normal operator action; recovery/destructive operations remain visible tasks but are never made the default launch action.
- Task and launch execution must reach a native wrapper before reaching the pipeline Python command. The wrappers are the authority for bootstrap and must invoke Python only after success.
- Bootstrap is visible in the integrated terminal: discovery, current-versus-install status, installation intent, environment location, selected Python, requested operation, errors, Ctrl+C handling, and final exit status must be operator-visible without exposing credentials or protected content.
- Bootstrap must verify prerequisites first, and only install a missing prerequisite when a supported installer, required network access, and required privilege are available. It must print the exact next action and fail safely rather than guessing on unsupported/offline/permission-denied systems.
- Python packages and optional runtime dependencies install only beneath an ignored host-local root; bootstrap never changes system Python packages. Machine-wide Python or OS-package installation is explicit, visible, and limited to a declared prerequisite.
- The two wrappers have the same operation/argument contract, path rules, exit-code behavior, and user-visible stage names. Platform-specific package-manager and virtual-environment details may differ only where necessary.
- The launch configuration must not run the main operation once as a pre-launch task and again under the debugger. The implementation must select and test one documented non-duplicating VS Code pattern before it becomes normative.
- All generated configuration and templates are valid JSON/JSONC as required by VS Code, use process/argument execution instead of shell-command concatenation wherever the VS Code schema permits, and provide explicit Windows and Linux/macOS behavior.

## 1. Establish the canonical entrypoint inventory and policy

- [ ] 1. Define the machine-verifiable meaning of a pipeline entrypoint.
  - [ ] 1.1 Inventory the standard Python CLI operations and each operation's required, optional, API-dependent, mutation, and recovery inputs.
    - [ ] 1.1.1 Map `preflight` to its API/pipeline inputs and safe operator use.
    - [ ] 1.1.2 Map `discover` to pipeline selection inputs and deterministic use.
    - [ ] 1.1.3 Map `run` to bounded execution inputs, including dry-run and run limits.
    - [ ] 1.1.4 Map `inspect-entity` to its required entity identifier input.
    - [ ] 1.1.5 Map `report` to its safe deterministic inputs.
    - [ ] 1.1.6 Map `analyze` to run-selection, bounds, and API inputs.
    - [ ] 1.1.7 Map `retry-cohort` to report/cohort inputs and its explicit recovery boundary.
    - [ ] 1.1.8 Map `rollback-entity` to its required entity identifier and recovery boundary.
  - [ ] 1.2 Define how a host declares additional entrypoints and how their task coverage is verified.
  - [ ] 1.3 Define the designation rule for exactly one main entrypoint and prohibit choosing destructive/recovery commands as the default.
- [ ] 2. Add the mandatory policy to `AGENTS.md` without duplicating the procedure.
  - [ ] 2.1 Require every entrypoint to be listed in `.vscode/tasks.json`.
  - [ ] 2.2 Require the designated main entrypoint to also be listed in `.vscode/launch.json` as the primary Run/Debug action.
  - [ ] 2.3 Require all task and launch paths to enter the platform-native wrapper before Python pipeline execution.
  - [ ] 2.4 Route creation, update, and review of that surface to the dedicated playbook.

## 2. Define the native bootstrap-wrapper contract before implementing it

- [ ] 3. Specify a single wrapper command-line contract shared by `scripts/run_pipeline_entrypoint.ps1` and `scripts/run_pipeline_entrypoint.sh`.
  - [ ] 3.1 Define operation selection and lossless forwarding of declared Python CLI arguments.
  - [ ] 3.2 Define `--host-root`, framework-root discovery, pipeline-definition, API-config, and dependency-manifest path resolution without unsafe path escapes.
  - [ ] 3.3 Define a setup-only mode only if it is needed by the tested launch/debug pattern; prohibit it from accidentally running an operation.
  - [ ] 3.4 Define standard nonzero failures, passthrough of Python exit codes, and Ctrl+C exit status 130.
- [ ] 4. Specify the visible bootstrap stages and their fail-closed behavior.
  - [ ] 4.1 Verify the wrapper is invoked from a supported operating system and resolve the host/framework roots before touching source or model state.
  - [ ] 4.2 Discover a supported Python version and verify that `venv` and `pip` are usable.
    - [ ] 4.2.1 Define supported Python version bounds and the exact visible remediation when Python is absent or incompatible.
    - [ ] 4.2.2 Define Windows discovery order and supported installers without assuming a particular terminal profile.
    - [ ] 4.2.3 Define Linux/macOS discovery order and supported package-manager behavior without assuming one distribution.
  - [ ] 4.3 Create or reuse an ignored host-local virtual environment and report its path and selected interpreter.
  - [ ] 4.4 Install or validate each declared host and framework Python requirements file using the virtual-environment interpreter.
    - [ ] 4.4.1 Define a deterministic freshness/fingerprint record and the conditions that require reinstalling dependencies.
    - [ ] 4.4.2 Define offline, index/authentication, dependency-resolution, and interrupted-install failure messages.
  - [ ] 4.5 Validate or install declared optional local runtime dependencies, including browser assets only when the selected pipeline requires them.
  - [ ] 4.6 Run definition/storage/prompt/API preflight at the appropriate point, preserving the rule that deterministic commands do not require API credentials.
  - [ ] 4.7 Invoke the requested Python entrypoint with the prepared interpreter only after all required stages pass.
- [ ] 5. Specify safe machine-wide prerequisite installation.
  - [ ] 5.1 Require an explicit wrapper mode or VS Code input before attempting installation of Python or OS packages.
  - [ ] 5.2 Define supported Windows package-manager detection, exact command reporting, elevation behavior, and clear manual fallback.
  - [ ] 5.3 Define supported Linux/macOS package-manager detection, privilege behavior, exact command reporting, and clear manual fallback.
  - [ ] 5.4 Prohibit automatic installation through an unknown package manager, unbounded downloads, system-Python package changes, credential output, or silent elevation.

## 3. Design and implement the VS Code task and launch surface

- [ ] 6. Provide canonical `.vscode/tasks.json` content or a host template that maps every entrypoint to a task.
  - [ ] 6.1 Use a stable task-label convention that makes operation, risk level, and normal/default use clear in the task picker.
  - [ ] 6.2 Use VS Code process/argument execution and OS-specific `windows` versus Linux/macOS overrides rather than shell-specific command concatenation.
  - [ ] 6.3 Configure every task for integrated-terminal, visible, non-background execution and correct problem/output presentation.
  - [ ] 6.4 Route Windows tasks to the PowerShell wrapper and Linux/macOS tasks to the Bash wrapper with equivalent arguments.
  - [ ] 6.5 Define reusable VS Code inputs for pipeline path, API config, entity ID, report path, cohort ID, run ID, dry-run choice, entity bounds, and runtime bounds.
  - [ ] 6.6 Include each standard entrypoint task and verify task arguments match the Python CLI contract.
  - [ ] 6.7 Define the extension point for host-specific operations and verify that their task arguments are declared rather than free-form shell text.
- [ ] 7. Provide a canonical `.vscode/launch.json` main-entrypoint configuration.
  - [ ] 7.1 Research the current VS Code/Python-debugger schema and select one portable mechanism by which the play button prepares the environment and runs the main entrypoint through the required wrapper chain.
  - [ ] 7.2 Prove with an automated or documented manual fixture that the selected mechanism executes the main operation exactly once.
  - [ ] 7.3 If a debugger must run Python directly after a setup-only native wrapper, constrain that exception to the launch configuration, document why it is necessary, and prove the normal task still follows wrapper-to-Python execution.
  - [ ] 7.4 Configure the launch action to use the host-local virtual-environment interpreter, selected main-entrypoint arguments, integrated terminal, and non-secret environment settings.
  - [ ] 7.5 Make the main launch configuration identifiable as the primary operator action without making recovery operations default launch actions.

## 4. Integrate safely with host bootstrap and framework updates

- [ ] 8. Define the canonical template and ownership model.
  - [ ] 8.1 Place framework-owned task/launch templates and wrapper assets in explicit framework paths.
  - [ ] 8.2 Define the host-owned `.vscode/tasks.json` and `.vscode/launch.json` installation locations.
  - [ ] 8.3 Create missing host configuration from canonical templates without creating credentials or runtime state.
  - [ ] 8.4 For an existing host configuration, detect it and stop with deterministic merge instructions or a safe managed-section mechanism; never overwrite user configuration.
  - [ ] 8.5 Define how customized tasks, launch configurations, selected interpreters, and host-specific entrypoints survive framework updates.
- [ ] 9. Update host lifecycle guidance.
  - [ ] 9.1 Update the host-bootstrap playbook to require setup of all tasks and the primary launch configuration before the host is considered ready for interactive operation.
  - [ ] 9.2 Update the submodule-update synthesis playbook to review task, launch, wrapper, and template changes without overwriting host-owned configuration.
  - [ ] 9.3 Update the pipeline-operation playbook to direct interactive operators to the task/launch surface while retaining raw CLI for CI and scheduler use.
  - [ ] 9.4 Update README and relevant catalogs to explain the preferred interactive interface and link to the owning playbook rather than repeat its procedure.

## 5. Create the dedicated playbook and keep authority boundaries clear

- [ ] 10. Add `playbooks/how_to_set_up_pipeline_entrypoints_in_vscode.md`.
  - [ ] 10.1 State applicability, prerequisites, required inputs, outputs, verification, and stopping/escalation conditions.
  - [ ] 10.2 Require an entrypoint inventory and one-to-one task mapping before writing VS Code configuration.
  - [ ] 10.3 Require explicit selection and review of the main entrypoint before writing the launch configuration.
  - [ ] 10.4 Require both native wrapper files, their common contract, visible bootstrap stages, safe installation behavior, and Python delegation.
  - [ ] 10.5 Require safe installation or merge of host-owned VS Code files and a review of customized configuration.
  - [ ] 10.6 Require the non-duplicating launch/debug verification before declaring the play button ready.
  - [ ] 10.7 Route exceptions—unsupported operating systems, absent package managers, missing privileges, offline dependencies, custom debugger adapters, and unclear main entrypoint—to explicit operator decisions.
- [ ] 11. Catalog and test the new route.
  - [ ] 11.1 Add the playbook to the playbook catalog and root task-routing table.
  - [ ] 11.2 Keep `AGENTS.md` limited to the mandatory invariant and route; keep operational detail only in the new playbook.

## 6. Verify the full contract

- [ ] 12. Add deterministic structural tests.
  - [ ] 12.1 Parse the template tasks and launch configuration and reject invalid syntax or missing required fields.
  - [ ] 12.2 Reject a standard or declared host entrypoint that lacks a task mapping.
  - [ ] 12.3 Reject a missing or ambiguous main-entrypoint launch mapping.
  - [ ] 12.4 Reject a task or launch path that bypasses the required platform wrapper without a documented launch-debug exception.
  - [ ] 12.5 Reject unsafe task command construction, hidden/background execution, or missing required interactive inputs.
  - [ ] 12.6 Reject missing wrapper assets, mismatched wrapper operation contracts, or wrapper paths outside the declared roots.
- [ ] 13. Add focused wrapper and host-integration tests.
  - [ ] 13.1 Test prerequisite-present and prerequisite-missing behavior without mutating the test machine.
  - [ ] 13.2 Test virtual-environment creation/reuse, requirements freshness, argument forwarding, Python selection, and exit-code propagation.
  - [ ] 13.3 Test interrupted bootstrap and Python operation behavior, including truthful output and exit code 130.
  - [ ] 13.4 Test missing/unsupported package managers, denied privileges, offline dependency failures, and non-secret diagnostics.
  - [ ] 13.5 Test creation for a missing host `.vscode` directory and preservation/manual-merge behavior for existing host task and launch files.
  - [ ] 13.6 Test the selected main launch pattern against duplicate operation execution.
- [ ] 14. Perform documented operator validation.
  - [ ] 14.1 Verify every task is visible in VS Code and launches the correct native wrapper on Windows and Linux/macOS.
  - [ ] 14.2 Verify the play button starts the designated main entrypoint exactly once and exposes material output in the terminal.
  - [ ] 14.3 Verify no credential, API secret, protected source content, or unredacted model data appears in task/launch/bootstrap output.
  - [ ] 14.4 Review the diff against every item in this plan, update checklist states with evidence, regenerate plan indexes, record the journal checkpoint, and propose a scoped commit.
