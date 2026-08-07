# Schemas

`run_evidence.schema.json` defines the minimum machine-readable companion to every human run narrative. `prompt_outputs.schema.json` owns model contracts, including existing-pipeline conformance review. `pipeline_package.schema.json` preserves schema-1 compatibility while schema 2 enforces authority and evidence declarations.

- `prompt_outputs.schema.json`: strict model outputs referenced by prompt metadata.
- `pipeline_package.schema.json`: reviewable package manifest.

Runtime code validates model output before state changes. Agents designing a pipeline load only the definitions referenced by the prompts they are using.
