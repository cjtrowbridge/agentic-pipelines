# Playbook: Investigate a Pipeline Entity

## Use when
Explaining why one entity was accepted, rejected, retried, or quarantined.

## Load
Only that entity’s source revision metadata, run narrative, transition history, attempts, rejected candidates and appended reasons, validator/reviewer evidence, prompt identity, and thread captures. Load the authority and run-evidence references when classification is disputed.

## Procedure
1. Verify entity/revision identity and source hash.
2. Reconstruct transitions and attempts in order.
3. Verify evidence hashes and prompt/model/config identity.
4. Identify the first failing gate, property actually proved, verdict authority, repeated/changing feedback, and first preventable retry. Distinguish observation, metric, hypothesis, and recommendation.
5. Identify the earliest responsible input, prompt, context, schema, normalizer, validator, reviewer, provider, or orchestration layer.
6. Recommend inspect, retry, specialized repair, cohort assignment, design correction, manual handling, or no action, with a regression fixture for changes.

## Output and safety
An entity evidence summary with links and confidence. Do not expose unrelated entities, change state, or retry work during investigation.

