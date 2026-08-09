# LIR-3 — observable provenance bridge

**Status:** method, split rule, candidate grid, selection rule, perturbation, and
success criterion frozen before development outcomes are computed.

## Question

Can weak provenance that remains visible when an exact platform edge is missing
recover substantially more recorded lineage than text and time alone, without
creating materially more false root merges?

LIR-2 transferred poorly to PHEME at 40% edge hiding: root precision was `1.0`,
but recall was `0.2020`, F1 was `0.3362`, and root-count MAE was `5.5517`.
LIR-3 tests the identified missing bridge rather than retuning LIR-2 on its old
test set.

## Evidence and claim boundary

- Corpus: PHEME rumor threads not used by LIR-1/PHEME pilot or PHEME-R2.
- Target: recorded PHEME reply-tree roots (`explicit_edge`, `record_root`).
- This target is platform lineage, not proof of causal influence, evidence
  independence, content truth, or a common real-world source.
- Tweet text, identities, and normalized rows stay local. Public records contain
  only hashes, counts, code, metrics, and aggregate results.

## Disjoint split and sealing

Previously used case IDs are excluded. Each remaining case is assigned by the
first eight bytes of SHA-256 over
`minority-prophet-lir3-pheme-split-v1|<case-id>`: buckets `0..24` are
development and `25..99` are confirmatory. Within each split, cases are ordered
by a separately salted SHA-256 selection key and admitted whole until the next
case would exceed 5,000 claims. Missing-file threads are rejected whole.

The public inventory records each case-set digest and each local normalized-file
digest. Development can be inspected during selection. Confirmatory outcomes
must not be scored until a selected configuration and confirmatory input digest
are committed.

## Allowed features and forbidden leakage

The method may see case/proposition grouping, claim ID, author ID, timestamp,
text, exposed parent edges, the reply-target **author** ID, mentioned author IDs,
normalized URL domains, and normalized hashtags.

When an edge is hidden, the exact reply-parent status ID is removed and is never
copied into metadata. True roots, annotations, truth values, split outcomes,
source/reaction directory roles, screen names, engagement, location, and user
profile fields are forbidden inference features.

## Frozen perturbation and method family

The deterministic LIR seed hides 40% of recorded edges. Exposed edges are always
followed. For a hidden edge, the method ranks earlier claims by `0.70` text
Jaccard + `0.20` 24-hour temporal decay + `0.06` shared URL-domain indicator +
`0.04` shared-hashtag indicator.

The 36 candidates are the Cartesian product of:

- reply-target-author minimum score: `0.00, 0.25, 0.45, 0.65`;
- winner margin: `0.00, 0.10, 0.20`; and
- fallback: `none`, `mention`, or `mention-text`.

Mention fallback has a fixed `0.45` minimum. Text fallback has a fixed `0.75`
minimum. Fallback is attempted only for a record that declares a reply-target
author, preventing ordinary roots from being attached merely because they quote
or mention another record.

## Development selection

A candidate is eligible only when development root-pair precision is at least
`0.99`. Among eligible candidates, select maximum root recall, then F1, then
minimum root-count MAE, then higher author score, higher margin, and lexical
configuration ID. If no candidate is eligible, stop with no selection and do
not score the holdout.

## Confirmatory joint success criterion

At 40% hiding on the sealed confirmatory split, all conditions must hold:

1. root-pair precision at least `0.99`;
2. root-pair recall at least `0.45`;
3. root-pair F1 at least `0.60`;
4. root-count MAE strictly below `4.0`;
5. recall at least `0.15` higher than frozen LIR-2 on the same cases; and
6. F1 at least `0.15` higher than frozen LIR-2 on the same cases.

Report the point estimates and 10,000 whole-case bootstrap intervals with seed
`20260809`. Failure of any condition rejects the joint claim. No subgroup,
secondary fraction, or post-hoc exclusion may rescue it.

## Interpretation

Success would show that retained, non-exact provenance fields bridge a specific
real-corpus failure of text/time lineage reconstruction. It would still not
establish causal ancestry, evidence independence, truth, or transfer beyond
PHEME. Failure would show that these metadata are insufficient under this
transparent method and perturbation; it would not show that provenance itself
has no value.
