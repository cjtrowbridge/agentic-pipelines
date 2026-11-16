---
plan_id: 2026-11-12-11-19-14_add-ollama-performance-playbook
title: Add Routed Playbook and Reference for Ollama Cache/Performance Optimization
summary: Route a thin playbook to a deep reference that defines structural Ollama optimizations, required telemetry fields, metric formulas, and a controlled benchmark suite, with concrete tests co-located per optimization.
status: current
created_at: 2026-11-12-11-19-14
---

# Add Routed Playbook and Reference for Ollama Cache/Performance Optimization

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

- [x] 1. Author the reference.
  - [x] 1.1 Create `references/ollama_performance_optimizations.md` with the metric definitions (theoretical reusable prefix, actual reused, cache efficiency), telemetry field contract, prefix fingerprinting rules, structural diagnostic classification, metric formulas, and the controlled benchmark suite.
  - [x] 1.2 Add a per-optimization `Verify` test to every structural optimization entry.
  - [x] 1.3 Add the `prompt_eval_duration` subtlety and the disk-cache distinction as required caveats.
  - [x] 1.4 Add a verification summary table mapping each optimization to its test.
- [x] 2. Author the playbook.
  - [x] 2.1 Create `playbooks/how_to_optimize_ollama_performance.md` with `## Use when`, `## Load`, `## Required behavior`, and `## Procedure` sections; keep the body under 350 words and cite the reference as the sole authority for depth.
  - [x] 2.2 Ensure the playbook's procedure instructs the agent to run the per-optimization verification tests and record pass/fail evidence, and to record remaining blockers without claiming unsupported success.
- [x] 3. Update ownership and routing.
  - [x] 3.1 Add the ownership statement to `references/README.md`.
  - [x] 3.2 Add a task-table row in `AGENTS.md` mapping the cache/performance-optimization task to the new playbook.
  - [x] 3.3 Cross-link `how_to_optimize_vscode_and_ollama.md` to the new playbook where its scope overlaps (Q8 KV cache and inference timeouts remain owned by the VS Code playbook).
- [ ] 4. Verify and publish.
  - [x] 4.1 Run `python3 -m unittest tests.test_playbooks tests.test_documentation` and confirm no new failures. **Result:** 16/17 pass. The single failure (`test_routed_playbooks_are_small_and_structured` on `playbooks/how_to_optimize_vscode_and_cerebras.md`, 363 words) is pre-existing — that file is committed at 363 words in `main` and was not touched by this plan. The new playbook `how_to_optimize_ollama_performance.md` is 205 words and satisfies both structural assertions.
  - [x] 4.2 Regenerate framework plan indexes with `python3 scripts/regenerate_plan_indexes.py`.
  - [ ] 4.3 Record the checkpoint in today's journal.
  - [ ] 4.4 Propose a task-scoped commit; commit and push only with explicit approval.

## Authoring Rules

- The reference is the sole authority for depth. The playbook must remain a thin router: no configuration examples, no metric formulas, no test code.
- Do not duplicate Q8 KV cache or 45-minute timeout requirements; those remain owned by `playbooks/how_to_optimize_vscode_and_ollama.md` and `references/vscode_ollama_configuration.md`.
- Do not add fleet deployment tooling (Docker compose, Grafana, PostgreSQL, DCGM) to the framework. The reference names the telemetry contract; the host owns deployment.
- Do not treat `prompt_eval_cached_count` absence as zero. The reference must keep the unknown/zero distinction explicit.
- The playbook's body (including headers) must stay under 350 words to satisfy `tests.test_playbooks.PlaybookTests.test_routed_playbooks_are_small_and_structured`.
