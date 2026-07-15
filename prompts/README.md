# Prompt Catalog

- `design/`: cloud/high-capability prompts that design a pipeline.
- `generate/`: prompts that create and tighten host runtime prompts.
- `execute/`: canonical local per-entity stage prompts.
- `analyze/`: local or reviewed prompts for entity, cohort, remediation, and performance analysis.

Each prompt declares an ID, version, kind, inputs, and output contract. Host-customized runtime prompts are host-owned.

