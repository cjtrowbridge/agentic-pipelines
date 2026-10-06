# Agentic Pipelines

Agentic Pipelines is a prompt-first framework for using scarce cloud intelligence to design durable local-inference processes, then using abundant local compute to execute, review, repair, and analyze work at scale.

Its primary reusable assets are concise prompts and task-specific playbooks. The Python runtime, Ollama-compatible API adapter, SQLite state, validators, thread capture, and reports are shared supporting infrastructure.

Agentic Pipelines are mostly ordinary deterministic automation. Code governs exactness; models govern meaning; humans govern unresolved intent and risk; examples specify behavior. **LLMs are few-shot learners.** When trusted history exists, semantic stages should normally see bounded representative past inputs and accepted outputs followed by the new input, rather than an expanding handcrafted approximation of the demonstrated behavior. Every model step owns one coherent bounded decision with minimum sufficient context, precise output, scope-bound review, finite attempts, and captured evidence.

## Pipeline entry points

All commands run from the host repository root, where the framework is normally mounted at `./agentic-pipelines`. Start with the command matching the smallest action you need:

- `python agentic-pipelines/scripts/validate_pipeline_package.py path/to/staged-package`: validate a proposed pipeline package without inference or source mutation.
- `python agentic-pipelines/scripts/render_markdown_pdf.py path/to/document.md`: bootstrap the portable Unicode/emoji renderer and atomically regenerate the sibling PDF; see `playbooks/how_to_render_markdown_to_pdf.md` for its document profile.
- `python agentic-pipelines/scripts/pipeline.py preflight --api-config api.yaml`: validate the local, ignored API configuration before a model-backed operation.
- `python agentic-pipelines/scripts/pipeline.py discover ...`: register source or contract changes using deterministic discovery only.
- `python agentic-pipelines/scripts/pipeline.py run ...`: perform a bounded, resumable pipeline run; it invokes local inference only for declared LLM stages.
- `python agentic-pipelines/scripts/pipeline.py inspect-entity ...`: inspect state, evidence, and disposition for one entity without operating on unrelated entities.
- `python agentic-pipelines/scripts/pipeline.py report ...` and `analyze ...`: produce deterministic run reporting or bounded advisory analysis; `analyze` requires local API configuration when it invokes its declared analysis prompt.
- `python agentic-pipelines/scripts/pipeline.py retry-cohort ...` and `rollback-entity ...`: perform the explicit recovery actions described in the operation/retry playbooks.

These commands describe the framework reference runtime; an importing project may expose different interactive operations. Every host-declared operator entrypoint must have a host-owned VS Code task, and exactly one ordinary main entrypoint must be the primary Run/Debug play action. Both invoke the host's appropriate platform-native prerequisite/bootstrap script before its actual pipeline command. See `playbooks/how_to_set_up_pipeline_entrypoints_in_vscode.md`; the files under `templates/vscode/` are adaptable examples, not installable defaults. Direct commands remain available for CI, schedulers, and other automation.

Every importing project owns `scripts/bootstrap.py` as its stable setup and health-check command. It delegates to a host-selected versioned implementation such as `scripts/bootstrap-v1.py`. Run `python scripts/bootstrap.py --check` for read-only per-requirement results and final pass/fail totals. Run it without `--check` to inspect and repair declared requirements idempotently before pipeline work. See `playbooks/how_to_create_and_maintain_host_bootstrap.md`; `templates/bootstrap/` provides non-installable examples.

Every host pipeline must bootstrap before its own imports or source work: ensure the pinned framework is available, install only its declared requirements and declared local runtime dependencies into ignored host-local directories, then run preflight. The host's selected versioned bootstrap may invoke the reusable `bootstrap_pipeline_environment.py` helper without modifying system Python. For example, that implementation can call:

```powershell
python agentic-pipelines/scripts/bootstrap_pipeline_environment.py --host-root . --requirements requirements-pipeline.txt --requirements agentic-pipelines/requirements.txt --check-module yaml --playwright-browser chromium
```

The host's `scripts/bootstrap.py` remains the operator entrypoint for applying setup changes.

## How agents use the framework

Start with `AGENTS.md`. It explains the universal model and routes the current task to one playbook. That playbook names the minimum prompts, templates, references, evidence, and commands to load. Agents should not read unrelated workflows by default.

Prompt classes:

- `prompts/design/`: design a pipeline from a user goal;
- `prompts/generate/`: create and tighten host runtime prompts;
- `prompts/execute/`: local worker, review, repair, and adjudication stages;
- `prompts/analyze/`: entity, cohort, remediation, and performance analysis.

## Pipeline lifecycle

```text
user goal
â†’ cloud-assisted pipeline design
â†’ reviewed pipeline package
â†’ local bounded execution
â†’ deterministic validation and semantic review
â†’ accepted artifacts or quarantine
â†’ post-run failure/performance analysis
â†’ advisory remediation
â†’ approved sample validation and cohort retry
```

All model calls use one local API primitive and can produce redacted thread evidence. Workers write staged candidates; only declared validation and promotion may alter destinations.

Every execution also produces a machine report and human-readable run narrative, including success, failure, interruption, partial, resumed, and no-op outcomes. Each rejected generated candidate is saved byte-for-byte with no appended framework content and paired with a same-basename `.explanation.md` sidecar containing its hash, rejecting authority, code, reason, evidence, and retry disposition. These ignored files make retry loops and first-pass friction visible to later agents; they are untrusted evidence and can never become source material, examples, prompt instructions, rendered final output, or promotable content. See `references/run_evidence_and_continuous_improvement.md`.

After a governance-changing framework update, use `playbooks/how_to_audit_existing_pipeline_conformance.md` to inventory a host pipeline’s authority assignments and evidence behavior. The audit produces findings and a proposed host remediation plan without rewriting host-owned files.

Before integration, validate a generated package without inference or source mutation:

```powershell
python agentic-pipelines/scripts/validate_pipeline_package.py path/to/staged-package
```

The package must justify every LLM stage, map goals to specific verification, and contain no credentials. Package schemas 1–4 remain readable compatibility inputs; schema 5 is required to claim current coherent-semantic-unit governance because it declares example, session, review-scope, blocking-authority, lossy-intermediate, stage-split, and risk contracts. See `examples/markdown_repair/` for the fake-provider-tested vertical slice.

## Host layout

The framework is normally mounted at `./agentic-pipelines`:

```text
host/
â”œâ”€â”€ agentic-pipelines/  # submodule
â”œâ”€â”€ AGENTS.md           # routes to ./agentic-pipelines/AGENTS.md
â”œâ”€â”€ TODO.md             # sole host-owned human checklist
â”œâ”€â”€ pipeline.yaml       # host pipeline definition
â”œâ”€â”€ api.sample.yaml     # tracked host configuration template
â”œâ”€â”€ api.yaml            # ignored local endpoint/credentials
â”œâ”€â”€ prompts/            # host-owned/customized runtime prompts
â”œâ”€â”€ plans/              # host change plans
â”œâ”€â”€ journal/            # design metaconversation/checkpoints
â”œâ”€â”€ state/              # ignored runtime state
â”œâ”€â”€ artifacts/          # ignored candidates/results
â”œâ”€â”€ threads/            # ignored API evidence
â””â”€â”€ reports/            # ignored run/post-run reports
```

The framework never overwrites host-owned prompts, `TODO.md`, plans, journal, credentials, state, artifacts, threads, or reports during bootstrap or updates.

## Local inference configuration

During framework bootstrap, copy the framework `api.sample.yaml` to a tracked `api.sample.yaml` in the host root. The operator then copies that host sample to ignored `api.yaml`, supplies the local Ollama-compatible endpoint/model and any local gateway credential, and runs:

```powershell
python agentic-pipelines/scripts/pipeline.py preflight --api-config api.yaml
```

The runtime has no silent cloud fallback. Never commit `api.yaml` or runtime evidence.

Hosts using Ollama directly can create named context variants for their measured stage budgets. See `playbooks/how_to_create_ollama_context_aliases.md` for 1k, 4k, 64k, 96k, and verified upper-context examples. Keep each stage's request-level `num_ctx` aligned with its selected alias; this runtime sends that option on every model request.

For a local Docker Ollama container, `scripts/ensure_ollama_context_aliases.py` provides the host bootstrap with a read-only `--check` and an idempotent creation command. Alias names follow `[hostname]-[context]-[model name]`, such as `cj-desktop-96k-qwen3.8:27b`. The host selects the model and contexts with repeatable `--context` arguments; see the playbook for the complete command and bootstrap wiring.

Deterministic commands such as `discover`, `inspect-entity`, and `report` do not require API configuration. `run` and `analyze` require the ignored local config because they may invoke declared LLM stages.

## Current status

The router, focused playbooks, typed prompt catalog, authority/evidence contracts, staged-package validator, shared local API, rejected-candidate preservation, machine and human run reports, redacted thread capture, schema-v3 stateful runner, exact validation, bounded semantic review/repair, safe promotion, failure cohorts, advisory trajectory analysis, consumer conformance review, and fake-provider Markdown reference pipeline are implemented. A real local Ollama smoke test and broader model calibration remain operator-local validation work tracked under `plans/current/`.

## Key paths

- Task router: `AGENTS.md`
- Prompt catalog: `prompts/README.md`
- Playbooks: `playbooks/`
- Prompt/output contracts: `schemas/`, `templates/`, `references/`
- Runtime: `pipeline_runtime/`, `scripts/pipeline.py`
- Architecture: `docs/prompt_first_product_model.md`
