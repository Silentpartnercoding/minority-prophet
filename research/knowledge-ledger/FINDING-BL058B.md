# BL-058b — the immunity ablation is blind to the *worst* mutations

Produced by `lineage/reference_mutant_audit.py`, the programme's first mutant
audit meeting Amendment 2 of `AMENDMENT-BL058.md`: every mutant implementation is
published, every mutant is classified equivalent or behaviour-changing, and the
unit of counting is stated.

    unit      one (world, rewiring) pair
    checked   root set preserved, both worlds side-consistent under the reading
    fired     the verdict changed on an eligible pair -- an immunity violation

| mutant | class | parentLocal checked/fired | rootBased checked/fired |
|---|---|---|---|
| correct | EQUIVALENT | 116032 / **0** | 116032 / **0** |
| depth0 | BEHAVIOUR_CHANGING | 116032 / **0** | 2834528 / **0** |
| depth1 | BEHAVIOUR_CHANGING | 116032 / 2848 | 116032 / 2848 |
| depth2 | BEHAVIOUR_CHANGING | 116032 / 3940 | 116032 / 3940 |
| alwaysZero | BEHAVIOUR_CHANGING | 116032 / **0** | 90280 / **0** |
| offByOneStop | BEHAVIOUR_CHANGING | 116032 / 1720 | 687288 / 118968 |
| minIndexInChain | EQUIVALENT | 116032 / 0 | 116032 / 0 |
| grandparentSkip | EQUIVALENT | 116032 / 0 | 116032 / 0 |

The control fires zero under both readings, so immunity holds and every other row
means something. Without that line the table would be unreadable.

## The finding

**`depth0` and `alwaysZero` change `root_of` and are never caught, under either
reading.** They are not equivalent mutants — their zeros are not forced — so this
is a blind spot, not a harmless result.

Both make `root_of` ignore lineage entirely: `depth0` returns each claim as its
own root, `alwaysZero` returns claim 0 for everything. Under either, the verdict
collapses to a function of the *multiset of sides*, and rewiring preserves sides
by construction. So the verdict is trivially invariant and immunity trivially
holds.

The immunity ablation tests **invariance under rewiring, not correctness of
`root_of`**. A mutation that is uniformly wrong preserves invariance and is
invisible. A mutation that is partly wrong — `depth1`, `depth2`, `offByOneStop` —
breaks invariance and is caught.

That ordering is the wrong way round. The ablation catches subtle errors and
misses gross ones, and "the ablation fired on 3,940 worlds" has been read as
evidence of checker power when it is evidence of a *particular kind* of checker
power that excludes the most severe defects.

## What this does and does not say

It does **not** say Theorem 1 is wrong. Immunity holds for the correct
implementation, exhaustively, and this audit confirms it at 116,032 eligible pairs
with zero violations.

It says the immunity ablation is **not a test of `root_of`**, and must not be
counted as one. A separate check is required for that — enumerating `root_of`
against its specification, which is what the `equivalent` column here does and
what no previous audit reported.

## Confirming Amendment 1 independently

Three mutants have divergent populations between the readings — `depth0`
(116,032 against 2,834,528), `alwaysZero` (116,032 against 90,280) and
`offByOneStop` (116,032 against 687,288). BL-058 was raised from the independent
audit; this reproduces it from our own implementation with published semantics.
`offByOneStop` also changes its *firing* count, 1,720 against 118,968, so the
divergence is not confined to eligibility.

## Not a replication

`IND-v4-RESULTS.json` does not state its unit of counting, so these figures are
not comparable to it number-for-number and no correspondence is claimed. The two
audits agree on the two facts that matter — the readings diverge under mutation,
and `minIndexInChain` and `grandparentSkip` fire zero — while this one adds the
classification that makes those zeros interpretable.

## Cost

105 seconds at `MAX_CLAIMS_EXHAUSTIVE = 6`, so it is not in the default suite. It
is a deliberate audit, run and committed with its output.
