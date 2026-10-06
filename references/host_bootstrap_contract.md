# Reference: Host Bootstrap Contract

Detailed contract for the host-owned bootstrap described by `playbooks/how_to_create_and_maintain_host_bootstrap.md`. This reference does not authorize changes to a particular host.

## Contract

- `scripts/bootstrap.py` is the stable, portable command. It delegates to the selected `scripts/bootstrap-vN.py` using the current Python interpreter and forwards `--check`, other declared arguments, and the exit status. The user decides when to make a new version, typically for an architectural overhaul or when preserving an old process matters. Do not automatically bump versions or run historical versions on every invocation.
- The selected implementation defines the host's desired machine and environment state. Maintain an explicit inventory of every declared dependency, local artifact, configuration prerequisite, and required service, with a read-only probe and an authorized repair where one is safe. This inventory, rather than an opaque success marker, determines readiness.
- Normal mode probes each requirement, applies only necessary authorized changes, and probes it again. Repeated runs must converge without repeat installs, duplicate configuration, or unnecessary service restarts. Record PASS/FAIL per requirement, the action taken, and final pass/fail totals; return nonzero if any required check fails and 130 on interruption.
- `python scripts/bootstrap.py --check` runs every probe and reports PASS/FAIL plus final totals without installing, starting, stopping, writing, or repairing anything. A failed probe must not prevent independent later probes. Missing tools and probe exceptions count as failures, with useful non-secret reasons.
- Outside-repository setup and remediation must flow through the reviewed bootstrap implementation. Diagnose a new failure, encode a bounded probe and safe repair, test both modes, then use the stable entrypoint to apply it. Do not perform an unrecorded one-off machine change and leave bootstrap unaware. Privileged or machine-wide operations require explicit host authorization and cannot silently elevate; missing credentials or human decisions remain visible failures with operator instructions.

## Procedure

1. Inventory all project requirements and their dependency order: runtime, packages, ignored local environments, framework/submodule availability, configuration, data stores, Docker or other services, and pipeline preflight. Identify which are inspectable before imports or model/source work. Mark optional services explicitly so their absence is not silently treated as success.
2. Review existing host bootstrap files and state. Preserve custom scripts and settings. Propose an incremental merge. Keep the stable dispatcher small and standard-library-only; keep current setup logic in the selected versioned file. Store generated project state in ignored host-local paths where possible. The host must name and authorize any necessary external target.
3. Implement each requirement as a read-only probe and, when authorized, an idempotent repair. For services, distinguish installed tool, reachable daemon, expected container/process state, and application health. Use a bounded health probe after any start/restart; a running container alone may not mean the service is ready. On failure, continue independent checks and report dependency-blocked checks honestly.
   For Docker Ollama alias requirements, use `scripts/ensure_ollama_context_aliases.py --check` as the probe and the same command without `--check` as the repair after the container and base model are ready; see the Ollama alias playbook.
4. Implement normal mode as probe → repair if needed → re-probe. Never call a repair from `--check`. Validate paths and commands before applying changes. Keep a repair inside its declared scope and avoid destructive resets or overwriting user data. Promote a successful manual diagnosis into the versioned bootstrap only after the root cause and safe repair are understood.
5. Run `--check` on a healthy host and on controlled missing/unhealthy fixtures. Confirm no files, services, or environment settings changed, that every declared requirement received a result, and that totals and exit status match the results. Run normal mode twice and confirm the second run performs no repair. Test a failed repair and interruption path.
6. Wire every host task and the primary `launch.json` action through the platform-native wrapper, which invokes `scripts/bootstrap.py` once and starts the requested pipeline operation only after success. Keep direct CLI, CI, and scheduler entrypoints available through the same bootstrap boundary. See the VS Code entrypoint playbook.
7. Record the supported platforms, external changes, required privileges, check list, repair policy, and verification evidence in the host README. When an issue is fixed later, update the active versioned implementation and its focused regression evidence; create a new version only at the user's discretion.

## Outputs

The host-owned stable entrypoint, selected versioned implementation, declared requirement inventory, healthy and failing `--check` evidence, repeated-run evidence, and entrypoint wiring. Report any checks requiring human action.

## Stop conditions

No approved active host plan for repository edits; a required repair's authority or target is unclear; a proposed change would overwrite host data or credentials, modify system Python, elevate, or change machine-wide state without explicit authorization; or the check mode cannot be made read-only.
