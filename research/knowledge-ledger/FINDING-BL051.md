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

    exhaustive   50,362 worlds   sha256:a71c64eb…3be711
    randomized  100,000 worlds   sha256:e69fc115…32a2a3e

Both regenerate identically within the run (a registered invalidation
condition). Prefix digests: 50 and 100 respectively. The two totals and all 150
prefixes are deliberately shipped in the commission package — they are the pass
condition.

**Theorems held.** Zero L1-positive violations and zero T1-positive violations in
both phases. Negative controls fired in both, so the tests can detect failure.
The exhaustive structural counts are identical to v0.1, which is the expected
cross-check: those are properties of the world *set*, which v0.2 does not change,
not of its order or its generator.

**Every count above is stated qualitatively on purpose.** BL-051 is a live
commission, and its withheld set is exactly these figures — stream byte lengths,
rewiring totals, witness counts, per-phase partitions. Publishing them here would
retire the counter evidence of the commission this document creates. They are in
`results/lin000-v2-result.json`, and they become publishable when BL-051 closes.

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

An earlier draft of this finding published those counters in its results
section. `scripts/check_withheld_leak.py` rejected it in CI — the control
catching the M27 defect inside the pull request that declares the commission it
protects. It was not caught locally because the guards were run before the files
were committed, so the diff they inspected was empty: the fourth vacuous
verification of this session, and the first one a control saved rather than a
reviewer.

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
