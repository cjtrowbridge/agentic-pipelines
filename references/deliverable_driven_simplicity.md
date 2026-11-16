# Deliverable-driven simplicity

Deliver the required experience with the fewest interacting mechanisms, then improve it through measured, bounded iteration. Optimize understandable execution and failure behavior, not line count. This guidance applies to planning, implementation and review; it does not require a pipeline runtime for ordinary development.

## Plan a coherent outcome

State the observable outcome, protected behavior, simplest path through existing code, material uncertainty, acceptance evidence and stopping condition. Decompose only to resolve uncertainty, expose a necessary dependency or separate an independently verifiable outcome. Stop when the next useful implementation and verification step is clear. Checklist items do not imply components, services, interfaces, agents or additional plans. Preserve host roadmap/plan mappings; a requirement plan can be short and link shared evidence.

Approval binds outcomes and material constraints. Record routine implementation adjustments within that scope without repeatedly requesting approval. Ask when behavior, authority, irreversible actions, material cost or scope changes. Existing user authorization persists. Preserve branch and other explicit permission boundaries.

## Implement a direct path

Start with concrete data, ordinary functions and explicit control flow. Give mutable state one clear owner. Prefer one authoritative representation; derived caches need explicit invalidation and lifetime. Keep small duplication when a shared abstraction would couple independent behavior. Explain a new abstraction by the existing requirement it simplifies.

Remove unnecessary work before accelerating it: eliminate, precompute, reduce frequency, or limit work to what is needed. Justify concurrency with an actual blocking operation or measured throughput need. Name state ownership, maximum outstanding work, result ordering, stale-result handling and shutdown behavior in a short explanation. Do not add a queue, worker pool, retry layer or event bus speculatively.

Validate external data at boundaries and retain meaningful internal invariants. Every blocking check must establish a relevant property and have a clear failure outcome. A fallback must not conceal failure or change required behavior. Preserve compatibility, accessibility and recovery; simplicity does not excuse deleting requirements.

## Review to remove mechanisms

Trace a complete user or entity path, including failure and interruption. Look for duplicate decisions, overlapping validation, multiple sources of truth, avoidable conversions, stale caches and undocumented ordering. Check logical ordering separately from data-race freedom. Prefer local simplification over a new general subsystem. Reviewer preferences are advisory unless they establish a requirement violation; tests should protect behavior rather than freeze implementation structure.

Apply existing explicit source/build policies where present. File-length limits are not proof of simplicity: satisfy required decomposition with cohesive local responsibilities, not gratuitous interfaces. Propose a separately authorized policy change if a binding gate demonstrably worsens the outcome; never bypass it silently.

## Measure and close the loop

Select metrics for the delivered experience: startup and input latency; frame-time tails/stalls; peak and retained memory/allocations; I/O and energy; artifact size; or accepted-output quality, false rejection, attempts, latency and inference/evidence costs. Do not require every metric for every change. Record revision, environment/device, workload, configuration, method and unavailable measurements. Establish budgets from user needs and representative hardware, not arbitrary universal thresholds.

Reproduce -> measure -> identify a likely cause -> change one coherent mechanism -> check correctness -> repeat under comparable conditions -> retain or revert. Distinguish observations, calculations, hypotheses and unknowns. Repeat enough to assess noise; report instrumentation overhead. Local bounded diagnostics can precede any remote collection decision. No telemetry or inference service is implied by this workflow.

Every material finding receives a disposition: fix within authorized scope, defer to an identified requirement with a reason, reject for insufficient evidence/benefit, or record that the current solution meets the need. A selected improvement records baseline, expected benefit, regression checks, comparison method and final disposition in the existing plan/report. Recommendations remain advisory until authorized; this loop grants no automatic retries or mutations.

Stop when acceptance and relevant budgets are met, uncertainty is documented, and added complexity has no demonstrated worthwhile benefit. Do not manufacture optimization work or universal complexity scores.

## Worked example: STMPCK previews

STMPCK replaced runtime game demonstrations and move searches in its gallery with development-time captures from the actual rules/renderer. Runtime playback uses visible cards, a bounded cache, one background decode and poster fallback. Its recorded same-host browser sample improved median frame time from 83.50 ms to 17.04 ms and p99 from 149.88 ms to 17.26 ms. These are historical browser observations, not phone/GPU/energy evidence. The lesson is removal of runtime work with explicit asset/memory tradeoffs, not a requirement that every project use sprites.

## Scenario review

Use these as semantic review cases, not keyword tests or mandatory model calls:

| Scenario | Expected decision | Reject |
| --- | --- | --- |
| Small local behavior change | Short outcome/acceptance plan and proportionate check | Recursive workstreams and speculative shared architecture |
| Slow gallery running simulations | Compare removing/precomputing work before scheduling it | Worker pool without workload evidence |
| Lifecycle saves with two callers | Inspect snapshot selection and write ordering; test the relevant interleaving | Treating a mutex or clean race report as proof of newest-state persistence |
| Repeated false rejection in a model pipeline | Check gate authority and earliest cause; measure quality and attempts | Additional reviewers/retries that conceal the original defect |
| Budgets met, no material defects | Record no change and stop | Inventing optimization work to keep the loop active |

Record actual outcomes and limits when applying these cases. Structural document checks cannot prove future agent behavior.
