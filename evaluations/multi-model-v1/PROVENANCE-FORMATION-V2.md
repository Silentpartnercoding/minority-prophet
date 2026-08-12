# Provenance formation v2 — local design and proof boundary

Status: **local development architecture; not a verified public claim**

## Deterministic first pass

`inferProvenance` now emits three deliberately separate structures:

1. `accepted_links`: ancestry supported by deterministic evidence such as a
   temporally valid citation or a distinctive shared field observation;
2. `claim_clusters`: exact normalized statements that can be collapsed for
   search and display, while their evidential independence remains
   `unresolved`;
3. `review_links`: exact-text or high-overlap candidates that warrant semantic
   investigation but cannot alter trusted root counts.

It also emits integrity warnings for unknown, non-prior, or assertion-conflict
citations and routes each packet to `auto_collapse`,
`integrity_review_required`, or `semantic_review_required`.

On the 24-world development corpus, the deterministic pass produces seven
accepted links per world for the three clean observable families, seven links
plus seven integrity warnings for deceptive citations, and 21 review links
with zero accepted links for both generic-boilerplate and opaque-paraphrase
families. The latter 21 links cover 75% of the hidden copied-root pairs while
remaining untrusted.

## Why exact text is not auto-provenance

`ambiguityPair()` constructs one public packet and two opposite hidden worlds:

- in one world, six identical reports descend from one observation;
- in the other, six independent observers use the same reporting template.

The model-visible bytes are identical. Auto-collapsing exact text scores 100%
on the copied world and 0% on the independent world. Leaving every report as a
separate root reverses those scores. Both configurations average 50% across
the pair. No threshold or model operating only on those bytes can distinguish
the hidden graphs; additional evidence or abstention is required.

Exact text is therefore a safe **claim cluster** and a useful review signal,
but not proof of common evidential ancestry.

## Guarded LLM handoff

The LLM never produces a trusted MP receipt. It produces an untrusted
`mp-lineage-proposal.v1` containing only candidate child/parent IDs,
confidence, evidence-type labels, unresolved IDs, and a concise summary.

`compileProvenanceProposal` then:

- rejects unknown fields, answer/truth fields, malformed confidences, unknown
  IDs, self-parenting, duplicates, non-prior links, unsupported links, and
  assertion conflicts;
- independently recomputes observable support from the original packet;
- keeps semantic, exact-text, and publisher arguments review-only regardless
  of model confidence;
- derives accepted roots exclusively from deterministic observations;
- excludes the model's prose from the trusted receipt;
- records input and proposal hashes and mints the final deterministic receipt
  hash.

The trusted output is `mp-provenance-receipt.v1`. It contains no answer or
ground-truth label. Invalid structured output fails closed.

## Supported conclusion

The defensible configuration is precision-first:

`deterministic evidence -> claim clustering -> guarded semantic proposal -> deterministic receipt compiler -> abstain if unresolved`

This proves internal invariants and an information-theoretic limitation. It
does not prove real-world recall, publisher identity, or the truth of an LLM's
semantic ancestry hypothesis. Those require held-out natural corpora with
externally documented lineage.
