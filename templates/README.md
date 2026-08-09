# Templates

`run_report.md`, `rejected_artifact_explanation.md`, and `pipeline_conformance_report.md` expose the required human-facing execution and migration evidence. Hosts may adapt presentation and paths but must preserve the corresponding schemas, trust boundaries, and required fields.

`vscode/` contains non-installable, placeholder-marked examples for host-owned VS Code tasks, one primary play action, and platform-native prerequisite/bootstrap scripts. Use the owning VS Code entrypoint playbook before adapting them.

- `pipeline_design_intake.yaml`: unresolved goal-to-pipeline intake.
- `pipeline_package.yaml`: staged package manifest.
- `task_execution_plan.md`: framework or host change plan.
- `change_plan.md`: proposal-only change summary.
- `daily_journal_entry.md`: human/agent design checkpoint.
- `playbook_proposal.md`: proposed routed task procedure.
- `submodule_update_synthesis_report.md`: host-preserving update review.

Load only the template named by the active playbook.
