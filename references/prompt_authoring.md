# Prompt Authoring: Terse but Complete

A prompt owns one model job. Include only: objective, declared inputs, protected invariants, permitted action, exact output contract, and stop/uncertainty behavior.

Before writing a prompt, prove that the job requires an LLM. Prefer a trusted tool, parser, query, shell command, or small program whenever it can perform the step reliably. A model is appropriate only for a narrow semantic transformation or judgment whose ambiguity cannot be removed deterministically. Do not use inference for file selection, routing, parsing, counting, comparison, state transitions, policy, promotion, or other exact operations.

Put procedures in playbooks, shared concepts in references, output shapes in schemas/templates, and deterministic rules in code/configuration. Link those artifacts; do not restate them.

Review every prompt for:

- no undeclared inputs or unresolved placeholders;
- no repeated project philosophy or repository governance;
- no authority to change pipeline policy, credentials, tools, paths, source, or retry scope;
- facts, hypotheses, confidence, and unknowns separated when analysis is involved;
- machine-readable output validated before state changes;
- critical constraints preserved after compression.
- the job cannot be replaced by deterministic logic, and the prompt receives no context beyond that job.

Prefer a shorter prompt only when it remains behaviorally complete. Concision is the removal of irrelevant or duplicated context, not the removal of safeguards.

## Placement decision

| Content | Put it in |
| --- | --- |
| One model invocation's objective and constraints | Prompt |
| Ordered human/agent workflow | Playbook |
| Concept reused across workflows | Reference |
| Exact response/document shape | Schema or template |
| Fast objective acceptance rule | Deterministic validator |
| Universal task routing or safety invariant | `AGENTS.md` |

## Compression example

Verbose: “You are an expert editor working in our sophisticated pipeline system. It is very important to remember that our project values safety. Please carefully read the post below, take your time, and attempt to repair it. You should not change things unnecessarily.”

Complete and terse: “Repair only the declared Markdown violations in `source_entity`. Preserve `protected_invariants`. Return `repair_result`; if safe repair is impossible, return `status: unable` with unresolved violation IDs.”

The shorter form removes role theater and repeated philosophy while adding explicit inputs, scope, output, and stop behavior.

