# DRI-4 — preregistration draft

**Status: DRAFT. NOT FROZEN. NOT RUN.** It becomes the preregistration when it is
renamed, committed and pinned by hash in the runner, before any confirmatory world
is generated or scored. No comparative outcome has been computed on any DRI-4
world.

Design rationale: `research/decision-relative-independence/DRI-4-DESIGN-DRAFT.md`.
Implementation: `experiments/dri4/`, which reuses the frozen DRI-3 generator, arms
and decision scoring. The proven guarantee it tests the assumption of:
`formal/lean/MinorityProphetCore/DependenceRobustness.lean`, ledger DR1 and DR2.

## 1. Identifier

DRI-4, protocol v1.

## 2. Questions

1. **Incomplete record.** When real shared identities are missing from the record,
   or spurious ones are added, how many silent false settlements does the tiered rule
   make? Is that ever more than the agreement rule makes? Is it significantly fewer
   at moderate missing rates?
2. **Side-asymmetric trap.** Does dependence split across the two sides, recorded at
   different cuts, produce the agreement trap? Under a complete record, does the
   tiered rule avoid silent false settlements there?

## 3. Hypotheses

- **Null:** the tiered rule makes as many silent false settlements as the agreement
  rule, or more, once the record is incomplete.
- **Target:** section 10.

## 4. Generated worlds

- **Families and size.** Five families, 2,000 base worlds each. Each world has 3
  decisions, a lookup in even-numbered worlds, and exactly half of the decisions
  irreversible, as in DRI-3.
  - `joint_domain`, `separate_control_shared_origin`, `three_stacked` and
    `decoy_shared_identity` come from the frozen DRI-3 generator, on this
    protocol's own salt.
  - `side_asymmetric_trap` is new, as described below.
- **The trap family.** Every decision has six roots:
  - **the winning side:** three wrong roots, copied 3, 7 or 15 times. Copies are
    distinct everywhere except the upstream component. Roots 0 and 1 are one source,
    recorded at the machine, controller or evidence-origin cut.
  - **the losing side:** three right roots. Roots 3 and 4 are one source, recorded
    at the upstream component.
  - **the result:** the true units tie 2–2, yet all five cuts settle for the winning
    side. The generator raises an error if any decision lacks that structure.
- **Degradation cells.** Every base world is scored through each of 8 record cells,
  m ∈ {0, 0.1, 0.25, 0.5} × s ∈ {0, 0.1}:
  - **missing (m):** each identity group that encodes a true dependence (two or more
    observations of one true unit sharing an identity at one cut) is split into
    distinct identities with probability m.
  - **spurious (s):** each pair of true units gets one shared identity with
    probability s, at a random cut, covering all observations of both units.
  - **unchanged:** truth, true grouping and lookup.
  - **paired:** cells use the same base worlds.
  - **proof relationship:** at m = 0 the true grouping remains a reading the record
    allows, so DR2 applies. For m > 0 it can fail.
- **Totals.** 10,000 base worlds × 8 cells = 80,000 scored worlds, with 6,000
  decisions per family per cell.
- **Seeds.** Base worlds use SHA-256 of `salt|family|replicate`. Degradation uses a
  separate stream, SHA-256 of `salt|degrade|family|replicate|m|s`. The confirmatory
  salt is `minority-prophet-dri4-v1-confirmatory`. Development uses
  `minority-prophet-dri4-development` only.

## 5. Arms

These are the frozen DRI-3 arms (`experiments/dri3/arms.py`), unchanged:

- agreement rule;
- robustness everywhere;
- tiered rule (the method under test);
- always look;
- oracle reference.

There is no human. Lookups are truthful; imperfect lookups are a separate follow-up
(owner decision).

## 6. Scoring

Scoring follows DRI-3 exactly (`experiments/dri3/scoring.py::score_decision`):

- correct settlement;
- false settlement, which is **flagged** if stamped "not robust" and **silent**
  otherwise;
- unneeded abstention;
- required abstention.

Every decision is scored. Results are kept per family and per cell and are never
pooled. Time is measured, not a criterion.

## 7. Endpoints

- **Primary, per family and cell:**
  - silent false settlements by the tiered rule and by the agreement rule;
  - the paired comparison between them.
- **Reported, per family and cell:**
  - false settlements on irreversible decisions, for the tiered rule, with counts;
  - every outcome count for every arm;
  - looks and stamped settlements;
  - the reversible scorecard.

## 8. Uncertainty and multiple testing

- **Zero-event bound.** With zero events in 6,000 decisions, the exact one-sided 95%
  upper bound is 0.000499.
- **Paired test.** Exact McNemar on paired per-decision silent-false-settlement
  indicators, with Holm correction at a family-wise α of 0.05 across every powered
  comparison.
- **When a comparison is run.** At most 20 comparisons are possible: 5 families × 4
  cells with m ∈ {0.1, 0.25}. A comparison runs only when the agreement rule makes
  at least 12 silent false settlements in that family and cell. Twelve lets an exact
  test with no discordance on the other side reach significance even at the
  strictest Holm step (2 × 0.5¹² < 0.05 / 20). Otherwise the comparison is reported
  as underpowered and is not a check.

## 9. Invalidation

- the runner detects a changed hash;
- the two executions differ;
- a trap decision lacks its structure;
- a contestant arm is shown to have read a hidden field.

## 10. Success criterion

Supported only if all of the following hold:

1. **Complete record (m = 0, both s):** in every family, the tiered rule makes zero
   silent false settlements, with the 95% upper bound below 0.001. This checks the
   implementation of a proven guarantee; it is not a discovery.
2. **Incomplete record (m > 0):** in every family and cell, the tiered rule makes no
   more silent false settlements than the agreement rule.
3. **Moderate incompleteness (m ∈ {0.1, 0.25}):** in every powered comparison
   (section 8), the tiered rule makes significantly fewer silent false settlements
   than the agreement rule.
4. **Reproducibility:** two complete executions give identical semantic results.

False settlements on irreversible decisions are reported for every cell, with no
pass mark, because they are expected to rise with m.

## 11. Frozen inputs and environment

- **Pinned by SHA-256 in the runner at the freeze commit:**
  - this protocol and `EXECUTION-CONFIG.json`;
  - `experiments/dri4/world.py` and `experiments/dri4/scoring.py`;
  - the DRI-3 files it reuses (`world.py`, `arms.py`, `scoring.py`);
  - `experiments/dri2/stats.py`;
  - `provenance/dependence_robustness.py` and `provenance/decision_relative.py`.
- **Environment:** CPython 3.12, with no third-party packages beyond the repository.
- **Candidate record:** committed before the run.

## 12. Boundary and disclosure

- **Where the engine came from.** The engine and its proof came from DRI-2's
  failures, and DRI-3 was already run and seen. The owner approved this design's
  proposals on 2026-09-15.
- **Trap family.** The side-asymmetric trap family is built to contain the trap, so
  the agreement rule is expected to fall in it at m = 0. It tests the tiered rule's
  behaviour there, not how common the trap is.
- **Degradation model.** The rates are a stated model of incompleteness, not
  estimates of real-world rates.
- **Authorship.** Everything is authored in the same control domain as the engine.
- **Scope.** Synthetic worlds only. No real-world lineage, lookup-error or
  authority claim.
