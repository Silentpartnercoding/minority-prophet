# LIN-000 v0.4 — self-contained, and the tests carry their own load

Registered by RUN-20260809-2 **before the v0.4 reference exists**. Supersedes
v0.3 and v0.3.1, which are preserved. This document is **complete**: it restates
everything an implementer needs and incorporates nothing by reference. v0.3
carried v0.2's generator and notation by reference, shipped neither, and its
regression arm could not be attempted.

Traceability: `TRACEABILITY-v0.4.json`, written at registration time (BL-042).

## What v0.3 got wrong, and what is decided here

| | v0.3 | v0.4 |
|---|---|---|
| **package** | carried v0.2 by reference, shipped neither | fully restated below |
| **the verdict** | four tests stated in terms of it; defined nowhere | defined |
| **L1-NEG** | "differs > 0" — fires on 44,450/44,450, provably all | replaced by a distribution that discriminates |
| **T1-POS** | cited as Theorem 1 evidence; a corollary of L1-POS | retained, **not** cited as independent evidence |
| **identity rewiring** | excluded, while citing a figure that includes it | RW-001: excluded, and the citation withdrawn |
| **populations** | three unstated | stated |
| **erratum** | corrected the prose, not the traceability | propagated |

## 1. Schema

A world is an ordered list of claims `[{parentIndex, side}]`. `parentIndex` is
`null` (the claim is a **root**) or the index of a **strictly earlier** claim.
`side ∈ {0,1}`. There is no `id` field; v0.3 removed it as unbound.

- `root(c)`: follow `parentIndex` until `null`; that claim's index is the root.
- **root set** of `W`: `{i : W[i].parentIndex is null}` — the set of claims that
  are roots.
- **side-consistent**: every claim with a parent has its parent's side.
  (Equivalent to "every claim has its root's side": each implies the other by
  induction along the chain, verified across all 50,362 worlds with 0
  disagreements. Either may be implemented.)
- `S_a = {root(c) : side(c) = a}`, computed over **all** claims, deliberately not
  restricted to roots, so Lemma 1 is a theorem *about* this function.

**The verdict** — defined here because v0.3 stated four tests in terms of it and
defined it nowhere:

    verdict(W) = "1"       if |S_1| > |S_0|
                 "0"       if |S_0| > |S_1|
                 "abstain" otherwise                     (tau = 0, paper [E6])

## 2. Generator — defined, not referenced

`seed = 20260808`, as 8 bytes big-endian (`seed_be`). An infinite sequence of
32-bit unsigned words:

    block(m) = SHA-256( seed_be || uint64_be(m) )        # 32 bytes
    w(i)     = uint32_be( block(i // 8)[ 4*(i % 8) : 4*(i % 8) + 4 ] )

Consumed strictly in order from `w(0)`.

**`uniform_below(n)`**, the only sampler, for integer `n ≥ 1`:

    limit = 2**32 - (2**32 mod n)
    repeat: take the next word w; if w < limit return w mod n, else redraw

`uniform_below(1)` consumes exactly one word and returns 0. There is no float
primitive. "With probability 3/10" means `uniform_below(10) < 3`.

## 3. Randomized phase — the draw schedule

**100,000 worlds.** Per world: `k = 1 + uniform_below(20)`. Then for each claim
index `i = 0 .. k-1` ascending:

- **Root decision.** If `i == 0` the claim is a root and **no draw is consumed**.
  Otherwise `is_root = uniform_below(10) < 3`.
- **Parent.** If not a root, `parentIndex = uniform_below(i)`; if a root,
  `parentIndex = null` and no draw is consumed.
- **Side.** If a root, `side = uniform_below(2)`. Otherwise
  `keep = uniform_below(10) < 9`; the side is the parent's if `keep`, else its
  complement.

## 4. Exhaustive phase — the enumeration order

All worlds with `k = 1..6`. `count(k) = k! · 2^k`; the declared total is
**50,362**, asserted before evaluation.

1. Across `k`: ascending.
2. Within `k`: an odometer over positions `0..k-1` with position `k-1` varying
   fastest.
3. Within a position `i`: parent-major — parents in the order `null, 0, …, i-1`,
   and for each, `side = 0` then `side = 1`.

## 5. Canonical form

Render each claim as `P|S`, `P` the decimal `parentIndex` or `-` for a root.
Join a world's claims with `;`. Terminate each world with one `\n` (U+000A).
ASCII. The stream digest is SHA-256 over the concatenation. Prefix digests every
**1,000** worlds.

## 6. Generator conformance

For each modulus in order — `2863311531, 2576980378, 1717986919, 20, 10, 2, 1` —
draw `uniform_below(n)` 1,000 times from a generator freshly seeded per modulus.
Report the SHA-256 over the decimal values joined by `,`, and **the words
consumed**. The first three reject on roughly 33%, 40% and 20% of draws
(`2**32 mod n` = 1,431,655,765, 1,717,986,918 and 858,993,458); the word count is
the observable.

## 7. Tests

### RW-001 — what a rewiring is (owner-decided)

A **rewiring** of `W` is a world with the same claim count, the same side at
every index, and a `parentIndex` vector differing in at least one position.
**The identity is not a rewiring.** Owner decision, 2026-08-09;
`DECISION-RW-001.md`. The paper's published count of 121,944 includes the
identity and this definition excludes it, so the registered figure is 116,032 and
the two reconcile as `116,032 + 5,912`. This registration makes no claim of
agreement with that figure.

### T1-POS — the paper's Theorem 1. Violations MUST be 0.

Over rewirings where `W` and `W'` are both side-consistent and the **root set**
is preserved: the verdict MUST NOT change.

**Not cited as independent evidence for Theorem 1.** On side-consistent worlds
Lemma 1 forces `S_a` to equal the roots asserting `a`; the root set and sides are
preserved by definition; so the verdict is preserved. T1-POS therefore cannot go
red while L1-POS is green. Retained as a consistency check on the
implementation's `S_a`, and excluded from `paperClaims`.

### T1-NEC — clause (ii) is load-bearing. Verdict changes MUST be > 0.

The same population with side-consistency **not required of `W`** — that is,
`W` unrestricted, `W'` side-consistent. v0.3 said "removed", which one
implementation read as unrestricted and another as the complement; the two
populations differ by exactly T1-POS's. **Unrestricted is registered.**

**T1-NEC carries Theorem 1's evidential load**, being the only registered test
whose outcome is not forced by another.

### T1-ID — an identity. Population: `W` unrestricted.

Over rewirings preserving `root(c)` for every `c`. Cannot fail by construction.
Reported, excluded from all paper claims.

### L1-POS — Lemma 1. Violations MUST be 0. Population: both phases, reported separately.

On side-consistent worlds, `S_a` MUST equal `{i : root and side == a}`.

### L1-DISC — replaces L1-NEG (decision, 2026-08-09)

v0.3 required side-inconsistent worlds where `S_a` differs to exist, `> 0`. That
fires on **44,450 of 44,450** and **52,178 of 52,178** — provably all, since a
side-inconsistent world always has a claim whose root asserts the other side. It
measured the population, not the checker.

**Replaced by a distribution.** Over side-inconsistent worlds, report the
histogram of `|S_0 Δ roots_0| + |S_1 Δ roots_1|`. Measured on the reference at
`k ≤ 5`: `{1: 3038, 2: 372}`. The shallow ablation yields
`{1: 1372, 2: 1472, 3: 518, 4: 48}` on the same population — the saturated
statistic cannot tell them apart and the histogram can. **The histogram MUST
differ from every ablation's**, and both are reported.

### Ablations. Caught MUST be > 0; checked reported. Population: both phases.

- **ABL-SHALLOW.** `root(c)` replaced by `parentIndex(c)` where non-null, else
  `c`. Caught iff `S_a^shallow ≠ S_a` for either `a`.
- **ABL-CLAIMCOUNT.** `S_a` replaced by the claims asserting `a`, compared by
  cardinality. Caught iff the resulting verdict differs from the registered one.

## 8. Invalidation

Exhaustive count ≠ 50,362; any MUST-be-0 observed non-zero; any MUST-be->0
observed zero; L1-DISC's histogram equal to any ablation's; any `uniform_below`
implemented with a float; any modulus whose rejection probability exceeds 1/1000
consuming exactly 1,000 words; either phase digest differing from its first
computation within the run.
