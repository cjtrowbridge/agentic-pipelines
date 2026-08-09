# Agentic Pipelines

Agentic Pipelines is a prompt-first framework for using scarce cloud intelligence to design durable local-inference processes, then using abundant local compute to execute, review, repair, and analyze work at scale.

Its primary reusable assets are concise prompts and task-specific playbooks. The Python runtime, Ollama-compatible API adapter, SQLite state, validators, thread capture, and reports are shared supporting infrastructure.

Agentic Pipelines are mostly ordinary deterministic automation. Exact discovery, parsing, filtering, routing, validation, state transitions, and promotion use code or standard tools whenever they can establish the required property. Meaning, entailment, equivalence, relevance, and qualitative fitness use bounded semantic or human judgment; deterministic heuristics may route those questions but cannot issue semantic verdicts. Every model step receives minimum necessary context and is constrained by a precise output contract, exact gates, finite attempts, and captured evidence.

## Pipeline entry points

All commands run from the host repository root, where the framework is normally mounted at `./pipelines`. Start with the command matching the smallest action you need:

- `python pipelines/scripts/validate_pipeline_package.py path/to/staged-package`: validate a proposed pipeline package without inference or source mutation.
- `python pipelines/scripts/pipeline.py preflight --api-config api.yaml`: validate the local, ignored API configuration before a model-backed operation.
- `python pipelines/scripts/pipeline.py discover ...`: register source or contract changes using deterministic discovery only.
- `python pipelines/scripts/pipeline.py run ...`: perform a bounded, resumable pipeline run; it invokes local inference only for declared LLM stages.
- `python pipelines/scripts/pipeline.py inspect-entity ...`: inspect state, evidence, and disposition for one entity without operating on unrelated entities.
- `python pipelines/scripts/pipeline.py report ...` and `analyze ...`: produce deterministic run reporting or bounded advisory analysis; `analyze` requires local API configuration when it invokes its declared analysis prompt.
- `python pipelines/scripts/pipeline.py retry-cohort ...` and `rollback-entity ...`: perform the explicit recovery actions described in the operation/retry playbooks.

These commands describe the framework reference runtime; an importing project may expose different interactive operations. Every host-declared operator entrypoint must have a host-owned VS Code task, and exactly one ordinary main entrypoint must be the primary Run/Debug play action. Both invoke the host's appropriate platform-native prerequisite/bootstrap script before its actual pipeline command. See `playbooks/how_to_set_up_pipeline_entrypoints_in_vscode.md`; the files under `templates/vscode/` are adaptable examples, not installable defaults. Direct commands remain available for CI, schedulers, and other automation.

Every host pipeline must bootstrap before its own imports or source work: ensure the pinned framework is available, install only its declared requirements and declared local runtime dependencies into ignored host-local directories, then run preflight. The reusable helper supports that contract without modifying system Python:

```powershell
python pipelines/scripts/bootstrap_pipeline_environment.py --host-root . --requirements requirements-pipeline.txt --requirements pipelines/requirements.txt --check-module yaml --playwright-browser chromium
```

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
python pipelines/scripts/validate_pipeline_package.py path/to/staged-package
```

The package must justify every LLM stage, map goals to specific verification, and contain no credentials. See `examples/markdown_repair/` for the fake-provider-tested vertical slice.

## Host layout

The framework is normally mounted at `./pipelines`:

```text
host/
â”œâ”€â”€ pipelines/          # submodule
â”œâ”€â”€ AGENTS.md           # routes to ./pipelines/AGENTS.md
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
python pipelines/scripts/pipeline.py preflight --api-config api.yaml
```

The runtime has no silent cloud fallback. Never commit `api.yaml` or runtime evidence.

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
