---
id: execute.repair
version: 1.0.0
kind: pipeline-running
model_role: repairer
inputs: [goal, source_entity, candidate, violations, protected_invariants]
output: repair_result
---
Repair only the listed violations. Preserve valid candidate content and every protected invariant; do not broaden the transformation. Return repaired candidate plus addressed/unresolved violation IDs, or unable. Return only the repair-result schema.
