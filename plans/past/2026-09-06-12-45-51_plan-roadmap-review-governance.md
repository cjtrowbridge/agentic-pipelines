---
plan_id: 2026-09-06-12-45-51_plan-roadmap-review-governance
title: Require Roadmap Review During Every Plan Review
summary: Add a universal framework rule requiring plan reviews to evaluate the governing roadmap and recommend synchronized corrections for every discovered mismatch.
status: past
created_at: 2026-09-06-12-45-51
---

# Require Roadmap Review During Every Plan Review

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

- [x] 1. Add the universal review invariant.
  - [x] 1.1 Update `AGENTS.md` so every task-execution-plan review also reviews the governing roadmap.
    - [x] 1.1.1 Require the review to identify scope, status, sequence, dependency, deliverable, milestone, and acceptance mismatches and propose concrete changes to the plan, roadmap, or both.
    - [x] 1.1.2 Require approved plan and roadmap changes to remain synchronized in the same checkpoint, or leave an explicit unresolved mismatch when authority is unavailable.
- [x] 2. Verify and publish the framework change.
  - [x] 2.1 Regenerate framework plan indexes and validate the diff.
  - [x] 2.2 Record the completed governance checkpoint in the framework journal.
  - [x] 2.3 Commit and push the framework revision to `origin/main`.
- [x] 3. Propagate the published revision.
  - [x] 3.1 Update the parent repository's direct `agentic-pipelines` gitlink.
  - [x] 3.2 Update and publish the `iftf-thor-runtime` nested gitlink.
  - [x] 3.3 Initialize/update and publish the `iftf_ebe_runtime` nested gitlink without including unrelated worktree changes.
  - [x] 3.4 Record the two updated runtime revisions in the parent repository and push the parent gitlinks without including unrelated plan changes.
