# Playbook: Build Pipeline Prompts

## Use when
Creating or revising worker, self-review, independent review, repair, adjudication, failure-analysis, or performance-analysis prompts.

## Load
The relevant generator under `prompts/generate/`, `references/prompt_authoring.md`, the target output schema, entity/goal contracts, and no unrelated playbook.

## Procedure
1. Reject the prompt request if a trusted tool, parser, query, shell command, or small program can reliably perform the job.
2. Give a necessary LLM call one semantic job, declared minimal inputs, allowed transformation, protected invariants, exact output schema, and stop conditions.
3. Keep governance and repeated project exposition out of runtime prompts.
4. Keep reviewers independent from worker hidden reasoning.
5. Version the prompt, validate metadata/schema references, and run compression/completeness review.
6. Test normal, missing-input, adversarial-input, and ambiguous cases before activation.

## Output and verification
A lint-clean versioned prompt with fixtures and a recorded LLM justification. Reject deterministic jobs, undeclared inputs, prose-only machine outputs, authority to change pipeline policy, or removed critical constraints.
