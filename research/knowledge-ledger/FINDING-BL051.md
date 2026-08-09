# BL-051 — LIN-000 v0.2: the F11 repair, repaired

Recorded by RUN-20260808-3. The registration is `lineage/REGISTRATION-v0.2.md`,
committed at `7c8233c` **before any v0.2 implementation existed**; the reference
follows in the next commit, so the ordering is checkable in git rather than
asserted.

## What BL-044 measured, and what v0.2 changes

BL-044 commissioned an independent Rust implementation against v0.1. Both
pre-declared readings missed; the matches were found by sweeping **96**
enumeration orders and **72** draw-schedule readings, one correct each. The F11
repair — register the schedule, not just the seed — was therefore **necessary but
not sufficient**.

Three measured defects, three fixes:

| defect | v0.1 | v0.2 |
|---|---|---|
| **D1** generator named, not defined | `random.Random` — required CPython internals; two conforming MT19937s diverge on the same seed | word sequence from `SHA-256(seed_be ‖ uint64_be(m))`, defined in the document |
| **D2** draws as distributions | "k uniform in 1..20" — several stream-distinct realisations | one sampler, `uniform_below(n)`, rejection rule and word cost stated, including `uniform_below(1)` consuming one word |
| **D3** no enumeration order | order-sensitive digest, unstated order | order registered across k, within k, and within a position |

Also moved into the registration: the canonical stream form, which v0.1 left to
the covering brief. Added: prefix digests every 1,000 worlds.

Probabilities are integer comparisons (`uniform_below(10) < 3`). There is no
float primitive, so no float-representation question can arise. Claim 0's draw —
the v0.1 implementer's R3, *"a genuine coin-flip in the prose"*, which they won —
is decided in the text: no draw is consumed.

## Reference results

    exhaustive   50,362 worlds   1,189,512 bytes   sha256:a71c64eb…3be711
    randomized  100,000 worlds   4,230,583 bytes   sha256:e69fc115…32a2a3e

Both regenerate identically within the run (a registered invalidation
condition). Prefix digests: 50 and 100 respectively.

**Theorems held.** Zero L1-positive violations and zero T1-positive violations in
both phases, across 11,976 exhaustive and 567,497 randomized root-preserving
side-consistent rewirings. Negative controls fired: 44,450 and 45,253
L1-negative witnesses, 79,496 and 497,603 verdict changes under cross-side
rewiring, so the tests can detect failure.

The structural counts — 5,912 side-consistent and 44,450 side-inconsistent in the
exhaustive phase — are **identical to v0.1**. They should be: those are properties
of the world *set*, which v0.2 does not change, not of its order or its
generator. That agreement is a cross-check on the new enumeration, not a new
result.

## The disclosure this finding exists to make

**v0.2's exhaustive digest `a71c64eb…` is exactly the digest the v0.1 implementer
recorded as their pre-declared MISS.**

Two things follow, and neither should be discovered later by someone reading the
digests side by side.

**Their reading was the natural one.** They did not misread v0.1's prose. The
v0.1 *reference* was the outlier, and the independent implementer reached the
order a careful reader reaches. What v0.1 called a miss was the specification
failing, not the implementer.

**The v0.2 order was not independently derived.** It was written after reading
their `DECISIONS.md` and adopts all four of their enumeration choices — including
E4, which they rated *"low confidence — nothing in the text speaks to this"*.
Registering the reading people actually reach is a defensible design decision and
arguably the right one. But it is a choice made with their answer in hand, and a
fresh implementer hitting it easily is weaker evidence than an order chosen
blind.

Stated in the commission brief as well, so the next implementer starts with it
rather than inferring it.

The randomized schedule carries no such qualification: v0.2's generator is new
and its digest matches nothing from v0.1.

## The commission

Packaged at `$HOME/Development/lin000-v2-spec`: the registration, 150 prefix
digests plus two totals, the governing method, and a manifest. Screened clean
against all 13 withheld counters in bare and comma-grouped form.

Declared **live** in `LIVE-COMMISSIONS.json`, which makes BL-051 the first
commission `scripts/check_withheld_leak.py` protects while outstanding — the
control built for the leak that spoiled its predecessor, now doing the job it
was built for rather than passing a test.

**The question it answers:** does a pre-declared reading of v0.2 hit both digests
with no sweep? A miss is the finding, not a failure, and the brief says so.

## What would falsify the repair

A fresh implementation that still needs a sweep. If the ambiguity count is above
zero and the pre-declared reading misses, "define the generator, register draws
as primitives, specify the orders" is insufficient too, and the honest conclusion
becomes that prose cannot specify a stream at all — that a registration must ship
executable reference vectors, not sentences.
