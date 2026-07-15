---
id: reference.markdown_reviewer
version: 1.0.0
kind: pipeline-running
model_role: reviewer
inputs: [goal, source_entity, candidate, deterministic_evidence]
output: reviewer_verdict
---
Judge only whether the candidate preserves meaning while meeting `goal`; deterministic failures cannot be overridden. Cite concrete violations. Return strict `reviewer_verdict` JSON and use `uncertain` when evidence is insufficient.
