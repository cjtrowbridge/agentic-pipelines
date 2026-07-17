# Playbook: Build Pipeline Prompts

## Use when
Creating or revising worker, self-review, independent review, repair, adjudication, failure-analysis, or performance-analysis prompts.

## Load
The relevant generator under `prompts/generate/`, `references/prompt_authoring.md`, the target output schema, entity/goal contracts, and no unrelated playbook.

## Procedure
1. Reject the prompt request if a trusted tool, parser, query, shell command, or small program can reliably perform the job.
2. Give a necessary LLM call one semantic job, declared minimal inputs, allowed transformation, protected invariants, exact output schema, a completion-token limit (`num_predict`), a context-window limit (`num_ctx`), and stop conditions. Size `num_ctx` from a measured maximum assembled request plus the completion budget; never rely on a model's advertised maximum context, and never mistake `num_predict` for a context/KV-cache limit. Treat reasoning as opt-in: require a stage-specific justification, and disable it for clear, constrained transformations with representative examples.
2.1 Treat one entity's pipeline instance as one interactive session by default: supply stable source context once, retain the prior model response, and append concise trusted validator/reviewer feedback for each bounded next step. Start fresh only for a declared reason—independent review, security/isolation, or provider limits. Declare a finite session-step budget and a finite stage retry budget. A transport/API or parse/schema/validator retry is not a new session step; log its reason, include that reason with the unchanged original inputs, append corrective feedback, and never silently coerce an invalid result into acceptance.
3. Keep governance and repeated project exposition out of runtime prompts.
4. Keep reviewers independent from worker hidden reasoning.
5. Version the prompt, validate metadata/schema references, and run compression/completeness review.
6. Test normal, missing-input, adversarial-input, and ambiguous cases before activation.

## Output and verification
A lint-clean versioned prompt with fixtures and a recorded LLM justification. Reject deterministic jobs, undeclared inputs, prose-only machine outputs, authority to change pipeline policy, or removed critical constraints.
