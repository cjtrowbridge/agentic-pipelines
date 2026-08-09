# Deterministic, Semantic, and Human Authority

## Why this boundary exists

“Deterministic first” is a resource and reliability discipline, not permission to approximate meaning with ever more rules. A mechanism is sufficient only when it can establish the property actually being tested. Repeatability, conservatism, lexical overlap, embedding distance, confidence, or rule complexity does not turn a semantic proxy into proof.

The inverse rule is as important as avoiding unnecessary inference: never pretend deterministic logic is sufficient when correctness depends on meaning. False certainty at this boundary creates brittle rejection loops, hides valid transformations, and prevents the semantic reviewer from exercising the authority it was designed to hold.

## Property classes and authority

| Property class | Examples | Authoritative mechanism |
| --- | --- | --- |
| Representational | Parse success, schema, paths, hashes, IDs, exact literals, declared limits, render/page count | Deterministic code |
| Semantic | Entailment, equivalence, relevance, faithful paraphrase, overstatement, material omission, quality | Bounded model or human judgment |
| Human/policy | Ambiguous material decisions, risk acceptance, policy exceptions, publication approval | Explicit human decision |

A semantic conclusion can become deterministically checkable only after a trusted process represents it explicitly. Code may prove that evidence ID `x` exists and was supplied; it cannot infer from that fact alone that a rewritten claim is entailed by `x`.

Exact citation validation must operate on independently resolvable source IDs or exact contiguous excerpts. When support spans multiple passages, the contract must accept a list of separately exact references; it must not ask a model to concatenate passages into one supposedly exact string. Whitespace, Markdown bullets, or punctuation may be normalized only under a declared meaning-preserving representation rule and may never become semantic factual rejection authority.

## Exact domain rules

An exact domain rule may reject deterministically only when all of these are declared:

1. the canonical representation;
2. the source contract that makes it authoritative;
3. the exact property computed;
4. normalization that cannot change meaning;
5. counterexamples demonstrating the rule does not stand in for semantic judgment.

“This date differs from the linked typed date field” may be exact. “This number is followed by a word not found beside it in the source” is only a lexical anomaly unless the domain contract defines that token pair as the canonical typed quantity.

## Proper role of heuristics

Lexical matching, keywords, edit distance, embeddings, synonym lists, anomaly scores, and confidence may:

- shortlist candidates;
- prioritize review;
- route uncertain cases;
- trigger semantic or human review;
- surface anomalies for investigation.

They may not directly accept or reject semantic correctness. Name them `review trigger`, `routing heuristic`, `lexical anomaly`, or `candidate score`, not `semantic failure gate`.

## Mixed gates

A rigorous semantic transformation commonly uses this sequence:

```text
source passages receive stable IDs
→ semantic selection or transformation cites those IDs
→ deterministic code validates schema, ID resolution, source availability, and protected literals
→ an independent semantic reviewer judges support and materiality
→ ambiguity escalates to a human
→ deterministic promotion verifies the accepted transaction
```

Free-text fact extraction and relevance selection are not inherently deterministic. Code can segment text and assign IDs without claiming that a segment expresses a normalized fact.

## Repair ownership

Perform safe, fact-preserving canonicalization in code: whitespace, stable headings, known serialization, ordering required by schema, or other exact representation. Send a candidate back to a model only when correction requires choosing, rewriting, compressing, interpreting, or preserving meaning.

Every gate must declare the property, property class, mechanism, verdict authority, proof basis, evidence, materiality, repair owner, and escalation. An auditor must flag any mechanism whose error message or control flow claims more authority than its evidence establishes.

## Semantic review is still untrusted

A model reviewer is not a truth oracle. Give it narrow claims, cited evidence, a structured rubric, finite attempts, and classifications such as supported, partially supported, overstated, unsupported, ambiguous, or contradicted. Validate its schema and cited evidence deterministically. Use independent review for material decisions and escalate ambiguity or unacceptable risk to a human.

## Scope the semantic unit before judging it

Claim review applies to factual propositions, not every string in a document. A deterministic parser may identify structural zones such as a contact block, salutation, closing, signature, heading, or declared section without making a factual judgment. Conventional, performative, prospective, polite, or structural language (for example `Dear Hiring Manager`, `Thank you for your consideration`, an objective, an expression of interest, or `Sincerely`) must be classified `not_factual`, not `unsupported`. That result is non-blocking and non-repairing unless a separate exact structural rule rejects it.

Coverage review likewise cannot manufacture qualifications. `repairable_missing` requires material trusted source evidence that is independently resolvable by an exact source ID or excerpt and can be added without invention. An unsupported qualification is `unsupported_gap`; a deliberate, source-backed selective omission is `optional_omitted`. Neither can trigger model repair. A cover letter normally selects the strongest material alignments rather than enumerating every posting phrase. Any disagreement between a structural validator and a semantic reviewer is an authority-boundary defect requiring correction or human review, never automatic deletion of required structure.

Every model-output field needs a declared consumer and material consequence. Prompts, schema, examples, validators, and consumers must agree on its shape. Do not discard an otherwise usable candidate for decorative metadata, silently coerce invalid output, or repeat the same schema rejection after feedback. A finite retry policy must stop, change strategy, or escalate and report the rejection path, feedback delta, and response delta.
