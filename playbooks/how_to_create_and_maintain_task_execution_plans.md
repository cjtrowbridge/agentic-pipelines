# Playbook: Create and Maintain Task Execution Plans

## Use when

Planning, implementing, reviewing or archiving a coherent deliverable.

## Load

`AGENTS.md`, the governing roadmap if present, applicable host planning rules, `templates/task_execution_plan.md`, and `references/deliverable_driven_simplicity.md`.

## Procedure

1. Select the plan matching the authorized outcome. Ask only if governing scope is materially ambiguous. Preserve unrelated work and explicit branch-permission boundaries.
2. State outcome, protected behavior, simplest implementation, uncertainty, acceptance evidence and stopping condition. Decompose only until the next useful implementation/check is clear. Do not turn checklist detail into architecture or additional plans automatically.
3. Compare roadmap and plan scope, status, sequencing, dependencies and acceptance. Preserve host one-to-one mappings and links. Record a missing roadmap explicitly; do not invent one merely for this procedure.
4. Record existing user authorization. Request approval only for unauthorized work or material changes to scope, behavior, authority, irreversible actions or cost. Routine implementation discoveries within the approved outcome require plan updates, not renewed permission.
5. Use `YYYY-MM-DD-HH-mm-ss_slug.md` and matching `plan_id`, with `title`, `summary`, `status`, `created_at`. Keep the template's status key. Host-established formats take precedence.
6. Promote `future` to `current` before implementation. Implement a coherent outcome and review its complete path for correctness, simplification and relevant costs. Mark completed items `[x]`, uncertain verification `[?]`, and intentionally closed items `[-]`.
7. Record material findings and dispositions. For selected improvements compare baseline and result, retain or revert, and stop at acceptance. Keep unavailable device evidence explicit.
8. Archive to `past` when no work remains, respecting host lifecycle rules. Update affected roadmap links and regenerate framework indexes with `python scripts/regenerate_plan_indexes.py`; use host index tooling/formats for host plans.
9. Record concise evidence and handoff in the journal. Review the diff and scope before proposing a commit; this playbook does not authorize commit, push or branch creation.

## Output and verification

A traceable plan with authorized outcome, evidence, truthful status and resolved links. Verify behavior proportionately; structural plan checks do not establish product correctness.
