# DRI-9 v1 confirmatory result

**Outcome:** the preregistered criterion was **not supported**. 58 of 65 checks
passed. All seven failures are the same check, in seven of the eight powered
cells: the method under test did not prevent a quarter of the baseline's
margin-critical silent false settlements.

**The named method lost to the simplest instrument, and that is the result.**

| Arm | Cells clearing the 25% effect floor | Share prevented | Harm flags |
|---|---:|---|---:|
| **ladder** (method under test) | **1 of 8** | 0.15–0.28 | 0 |
| bait | 8 of 8 | 0.34–0.77 | 0 |
| reflection | 8 of 8 | 0.61–0.66 | 4 |
| ablation | 4 of 8 | 0.19–0.57 | 4 |
| fragile refusal | 4 of 8 | 0.00–0.54 | 0 |

The ladder was named as the method under test **before the run**, in
`PREREGISTRATION.md` §6, precisely so that the winner could not be chosen after
the outcomes were visible. It lost. The criterion is reported as it was written.

## 1. Why the combination lost

The ladder required two independent signals to agree before believing two sources
were one. That made it the most precise arm in the experiment — 217 to 942 true
merges against **0 to 6** false ones, and it never cost a single correct
settlement, keeping 2,035 of 2,035 and 1,416 of the baseline's 1,282 — and the
least useful. Waiting for a second witness meant it acted late or not at all:
it left 668–972 silent errors standing where bait left 278–643.

**A combination of weak signals was more cautious and less useful than its best
ingredient.** That is the finding, and it is the opposite of the intuition that
motivated building it.

## 2. What bait did

Planting a marker upstream and watching who carries it cleared the floor in every
powered cell, and its performance tracked the cell's pickup rate exactly as the
mechanism predicts:

| Family | Pickup 0.5 | Pickup 0.9 |
|---|---|---|
| shared upstream pair | 0.34–0.36 prevented | 0.70 prevented |
| shared upstream trio | 0.45–0.46 prevented | 0.76–0.77 prevented |

It did this while keeping correct settlements at or above the baseline — 2,056 of
2,077 in the pair family, and **1,622 against the baseline's 1,273** in the trio,
where believing true merges recovers decisions the record alone gets wrong. Its
false merges stayed low (40–138 against 374–1,500 true ones), and in the decoy
family it made **zero** merges, zero silent errors and lost **zero** correct
settlements.

## 3. Reflection cleared the floor and should still be rejected

Arrival-order timing prevented 61–66% of margin-critical errors — and made
**6,497 to 8,782 false merges per cell**, collapsing correct settlements from
3,000 to about 1,300 in the decoy family and from ~2,050 to ~970 in the pair
family. It carries 4 harm flags.

This is why the criterion has a no-harm clause and why timing was excluded from
the ladder before the run, on development evidence (`PREREGISTRATION.md` §6).
An arm can score well on prevention by believing almost everything is an echo.
Prevention alone is not a measure of a detector.

## 4. Fragile refusal: free, and blind to groups of three

Refusing to answer when any two winning-side sources might be one prevented
50–54% in the pair family at no cost in instruments — but **0.00 in every trio
cell**. It tests pairs; where three sources share an origin, no pair test changes
the answer, so it never fires. It also costs correct settlements heavily
(2,035 → 1,540), since refusing is its only move.

## 5. Ablation: real but rationed

Cutting an upstream and watching who changes prevented 0.19–0.57, spending
496–739 interventions per cell against a budget of 2 per campaign. It carries 4
harm flags in the decoy family, where it made 29–34 false merges — the price of
acting on a noisy cut response.

## 6. The decoy family behaved

With no shared component, the baseline made **zero** silent false settlements in
every cell, and bait and the ladder kept it there with zero false merges and zero
lost correct settlements. Reflection and ablation did not.

## Run

- **Scope:** criterion on reversible decisions, by owner decision
  (`PREREGISTRATION.md` §4). 3 families × 500 campaigns × 12 decisions × 4 cells;
  3,000 reversible decisions per family per cell. Irreversible decisions are
  tallied and reported without a pass mark, because belief cannot move that path
  in this world.
- **Reproducibility:** two executions gave identical semantic results, SHA-256
  `8a6c42246c164d5ee5239ccfca46210b2c124fc53a27fcf24ad37293094e16e1`.
- **Output:** `result.json`, SHA-256
  `8718cce94dd35782ce3758b66ba8592d6a8c9db2c817a569679b855ed9233db5`.
- **When:** 2026-09-16, 19:25:19 to 19:39:07 UTC.
- **Environment:** CPython 3.12 on macOS arm64, commit `4b0b787`, clean worktree.
  Logs are `run-stdout.txt` and `run-stderr.txt`.

| What | Commit |
|---|---|
| Draft | `5baf996` |
| Protocol | `cd4a3630a8a1863e1c854ee74ba4663f974c2736` |
| Pinned runner | `1c552de` |
| Candidate record `DRI-9-V1` | `4b0b78713` |

## What this establishes

Within this frozen synthetic model, on reversible decisions:

- **Intervention works, and the mechanism is legible.** Bait prevented 34–77% of
  the errors that mattered, scaling with how often a shared source carries the
  marker, at no cost to correct settlements and with no harm in the decoy family.
- **Belief has to override the record to do anything.** This experiment exists
  because DRI-8's arms could not act on what they found; see
  `results/dri8-v1/POST-RESULT-NOTE.md`. With belief overriding recorded
  identities, the same class of instrument moves hundreds of decisions per cell.
- **Combining weak signals can cost more than it buys.** The ladder's precision
  was near-perfect and its coverage was the worst of the instruments.
- **Prevention without a harm test is meaningless.** Reflection would have looked
  like the best arm on prevention alone.

## What it does not establish

- **That bait is the answer.** It was a reported arm, not the method under test.
  Declaring it the winner now would be choosing after seeing the outcome. A
  successor must name it in advance and test it on fresh worlds.
- **Anything about irreversible decisions**, which are out of scope here.
- **Real-world rates.** Pickup, leak, cut-response and jitter are stated, not
  measured, and probing assumes an upstream that can be touched at all.
- **Independence of authorship.** Families, instruments and arms are authored in
  the same control domain as the engine.
- **Authority.** It grants no permission for anything to act.
