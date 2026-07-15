# Runtime Plan Reconciliation

## Decision

`2026-07-14-13-12-31_reorient-pipelines-around-prompts-and-playbooks` supersedes `2026-07-14-11-57-14_build-local-agentic-pipelines-framework`. Completed runtime work is retained as provisional supporting infrastructure. Every unfinished item from the older plan is transferred to, narrowed by, or intentionally replaced by the successor plan.

## Checked-item evidence audit

| Old workstream | Evidence | Assessment |
| --- | --- | --- |
| 0.1-0.2 | Superseded backlog removed; `docs/pipelines_architecture.md` defines handoff fields | Supported |
| 1.1-1.8 | `docs/pipelines_architecture.md` | Supported as an architecture decision, now subordinate to the prompt-first product model |
| 2.1-2.8 | `docs/pipeline_state_and_evidence_contract.md` | Supported as design documentation; implementation remains incomplete and is not implied by these checked design items |
| 3.1-3.8 | `api.sample.yaml`, `.gitignore`, `pipeline_runtime/config.py`, `pipeline_runtime/api.py`, `scripts/pipeline.py`, `tests/test_api_primitive.py` | Implemented provisionally and covered by the current fake-transport test |
| 4.1-4.4 | `pipeline_runtime/thread_capture.py`, API integration, `tests/test_api_primitive.py` | Implemented provisionally; database linking, retention, and query completeness remain open |

No checked old-plan item is being treated as proof that semantic review, repair, locking, migrations, cohort analysis, prompt generation, or production readiness exists.

## Open-item disposition

| Old workstream | Disposition in successor plan |
| --- | --- |
| 0.3 durable handoff integration | Section 9.1 |
| 3.9 shared API enforcement | Section 7.1 |
| 4.5-4.7 evidence links/query/retention | Section 7.5 |
| 5 entity quality lifecycle | Sections 5.3 and 7.2-7.3 |
| 6 bounded runner/operator experience | Sections 3.3, 6.4, and 7.4 |
| 7 post-run failure/performance analysis | Section 8 |
| 8 evaluation/security/reliability | Sections 5.4, 11, and 12 |
| 9 documentation/templates/journal/migration | Sections 2-5 and 9-10 |
| 10 Markdown reference pipeline | Section 11 |
| 11 delivery and verification | Delivery checkpoints A-E and Section 12 |

## Retained provisional runtime interfaces

The successor plan may build on these interfaces while retaining authority to refactor them behind regression tests:

- `load_api_config()` for ignored local API configuration;
- `InferenceClient.invoke()` and `InferenceRequest`/`InferenceResponse` for the sole provider-call boundary;
- `ThreadCaptureWriter.write()` for redacted call evidence;
- `load_definition()` for the provisional pipeline-definition boundary;
- `PipelineRunner.discover()`, `run()`, `inspect()`, and `report()` for the provisional CLI workflow;
- SQLite entity/transition records in `StateStore` as a prototype, not a frozen production schema.

## Known runtime gaps

- Several modules use compressed one-line implementations that must be made maintainable.
- No durable runner lock, lease recovery, schema migration system, or crash-safe run identity exists.
- Prompt paths are not yet backed by manifests, semantic versions, output schemas, or complete provenance links.
- Self-review, independent review, repair, adjudication, cohort analysis, retention cleanup, and cohort retry are not implemented.
- The two passing tests prove only shared API capture/redaction and a basic discovery-to-acceptance path.

## Verification evidence

- `python -m unittest discover -s tests -v`: 2 tests passed.
- Python compilation passed for current runtime and CLI modules.
- Plan indexes were current before the lifecycle transition.
