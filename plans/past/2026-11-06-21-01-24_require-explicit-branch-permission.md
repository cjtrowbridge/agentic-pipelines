---
plan_id: 2026-11-06-21-01-24_require-explicit-branch-permission
title: Require explicit permission before branch creation or planning
summary: Establish canonical branch permission policy and publish on the existing framework branch.
status: past
created_at: 2026-11-06-21-01-24
---

# Require explicit permission before branch creation or planning

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

Authority: User explicitly requested this canonical rule, commit and push on 2026-11-06.
This narrow framework policy task is independent of existing host/runtime plans.

- [x] 1. Establish branch permission governance.
  - [x] 1.1 Add a canonical high-priority rule to AGENTS.md covering creation and planning, including indirect creation and the limits of implied authority.
  - [x] 1.2 Link planning instructions to the canonical rule.
- [x] 2. Verify and publish the policy.
  - [x] 2.1 Review the scoped diff and run the staged source-governance gate.
  - [x] 2.2 Record the host journal checkpoint, archive the completed policy plan, and regenerate framework indexes.
  - [x] 2.3 Prepare task-scoped staging and existing-branch commit/push commands; preserve parent work and report delivery from Git results.

## Authorized publication correction — 2026-11-06

User approved publishing on existing framework `main` and committing/pushing the parent submodule pointer while preserving unrelated work. This supersedes the earlier checkpoint-branch publication target.

- [x] 3. Prepare corrected publication.
  - [x] 3.1 Fetch framework remote and compare histories: remote main is ancestor of `f73335d`; retain the already-checked-out source-governance fix `763aed0` and rule `f73335d` by fast-forwarding existing main.
  - [x] 3.2 Run focused governance tests: 20 of 21 passed; Go hook regression cannot pass because this host has no `go` executable. No source code changed in this correction.
  - [x] 3.3 Record correction and prepare staged governance checks and publication commands for existing main in both repositories; parent commit must include only `agentic-pipelines`, preserving its pre-existing staged archive changes.

Commit/push success is established by live Git results, not by these preparation checkboxes. No new branches or worktrees are needed; the checkpoint branch remains intact. Parent roadmap/runtime scope and maturity are unchanged by this publication correction.
