# Prompt Authoring: Terse but Complete

A prompt owns one coherent semantic decision. Include only its objective, minimum sufficient inputs, trusted demonstrations, protected invariants, permitted action, exact output contract, review scope, and stop/uncertainty behavior.

Before writing a prompt, prove that the job requires meaning. Use a trusted tool, parser, query, shell command, or small program for exact file selection, routing, parsing, counting, state transitions, policy enforcement, promotion, or other mechanically decidable work. Comparison, extraction, matching, ranking, selection, and transformation remain semantic when correctness depends on meaning; never replace them with deterministic proxies that merely look rigorous.

Use minimum sufficient context, not merely the fewest bytes. Include stable source context and bounded representative past input/accepted-output pairs when they materially demonstrate the desired ontology, selection, abstraction, output relationships, tone, or boundaries. Declare example authority and provenance. Exclude rejected or untrusted artifacts and record whole-example omission under the packet budget.

Do not split one coherent decision into semantic microstages merely to make intermediate labels easier to validate. Split only for a declared risk, isolation, provider/context, reuse, or measured-quality reason. Treat lossy semantic intermediates as derivatives, never silent source replacements.

Review every prompt for:

- declared inputs and resolved placeholders;
- one bounded coherent decision and no authority outside it;
- exact output and inability contracts;
- facts, hypotheses, confidence, and unknowns separated when needed;
- representative examples plus concise invariants instead of exhaustive behavioral prose;
- schema validation before state changes without semantic laundering;
- reviewer scope limited to the current goal or requested delta;
- retry feedback as a concise trusted summary, never rejected content re-ingested as instructions;
- critical constraints retained after compression.

Use a retained session for source, candidate, audit, and bounded repair by default. Fresh-session independent review requires a risk or empirical justification. A revision prompt receives the accepted baseline, exact request, and necessary factual authority; broader reviewer preference is advisory.

| Content | Canonical owner |
| --- | --- |
| One invocation's objective, examples, constraints, and scope | Prompt |
| Ordered human/agent workflow | Playbook |
| Reusable concept | Reference |
| Exact response shape | Schema/template |
| Exact acceptance rule | Deterministic validator |
| Cross-version semantic quality | Golden evaluation set |
| Universal routing or safety invariant | `AGENTS.md` |

Prefer shorter prompts only when behavior remains complete. Concision removes irrelevant or duplicated context; it does not remove evidence, demonstrations, safeguards, or semantic coherence.
