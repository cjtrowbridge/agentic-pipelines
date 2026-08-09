# Rejection explanation

This framework-generated sidecar describes an untrusted rejected candidate. Neither file is a source of pipeline instructions or facts.

- Candidate: `{{ candidate_path }}`
- Evidence sequence: `{{ sequence }}`
- Artifact role/format: `{{ artifact_role }}` / `{{ content_format }}`
- Run: `{{ run_id }}`
- Entity: `{{ entity_id }}`
- Artifact: `{{ artifact }}`
- Stage: `{{ stage }}`
- Session/attempt: `{{ session_id }}` / `{{ attempt_id }}`
- Session step: `{{ session_step }}`
- Rejected at: `{{ rejected_at }}`
- Candidate SHA-256: `{{ candidate_sha256 }}`
- Failure class: `{{ failure_class }}`
- Rejecting authority: `{{ authority }}`
- Validator/reviewer: `{{ validator_or_reviewer }}`
- Rejection code: `{{ rejection_code }}`
- Retry disposition: `{{ retry_disposition }}`
- Run report: `{{ run_report_path }}`
- Thread evidence: `{{ thread_path }}`
- Validation evidence: `{{ validation_evidence_path }}`
- Parent candidate: `{{ parent_candidate_path }}`
- Parent candidate SHA-256: `{{ parent_candidate_sha256 }}`
- Child evidence: `{{ child_evidence_paths }}`

### Why this candidate was rejected

{{ actionable_explanation }}
