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

**Theorems held — with one claim since withdrawn.** Zero L1-positive violations
and zero T1-positive violations in both phases; negative controls fired in both.
**The T1-positive zero was later shown to be a definitional identity rather than
a test** (see the closing section below); the informative results are L1-positive,
L1-negative, T1-negative and the two ablations.
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

---

# Closed 2026-08-09 — the repair works, and the test it enabled does not

Independent reimplementation delivered. Artifacts imported verbatim to
`lineage/results/independent-v2/`.

## The commissioned question: answered, yes

Both digests reproduced **on the pre-declared reading, with no sweep**, in **two
languages** — Rust with a hand-written SHA-256 and JavaScript on Node with
`node:crypto`, written separately and required to agree with each other on 57
fields before either was compared with the pinned file.

All **150 prefix digests** matched as well as the two totals; `firstDivergentBlock`
is null in both phases. The implementer's `DECISIONS.md` is SHA-256 pinned and the
hash still verifies, and they emitted machine-readable
`sweptOrTuned: false` and `readingAmendedAfterComparison: false`.

The ambiguity space, measured after the hit rather than searched before it:

| | v0.1 | v0.2 |
|---|---|---|
| exhaustive readings admitting a distinct digest | 96 | **8** |
| randomized readings admitting a distinct digest | 72 | **12** |
| correct one | found by sweep | **the frozen baseline, both phases** |

**F11's repair is sufficient in the v0.2 shape** — define the generator in the
document, register draws as primitives with their word costs, state every order.
Not in the v0.1 shape, which named a language's generator and left orders unsaid.
That distinction is the deliverable.

## T1-positive is an identity, and this programme said otherwise

`S_a` is defined as `{root(c) : side(c) = a}`, so it is a function of the multiset
of `(root(c), side(c))` pairs alone. A rewiring that preserves every `root(c)` and
touches no side leaves that multiset identical — therefore `S_0`, `S_1` and the
verdict are identical **by construction**.

T1-positive cannot fail. Its zero is not evidence about the schema; it is evidence
that the implementer's `S_a` matches the registered one, which the digests already
established. It sits under the registration's heading *"Tests that can fail"*.

**FINDING-BL044 and the body of this finding both claimed Theorem 1 was "no longer
shadow-tested".** For T1-positive that was wrong, and it was wrong in the same way
twice, in this programme's own records. Both are corrected in place. The results
that do carry information — and all passed — are L1-positive, L1-negative,
T1-negative (17.5M verdict changes, so the positive case is not vacuous by
absence), and the two ablations.

## And under a defensible reading, the registration's claim is false

"Rewiring", "root-preserving", and the scope of "side-consistent" are all
undefined. Four readings survive; the implementer tested all four:

| reading | root-preserving means | original must be side-consistent | rewirings | violations |
|---|---|---|---|---|
| A (their pre-declared) | `root(c)` preserved ∀c | yes | 57,240 | 0 |
| B | only the *set* of root claims | yes | 121,944 | 0 |
| C | `root(c)` preserved ∀c | no | 57,240 | 0 |
| **D** | only the *set* of root claims | no | 200,024 | **47,224** |

Under reading D the registration's *"Violations MUST be 0"* is false 47,224 times.
Verified independently here, at k = 3:

    original :  -|0 ; -|1 ; 0|1    side-inconsistent   S1={0,1}   verdict 1
    rewired  :  -|0 ; -|1 ; 1|1    side-consistent     S1={1}     verdict abstain

The set of root claims is preserved, no side moves, and only `root(2)` shifts from
0 to 1. So **v0.2 does not determine T1's truth value.** One sentence would.

The implementer also filed a correction against their own pre-declaration: `R23`
predicted the weak root-preservation reading alone would break T1-positive, and it
does not — reading B holds, because side-consistency plus Lemma 1 forces `S_a` to
equal the root set. The failure needs both loosenings. *"My prediction identified
the right term and the wrong boundary."*

## A coverage gap neither party set out to find

The registered rejection rule — the acceptance test v0.2 added specifically to
remove v0.1's "uniform in 1..20" ambiguity — was exercised **zero times**:

    2,759,273 words consumed    0 rejections    66,427 uniform_below(1) calls

It cannot be exercised by accident. `uniform_below(20)` rejects 16 of 2^32 values,
`uniform_below(10)` rejects 6, and `uniform_below(2)` and `(1)` never reject. Two
implementations could disagree entirely about the rejection rule and still match
every digest. This is the same shape as I9 in the conformance profile: a rule
whose evidence is structurally absent rather than merely thin. The degenerate case
is genuinely covered, at 66,427 calls.

## v0.3, and it is a different kind of work

The stream problem is solved. What remains is what the theorems are tested *over*:

1. **Define "rewiring", "root-preserving", and the scope of "side-consistent"** —
   and decide reading A–D deliberately, since D makes the registered claim false.
2. **Replace T1-positive with something that can fail**, or relabel it as the
   consistency check it is. A definitional identity under "Tests that can fail" is
   the vacuity this programme exists to catch.
3. **Define the two ablations.** Named, not specified; the reference and the
   independent implementation caught different counts because they built different
   ablations.
4. **Force the rejection path** with a seed or phase that triggers it.
5. **Bind or remove `id`** — present in the schema, never generated, never in the
   canonical form.
6. **State L1-negative's population.**

BL-051 closes. Items 1–6 open as **BL-053**.
