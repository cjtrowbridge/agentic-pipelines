# Playbook: Investigate a Pipeline Entity

## Use when
Explaining why one entity was accepted, rejected, retried, or quarantined.

## Load
Only that entity’s source revision metadata, transition history, attempts, candidate/validator/reviewer evidence, prompt identity, and thread captures.

## Procedure
1. Verify entity/revision identity and source hash.
2. Reconstruct transitions and attempts in order.
3. Verify evidence hashes and prompt/model/config identity.
4. Identify the first failing gate and distinguish observed error from later model hypothesis.
5. Recommend inspect, retry, specialized repair, cohort assignment, manual handling, or no action.

## Output and safety
An entity evidence summary with links and confidence. Do not expose unrelated entities, change state, or retry work during investigation.

