# KL-000 — independent reimplementation: results and findings

Written from `PROTOCOL.md`, `preregistration.json` and `fixtures/c01…c10.json`
only. The reference implementation was not located and not read. Nothing in this
document is a comparison against it.

Language: Rust 2021, zero dependencies. JSON codec, SHA-256 and the PRNG are
hand-written so that no library is shared with a Python reference.

Status of this run: **passed** — 0 hard-invariant violations by B5 across all
four phases, with all four preregistered baselines caught.

---

## 1. Counts per phase

### World count, derived before implementing

`sum(4^L for L in 1..4) = 340` location ledgers ·
`sum(6^R for R in 0..3) = 259` evidence ledgers · 2 claim types = **176,120**.
Derived independently; **agrees** with `declaredWorldCount`. No finding here.

### Phase 1 — fixture (C01–C10)

10 / 10 match on the first execution. Every declared field of `expected`
compared: `conclusion`, all four `search` fields, all seven `evidence` fields.
0 invariant violations. No fixture required a second attempt or a tolerance.

### Phase 2 — exhaustive-small

| | |
|---|---|
| worlds enumerated | 176,120 (asserted before any invariant was evaluated) |
| **receipt-producing** | **110,840** |
| **fail-closed, no receipt** | **65,280** (37.07%) |
| fail-closed causes | `root_on_both_sides`: 65,280 — **one cause, 100%** |
| unexpected causes | none |
| hard violations (B5) | **0** |
| stop condition | armed, never triggered |
| wall clock | 12.2 s, 14,448 worlds/s |

Conclusion distribution over the 110,840 receipts:

| conclusion | count |
|---|---|
| `present` | 41,820 |
| `supported` | 41,820 |
| `not_established` | 27,040 |
| `absent_within_declared_scope` | **160** |

**Why 65,280 produce no receipt.** The evidence-ledger enumeration is over
(root, side) pairs, so it contains ledgers in which one rootId carries both
`support` and `oppose`. I3 requires those to fail closed. Of the 259 evidence
ledgers, 96 contain such a conflict (0 at length 0–1, 6 of 36 at length 2, 90 of
216 at length 3), leaving 163 clean. `340 × 96 × 2 = 65,280` and
`340 × 163 × 2 = 110,840`. Both figures were derived from the declared bounds
**before** the implementation was written and were then reproduced by it.

The whole distribution is independently re-derivable, which is how I checked the
code rather than trusting it: 123 of the 163 clean ledgers carry at least one
opposing record, so `present = 340 × 123 = 41,820`; by root/side symmetry
`supported = 41,820`; only 4 of the 340 location ledgers are all-`searched`, and
40 clean ledgers have no opposing record, so `absent = 4 × 40 = 160`; and
`not_established = 336 × 40 + 340 × 40 = 27,040`. All four match the run exactly.

### Phase 3 — randomized

Seed 20260807, 1,000,000 worlds, bounds 1–12 locations / 0–24 records / 8 roots.

| | |
|---|---|
| worlds | 1,000,000 |
| **receipt-producing** | **244,091** |
| **fail-closed, no receipt** | **755,909** (75.59%) |
| fail-closed causes | `root_on_both_sides`: 755,909 — **one cause, 100%** |
| unexpected causes | none |
| hard violations (B5) | **0** |
| generator within declared bounds | yes |
| seed reproduces an identical stream | yes (regenerated and hash-compared) |
| wall clock | 35.8 s, 27,970 worlds/s |

| conclusion | count |
|---|---|
| `present` | 82,077 |
| `supported` | 81,912 |
| `not_established` | 79,032 |
| `absent_within_declared_scope` | 1,070 |

The fail-closed rate is not an implementation artefact. The analytic
probability that a uniform draw of R ∈ 0..24 records over 8 roots × 2 sides
contains no both-sided root is 0.24369, predicting 243,686 receipts; 244,091
were observed, inside one standard deviation (429). Generator and evaluator
agree with the closed form.

**These randomized counts are not comparable to any other implementation's** —
see finding F11.

### Phase 4 — adversarial

10 / 10 attacks behaved as specified. These are **my own ten attacks**, not the
reference's; see finding F12.

### Positive control — baselines over the full 176,120-world set

Not a subsample. Halting disabled so complete counts are obtained.

| baseline | total violations | by invariant |
|---|---|---|
| B1 head-count | 1,206,000 | I1 816,000 · I10 297,840 · I3 65,280 · I2a 13,440 · I2b 13,440 |
| B2 source-count | 124,280 | I8 110,840 · I2b 13,440 · **I2a 0** |
| B3 evidence-without-coverage | 26,880 | I2a 13,440 · I2b 13,440 |
| B4 search-without-collapse | 681,360 | I1 514,080 · I10 167,280 |

All four non-zero. **The checker has power; the run is not vacuous.** Each
baseline fails the invariant the preregistration nominates — with one exception
that is finding F1.

### Uncertainty

Zero violations in n = 1,000,000: rule-of-three 95% upper bound on per-world
violation probability **3.0 × 10⁻⁶**; Bonferroni-adjusted per-invariant
**5.3 × 10⁻⁶**. This bounds a rate. It does not establish zero.

---

## 2. Which invariants the phases exercise, and which they do not

Worlds reaching each invariant's check:

| | fixture (10) | exhaustive (176,120) | randomized (1,000,000) |
|---|---|---|---|
| I1 copy invariance | 10 | 110,160 | 203,943 |
| I2a / I2b bounded absence | 10 | 110,840 | 244,091 |
| I3 side separation | 10 | 176,120 | 1,000,000 |
| I4 deterministic replay | 10 | 110,840 | 244,091 |
| I5a / I5b counterexample dominance | 8 | 55,420 | 121,875 |
| I6 digest integrity | 10 | 110,840 | 244,091 |
| I7 order invariance | 10 | 110,840 | 244,091 |
| I8 search arithmetic | 10 | 110,840 | 244,091 |
| I9 fail-closed parsing | **0** | **0** | **0** |
| I10 copies never mint roots | 10 | 110,840 | 244,091 |

**Not exercised, and worth saying plainly:**

- **I9 is exercised by no non-adversarial phase at all.** No fixture is
  malformed and both generators emit only well-formed documents. The 65,280 and
  755,909 refusals are all I3, not I9. I9's entire evidence is the five schema
  attacks I wrote myself. A run that reported "fail-closed count" as one integer
  would have hidden this completely.
- **I3 is not exercised by any fixture.** No control has a root on both sides.
  I3 is a hard invariant whose fixture coverage is zero.
- **I4, I6 and I7 are not exercised by the fixtures as written** — no fixture
  states a digest or a permuted variant. They are exercised here only because my
  checker runs over the fixture worlds too.
- **I1 is vacuous for 680 exhaustive worlds** (110,840 − 110,160): an empty
  evidence ledger has no record to duplicate. Same for 40,148 randomized worlds.
- **The `absent_within_declared_scope` conclusion is reached 160 times in
  176,120 worlds (0.09%),** across only 4 distinct location ledgers (the
  all-`searched` ones). The negative direction of I2 is covered 13,440 times;
  the positive direction rests on a very narrow slice.
- **No fixture, and no preregistered baseline, distinguishes I5a from I5b** (F2).

---

## 3. Findings

### F1 — I2 is stated in two forms that are not equivalent, and the difference lets a preregistered must-fail baseline through

`preregistration.json` I2:

> conclusion == 'absent_within_declared_scope' implies **search.complete** is
> true and opposingRoots is empty. **Equivalently** no absence conclusion is
> reachable while any **location status** is not 'searched'.

The first clause is about fields **of the receipt**. The second is about **the
world**. They coincide only if I8 already holds. They are not equivalent, and
the word "Equivalently" asserts that they are.

I implemented both — I2a (receipt-internal) and I2b (world-referential) — and
kept the counts apart. The consequence is measurable:

> **B2-source-count records 0 I2a violations across all 176,120 worlds.**

B2's registered `expectedOutcome` is "MUST FAIL bounded absence (I2)". An
evaluator that never reads the search ledger has nothing to put in `search`, so
it reports `complete: true`; I2's antecedent is then satisfied by construction
and the literal invariant passes. B2 is caught only by I2b (13,440) and by I8
(110,840). Under the invariant exactly as registered, **B2 does not fail I2**.

This is the finding the exercise is for: an implementation reading I2 the other
way would report B2 as failing I2 and neither implementation would notice the
gap. The reading is what differs, not the arithmetic.

*Recommended repair:* state I2 world-referentially and make the receipt-internal
form a corollary of I8, or register both as separate invariants.

### F2 — I5 has the same defect, and nothing in the protocol would reveal it

I5 reads "a non-empty **opposingRoots** implies conclusion == 'present'" —
again a receipt field. An evaluator that simply omits opposing roots from the
receipt satisfies it vacuously while converting counterexamples into silence.
I check I5a and I5b separately for the same reason.

Unlike F1, **no preregistered baseline exposes this**: B1–B4 all report opposing
roots faithfully, so I5a and I5b have identical counts (both 0) throughout. The
defect is real but the declared positive control has no power against it. A
fifth ablation — "drops opposing roots from the receipt" — would close the gap.

### F3 — B2 and B3 are the same ablation

- B2: "counts distinct roots but ignores the search ledger."
- B3: "full root collapse, no coverage requirement for absence."

An evaluator that ignores the search ledger *is* an evaluator with no coverage
requirement. I built B2′ — B2 with an honest `search` block — and it is
**byte-identical to B3 on all 176,120 worlds** (both 26,880 violations, both
I2a 13,440 / I2b 13,440). The two baselines are only distinguishable if B2 is
additionally taken to *fabricate* its search block, which is the reading I used
for the registered B2. Nothing in the preregistration says so. Two of the four
positive controls may be one control counted twice.

### F4 — `conversionsToReverse` is never defined anywhere

It appears in all ten fixtures and in I1's freeze list, and is defined in no
document. I reverse-engineered it. The unique formula fitting all ten fixtures:

```
conversionsToReverse = floor(|margin| / 2) + 1
```

— the least k such that converting k roots from the majority side to the
minority side makes the minority **strictly** larger. Fixture margins
1,3,3,1,2,3,1,3,1,1 → 1,2,2,1,2,2,1,2,1,1. ✓

**Rejected:** `ceil(|margin|/2)`, the least k reaching margin ≤ 0. C05 rules it
out (margin 2, expected 2; `ceil` gives 1). Distinguishing fixture: C05.

**Still undetermined:** negative margin (no fixture has one), and the empty
ledger, where the formula returns 1 although there is **no root available to
convert**. A receipt saying "1 conversion would reverse this" when the ledger is
empty is arguably wrong; reversing it needs an *addition*, not a conversion.
Nothing in the specification decides this. I did not cap the value.

### F5 — `margin` sign is undetermined, and it moves 38,760 worlds

Every fixture has margin > 0, so nothing distinguishes signed
`|support| − |oppose|` from absolute value. I chose signed. **38,760 of 176,120
exhaustive worlds (22.0%) get a different receipt** under the other reading.
Both implementations could pass all ten fixtures and disagree on a fifth of the
enumeration.

### F6 — presence-claim semantics are almost entirely undetermined

Only C01 and C02 are presence claims. Both have complete coverage, both are
support-only. Nothing in the fixture set or the invariants says what a presence
claim does with incomplete coverage or with opposing evidence. Measured cost of
the two readings I rejected:

| ambiguity | rejected reading | exhaustive worlds changed |
|---|---|---|
| A2 | presence also requires complete coverage | **41,328 (23.5%)** |
| A3 | opposing ≥ supporting defeats a presence claim | **22,440 (12.7%)** |

I chose "no" for both: presence is existential, one witness settles it, and
"I searched and did not find it" cannot defeat "it was found" — which is exactly
the asymmetry the protocol exists to encode. But that is my inference, not the
specification's statement. **Together, F5 and F6 leave roughly a third of the
exhaustive enumeration underdetermined by the documents I was given.**

### F7 — does absence need any supporting evidence?

I2 gates absence on coverage alone. Under that reading a world with complete
coverage and an **empty evidence ledger** receives
`absent_within_declared_scope`. Under the alternative, absence needs ≥ 1
supporting root. Only **4 worlds** differ, so the practical cost is small — but
those 4 are the epistemically loudest worlds in the enumeration: a receipt
asserting bounded absence with no evidence in it at all. C04 and C07 show a
single collapsed root (margin 1) is enough, so the evidence ledger is doing no
work at the threshold anyway. I chose coverage-alone and flag it.

### F8 — a zero-location search ledger yields absence for free (specification defect)

Under the literal text — `declared == len(locations)`,
`complete == (searched == declared)` — a search ledger with **no locations** has
`declared == 0`, `searched == 0`, `complete == true`. I2's antecedent is
satisfied vacuously and `absent_within_declared_scope` is issued for a world in
which **nothing was searched**. That is precisely the laundering the experiment
exists to prevent, and it is reachable by following the specification exactly.

The declared bounds say `locationCount ≥ 1`, so the enumerated phases never
reach it — the phases cannot find this, only an adversary can. I refuse the
input (`empty_search_ledger`, attack A06). An implementation that follows the
text literally will emit an absence receipt here, and I would call that
implementation wrong rather than call this a disagreement.

*Recommended repair:* `complete` should require `declared > 0`.

### F9 — location id uniqueness is never stated (specification gap)

I8 fixes `declared == len(locations)`. Nothing says location ids must be
distinct. If duplicates are permitted, `declared` counts **entries**, not
locations, so padding the ledger with copies of an already-`searched` location
changes the coverage arithmetic — the search-ledger analogue of exactly the copy
attack I1 exists to stop on the evidence ledger. I refuse duplicates (attack
A07). Nothing in the specification requires that, and the mirror-image of I1 for
the search ledger is simply absent from the invariant set.

### F10 — "canonical JSON" and `contentDigest` are undefined

I4 requires "byte-identical canonical JSON", I6 requires a self-verifying
`contentDigest`, and neither is defined: no key ordering, no escaping rule, no
statement of which fields the digest covers. No fixture states a digest, so
nothing pins it down. I declared a canonicalisation (sorted keys, no whitespace,
digest = sha256 over the receipt minus `contentDigest`) and documented it.

**Consequence: digest values cannot agree across implementations, and were never
going to.** I4 and I6 are self-referential — they constrain an implementation
against itself, not against the protocol. What *is* cross-checkable is the
structural property behind them, which I verified: the receipt contains no
input ordering anywhere, which is what makes the digest survive permutation
(I7). I6 was checked by mutating each of the 15 receipt fields in turn,
including substituting `contentDigest` itself; all 15 mutations fail
verification on every world in every phase.

### F11 — the frozen seed does not freeze a world stream

`randomizedSeed: 20260807` and "Python stdlib random.Random" fix a generator but
**not the draw schedule**: how many variates per world, in what order, or with
what distribution over the declared ranges (the preregistration gives ranges
only — uniformity is nowhere stated). Two independent implementations cannot
sample the same worlds even if both used Mersenne Twister.

So the invalidation clause *"the frozen seed does not reproduce an identical
world stream"* is checkable only **within** one implementation. I check it that
way — regenerate the stream, hash it, compare
(`fnv1a64:4dee7326f948b0fe`, reproduces) — and state clearly that **my randomized
counts and the reference's are not comparable quantities.** Only the shape is:
one dominant fail-closed cause, a ~24% receipt rate that matches the closed form,
zero violations.

*Recommended repair:* register the draw schedule and the distribution, or drop
the invalidation clause as unverifiable.

### F12 — the adversarial phase has no specification

PROTOCOL.md phase 4 is "the ten attacks in `tests/test_kl000_adversarial.py`".
That file is not in the package and its contents are described nowhere. The
adversarial phase is therefore **not reproducible from the protocol** — it is
defined by reference to code, which is the one thing a preregistration is
supposed not to do. RESEARCH-METHOD.md's requirement that "a clean environment
must reproduce the artifact from the public protocol" cannot be met for this
phase.

My ten attacks (A01–A10) are my own construction from the invariants and the two
declared limits. They should not be read as agreeing or disagreeing with the
reference's ten.

### F13 — C06's note contradicts C04 and C07 in the same fixture set

C06: *"Absence is admissible here and only here."* But C04 (8 records, 1 root)
and C07 (20 records, 1 root) both also conclude `absent_within_declared_scope`.
The distinguishing feature C06 names — "three distinct roots, nothing collapsed"
— is not what the evaluator gates on; complete coverage with no counterexample
is. A reader calibrating on that note would build an evaluator that fails C04
and C07. The note is wrong about the fixture set it belongs to.

### F14 — `unavailable`, `failed` and `not_searched` are reported but inert

`unavailable` gets its own receipt field and its own clause in I8, yet no
conclusion anywhere depends on it: coverage is `searched == declared`, so
`unavailable`, `failed` and `not_searched` are equivalent in every conclusion the
evaluator can reach. C08's own note flags the residue (`searched + unavailable =
4 ≠ declared 5`, "and the receipt does not say why"). The receipt therefore
carries a distinction it never uses, which invites a reader to believe
`unavailable` is doing epistemic work. It is not.

### F15 — the exhaustive phase tests conclusions on 63% of what it enumerates

"Complete cartesian enumeration of 176,120 worlds" is accurate about
enumeration and misleading about coverage: 65,280 of those worlds (37%) fail
closed before any conclusion logic runs. The conclusion rules are exercised on
110,840. This is not a defect — fail-closing is correct behaviour — but the
protocol reports one number where two are needed, and the same is much starker in
the randomized phase (76% fail closed). Amendment 2(b) added cause-bucketing for
exactly this reason; the count itself deserves the same treatment.

---

## 4. Where I think the specification is wrong, not merely ambiguous

Ranked:

1. **F8, the empty search ledger.** Following the text produces a bounded-absence
   receipt for a world where nothing was searched. This is a defect, not a
   reading — the protocol's own question is whether the evaluator can stop
   "incomplete coverage from proving absence", and zero coverage is the limiting
   case of incomplete.
2. **F1, "Equivalently" in I2.** The two clauses are not equivalent, and the
   difference is large enough that a registered must-fail baseline survives the
   invariant it was registered to fail.
3. **F13, C06's note.** Contradicted by two other fixtures in the same directory.
4. **F12, the adversarial phase defined by reference to absent code.**
5. **F3, B2 and B3 being one ablation.** The positive control is weaker than the
   four-baseline table implies.

## 5. What this run does and does not establish

It establishes that **an implementation written from these documents alone
satisfies all ten invariants, under the readings recorded above, across 176,120
enumerated worlds and 1,000,000 seeded worlds, with a checker demonstrated to
have power against four ablations.**

It does not establish that the reference implementation is correct. It does not
establish that these two implementations agree — that has not been tested, and
if it is tested later, agreement will establish agreement and nothing more. On
the specific readings in F4–F7 the specification does not determine an answer, so
agreement there would be evidence about shared assumptions, not about
correctness. Digest values (F10) and randomized counts (F11) cannot agree in
principle and their disagreement means nothing.
