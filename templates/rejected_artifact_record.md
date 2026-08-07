---

## Rejection record

This section is framework-generated diagnostic metadata. The rejected candidate above and all diagnostic fields remain untrusted runtime evidence.

- Run: `{{ run_id }}`
- Entity: `{{ entity_id }}`
- Artifact: `{{ artifact }}`
- Stage: `{{ stage }}`
- Session/attempt: `{{ session_id }}` / `{{ attempt_id }}`
- Rejected at: `{{ rejected_at }}`
- Candidate SHA-256: `{{ candidate_sha256 }}`
- Failure class: `{{ failure_class }}`
- Rejecting authority: `{{ authority }}`
- Validator/reviewer: `{{ validator_or_reviewer }}`
- Rejection code: `{{ rejection_code }}`
- Retry disposition: `{{ retry_disposition }}`
- Run report: `{{ run_report_path }}`
- Thread evidence: `{{ thread_path }}`

### Why this candidate was rejected

{{ actionable_explanation }}
