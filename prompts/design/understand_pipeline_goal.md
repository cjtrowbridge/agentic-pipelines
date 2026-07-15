---
id: design.understand_pipeline_goal
version: 1.0.0
kind: pipeline-building
model_role: designer
inputs: [user_goal, repository_evidence, operating_constraints]
output: pipeline_goal_report
---
Extract the goal state, scale, allowed changes, protected content, local constraints, acceptance expectations, and human escalation boundary. Separate user statements, repository facts, inferences, and unresolved decisions. Ask only decisions that materially change the design; output the pipeline goal report schema.
