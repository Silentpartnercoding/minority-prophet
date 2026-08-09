# LIN-000 v0.3 — testing the theorem the paper states

Registered by RUN-20260809-1 **before the v0.3 reference exists**. Supersedes
v0.2's Part 5 (the semantics under test) and adds a generator-conformance phase.
v0.2's generator, draw schedule, enumeration order and canonical form are
**carried unchanged** — BL-051 established they are sufficient for
cross-implementation reproduction, and nothing here disturbs them.

Traceability per TRC-101: `TRACEABILITY-v0.3.json` (BL-042 — applied at
registration time, which is the point).

## Why v0.3

BL-051 confirmed v0.2's stream is reproducible. It also found that the thing the
stream exists to test was not being tested.

**D4 — T1-positive was an identity, not a test.** v0.2 asked for rewirings
"root-preserving" in the sense that `root(c)` is unchanged for every claim `c`.
`S_a` is defined as `{root(c) : side(c) = a}`, so preserving every `root(c)` and
touching no side leaves `S_a` unchanged **by construction**. It cannot fail. It
appeared under the heading "Tests that can fail".

**And it was the wrong statement.** Paper v1.0.4, Theorem 1 (Immunity), line 63:

> *Any rewiring of parent edges that (i) preserves the **root set** and (ii)
> preserves side-consistency leaves S₀, S₁, and the verdict exactly unchanged.*

The paper preserves the **root set** — the set of claims that are roots — not
each claim's individual root. That is strictly weaker, and therefore a real
claim. v0.2 tested a condition *stronger* than the theorem, which is why it could
not fail.

The independent implementation measured all four parses. Under the paper's
reading it checked **121,944 rewirings with 0 violations** — a figure that
appears nowhere in the commission package and matches the paper's own published
exhaustive check (*"5,912 worlds; 121,944 rewirings"*) exactly. That agreement,
reached blind, is the evidence that this reading is the intended one.

**D5 — dropping clause (ii) breaks it, and that was never registered as a
control.** With side-consistency not required of the original world, the same
weak root-preservation yields **47,224 violations**. That is not a
counterexample to Theorem 1; it is a demonstration that clause (ii) is
load-bearing. It belongs in the registration as a *required* failure.

**D6 — the ablations were named, not defined.** "A shallow-`S_a` and a
claim-count ablation" fixes neither construction nor catch criterion. The
reference and the independent implementation built different ones and reported
different counts.

**D7 — the rejection rule is never exercised.** Across 2,759,273 words, zero
rejections, and not by chance: `uniform_below(20)` rejects 16 of 2³² values,
`uniform_below(2)` and `(1)` never reject. Two implementations could disagree
about the rule entirely and match every digest.

**D8 — `id` is unbound.** Present in the schema, never generated, never in the
canonical form.

**D9 — L1-negative's population was unstated.**

## Carried unchanged from v0.2

The generator (`SHA-256(seed_be ‖ uint64_be(m))`, words consumed in order),
`uniform_below(n)` with its stated rejection rule and word costs, the randomized
draw schedule including claim 0, the exhaustive enumeration order, and the
canonical stream form. Seed **20260808**. Both phase digests are unchanged from
v0.2 and are **not** re-pinned here; a v0.3 implementation must reproduce the
v0.2 digests, which are already published in `results/lin000-v2-result.json`.

## Schema: `id` bound (D8)

`id` is **removed** from the world schema. It was never generated, never
referenced, and never entered the canonical form. A world is an ordered list of
claims `[{parentIndex, side}]`. Nothing else changes.

## Generator conformance phase (D7) — new

Before either world phase, an implementation must emit a **generator conformance
vector** that forces the rejection rule.

For each modulus `n` in the registered list below, in order, draw
`uniform_below(n)` **1,000 times** from a generator freshly seeded at
`seed = 20260808`, restarting the word sequence for each modulus. Report, per
modulus: the 1,000 outputs' SHA-256 over the ASCII decimal values joined by `,`
with no trailing separator, and the **number of words consumed**.

    moduli: 2863311531, 2576980378, 1717986919, 20, 10, 2, 1

The first three have `2**32 mod n` large — 1,431,655,765, 1,717,986,164 and
1,431,655,763 respectively — so rejection occurs on roughly 33%, 40% and 33% of
draws. The word count is the observable: an implementation that omits the
rejection rule consumes exactly 1,000 words and produces different values.

`uniform_below(1)` is included because it consumes one word and returns 0, and an
implementation that short-circuits it consumes zero.

## Semantics under test — defined, not named

### Rewiring (D4)

A **rewiring** of a world `W` with `k` claims is a world `W'` with the same `k`,
the same `side` for every index, and a `parentIndex` vector differing from `W`'s
in at least one position, where each `parentIndex` is `null` or a strictly
earlier index. The population is every such `W'`, enumerated over all worlds in
the exhaustive phase.

- **root set of `W`** = `{i : W[i].parentIndex is null}`, the set of claims that
  are roots.
- **root-preserving** = the root set of `W'` equals the root set of `W`. This is
  the paper's clause (i), and it does **not** require `root(c)` to be unchanged
  for each `c`.

### T1-POS — the paper's Theorem 1 (must be 0)

Over rewirings where `W` is side-consistent, `W'` is side-consistent, and the
rewiring is root-preserving: the verdict of `W'` MUST equal the verdict of `W`.
**Violations MUST be 0.** Rewirings checked MUST be > 0 and is reported.

### T1-NEC — clause (ii) is load-bearing (must be > 0) (D5)

The same population with the requirement that `W` be side-consistent **removed**.
Verdict changes MUST be **> 0**, and the count is reported. A zero here
invalidates the run: it would mean the precondition is decorative, contradicting
`CE06_root_supports_both_sides`.

### T1-ID — declared an identity, not a test (D4)

Over rewirings preserving `root(c)` for **every** `c`: the verdict cannot change,
because `S_a` is a function of the multiset `{(root(c), side(c))}` alone. This is
recorded as a **consistency check on the implementation's `S_a`**, not as
evidence about the schema. Reported, and expected 0 by construction.

### L1-POS / L1-NEG (D9)

- **L1-POS:** on side-consistent worlds, `S_a` MUST equal
  `{i : W[i].parentIndex is null and W[i].side == a}`. Violations MUST be 0.
- **L1-NEG:** on side-**inconsistent** worlds, worlds where `S_a` differs from
  that set MUST exist. **Population: the exhaustive phase and the randomized
  phase, reported separately.** Both MUST be > 0.

### Ablations (D6) — constructions and catch criteria stated

- **ABL-SHALLOW.** Replace `root(c)` with `parentIndex(c)` where non-null, else
  `c` itself — depth-one attribution instead of chain-walking. `S_a^shallow` is
  built from that. A world is **caught** iff `S_a^shallow ≠ S_a` for either `a`.
  Caught MUST be > 0.
- **ABL-CLAIMCOUNT.** Replace `S_a` with the multiset of claim indices asserting
  `a`, and compare cardinalities. A world is **caught** iff the resulting verdict
  differs from the registered verdict. Caught MUST be > 0.

Both are reported with their checked totals, so a catch rate is computable.

## Invalidation

Exhaustive count ≠ 50,362; either phase digest differing from the v0.2 published
value; any MUST-be-0 observed non-zero; any MUST-be->0 observed zero; any
`uniform_below` implemented with a float; any conformance modulus whose word
count equals 1,000 for a modulus with a non-empty rejection region.

## What v0.3 does not change

The generator, the streams, the schema's semantics, τ = 0, and the declared
bounds. Only what is tested, and how precisely it is stated.
