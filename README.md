# Pipelines

Pipelines is a prompt-first framework for using scarce cloud intelligence to design durable local-inference processes, then using abundant local compute to execute, review, repair, and analyze work at scale.

Its primary reusable assets are concise prompts and task-specific playbooks. The Python runtime, Ollama-compatible API adapter, SQLite state, validators, thread capture, and reports are shared supporting infrastructure.

Pipelines are mostly ordinary deterministic automation. File discovery, parsing, filtering, routing, comparison, validation, state transitions, and promotion should use code or standard tools such as shell commands whenever they can. An LLM belongs only at a narrow step that genuinely requires semantic interpretation or generation. Every such step receives the minimum necessary context and is constrained by a precise output contract, deterministic gates, finite attempts, and captured evidence.

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

Copy `api.sample.yaml` to ignored `api.yaml`, supply the local Ollama-compatible endpoint/model and any local gateway credential, then run:

```powershell
python pipelines/scripts/pipeline.py preflight --api-config api.yaml
```

The runtime has no silent cloud fallback. Never commit `api.yaml` or runtime evidence.

Deterministic commands such as `discover`, `inspect-entity`, and `report` do not require API configuration. `run` and `analyze` require the ignored local config because they may invoke declared LLM stages.

## Current status

The router, focused playbooks, typed prompt catalog, strict output schemas, staged-package validator, shared local API, redacted evidence capture, schema-v2 stateful runner, deterministic validation, bounded semantic review/repair, safe promotion, failure cohorts, advisory post-run analysis, and fake-provider Markdown reference pipeline are implemented. A real local Ollama smoke test and broader model calibration remain operator-local validation work tracked under `plans/current/`.

## Key paths

- Task router: `AGENTS.md`
- Prompt catalog: `prompts/README.md`
- Playbooks: `playbooks/`
- Prompt/output contracts: `schemas/`, `templates/`, `references/`
- Runtime: `pipeline_runtime/`, `scripts/pipeline.py`
- Architecture: `docs/prompt_first_product_model.md`

