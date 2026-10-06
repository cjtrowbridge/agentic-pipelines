---
plan_id: 2026-10-05-17-46-28_ollama-context-alias-guidance
title: Guide Ollama context aliases for host pipelines
summary: Document host-owned Ollama model aliases with measured context selection and clarify request-level overrides.
status: past
created_at: 2026-10-05-17-46-28
---

# Guide Ollama context aliases for host pipelines

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

Authority: user approved a scoped plan and playbook with documentation links on 2026-10-05. No runtime change was requested.

- [x] 1. Publish host-facing context-alias guidance.
  - [x] 1.1 Add a playbook with a repeatable Modelfile/create procedure for 1k, 4k, 64k, 96k, and a verified large-context alias.
  - [x] 1.2 Explain context sizing, model limit versus chosen operating cap, request-level `num_ctx` precedence, resource implications, verification, and host ownership.
  - [x] 1.3 Route the new task from `AGENTS.md` and link it from local inference documentation and the root README.
- [x] 2. Verify and checkpoint the documentation change.
  - [x] 2.1 Check examples against official Ollama documentation and verify links, plan/index consistency, and whitespace.
  - [x] 2.2 Update plan state and indexes, record today's journal checkpoint, and review the final diff and status.

No framework ROADMAP.md exists. This documentation scope adds no host delivery milestone. The existing PDF plan remains a separate active plan.

## Review checkpoint

- Ollama's current Modelfile and context-length documentation supports `FROM`, `PARAMETER num_ctx`, `ollama create -f`, `ollama show --modelfile`, and `ollama ps`. The model listing reports 256K for `qwen3.8:27b` as of 2026-10-05.
- The reference runner uses one configured model and generation setting; the shared API adapter also accepts explicit per-request overrides. The guidance records this distinction.
- `python -m unittest tests.test_documentation` passed (16 tests). `git diff --check` passed. Ollama CLI is unavailable in this workspace, so live alias creation and hardware measurements remain host-local verification, not a claim of completed runtime validation.
