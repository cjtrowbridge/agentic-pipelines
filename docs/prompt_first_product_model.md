# Prompt-First Product Model

## North star

Pipelines is primarily a library of concise, complete prompts and task-specific playbooks for designing, operating, reviewing, and improving local agentic pipelines. Templates and references supply shared contracts and concepts. Runtime code is a reusable execution substrate beneath that product surface.

An agent should load the universal router, identify its task, and then load only the playbook and supporting artifacts required for that task. An agent configuring Ollama does not need cohort-remediation procedure; an agent reviewing one entity does not need framework-maintenance or host-bootstrap policy.

## Product hierarchy

1. `AGENTS.md` is the concise universal model, safety kernel, and task router.
2. `playbooks/` owns task procedures and tells agents exactly what additional context to load.
3. `prompts/` owns executable reasoning/transformation instructions.
4. `templates/` and schemas own output shapes and machine contracts.
5. `references/` owns reusable concepts shared by multiple playbooks or prompts.
6. `pipeline_runtime/` and `scripts/` execute validated prompt-defined pipelines.
7. Run state, artifacts, threads, and reports preserve machine evidence.
8. `journal/` preserves the human/agent metaconversation about framework and pipeline design.

## Deterministic-first pipeline design

An agentic pipeline is not a chain of model calls. It is a deterministic program with occasional, tightly bounded inference stages.

For each proposed stage, choose the least powerful sufficient mechanism in this order:

1. existing trusted tool or library;
2. small deterministic program, parser, query, or shell command;
3. deterministic heuristic that routes uncertainty without claiming semantic correctness;
4. LLM call, only when the task requires interpretation or generation that the earlier mechanisms cannot reliably provide;
5. explicit human decision when neither code nor bounded inference can meet the required confidence.

An LLM stage must state why inference is necessary, the smallest entity/context it may see, its exact output schema, protected invariants, deterministic preconditions and postconditions, finite retry/repair behavior, and its quarantine or human-escalation path. Passing broad criteria such as nonempty output, general similarity, or model confidence is never enough to establish correctness. Acceptance must trace to the goal and protected invariants through specific validators or an explicitly acknowledged semantic/human decision.

Design each entity path to pass specific evidence-backed gates or fail quickly. Reject missing inputs, unsafe paths, impossible invariants, oversized context, and malformed source before inference. After inference, parse the declared schema and run the cheapest authoritative validators first. A failure may route to one bounded repair, quarantine, or a human; it must not be converted into success by weakening acceptance criteria to raise throughput.

## Prompt classes

### Pipeline-building prompts

These are used by cloud or otherwise capable design agents to turn a user's goal and repository evidence into reviewable host artifacts. They may interpret goals, define entities and invariants, design stages and validators, generate runtime prompts, audit a proposed design, and assemble a pipeline package.

Required inputs include the stated goal, discoverable repository facts, scale/local-model constraints, allowed changes, protected content, acceptance policy, and escalation boundary. Outputs are proposals or staged files requiring the applicable repository approval flow. They never silently start the generated pipeline.

### Pipeline-running prompts

These are invoked repeatedly through the shared local API primitive. Their scope is one entity, attempt, review, repair, adjudication, cohort, or run-analysis decision. Inputs and outputs are schema-bound and versioned. Resolved prompt ID, version, and content hash are recorded with every thread capture and state-changing result.

Pipeline-running prompts cannot change pipeline definitions, code, credentials, validation policy, retry cohorts, or source artifacts directly. The runtime applies only declared transitions and promotion rules after validation.

Runtime prompts receive only the fields required for their one inference job. Deterministic stages do not load prompts at all.

## Information ownership

| Information | Canonical owner |
| --- | --- |
| Universal purpose, safety invariants, task routing | `AGENTS.md` |
| Steps for performing one task | One playbook |
| Executable model instruction | One prompt |
| Reusable concept used by multiple tasks | One reference |
| Structured output shape | One template or schema |
| Deterministic invariant | Runtime validator/configuration |
| Machine execution fact | State, artifact, thread, or run report |
| Design decision and checkpoint handoff | Journal and governing plan |

When normative instructions are duplicated, retain the most specific canonical owner and replace other copies with a short link plus any local context needed to apply it. Root routing must not reproduce full playbook procedures; prompts must not reproduce repository governance; playbooks must not restate schemas in prose.

## Framework and host ownership

The framework owns canonical meta-prompts, default execution prompt templates, playbooks, references, templates/schemas, and runtime code. A host owns its selected/generated pipeline definition, customized prompts, deterministic project validators, evaluation fixtures, `TODO.md`, journal/plans, ignored `api.yaml`, state, artifacts, threads, and reports.

Framework updates may propose prompt improvements through synthesis. They may not overwrite host-customized prompts or local runtime state. Generated pipeline packages are staged for review before integration.

## Progressive-disclosure acceptance criteria

- The universal entrypoint communicates project purpose, non-negotiable safety, and task routing without embedding detailed task procedures.
- Each supported task maps to one primary playbook; combined tasks load the smallest ordered set.
- Every playbook declares the prompts, references, templates, and commands it requires.
- An agent can explain why each loaded artifact is necessary for the current task.
- Unrelated playbooks are not mandatory context.
- Missing task coverage routes to a framework-change proposal instead of improvising hidden policy.

## Routing verification scenarios

| Request | Minimum intended route |
| --- | --- |
| “Design a pipeline for these exported posts.” | Pipeline-design playbook; design prompts; pipeline-package templates |
| “Write the worker and reviewer prompts.” | Prompt-building playbook; generator prompts; output schemas; prompt-authoring reference |
| “Connect this repo to my Ollama endpoint.” | Local-inference configuration playbook; `api.sample.yaml`; preflight command |
| “Resume yesterday's run.” | Operation/resume playbook; pipeline definition; runtime command reference |
| “Why did this entity fail?” | Entity-investigation playbook; only that entity's state/evidence trail |
| “Improve the failures from this run.” | Post-run review playbook followed, if approved, by cohort-retry playbook |
| “Change how Pipelines routes agents.” | Framework-change playbook; active plan; relevant router/playbook artifacts |

Passing these scenarios means each agent can identify a minimum sufficient context set. It does not impose an arbitrary universal word count; concision is judged by absence of unrelated procedure and duplicated explanation while retaining all required constraints.

