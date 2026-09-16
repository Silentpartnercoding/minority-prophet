# DRI-10 v1 confirmatory result

**Outcome: not supported.** 28 of 40 checks. Bait was named as the method under
test in the frozen protocol, and bait failed.

This world was written by an adversarial review of DRI-9 (`#204`, `#205`), not by
the author of the instrument. It separates the shared error from the mark, and it
contains two families DRI-9 could not contain: a shared library that carries no
shared error, and independents that can carry the mark. Bait failed in both.

## 1. What failed

| Check | Cells failed | What it means |
|---|---|---|
| `bait:didNotCollapseTheLibrary` | 4 of 4 in `common_carrier` | Bait believed a shared library was a shared source |
| `bait:correctSettlementFloor` | 8 | It destroyed correct settlements doing so |

**The library trap.** In `common_carrier` many sources touch one library that never
makes them wrong. The baseline makes **zero** silent false settlements there, so
there is nothing to prevent and everything to lose. Bait believed the carriers
were one source and correct settlements fell from the baseline's 2,830–2,866 to
**1,389–2,194**, with 1,431–9,118 false merges per cell and **zero** true ones.

**Leaked marks.** At the higher leak rate the same failure appears wherever marks
drift: 5,539 false merges in `marked_hidden_pair` at pickup 0.9, correct
settlements 2,046 → 1,297; and in `leaky_independents`, 867–940 false merges
where the baseline had nothing to fix.

**The mark has to be on the thing.** In `unmarked_hidden_pair` the dependence is
real and the mark is elsewhere. At leak 0.02 bait prevented **0 of 1,005 and 0 of
988** — it did not move a single decision. It sees marks, not dependence.

## 2. Scoreboard, every arm judged by the same criterion

Applying bait's own criterion to each arm, which is a diagnostic and **not** a
verdict on any of them:

| Arm | Checks | Failing |
|---|---:|---|
| ladder | 37 / 40 | prevents too little (2), mark does not do the work (1) |
| fragile refusal | 30 / 40 | cost of refusing (8), mark does not do the work (2) |
| ablation | 30 / 40 | cost (8), mark does not do the work (2) |
| **bait (named method)** | **28 / 40** | cost (8), collapsed the library (4) |
| reflection | 22 / 40 | cost (12), collapsed the library (4), mark (2) |

**No arm was supported.** These numbers are counterfactual relabelling of the
frozen `semanticResult`; DRI-9's own record shows why that is not an experiment
(`results/dri9-v1/POST-RESULT-NOTE.md` §3). They are reported here so the failure
is legible, not to promote a runner-up.

## 3. What the arms actually did

- **Refusing is the broadest instrument.** Declining to answer when two
  winning-side sources might be one prevented 473–521 of the critical errors in
  **every** hidden family, including `unmarked_hidden_pair`, where bait prevented
  none. It needs no marks, no probes and no budget. It pays in refusals:
  correct settlements 2,034 → 1,551.
- **The ladder was cautious in a world that rewards caution.** Requiring two
  signals to agree kept its false merges to 0–55 and cost almost no correct
  settlements (2,034 → 2,034 in one cell), while preventing only 0–258 — nothing
  at all in two cells. In
  DRI-9's world that caution looked like uselessness; here it is the only arm that
  never collapsed the library.
- **Ablation is steady and expensive**: 492–559 prevented, 728–753 interventions
  per cell, 24–30 false merges.
- **Reflection remains the worst instrument tested**: 6,431–10,854 false merges
  per cell, correct settlements roughly halved everywhere.

## 4. What this overturns

DRI-9's write-up said bait "cleared the floor in 8 of 8" and caused no harm. That
was measured on a world where the marked component *was* the hidden component and
the decoy emitted no markers at all. On a world built to test the instrument
rather than display it, **bait is the arm that does the most damage** in three of
four families. The DRI-9 verdict (rejected) stands; its interpretation does not,
and the post-result note already records why.

## Run

- **Scope:** criterion on reversible decisions. 4 families × 4 cells
  (pickup × leak); 3,000 reversible decisions per family per cell.
- **Reproducibility:** two executions gave identical semantic results, SHA-256
  `4848b9c24dd1654ee4ae052f0053eaf580a3790493b8e349e025400e25e65464`.
- **Output:** `result.json`, SHA-256
  `094c0f14a6723d1d4c1151d63bbd0363dba69218c30444f1f78ccbde46f924ea`.
- **When:** 2026-09-16, 21:11:53 to 21:30:28 UTC.
- **Environment:** CPython 3.12 on macOS arm64, commit `cb2a290`, clean worktree.
- **Powered comparisons:** 4, all in `marked_hidden_pair`. None underpowered.

## What this establishes

- **A mark is not dependence.** Bait detects whatever carries the mark: a shared
  origin, a shared library, or a stray leak. Where dependence is unmarked it is
  blind, and where innocents are marked it is harmful.
- **The harm test earns its place.** Every claim that bait was safe came from a
  family that could not express harm.
- **A criterion written by the instrument's author flatters the instrument.** The
  same arm passes 8 of 8 on DRI-9's world and fails on this one.

## What it does not establish

- **That any other arm works.** Section 2 is relabelling, not a verdict. A
  successor must name its method in advance, as this one did.
- **Real-world rates** for pickup, leak, library sharing or cut response.
- **Anything about irreversible decisions**, which remain out of scope.
- **Independent validation.** The adversarial world was written in the same
  control domain, after seeing DRI-9's result.
