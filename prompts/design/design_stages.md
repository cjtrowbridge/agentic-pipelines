---
id: design.design_stages
version: 1.1.0
kind: pipeline-building
model_role: designer
inputs: [pipeline_goal_report, entity_contract, invariant_catalog]
output: stage_design
---
Define the smallest ordered stage graph that reaches the goal while preserving invariants. Prefer trusted tools, parsers, scripts, queries, and deterministic routing; permit an LLM only for semantic work those mechanisms cannot reliably perform, and record why. For each stage declare mechanism, minimal inputs, output, evidence, validation, retry budget, and allowed next states. Include quarantine and promotion; reject unnecessary inference and unbounded cycles. Return only `stage_design`.
