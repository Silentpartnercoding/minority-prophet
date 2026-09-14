# When Counting Is the Wrong Instrument: Asymmetric Claims in Rooted Evidence Graphs

**Status: DRAFT v0.1. Not submitted. Not deposited. No DOI.**
Drafted 2026-09-14. Companion to *The Minority Prophet Property* (archival
record, all versions: `10.5281/zenodo.21965712`). Recorded in `papers/ERRATA.md`
under `[E9]`.

---

## Abstract

The aggregator at the centre of this programme compares two root counts. This
paper exhibits a class of claims for which that comparison returns **the wrong
side**, proves the rules that replace it, and shows that the failure cannot be
repaired by any threshold on the margin.

The result is not that the aggregator is unsound. Every theorem about it holds.
The result is that for asymmetric claims it is **answering a different question
from the one being asked**, and the two questions have different answers on the
same evidence.

Both replacement rules are Lean-checked and shipped:
`formal/lean/MinorityProphetCore/Asymmetric.lean` (10 results, ledger AC1–AC5)
and `aggregation/root_vote.asymmetric_verdict`.

---

## 1. The shape of the problem

Two claim shapes do not answer to counting.

**Universal** — *every member of the scope satisfies P.* One counterexample root
settles it **against**, whatever the confirming count. A thousand white swans do
not establish the claim; one black swan ends it.

**Existential** — *some member of the scope satisfies P.* One verified root
settles it **for**, and roots reporting an unsuccessful search cannot out-vote a
find. Not finding a thing is not evidence that it is absent.

In both, the two sides carry different logical weight. Any method that compares
*how many asserted yes* against *how many asserted no* is applying a symmetric
instrument to an asymmetric question.

## 2. The machine-checked failure

`CE14_world` is four roots: three confirming, one counterexample.

| | verdict | margin |
| --- | --- | --- |
| `F` — the counting aggregator | `Verdict.one` (the confirming side) | `2` |
| `universalF` | **`refuted`** | — |

Same world, same roots, **opposite answers**. Proved by `decide`, not argued.

The mirror, `CE14_mirror_world` — one find, three unsuccessful searches:

| | verdict | margin |
| --- | --- | --- |
| `F` | `Verdict.zero` (the claim is false) | `-2` |
| `existentialF` | **`established`** | — |

`F` is wrong in the opposite direction, for the same reason. These are not
answers of differing quality. They are answers to different questions, and only
one of them is the question the claim asks.

## 3. The rules that replace it

```
universalF   W = refuted      iff  some root asserts a counterexample
existentialF W = established  iff  some root reports a find
```

**Note what is absent: no comparison, no margin, no count.** The entire
apparatus this programme is built on does not appear, because for this class of
claim it has nothing to contribute.

**Indifference (AC2).** `universal_indifferent_to_confirming_side`: worlds
agreeing on the counterexample-side roots have the same universal verdict,
whatever else differs. `F` is a function of both sides; `universalF` is a
function of one. So no amount of confirming evidence — and therefore no margin,
and therefore no flip budget — bears on a universal verdict. The corresponding
statement for `F` is false. The existential mirror is
`existential_indifferent_to_unsuccessful_search`.

**The statement is not vacuous (AC3).** Indifference alone would be satisfied by
a rule that never returns `refuted`, so the file constructs
`universal_refuted_at_arbitrarily_large_margin`: for every `k`, a world with
margin exactly `k` whose universal verdict is `refuted`. **No threshold on the
margin rescues the counting rule** — the counterexample is not outvoted at any
scale. Constructed rather than assumed, because a theorem whose hypothesis is
unreachable proves nothing.

**Robustness is strictly greater, not lesser (AC4).**
`universal_immunity_of_counterexample_roots` preserves the verdict under a
strictly **weaker** hypothesis than `immunity` in `Immunity.lean` requires: only
one side's roots need be preserved. Copy invariance follows as the special case
where copies are recorded and so create no root. The asymmetric verdicts survive
corruption the symmetric one does not.

## 4. What was done about it

The repository's standard is that **a proved rule may be implemented; an
implemented rule may not be assumed proved.** Accordingly the rules were compiled
first and shipped second.

`aggregation.root_vote.asymmetric_verdict` implements AC1–AC5. It is a
**separate function, not a mode** of `verdict`, so a caller cannot reach it by
passing a flag and cannot reach the counting rule by forgetting one.

And `verdict(..., claim_shape=)` **refuses** the universal and existential
shapes rather than answering them. The symmetric path raises instead of
returning a number it has no standing to return — which is the same fail-closed
posture the rest of the stack takes, applied to the aggregator's own scope.

## 5. What is not claimed

**The aggregator is not unsound.** Every theorem in `Margin.lean` and `Copy.lean`
holds exactly as stated. This paper adds a **scope condition**: those theorems
are about a comparison, and a comparison is the wrong instrument here.

**These rules do not establish truth.** `universalF` reports that a
counterexample was *asserted by a root*, not that the counterexample is correct.
Root qualification, authenticity and authority are outside this result, as they
are outside the foundation paper.

**One asserted counterexample is a single point of failure, by design.** A
fabricated or mistaken counterexample root refutes a universal claim on its own.
That is the correct logical behaviour and a genuine operational exposure, and the
two must be stated together. It is the reason these rules belong behind root
qualification rather than in front of it.

**Root identity still applies.** Whether two counterexample roots are one root is
the U1 question, closed separately by proximate cause and carrying its own
residual — detection is not definition.

## 6. Relation to the rest of the programme

This is the same asymmetry the assay discipline runs on. Absence of water in the
milk cannot be shown; presence of a trout can. `ASSAYER.md` §5 states it as an
evidential rule; this paper states it as a verdict rule and proves the
consequences.

## Availability

`formal/lean/MinorityProphetCore/Asymmetric.lean` — 10 results, no `sorry`,
standard axioms only, rebuilt on Lean v4.33.1.
`aggregation/root_vote.asymmetric_verdict`.
Prose narration and both witnesses: `formal/COUNTEREXAMPLES.md`, CE-14 and its
mirror.
