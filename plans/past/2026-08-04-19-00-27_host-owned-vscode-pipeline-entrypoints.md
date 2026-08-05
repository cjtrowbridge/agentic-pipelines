---
plan_id: 2026-08-04-19-00-27_host-owned-vscode-pipeline-entrypoints
title: Require Host-Owned VS Code Pipeline Entrypoints
summary: Establish a concise framework policy and playbook requiring every host pipeline entrypoint to be a VS Code task and its main entrypoint to be a bootstrap-backed play action.
status: past
created_at: 2026-08-04-19-00-27
---

# Require Host-Owned VS Code Pipeline Entrypoints

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

## Outcome

Every project importing Agentic Pipelines provides a convenient, project-appropriate VS Code operator surface:

```text
each host-declared operator entrypoint
  -> one visible host-owned .vscode/tasks.json task
  -> the appropriate host-owned platform-native prerequisite/bootstrap script
  -> the host's actual pipeline entrypoint

one explicitly selected ordinary main entrypoint
  -> one primary host-owned .vscode/launch.json action
  -> the same platform-native prerequisite/bootstrap boundary
  -> exactly one execution of the main entrypoint
```

The framework owns the mandatory policy, setup/review playbook, minimal adaptable examples, and deterministic checks that apply across projects. Each host owns its entrypoint inventory, main-entrypoint choice, VS Code files, native scripts, supported platforms, prerequisite policy, dependency mechanism, paths, commands, and arguments.

## Baseline and non-goals

- Local `main` was restored to `2c6eddb` before this plan was created. The premature commits and worktree were preserved during recovery, inspected after replacement commits `2b2b243` and `90984db` became durable, and then removed under Section 8.
- The discarded proposal is retained in Git history but is not an active or archived implementation plan.
- This plan does not create a universal pipeline command inventory, mandate wrapper filenames, install machine-wide prerequisites, select package managers, prescribe a virtual environment or requirements filename, generate managed sections in host files, or introduce a second bootstrap subsystem.
- This plan does not make this framework repository's own `.vscode` directory a downstream template. Dogfooding the policy here requires a separate host-specific decision.
- Entrypoint discovery, JSON validation, task coverage, path checks, wrapper dispatch, and prerequisite checks are deterministic work and must not use an LLM.

## 1. Define the mandatory framework policy

- [x] 1. Establish the host-specific entrypoint invariant.
  - [x] 1.1 Define an operator entrypoint as each operation the host intentionally exposes for interactive use, whether implemented as a CLI subcommand, script, task-runner target, executable, or another project-native command.
  - [x] 1.2 Require every declared operator entrypoint to have one visible, accurately named task in the host-owned `.vscode/tasks.json`.
  - [x] 1.3 Require the host to designate exactly one ordinary, non-recovery entrypoint as its main interactive action in host-owned `.vscode/launch.json`.
  - [x] 1.4 Require both task and launch paths to invoke an appropriate host-owned platform-native prerequisite/bootstrap script before invoking the actual pipeline entrypoint.
  - [x] 1.5 Require the native script to check or prepare only project-declared prerequisites, report failures visibly, and return the pipeline process exit status.
- [x] 2. Place the policy at the correct authority boundary.
  - [x] 2.1 Add only the concise mandatory invariant and playbook route to `AGENTS.md`.
  - [x] 2.2 Keep project-specific commands, paths, dependencies, wrapper names, and installation decisions out of `AGENTS.md`.
  - [x] 2.3 Preserve direct CLI, CI, scheduler, and other non-VS-Code operation while making the VS Code surface mandatory for interactive host use.
  - [x] 2.4 Require bootstrap and framework-update workflows to preserve existing host `.vscode` files and native scripts.

## 2. Create the host-oriented setup and review playbook

- [x] 3. Add `playbooks/how_to_set_up_pipeline_entrypoints_in_vscode.md` as the owning procedure.
  - [x] 3.1 Require inspection of the host's actual entrypoints, current VS Code configuration, supported platforms, prerequisite mechanism, and existing native scripts.
  - [x] 3.2 Require a reviewed one-to-one mapping between the discovered host entrypoints and visible tasks without substituting this framework's reference CLI for the host's contract.
  - [x] 3.3 Require explicit operator or host-contract selection when the main entrypoint is ambiguous, and prohibit recovery or destructive operations from being selected by default.
  - [x] 3.4 Require task inputs for values an operator must supply, accurate argument forwarding, foreground integrated-terminal execution, and platform-appropriate native dispatch.
  - [x] 3.5 Require the main launch action to enter the same prerequisite/bootstrap boundary and execute the selected operation exactly once.
  - [x] 3.6 Permit creation of missing host configuration only from reviewed host-specific inputs; when files already exist, preserve them and present an explicit merge proposal.
  - [x] 3.7 Treat unsupported platforms, missing prerequisites, privilege requirements, unsafe installation behavior, ambiguous paths, and unclear entrypoints as host decisions or stop conditions.
  - [x] 3.8 Avoid mandatory wrapper filenames, fixed command lists, package-manager commands, virtual-environment layouts, requirements filenames, and framework-managed host file sections.

## 3. Provide minimal adaptable examples

- [x] 4. Add framework-owned examples that demonstrate the required shape without claiming to be universal host configuration.
  - [x] 4.1 Provide a concise `tasks.json` example using argument arrays and platform-specific overrides to invoke placeholder host-owned Bash and PowerShell scripts.
  - [x] 4.2 Check the current official VS Code launch schema and provide one minimal cross-platform main-action example that enters the host bootstrap boundary exactly once.
  - [x] 4.3 Provide minimal PowerShell and Bash script examples that visibly check declared placeholder prerequisites and delegate to a placeholder pipeline command.
  - [x] 4.4 Keep the native examples fail-closed and free of machine-wide installation, silent elevation, credentials, or assumptions about a host dependency manager.
  - [x] 4.5 Mark every project-specific path, command, argument, prerequisite, and supported platform as a placeholder that the host must resolve.
  - [x] 4.6 Keep examples separate from installed host files and from this framework repository's own `.vscode` configuration.

## 4. Align host lifecycle documentation

- [x] 5. Integrate the policy without duplicating project-specific procedure.
  - [x] 5.1 Update the host-bootstrap playbook to require a reviewed entrypoint inventory, full task coverage, one main launch action, and preservation of existing host configuration.
  - [x] 5.2 Update the submodule-update playbook to surface relevant policy and example changes without overwriting host-owned `.vscode` files or native scripts.
  - [x] 5.3 Update the pipeline-operation playbook to direct interactive operators to the host's VS Code surface while retaining direct commands for automation.
  - [x] 5.4 Update README and playbook catalogs with a concise explanation and a link to the owning playbook.
  - [x] 5.5 Verify all documentation consistently distinguishes framework policy, framework examples, host-owned configuration, and the framework's reference runtime.

## 5. Verify the delivered contract

- [x] 6. Add deterministic structural and policy tests.
  - [x] 6.1 Parse every framework-owned VS Code example and reject invalid syntax or missing required task, launch, platform-dispatch, foreground-terminal, or wrapper-boundary fields.
  - [x] 6.2 Verify the examples demonstrate one task per declared example entrypoint and exactly one eligible main launch action.
  - [x] 6.3 Reject examples that invoke Python or another pipeline implementation before the native prerequisite/bootstrap boundary.
  - [x] 6.4 Reject machine-wide installer commands, silent elevation, credentials, fixed framework CLI inventories, and unresolved placeholders presented as ready-to-install configuration.
  - [x] 6.5 Verify `AGENTS.md`, the owning playbook, lifecycle playbooks, README, and catalogs agree on host ownership and policy boundaries.
- [x] 7. Complete proportional operator validation and plan closure.
  - [x] 7.1 Validate the Windows example on Windows and document the equivalent Linux/macOS validation still required when those platforms are unavailable.
  - [x] 7.2 Confirm the play action invokes its example main wrapper exactly once and exposes prerequisite and pipeline output visibly.
  - [x] 7.3 Run the complete automated suite and review the diff for obsolete universal-wrapper, generic-installer, duplicate-bootstrap, fixed-inventory, and host-overwrite assumptions.
  - [x] 7.4 Update checklist states with evidence, regenerate plan indexes, record the journal checkpoint, and propose task-scoped commits before committing or pushing.
- [x] 8. Remove temporary recovery references after the replacement is durable.
  - [x] 8.1 Confirm the approved replacement implementation and plan evidence are committed and no retained change depends on the rejected commits or abandoned worktree.
  - [x] 8.2 Inspect `recovery/vscode-entrypoints-before-cleanup` one final time, confirm it contains no unique work to retain, and delete the recovery branch.
  - [x] 8.3 Locate the stash by its message `recovery: pre-cleanup vscode entrypoint worktree`, inspect it one final time, confirm it contains no unique work to retain, and drop that exact stash entry without relying on a potentially shifted stash index.
  - [x] 8.4 Verify the recovery branch and named stash are absent and the active worktree, committed history, tests, plan evidence, and indexes remain intact.

## Delivery checkpoints

- [x] A. Approve and deliver the mandatory invariant and host-oriented playbook in Sections 1–2.
- [x] B. Deliver the adaptable examples and lifecycle documentation in Sections 3–4.
- [x] C. Complete deterministic and operator verification in Section 5.
- [x] D. Remove the temporary recovery branch and stash only after the replacement is committed and verified.
