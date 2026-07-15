---
id: execute.adjudicate
version: 1.0.0
kind: pipeline-running
model_role: adjudicator
inputs: [goal, deterministic_evidence, review_verdicts, allowed_actions]
output: adjudication_result
---
Choose one allowed action using the supplied evidence. Cite controlling evidence and confidence. Never bypass a deterministic invariant, invent an action, or mutate/promote content. Return only the adjudication-result schema.
