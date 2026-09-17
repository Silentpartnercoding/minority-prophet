# DRI-8 v1 confirmatory result

**Outcome:** the preregistered criterion was **supported**, 49 of 49 checks. That
sentence is true and it is the least useful thing on this page. Read section 1
before citing it.

## 1. The criterion was too weak, and the result is nearly hollow

The criterion asked whether active probing made *significantly* fewer silent
false settlements than the tiered rule. It never asked whether the difference
mattered. It did not:

| Family | Tiered rule, silent | Probe arm, silent | Removed | Share |
|---|---:|---:|---:|---:|
| shared upstream pair (m = 0, b = 10) | 2,281 | 2,201 | 80 | 3.5% |
| shared upstream trio (m = 0, b = 10) | 3,084 | 3,074 | 10 | 0.3% |

With 6,000 paired decisions per cell, an effect that small clears exact McNemar
easily: the p-values run from 2.2 × 10⁻¹⁶ to 0.016. **Significance here is a
statement about sample size, not about protection.** A successor must state a
minimum effect it will accept before it runs, and this one did not. That is a
fault in the design I wrote, not a property of the method.

Two further facts sit alongside it:

- **Correct settlements never moved.** Every arm, in every cell, settled
  correctly exactly as often as the baseline: no gain and no loss.
- **The baseline is wrong far more often than either method can repair.** In the
  pair family the true grouping fails to settle on 3,560 of 6,000 decisions while
  the record settles anyway. Most of those thousands of "false settlements" are
  that, and knowing the hidden dependence does not fix them.

## 2. A defect in the reported margin split, found after the run

The margin-critical endpoint asks whether merging the true hidden group would
change a decision. It merges the **whole** group at once. In the trio family that
is the wrong counterfactual: merging all three never flips a decision, while
merging a pair sometimes does. On 480 development decisions:

| Family | Whole-group merge flips | Any-pair merge flips |
|---|---:|---:|
| shared upstream pair | 25 | 25 |
| shared upstream trio | 0 | 11 |

So every `criticalTieredSilent` figure for `shared_upstream_trio` in
`result.json` is 0, and that zero means "the whole-group test found nothing", not
"the hidden dependence never mattered". The protocol was frozen before the run
and is not being edited; the endpoint is disclosed as defective and should be
read as unmeasured for the trio family. The pair family's split is unaffected,
because there the two tests agree exactly.

## 3. What did happen

The probe arm's entire effect is converting a silent false settlement into a
flagged one: the counts above appear as `flaggedFalseSettlements` of 80 and 10
where the tiered rule has 0. Nothing is settled differently; a settlement the
record cannot support is stamped "not robust". That is the protection the tiered
rule offers, extended to dependence the record does not carry, and it works —
rarely, and expensively.

| Family, cell | Probes spent | Probes per silent error prevented |
|---|---:|---:|
| pair, m = 0, b = 2 | 850 | 16.3 |
| pair, m = 0, b = 10 | 4,127 | 51.6 |
| trio, m = 0, b = 2 | 954 | 59.6 |
| trio, m = 0, b = 10 | 4,679 | 467.9 |

A larger budget bought a worse rate in every family: the arm spends its extra
probes on pairs that do not pay. The owner's reversible-decision ceiling of 100
extra looks per prevented error would reject the generous budget in the trio
family outright.

## 4. Time, which was reported and not required to pass

The track-record arm is the passive rival: merge a pair once it has been wrong
with you often enough, on decisions whose outcome you learn.

- **In the trio family it did nothing at all**, in any cell: 3,058 silent errors
  against the baseline's 3,058.
- **In the pair family it needed full feedback to do anything**: 2,281 → 2,257
  at r = 1.0, and 2,281 → 2,280 at r = 0.25.
- **It merges independents freely.** At full feedback it made 328 false merges in
  the pair family and 872 in the decoy family, against the probe arm's 17 and 13.

Time is the weaker instrument here, and it is the one that guesses.

## 5. No harm, on a family with little to harm

In `coincident_independents` neither learning arm made more silent false
settlements than the baseline in any cell, so the no-harm checks passed. The
honest reading is weaker than it sounds: with a complete record that family
produced **zero** silent false settlements for every arm, and at m = 0.25 all
three arms produced exactly 251. The decoy did not tempt either method into harm,
and it also never gave them the chance.

## 6. The controls behaved

- **Content fingerprints did nothing**, as designed: the content arm's silent
  counts equal the tiered rule's in every cell. Content is independent per source
  here, so DRI-5's instrument cannot see this dependence. That is the control
  working, not a finding.
- **The lookup stayed blind.** It reports recorded dependence and never the
  hidden component, on every call, which is DRI-6's correlated-error case.

## Run

- **Scope:** 3 families × 500 campaigns × 12 decisions, scored through 8 cells:
  6,000 decisions per family per cell.
- **Reproducibility:** two executions gave identical semantic results, SHA-256
  `aa448b3b5d6682ffceae8849ae98e62e79331aa34124709e68be258121c84685`.
- **Output:** `result.json`, SHA-256
  `3233e673d45cbba4b89365b5a88cb3a471f3fea8cfeba8d369cd3cca8268327e`.
- **When:** 2026-09-16, 17:32:01 to 17:39:21 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, commit `84ad243`, clean
  worktree. Logs are `run-stdout.txt` and `run-stderr.txt`.

| What | Commit |
|---|---|
| Draft | `ef3434c` |
| Protocol | `489db2418613bdf9bd2c5531feb840fa153721bd` |
| Pinned runner | `cb562c2` |
| Candidate record `DRI-8-V1` | `84ad243a3ee36059d2369e08cb0dcf2a2bee7a21` |

## What this establishes

Within this frozen synthetic model:

- **Intervention reaches what reading cannot.** Probing dependence the record does
  not carry does prevent silent false settlements that no record-only rule can
  prevent, which is the practical counterpart of DR3. The mechanism is real.
- **The scale is small and the price is high.** 0.3% to 3.5% of the baseline's
  silent errors, at 16 to 468 probes each.
- **Passive history is weaker still**, needs full feedback to do anything, and
  merges independents an order of magnitude more often.

## What it does not establish

- **That this is worth doing.** The criterion had no effect-size floor, so
  "supported" carries no claim that the protection is worth its cost.
- **Anything about the trio family's margin split**, which section 2 shows is
  mis-specified.
- **Real-world rates.** Detection and coincidence rates for a tracer are stated,
  not measured, and probing assumes an upstream that can be touched at all.
- **Independence of authorship.** Families, probe model and arms are authored in
  the same control domain as the engine.
- **Authority.** It grants no permission for anything to act.
