# Playbook: Change the Agentic Pipelines Framework

## Use when

Changing framework prompts, playbooks, policy, templates, references, runtime code, schemas, or repository structure. Do not load this playbook merely to operate a host pipeline.

## Load

- `AGENTS.md`
- `playbooks/how_to_create_and_maintain_task_execution_plans.md`
- The active plan and only the artifacts affected by its approved checklist items
- Relevant verification or commit playbooks only when reaching those steps

## Procedure

1. Identify the active plan and exact checklist items authorizing the change.
2. Inspect repository status and preserve unrelated/user-owned work.
3. If required work is absent from the plan, stop and obtain approval for an atomic revision.
4. Apply only approved changes, keeping prompts, playbooks, references, templates, schemas, code, and documentation consistent.
5. Verify behavior and prompt/playbook routing in proportion to risk.
6. Update checklist states and regenerate plan indexes after plan edits or lifecycle moves.
7. Record the checkpoint in today's journal; do not write user-only journal fields without verbatim user text.
8. Review status/diff, pending framework-maintenance reports, and propose a task-scoped commit.

## Outputs

- Implemented framework change
- Updated active plan and indexes
- Verification evidence
- Journal checkpoint and commit proposal

## Stop conditions

- Required work is outside the approved plan.
- A change would overwrite user/host-owned content or credentials.
- Evidence contradicts the plan's assumptions.
- Required verification cannot be run or produces unexplained failure.

