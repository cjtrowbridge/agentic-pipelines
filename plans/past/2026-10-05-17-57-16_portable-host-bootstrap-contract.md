---
plan_id: 2026-10-05-17-57-16_portable-host-bootstrap-contract
title: Require a portable host bootstrap contract
summary: Add a dedicated host-bootstrap playbook and make scripts/bootstrap.py the stable setup and health-check entrypoint with versioned implementations and read-only check mode.
status: past
created_at: 2026-10-05-17-57-16
---

# Require a portable host bootstrap contract

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

Authority: proposed from the user's 2026-10-05 request; implementation approved by the user on 2026-10-05.

- [x] 1. Define the canonical host bootstrap contract.
  - [x] 1.1 Require a host-owned `scripts/bootstrap.py` that delegates to the host-selected, user-versioned `scripts/bootstrap-vN.py`; retain earlier versions when their history matters and never auto-bump the version.
  - [x] 1.2 Specify a complete declared requirement inventory, idempotent inspect/apply/recheck behavior, observable service health probes, safe in-repository repair logic, clear failure disposition, and a genuinely non-mutating `--check` path with per-check PASS/FAIL and final totals plus nonzero failure exit.
  - [x] 1.3 Establish the bootstrap as the host's desired-state authority for machine and environment setup; require setup and remediation outside the repository to occur only through the reviewed bootstrap path, with explicit authority for privileged or machine-wide actions and no hidden workarounds.
- [x] 2. Integrate the contract into framework guidance and examples.
  - [x] 2.1 Add a dedicated `playbooks/how_to_create_and_maintain_host_bootstrap.md` covering host requirement inventory, stable/versioned files, check/apply/recheck, service probes, repair integration, verification, and escalation.
  - [x] 2.2 Route host bootstrap creation, maintenance, and health-check tasks to that playbook from `AGENTS.md`; update the root README and host bootstrap/update, pipeline-operation, and Ollama alias playbooks without overwriting existing host files.
  - [x] 2.3 Update the VS Code entrypoint playbook and platform-native wrapper examples so tasks and the primary `launch.json` action invoke the same host bootstrap entrypoint once before the selected pipeline operation.
  - [x] 2.4 Add a minimal, non-installable portable bootstrap example illustrating stable dispatch, versioned implementation, check aggregation, idempotent apply, and service health-check extension points without assuming host dependencies.
- [x] 3. Verify and checkpoint the framework change.
  - [x] 3.1 Test the example's repeated apply, missing/pristine and healthy check cases, read-only `--check`, failure counts and exit status, and wrapper order/exit propagation; check routing and Markdown links.
  - [x] 3.2 Update checklist state and plan indexes, record the journal checkpoint, and review diff and status for unrelated work.

No framework ROADMAP.md exists. The existing PDF plan is unrelated and remains current. Host-specific migrations are outside this framework checkpoint and require host review rather than automatic file replacement.

## Review checkpoint

- Added the stable/versioned bootstrap contract, dedicated playbook, routing, host and operation guidance, Ollama alias integration, and VS Code wrapper examples. `templates/bootstrap/` is deliberately non-installable and requires a host-owned requirement inventory before adoption.
- `python -m unittest tests.test_host_bootstrap_example tests.test_vscode_entrypoint_examples tests.test_documentation tests.test_bootstrap` passed (28 tests). `python -m py_compile` on both example scripts and `git diff --check` passed. The focused tests cover check-only read behavior, repair, repeat-run idempotence, independent failure totals, an empty inventory, interruption, and wrapper ordering/exit structure.
- No real host dependency or Docker service was changed or probed. Service-specific health checks and safe repairs belong in each host's reviewed versioned bootstrap.
