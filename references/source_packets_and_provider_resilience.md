# Source Packets, Optional Stages, and Provider Resilience

## Why this is governance

A text-only prompt boundary is necessary but insufficient. A PDF may be converted correctly to Markdown and still be the wrong thing to send: a prior resume, generated candidate, rejected artifact, configuration file, or unrelated attachment is not a job-posting source. Source role and representation are separate deterministic facts.

Every source record therefore identifies a stable ID, canonical path, declared role, media type, hash, derivative link where required, discovery authority, and inclusion disposition. Stages declare their allowed roles. Unknown roles stay out of prompts or become an explicit operator decision; a heuristic may route uncertainty but cannot silently grant trusted-source status.

## Complete packet budgets

Measure the complete assembled request before transport, not just one source or the examples independently. Record static prompt bytes, every component's bytes, example authority roles, selected and omitted IDs, request bytes, retained-session reserve, `num_ctx`, `num_predict`, batch identity, and reduction reason. Preserve whole source and demonstration units and their identities; never hide truncation inside a record.

When a valid packet does not fit, use declared stable reduction or independent-unit batching. If neither can preserve the stage contract, emit `packet_budget_exhausted` with measurements. Scope that result to the affected stage or artifact. An advisory preflight may not block unrelated artifact generation.

## Optional stages and provider health

Every stage explicitly declares `required` or `optional`, failure scope, fallback, and terminal effect. Optional retrieval/reranking commonly falls back to an empty example set: preserve its failed evidence, say that the fallback activated, and continue. A fallback is not stage success.

Provider health uses the configured endpoint and hostname. Do not rewrite a hostname into an IP address. Classify DNS, socket permission/route, refusal, timeout, TLS, authentication, and HTTP failures. A run-local circuit breaker suppresses equivalent doomed calls after a decisive transport failure. It preserves deterministic work, marks unattempted model work pending, checkpoints normal reports, and never replaces a controlled Ctrl+C interruption (status 130).

## Consumer checklist

1. Inventory source roles and exclusion boundaries.
2. Declare allowed roles and complete packet budgets for every model stage.
3. Declare optional fallbacks and artifact-level failure scope.
4. Test a source-role exclusion, oversized packet, optional fallback, provider outage, and interruption.
5. Make the human report explain source selection, packet decisions, circuit transitions, suppressed calls, pending work, and terminal status.
