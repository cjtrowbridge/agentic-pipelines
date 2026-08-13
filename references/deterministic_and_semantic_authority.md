# Deterministic, Semantic, and Human Authority

## Core doctrine

Code governs exactness. Models govern meaning. Humans govern unresolved intent and risk. Examples specify behavior.

“Deterministic first” is a resource and reliability discipline, not permission to approximate meaning with more rules. A mechanism is sufficient only when it can establish the property actually being tested. Repeatability, conservatism, lexical overlap, embeddings, confidence, typed labels, or rule complexity do not turn a semantic proxy into proof.

**LLMs are few-shot learners.** For semantic transformations, the best outputs will come from giving the model representative examples of past inputs and their accepted outputs, followed by the new input, so the model can learn the demonstrated transformation rather than forcing agents to approximate that behavior with an expanding collection of handcrafted semantic rules.

This is the default when trusted representative examples exist. It is not permission to use inference for exact work, send unbounded examples, or let examples acquire undeclared factual authority. Demonstrations commonly specify ontology, selection behavior, abstraction level, relationships among outputs, tone, and boundary behavior; concise prose supplies invariants and exceptions.

## Property and authority classes

| Property | Examples | Authority |
| --- | --- | --- |
| Representational | Parse success, schema, paths, hashes, stable IDs, exact literals, declared limits, render/page count | Deterministic code |
| Semantic | Entailment, equivalence, relevance, faithful transformation, material omission, qualitative fitness | Bounded model or human judgment |
| Human/policy | Unresolved intent, material ambiguity, risk acceptance, policy exception, publication approval | Explicit human decision |

A semantic conclusion can become exactly checkable only after a trusted decision represents it explicitly. Code may prove that evidence ID `x` exists and was supplied; it cannot infer that a claim is supported merely because `x` exists, has a particular typed kind, or shares words with the claim.

## Smallest coherent semantic unit

Give one model stage the smallest coherent semantic decision whose parts must remain semantically coherent. “Narrow” means bounded goal, authority, context, output, and stop behavior—not atomizing meaning into independent microclaims.

Keep interdependent outputs together when selection, factual consistency, division of content, or operator intent crosses their boundary. Split a semantic stage only for a declared security/isolation boundary, provider or measured context limit, independently useful intermediate, material-risk review, or demonstrated quality failure. Every split states the observed failure, added context/schema/retry cost, lossy representation risk, and evaluation evidence. Making deterministic validation easier is not a sufficient reason.

Use minimum sufficient context. Stable sources, trusted demonstrations, the current candidate, and bounded feedback belong in one retained session when they are necessary for the coherent decision. Fewer bytes are not better when removing them destroys the evidence or examples needed to perform the task.

## Semantic laundering

Semantic laundering occurs when a pipeline:

1. converts meaning into a heuristic, inferred free-text class, model label, typed proxy, similarity score, or lexical relation;
2. validates that proxy exactly; and
3. lets the exact validator accept or reject the original semantic property.

The validator may be deterministic about the proxy while still lacking authority over meaning. Adding more regexes, categories, or evidence kinds enlarges the proxy; it does not repair the authority boundary.

Heuristics may shortlist, prioritize, detect anomalies, route review, or escalate uncertainty. Name them accordingly. They may not issue semantic verdicts.

An exact domain rule may reject only when the canonical representation, authoritative source contract, computed property, meaning-preserving normalization, and counterexamples are declared. Exact citation validation may establish resolvable IDs, contiguous excerpts, hashes, or supplied-source availability. It does not establish entailment or relevance.

## Default semantic transformation

```text
trusted sources and bounded representative demonstrations
-> deterministic provenance, preparation, bounds, and exact preconditions
-> one coherent semantic transformation in a retained session
-> scope-bound audit and bounded evidence-driven repair when justified
-> deterministic schema, resource, render, state, and promotion gates
-> human decision only for unresolved intent, material ambiguity, or risk
```

Each example declares whether it is authoritative for facts, behavior, style/format, ontology, boundary behavior, or negative behavior. Rejected, quarantined, diagnostic, unknown, or otherwise untrusted artifacts never become examples. Preserve whole examples; select within a measured complete-session budget and record omissions.

Examples can be inappropriate when they are contaminated, mutually inconsistent, privacy-restricted, policy-obsolete, adversarial, or likely to anchor an unacceptable error. Exact tasks remain deterministic.

## Review and revision authority

A retained-session self-audit is the routine default for reversible semantic transformations: tell the model to treat its prior output as an untrusted candidate, give a constrained rubric, and permit only bounded repair. Shared authorship does not make the candidate correct, but a retained session avoids context loss and duplicated prompts.

Fresh-session independent review and claim-level provenance are optional high-assurance patterns. Use them when a documented consequence analysis justifies the added assurance: safety-critical decisions, legal/medical/financial effects, adversarial inputs, irreversible publication, or demonstrated self-review blind spots. Independence is a tool, not a ritual.

A reviewer may judge only the declared decision scope. For a revision, supply the accepted baseline, exact requested delta, and necessary factual authority. Audit whether the delta was applied, whether changed material is supported, whether it creates a direct contradiction, and whether it violates exact constraints. Previously accepted unchanged content remains outside blocking review. A supported operator-requested inclusion remains valid within policy even if a reviewer would prefer another optimization; that preference is non-blocking advice.

Every audit/repair loop has finite attempts, specific repairable findings, a progress test, and a truthful unable or human branch. Changing or repeated feedback is evidence of a scope, prompt, context, or reviewer defect—not a reason to keep appending instructions.

## Lossy semantic intermediates

Summaries, simplified documents, extractions, classifications, and selected evidence packets are semantic derivatives. Declare whether each is lossy and what downstream authority it holds. A lossy derivative cannot silently become an exact substitute for its source. Define its preservation rubric, omission policy, fallback, audit path, or retained-source access in proportion to consequence. Cache it only under source, prompt, model/configuration, and output-contract identity.

## Runtime gates and evaluation

Runtime code applies the cheapest authoritative exact gates plus bounded semantic review appropriate to risk. Do not add live semantic microstages to compensate for a weak initial prompt or missing evaluation.

Use versioned golden sets to measure first-pass acceptance, unsupported content, omission, low-overlap equivalence, high-overlap contradiction, reviewer scope, operator-intent preservation, context reduction, repair progress, and justified high-assurance review. Prefer improving the initial examples, prompt, context, schema, or scope before adding another stage. A justified no-change conclusion is valid.

Every gate declares the property, property class, mechanism, verdict authority, proof basis, evidence, materiality, repair owner, and escalation. Auditors flag any control flow or message that claims more authority than its evidence establishes.
