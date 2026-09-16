# DRI-9 v1 — post-result note, 2026-09-16

**The verdict is unchanged: rejected, 58 of 65.** The arithmetic in `result.json`
stands, the manifest still matches every file it attests to, and the frozen
protocol is untouched. What this note corrects is three claims made *around* that
result, in the write-up and the indexes, and two structural holes in the
criterion.

The holes were found by an adversarial review of the published record (PR #204,
`ADVERSARY-NOTE.md`), written in the same control domain and therefore not
independent validation. Every claim below was re-measured here against the frozen
`result.json` and the pinned world before being accepted.

## 1. The decoy family planted no markers, so bait's "no harm" was not a test

`generate_campaign` marks a component only where one exists, and
`coincident_independents` has none, so `marked_component` is `None` there and
`marker_leak` never fires.

| Salt | Family | Marked component | Markers emitted |
|---|---|---|---:|
| development | shared upstream pair | `hidden:u` | 1,167 / 768 decisions |
| development | shared upstream trio | `hidden:u` | 1,719 / 768 decisions |
| development | **coincident independents** | **none** | **0 / 768 decisions** |
| confirmatory | shared upstream pair | `hidden:u` | 1,171 / 768 decisions |
| confirmatory | shared upstream trio | `hidden:u` | 1,687 / 768 decisions |
| confirmatory | **coincident independents** | **none** | **0 / 768 decisions** |

Bait's merge counts in that family are 0 true and 0 false in every cell, because
it never saw a marker to act on. The README's "in the decoy family it made
**zero** merges, zero silent errors and lost **zero** correct settlements" is
arithmetically true and evidentially empty: the instrument was unplugged. The
same sentence in `EVIDENCE-ALIGNMENT.md` and `CANONICAL-RECORDS.md` is corrected
in this commit to say no markers were emitted.

A harm test for bait requires a family where independent sources can carry the
mark. DRI-9 does not contain one.

## 2. "Margin-critical" filtered nothing

`criticalTieredSilent` equals `reversibleTieredSilent` in all eight hidden-family
cells: 965, 956, 923, 1,009 in the pair family and 1,154, 1,188, 1,181, 1,199 in
the trio — identical on both sides in every case.

So every reversible silent false settlement was margin-critical, and the effect
floor was measured over the whole set. The endpoint was built to repair DRI-8's
mis-specified margin test; here it is an identity, and the write-up's framing
"on margin-critical decisions" promises a filter that did no work.

## 3. Relabelling the method turns this same result green

Running `evaluate_criterion` on this record's `semanticResult` with
`method_under_test = "bait"` returns **supported, 65 of 65**. No new world, no new
salt, no new evidence — only a different name in the configuration.

That is why a successor must not simply name bait on this generator: it would
reprint a result already implied by these numbers. `PREREGISTRATION.md` §12 said
that if bait won on this salt, that was the finding; it did, and the finding is
recorded here rather than re-earned by relabelling.

## 4. Two structural holes in the criterion

- **All-underpowered reads as supported.** With no powered cell the criterion
  returns `supported: True`, and `test_criterion_logic_on_constructed_rows`
  asserts that as intended behaviour. "We could not test this" and "this passed"
  must not share an outcome. A successor must fail closed.
- **No-harm ignores lost correct settlements**, except for the named method.
  Reflection passes all four decoy harm checks while cutting correct settlements
  from 3,000 to about 1,300. The "4 harm flags" in the write-up were computed by
  hand for the narrative; they are not among the 65 checks.

## 5. What stands

- The verdict: **rejected**, on the effect floor, in seven of eight powered cells.
- The measured behaviour of every arm in the hidden families, including bait's
  34–77% prevention scaling with pickup rate, and the ladder's 1-of-8 result with
  0–6 false merges.
- The reason this experiment exists: belief must override the record's identities
  or an instrument cannot act on what it finds
  (`results/dri8-v1/POST-RESULT-NOTE.md`).

## 6. What a successor owes

1. A family where independent sources can carry the mark, so harm is testable.
2. A margin filter that filters, or no margin framing at all.
3. A criterion that fails closed when underpowered.
4. Harm scored as lost correct settlements for every arm, not only the named one.
5. Bait named in advance, on a world that can reject it — not this one.
