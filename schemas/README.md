# Schemas

- `prompt_outputs.schema.json`: strict model outputs referenced by prompt metadata.
- `pipeline_package.schema.json`: reviewable package manifest.

Runtime code validates model output before state changes. Agents designing a pipeline load only the definitions referenced by the prompts they are using.
