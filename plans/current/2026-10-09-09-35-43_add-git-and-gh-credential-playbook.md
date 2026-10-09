---
plan_id: 2026-10-09-09-35-43_add-git-and-gh-credential-playbook
title: Add a Routed Playbook for git/gh Credentials in Agent Shells
summary: Route and document the canonical way for agent shells to authenticate git and gh so push failures stop recurring as one-off conversations.
status: current
created_at: 2026-10-09-09-35-43
---

# Add a Routed Playbook for git/gh Credentials in Agent Shells

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

- [ ] 1. Author the playbook.
  - [ ] 1.1 Create `playbooks/how_to_use_git_and_gh_credentials_in_agent_shells.md` covering the non-interactive constraint, the canonical `gh auth login --web` device flow, `gh auth setup-git`, verification, and the never-commit-secrets guardrail.
  - [ ] 1.2 State the failure signature (`credential.interactive=never`, `unable to get password from user`) and why IDE interactive prompts do not satisfy an agent shell.
- [ ] 2. Route the playbook.
  - [ ] 2.1 Add a task-table row in `AGENTS.md` mapping the credential/push-failure task to the new playbook.
  - [ ] 2.2 Add the ownership statement to `playbooks/README.md` so the playbook is an active, non-duplicated instruction.
- [ ] 3. Verify and publish the framework change.
  - [ ] 3.1 Regenerate framework plan indexes and validate the diff.
  - [ ] 3.2 Record the completed checkpoint in the framework journal.
  - [ ] 3.3 Commit and push the framework revision to `origin/main`.
- [ ] 4. Propagate the published revision.
  - [ ] 4.1 Advance the `iftf_rpicap_runtime` submodule gitlink to the new framework commit and publish it.
