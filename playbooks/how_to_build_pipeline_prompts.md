# Playbook: Build Pipeline Prompts

## Use when
Creating or revising transformation, self-audit, request-aware review, independent high-assurance review, repair, adjudication, or analysis prompts.

## Load
The relevant generator under `prompts/generate/`, `references/prompt_authoring.md`, `references/deterministic_and_semantic_authority.md`, target schemas, entity/goal contracts, example strategy, and review-risk decision.

## Procedure
1. Reject exact work. Do not reject genuine semantic work merely because a lexical, similarity, embedding, label, or handcrafted proxy approximates it.
2. Give one prompt one coherent semantic decision with minimum sufficient sources, bounded trusted demonstrations, invariants, allowed transformation, exact output, scope, and inability behavior. Record example authority and omissions.
3. Treat one entity decision as one retained session by default. Supply stable context once; retain candidate output; append concise trusted audit or exact-validator feedback. Split sessions only for declared risk, isolation, provider/context, reuse, or measured-quality reasons.
4. Declare a completion-token limit (`num_predict`) and context-window limit (`num_ctx`). Size `num_ctx` from the measured complete session plus completion reserve; never mistake `num_predict` for a context/KV-cache limit. Reasoning is opt-in; disable it for clear, constrained transformations with representative examples.
5. Scope routine self-audit to the declared goal. Scope revision review to the exact delta and direct consequences; supported operator intent is blocking within policy and broader preference is advice. Independent review requires a high-assurance justification.
6. Declare a finite session-step budget and finite stage retry budget; count transport/schema retries separately. Preserve rejected output and evidence; include that reason with the unchanged original inputs as a concise trusted summary. Stop on repeated/changing feedback without progress.
7. Keep governance exposition out of runtime prompts; version, lint, and test normal, ambiguous, adversarial, context-reduction, scope-escape, and first-attempt cases.

## Output and verification
A lint-clean versioned prompt with fixtures, measured limits, example/session/review declarations, and LLM justification. Reject semantic laundering, undeclared inputs, prose-only machine outputs, lossy source substitution, authority expansion, or removed critical constraints.
