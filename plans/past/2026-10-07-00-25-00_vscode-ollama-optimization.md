---
plan_id: 2026-10-07-00-25-00_vscode-ollama-optimization
title: VS Code and Ollama optimization playbook
summary: Require q8_0 KV cache and 45-minute VS Code inference timeouts with measured prefix reuse.
status: past
created_at: 2026-10-07-00-25-00
---

# VS Code and Ollama optimization playbook

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

User authorization: create a playbook mandating Q8 KV cache and 45-minute VS Code inference timeouts.

- [x] Document exact settings, cache residency/prefix reuse and installed-provider verification.
- [x] Route the playbook from AGENTS.md and link local-inference guidance.
- [x] Verify links/settings against primary sources and record the documentation-only checkpoint.

No host settings, containers, provider extensions or runtime residency policies are changed by this playbook authoring task.

Verification: 18 existing router/documentation tests pass and git diff --check passes. Official Ollama VS Code package declares inferenceTimeoutMinutes (1-60 minutes) and the converter multiplies by 60000; the documented value 45 is 2700000 milliseconds. Official Ollama FAQ supports q8_0 and Flash Attention/residency controls. The operator-reported 20K prefix is recorded as workflow context, with live cold/warm measurement still host-owned. No live configuration was applied.
