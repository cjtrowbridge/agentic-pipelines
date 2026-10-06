---
plan_id: 2026-10-05-18-14-24_docker-ollama-context-alias-manager
title: Standardize Docker Ollama context alias names and provisioning
summary: Add a canonical, idempotent Docker Ollama alias script using hostname-context-model names and integrate it with host bootstrap guidance.
status: past
created_at: 2026-10-05-18-14-24
---

# Standardize Docker Ollama context alias names and provisioning

Key: `[ ]` pending task, `[x]` completed task, `[?]` needs validation, `[-]` closed task

Authority: proposed from the user's 2026-10-05 request; implementation approved by the user on 2026-10-05.

- [x] 1. Define the alias contract.
  - [x] 1.1 Specify `[hostname]-[context]-[model name]`, with a deterministic hostname normalization, Ki-token context labels, and preservation of the base model's Ollama name/tag syntax; document examples and collision handling.
  - [x] 1.2 Define missing, matching, conflicting, unavailable-container, missing-base, and unsupported-context outcomes without silent replacement or automatic model pulls.
- [x] 2. Add the canonical Docker Ollama alias script.
  - [x] 2.1 Add `scripts/ensure_ollama_context_aliases.py` with simple model, repeatable context, and container arguments; support a read-only `--check` for host bootstrap probes.
  - [x] 2.2 Verify the named local Docker container and its published Ollama endpoint, inspect the base and requested aliases, create only missing aliases through the local Ollama API, and recheck each creation. Use finite timeouts, standard-library dependencies, visible per-alias results and totals, and controlled interruption.
  - [x] 2.3 Refuse mismatched or unverifiable existing aliases and protect against path, name, and endpoint ambiguity; avoid changing unrelated models or host settings.
- [x] 3. Integrate the script with framework guidance.
  - [x] 3.1 Update the Ollama alias playbook and root README with the new naming structure, exact script invocation, context selection, Docker assumptions, and bootstrap probe/repair wiring.
  - [x] 3.2 Align host bootstrap guidance and any affected routing/reference documentation without changing host-owned files or credentials.
- [x] 4. Verify and checkpoint.
  - [x] 4.1 Add isolated fake-Docker/fake-Ollama tests for naming, argument validation, read-only check, missing-only creation, repeat-run idempotence, collisions, API/transport failure, counts, and interruption.
  - [x] 4.2 Run focused tests and syntax/link/whitespace checks; update plan and indexes, journal, and review the diff and status.
  - [x] 4.3 Move detailed bootstrap and alias contracts into focused references, keep both routed playbooks under 350 words, and rerun the full test suite before publication.

No framework ROADMAP.md exists. The existing PDF plan remains separate. Live Docker/Ollama provisioning is host-local validation and will not be run in this framework checkpoint without an approved host configuration.

## Review checkpoint

- The script uses the selected local Docker container's published Ollama port and the documented `/api/tags`, `/api/show`, and `/api/create` endpoints. It uses only standard-library Python and does not pull, delete, or replace models.
- Fake Docker/Ollama tests cover naming, local endpoint checks, missing-only creation, repeat idempotence, existing alias context/source conflicts, missing base, oversized context, transport failure, counts, and interruption. The full repository suite passed: 84 tests, one skipped. Syntax, plan-index, and whitespace checks passed. Detailed host-bootstrap and Ollama alias contracts now live in focused references; routed playbooks meet the length gate.
- No live Docker/Ollama instance was changed or validated in this framework checkout. A host bootstrap must supply the actual container, base model, and selected contexts and perform its own live check.
