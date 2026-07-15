# Agentic Pipelines Architecture Contract

## Purpose

Agentic Pipelines is a submodule-ready framework for constructing and operating long-running, local-inference production pipelines. A cloud model may help design a pipeline; the local model performs the high-volume work. The framework must make each processed entity resumable, auditable, reviewable, and recoverable.

The initial delivery is intentionally single-host and Ollama-compatible. It does not depend on a cloud API, a hosted database, a web UI, or a distributed scheduler.

## Authority boundaries

| Concern | Authority | Evidence |
| --- | --- | --- |
| Changes to a repository or its pipeline design | Approved plan and repository policy | Plan checklist, journal checkpoint, reviewed diff |
| A particular pipeline run | Validated pipeline definition and local runtime config | `pipeline.yaml`, redacted config identity, run manifest |
| Whether an entity may alter the source tree | Acceptance/promotion policy in the pipeline definition | Validator and review evidence, promotion record |
| What the local model was asked and returned | Shared API primitive | Redacted thread capture |
| What failed and what should be changed | Deterministic analysis plus advisory model hypotheses | Cohort report and remediation proposal |

No prompt, worker output, reviewer output, or failure-analysis output may modify pipeline code, runtime configuration, source artifacts, or retry cohorts by itself.

## Framework and host ownership

The framework is installed as `./pipelines` in a host repository. The framework owns reusable runtime code, schemas, templates, documentation, and playbooks. The host owns its pipeline definition, source data, prompts selected or customized for that project, local configuration, runtime state, artifacts, reports, and operational checklist.

```text
host/
â”œâ”€â”€ pipelines/                     # framework submodule
â”œâ”€â”€ AGENTS.md                      # points to ./pipelines/AGENTS.md
â”œâ”€â”€ TODO.md                        # host-owned human work checklist
â”œâ”€â”€ pipeline.yaml                  # host-owned pipeline definition
â”œâ”€â”€ api.yaml                       # local-only credentials/endpoint configuration
â”œâ”€â”€ prompts/                       # host worker/reviewer/repair prompt templates
â”œâ”€â”€ state/                         # ignored SQLite database and leases
â”œâ”€â”€ runs/                          # ignored run manifests and summaries
â”œâ”€â”€ threads/                       # ignored, redacted per-call evidence
â”œâ”€â”€ artifacts/                     # ignored staged/accepted/quarantined artifacts
â”œâ”€â”€ failures/                      # ignored cohorts and entity evidence views
â””â”€â”€ reports/                       # ignored run and post-run reports
```

The upstream framework ships a `TODO.md` template, but never overwrites a host's `TODO.md`. Framework updates must synthesize host-managed template/playbook changes and preserve host runtime content.

## Retained, replaced, and newly introduced framework concepts

| Earlier framework concept | Agentic Pipelines treatment |
| --- | --- |
| Plan-governed repository changes | Retained. Plans authorize framework or host changes. |
| Journal | Retained. It is the append-only human/agent metaconversation and checkpoint memory, not a machine event log. |
| Documentation, templates, references, playbooks | Retained and expanded. They are the reusable product interface. |
| Legacy multi-board task tracking | Removed; a host-owned root `TODO.md` is the sole human checklist and its task text remains human-owned. |
| Generic downtime task catalog | Removed. Framework maintenance uses an approved plan; run learning uses post-run reports. |
| Downtime report | Replaced by deterministic failure/performance reports and advisory remediation proposals. |
| One-off agent task execution | Complemented by a resumable entity-oriented runner. |
| Tool wrappers | Replaced for model calls by one shared inference primitive. |

## Pipeline definition contract

`pipeline.yaml` schema version 2 is a validated host artifact. It declares:

- `schema_version` and `pipeline_id`;
- entity discovery source and stable identity rule;
- declared source, artifact, state, thread, and report paths;
- ordered stages and their input/output contracts;
- worker, self-check, semantic-review, repair, and analysis prompt contracts where enabled;
- deterministic validators and acceptance thresholds;
- retry, backoff, lease, quarantine, and promotion policies;
- local model/API profile reference, without embedding credentials;
- retention/redaction policy; and
- post-run cohort and performance-report policy.

The runtime refuses unknown schema versions, missing required gates, unsafe path escapes, or configuration that would silently select a cloud endpoint.

## Initial packaging and command surface

The initial runtime targets Python 3.11 or newer and uses the standard library where practical (`sqlite3`, `json`, `argparse`, `logging`, `pathlib`, `urllib`) plus a pinned YAML parser. The framework code lives in a `pipeline_runtime` Python package in this repository, with thin scripts that may be invoked directly from a host as `python pipelines/scripts/pipeline.py <command>`. A host does not copy runtime source in order to run a pipeline.

The command surface is deliberately small: `preflight`, `discover`, `run`, `inspect-entity`, `report`, `analyze`, `retry-cohort`, and `rollback-entity`. Deterministic inspection/reporting commands do not require API configuration. Mutating run, retry, and rollback commands are explicit and bounded.

## Entity lifecycle

An entity is one independently auditable unit of work. It has a stable identity and immutable source snapshot for each processing revision.

```text
discovered â†’ staged â†’ leased â†’ worker_completed â†’ deterministic_validated
                                              â”œâ†’ validation_failed â†’ retry_eligible
                                              â”‚                         â””â†’ leased
                                              â””â†’ semantic_reviewed â†’ accepted â†’ promoted
                                                                     â”œâ†’ repair_eligible â†’ leased
                                                                     â””â†’ quarantined
```

`accepted`, `promoted`, and `quarantined` are terminal for a specific entity revision. A new source snapshot or explicitly approved cohort retry creates a new processing revision; it does not erase prior evidence. Every transition is transactionally persisted with its reason and evidence links.

## State, artifacts, and promotion

The initial state store is a local SQLite database. It records entities, source snapshots, attempts, leases, transitions, validator results, review results, run membership, and artifact/thread references. SQLite is the right initial boundary because the runner is single-host, needs transactions and queryability, and must not require a service.

Source content is never overwritten by a worker. A worker writes a uniquely named staged candidate. Required validation and review gates produce evidence. Only the promotion step may copy or swap an accepted candidate into the host's configured destination. Promotion records source hash, candidate hash, pipeline/prompt/model identity, and rollback location. Failed or interrupted promotion leaves the source untouched.

Entity identity, source hash, pipeline schema version, stage version, and idempotency key together prevent repeated cron invocations from accepting duplicate work. Stale leases are recoverable only after their expiration and after an attempt record indicates that the previous runner did not complete.

## Shared local API primitive

All model-facing stages use a single internal interface. No worker, reviewer, repair, or analysis module sends raw provider HTTP requests directly.

The initial adapter targets Ollama-compatible chat/generation endpoints and receives settings from an ignored `api.yaml`. The repository ships `api.sample.yaml` with non-secret example values. The runtime preflight fails clearly when `api.yaml` is missing or invalid, points the operator to the sample, and never writes credentials itself.

Configuration supports endpoint, model, optional auth/header settings, connect/read/request timeouts, TLS policy, and generation settings. Config values are schema-validated and redacted from logs, state, reports, and thread captures. Only a non-secret configuration fingerprint is recorded in a run manifest.

The primitive owns request normalization, cancellation, retry classification, bounded exponential backoff with jitter, response normalization, usage/timing collection when available, and structured errors. Missing usage data is reported as unknown.

## Thread capture and redaction

Each call creates a redacted, atomic evidence record before downstream code acts on the result. It includes:

- run, entity, revision, stage, and attempt identifiers;
- pipeline and prompt-template versions/hashes;
- rendered request and normalized response, subject to configured redaction;
- provider/model metadata, timing, availability of usage metrics, and normalized error;
- links/hashes for source snapshot, candidate artifact, validator evidence, and report; and
- capture schema version and redaction actions applied.

Thread captures are stored beneath `threads/<run-id>/<entity-id>/<stage>/<attempt>.json` (or equivalent schema-versioned form), while SQLite remains the query authority. Captures must exist for failures and partial responses as well as successful calls. Retention, compression, and opt-out are explicit pipeline policy.

## Validation and review model

Validation has separate roles:

1. Deterministic validation is cheap and authoritative for structural and invariant checks: existence, parsing, front matter/schema preservation, protected sections, required fields, forbidden changes, and bounded diff/edit distance.
2. Worker self-check is optional, low-cost, and explicitly non-independent.
3. Independent semantic review uses a separate prompt contract and sees the source, candidate, goal state, and deterministic evidence—not hidden worker reasoning. It returns a schema-validated verdict, confidence, violations, and recommended action.
4. Adjudication/repair selects accept, reject, focused repair, rerun, or quarantine based on declared policy.

Invalid model JSON or malformed reviewer output is a stage failure, not implicit approval. Retry budgets are finite; a terminal quarantine record includes reason, evidence, and next-action recommendation.

## Bounded runner and scheduler contract

The runner is designed for repeated scheduler invocation, not an immortal unbounded process. A run must:

1. validate layout, definition, API config, state migration compatibility, and write paths;
2. acquire a single-host lock and reclaim only expired leases;
3. select eligible work within `--max-entities` and `--max-runtime-minutes` bounds;
4. persist every transition and capture evidence before subsequent stages;
5. stop safely on cancellation or time budget, leaving resumable state;
6. generate machine-readable and human-readable summaries; and
7. release the lock.

Scheduler instructions must set the allowed runtime below the schedule interval and reject overlap. CLI commands will separate preflight, discovery, run, inspect-entity, report, and explicitly approved cohort retry.

## Post-run analysis and recovery

Post-run analysis is a required pipeline phase for substantial completed runs. It groups failures deterministically by stage, validator code, reviewer result, content type, size, prompt/model revision, endpoint error class, retry pattern, and output-shape/diff signals. Reports distinguish observed facts from model-generated hypotheses.

A failure-analysis prompt may inspect representative, redacted cohort evidence via the shared API primitive. Its remediation proposal must state common cause, likely ownership, feasibility, cohort-safe change, needed regression test, and retry-versus-human decision. It is advisory only.

Performance reports include throughput, per-stage duration, request/lease delays, retry/failure rates, acceptance/rejection/quarantine rates, local usage metrics when supplied, and estimated remaining duration. A curated evaluation set supplies false-accept and false-reject signals; absence of measurement is labeled unknown.

The recovery sequence is fixed:

```text
cohort evidence â†’ advisory remediation proposal â†’ approved repository change
â†’ evaluation/sample run â†’ approved cohort-scoped retry
```

No analysis output may automatically revise a pipeline or relaunch all failures.

## Security and data handling

Source documents and model output are untrusted data. They cannot change configuration, invoke tools, select files outside declared directories, or override validation rules. File paths derived from entity identifiers or model output are normalized and verified to remain inside configured artifact/state roots.

Secrets and configured sensitive patterns are redacted before persistence. Local API credentials are ignored by Git. Operators may reduce retained prompt/response content, but the runner must preserve enough non-sensitive metadata to explain outcome state.

## Evaluation and release gate

Before a pipeline is recommended for broad execution, it must pass a versioned golden evaluation set with protected invariants and edge cases. Tests must cover malformed input/output, timeout, interrupted run, stale lease, duplicate invocation, promotion failure, semantic disagreement, quarantine, resume, and post-run reporting. Integration tests use a fake Ollama-compatible service; a real local-model smoke test is explicit opt-in.

## Durable handoff contract

Every implementation checkpoint and long-running investigation records:

- active plan path and exact checklist deltas;
- approved decisions and unresolved decisions;
- links to relevant run manifests, reports, thread captures, or artifacts;
- material risks, assumptions, and validation gaps; and
- the exact next approved action or the approval required before it.

The journal holds the human-readable checkpoint summary. Run evidence remains in machine-oriented runtime folders. Future templates and playbooks must expose these fields directly.

## Deferred scope

The initial architecture intentionally defers multi-provider support, remote/cloud inference fallback, distributed/multi-host work leasing, UI/dashboard work, automatic application of remediation proposals, and domain-specific pipelines beyond the Markdown reference implementation.

