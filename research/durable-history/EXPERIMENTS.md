# Falsification program

Status: **preregistering candidates; not executed.**

Each experiment must freeze its fixtures, success criteria, implementation, and
environment before confirmatory execution. Null, failed, and incomplete outcomes
remain visible.

## DH-001 — Immutable falsehood

**Question:** Does anchoring change evidential status?

**Null:** A false or unsupported fixture has the same evidential status before
and after anchoring.

**Test:** Commit a deliberately false fixture, verify its timestamp and inclusion
proof, and then evaluate it under the knowledge-ledger rules.

**Pass condition:** Verification proves byte identity and historical inclusion
while the conclusion remains unsupported or false.

## DH-002 — Reproduction without anchoring

**Question:** Can evidence support a result without a blockchain?

**Null:** Independent reproduction and evidential support do not require an
external anchor.

**Test:** Independently reproduce a frozen, unanchored fixture in a clean
implementation and compare protected fields and conclusions.

**Pass condition:** The result reproduces, while its durable-history status is
accurately reported as unanchored.

## DH-003 — Mutation detection

**Question:** Does the receipt expose later alteration?

**Null:** Any one-byte mutation to a covered artifact invalidates its inclusion
proof or top-level commitment.

**Test:** Mutate every covered file position across bounded synthetic packages.

**Pass condition:** Every mutation is detected; unchanged packages verify.

## DH-004 — Copies do not become roots

**Question:** Can hashing or anchoring manufacture evidential independence?

**Null:** Duplicating one ground source produces no additional independent root,
regardless of the number of file hashes, signatures, or timestamps.

**Test:** Anchor increasing numbers of verbatim and paraphrased descendants of
one source and rerun root accounting.

**Pass condition:** The independent-root count and bounded conclusion remain
unchanged.

## DH-005 — Immutable uncertainty

**Question:** Does durable preservation pressure a system to overclaim?

**Null:** When a required search location is unavailable, the anchored receipt
still concludes `not_established`.

**Test:** Preserve a package with declared incomplete coverage and verify it
through independent implementations.

**Pass condition:** Every rendering and receipt preserves the unavailable
location, uncertainty, and bounded conclusion.

## Comparative preservation study

After DH-001 through DH-005 pass locally, compare Git commits, signed releases,
transparency logs, OpenTimestamps/Bitcoin, and an EVM L2 anchor. Measure:

- independent verifiability without the original operator;
- resistance to deletion and silent history rewriting;
- proof size, latency, monetary cost, and operational complexity;
- privacy leakage and metadata exposure;
- dependence on vendors, administrators, sequencers, and key custody;
- long-term availability of artifacts and verification software.

No provider or chain wins by definition. The preferred method is the least
expensive mechanism that satisfies the preregistered durability and independence
requirements for the record's consequence level.
