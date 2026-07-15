# Reference Design Trace

## Loaded artifacts

- `playbooks/how_to_design_a_pipeline.md`
- `prompts/design/understand_pipeline_goal.md`
- `prompts/design/define_entity_contract.md`
- `prompts/design/identify_invariants.md`
- `prompts/design/design_stages.md`
- `prompts/design/design_validation.md`
- `prompts/design/audit_pipeline_design.md`
- `prompts/design/assemble_pipeline_definition.md`
- `references/prompt_authoring.md` only when generating runtime prompts

No operation, framework-maintenance, migration, or cohort-retry playbook is required to design this package.

## Deterministic-first decisions

- Discovery, size bounds, snapshots, path safety, state, locks, retries, front-matter comparison, protected text, fence balance, diff bounds, evidence, cohorts, metrics, promotion, and rollback are deterministic.
- The worker exists only for structurally ambiguous repairs where syntax alone cannot select the intended boundary.
- The reviewer sees only the source, candidate, goal, and deterministic evidence; it judges meaning preservation that exact validators cannot establish.
- Repair receives only a rejected candidate and concrete violations. Failure after one repair quarantines the entity.
- Cohort and performance metrics are deterministic. Analysis prompts only interpret them and produce advisory output.

## Generated outputs

`package.yaml` is the review boundary. It names the schema-v2 definition, six prompts, fixtures, API sample, scheduler example, rollback notes, and requirement traceability. `scripts/validate_pipeline_package.py` verifies those relationships without inference or processing.
