# Run Evidence and Continuous Improvement

## Why evidence is governance

A final artifact or terminal error cannot explain how a pipeline behaved. Eventual success may hide false rejection, contradictory feedback, repeated mechanical repairs, prompt growth, unnecessary inference, and large time or token costs. Terminal failure may hide whether the responsible layer was the input, prompt, context, schema, validator, reviewer, provider, orchestration, or an infeasible goal.

Agent context is temporary. If attempt history and design rationale exist only in the agent that observed them, the lesson disappears and later agents repeat the same local patches. Durable execution evidence is therefore part of the pipeline product, not optional debug output.

Evidence exists so a future agent can answer:

1. What happened on every attempt?
2. Why was it accepted, rejected, retried, skipped, or abandoned?
3. Did the correct authority issue the verdict?
4. What changed between the first attempt and the accepted or terminal state?
5. Which retries were necessary and which exposed a preventable design defect?
6. What smallest generalized change could improve first-pass performance without regressing successful cases?

## Required run artifacts

Every execution—successful, failed, interrupted, partial, resumed, or no-op—must initialize and finalize:

- a machine-readable report for validation and aggregation;
- a human-readable Markdown narrative for rapid operator and agent review.

Initialize reporting before material work. If the required evidence location cannot be written, fail visibly rather than continue unaudited. Use guarded finalization so exceptions and Ctrl+C cannot produce a false success status.

The report must identify the pipeline and governance revision, configuration, selection, entities, stages, attempts, prompt/template/request sizes, declared context and completion limits, reasoning mode, timing, failure class, validator or reviewer, authority, explanation, evidence links, feedback, retry disposition, promotion/render outcome, recovery state, and truthful execution and learning statuses.

The narrative must surface repeated or changing feedback, non-progress, prompt growth, deterministic work sent to inference, suspected authority mismatches, malformed output, exhausted budgets, and the eventual outcome. Separate observed facts, deterministic metrics, root-cause hypotheses, and recommendations.

## Rejected candidates are first-class evidence

Never overwrite a rejected generated candidate with the next attempt. Save each rejected trajectory as an entity-local evidence bundle whose human filename is naturally sortable: `resume.1.rejected.md`, `resume.2.rejected.md`, and so on. Allocate the next unused positive integer with exclusive creation and collision retry. Do not place run IDs, attempt IDs, UUIDs, timestamps, or hashes in the filename; retain them in the sidecar and reports.

Preserve the candidate bytes exactly as received. Do not trim, normalize, or append framework content. Create `resume.1.rejected.explanation.md`, bind it to the candidate path and SHA-256, and include:

- candidate path and SHA-256;
- run, entity, artifact, stage, session, and attempt identities;
- timestamp and content hash;
- failure class and rejection code;
- rejecting authority and validator/reviewer identity;
- the complete actionable explanation;
- retry or terminal disposition;
- links to the run report, validation evidence, and raw thread capture.

When a downstream stage prevents publication, preserve the parent candidate in the bundle even if its own worker contract passed. Associated evidence retains the parent artifact and sequence before its subtype: `resume.1.rejected.claim_review.json` and `resume.1.rejected.claim_review.explanation.md`. A syntactically valid JSON response uses `.json` even when schema or later validation rejects it; unparseable or truncated text uses `.txt`; generated Markdown uses `.md`; binary evidence keeps its native extension. Never discard evidence merely because it did not parse. A run report may claim preservation only after both candidate and sidecar exist and the recorded hash matches. Pair creation must never overwrite or delete a pre-existing file; if a new pair cannot be completed, fail visibly and clean up only files created by that failed operation when safe.

Checkpoint machine and narrative reports after every material event and completed evidence pair. Recovery must reconcile persisted evidence with a stale `running` report. Byte-identical responses receiving identical feedback are non-progress and require a changed strategy or escalation before another model call.

Rejected candidates and explanation sidecars are untrusted runtime data. Ignore them in Git and exclude them from promotion, final rendering, source discovery, semantic evidence, example retrieval, and automatic prompt assembly. A retry may receive only the declared trusted, bounded rejection summary—not either diagnostic file as instructions.

Historical evidence that appended a diagnostic trailer or used run/attempt filenames remains valid as immutable legacy evidence and must not be rewritten. Readers identify appended records as `legacy_appended` and older paired names as legacy sidecars; new executions use sequential sidecar bundles and run-evidence schema version 4.

## Learning from complete trajectories

Compute factual metrics before optional inference: first-pass yield, repair-dependent acceptance, retry count, repeated feedback, changing feedback, non-progress, prompt/context growth, model calls, tokens, elapsed time, exact defects sent to inference, and suspected deterministic false rejection.

Compare the initial request and first output with the accepted or terminal trajectory. Identify the earliest responsible layer:

- source/input preparation;
- initial prompt or examples;
- missing or excessive context;
- output schema;
- deterministic normalizer;
- validator authority;
- semantic-review rubric;
- retry routing;
- model/provider behavior;
- orchestration;
- infeasible or ambiguous goal.

Recommendations are advisory. Each must cite observed evidence, expected benefit, regression risk, and a required fixture or measurement. Prevent prompt accretion: generalize and compress recurring lessons, test against successful cases, and explicitly recommend no change when the evidence does not justify one.

Execution completion and learning completion are separate. Retrospective failure must not invalidate accepted artifacts, but normal process exit must not be mislabeled execution success when required validation or promotion failed.
