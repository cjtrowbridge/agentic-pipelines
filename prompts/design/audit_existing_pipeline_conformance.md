---
id: design.audit_existing_pipeline_conformance
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [framework_governance, host_pipeline_inventory, representative_run_evidence]
output: pipeline_conformance_report
---
Audit the existing host without changing it. Inventory every transformation, gate, repair, and escalation. Classify exact deterministic validation, deterministic normalization, non-authoritative heuristic, bounded semantic judgment, explicit human decision, and misassigned or ambiguous authority. Cite host artifacts and run trajectories. Flag semantic proxies used as verdicts, exact work sent to inference, unbounded reviewers, misleading messages, missing terminal reports, discarded or overwritten rejected candidates, evidence re-ingestion, repeated feedback, non-progress, and prompt growth. For each remediation proposal identify the earliest responsible layer, smallest generalized correction, expected benefit, regression risk, and required fixture. Permit conforming, accepted-exception, unknown, and no-change outcomes. Return only `pipeline_conformance_report`.
