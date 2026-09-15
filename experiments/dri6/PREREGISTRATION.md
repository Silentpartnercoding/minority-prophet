# DRI-6 — preregistration, protocol v1

**Status: FROZEN, protocol v1, 2026-09-15. NOT RUN.** Frozen before any
confirmatory world is generated or scored. The runner pins this file, the
configuration, the implementation, the reused DRI-5, DRI-4 and DRI-3 files and the
engine by SHA-256, and refuses to run if any of them has changed. When this was
frozen, no comparative outcome had been computed on any DRI-6 world. Development
runs checked construction invariants and runtime only.

Design rationale: `research/decision-relative-independence/DRI-6-DESIGN-DRAFT.md`.
Implementation: `experiments/dri6/`. It reuses:
- the frozen DRI-4 generator;
- DRI-5's record-admissibility function;
- the DRI-3 arms and decision scoring.

## 1. Identifier

DRI-6, protocol v1.

## 2. Questions

1. **Harm.** How many silent false settlements do lookup errors cause under the
   tiered rule?
2. **Record check.** Does checking a reported grouping against the record reduce
   them?
3. **Confirmation.** Does a second, independent look reduce them, and at what cost?

## 3. Hypotheses

- **Null:** looking twice makes no difference to silent false settlements.
- **Target:** section 10.
- **Stated expectation:** the record check mainly catches invented dependence
  (merges), and catches few missed dependences (splits).

## 4. Generated worlds

- **Families and size.** DRI-4's five families, 2,000 base worlds each, from the
  frozen DRI-4 generator on this protocol's own salt:
  - `joint_domain`;
  - `separate_control_shared_origin`;
  - `three_stacked`;
  - `decoy_shared_identity`;
  - `side_asymmetric_trap`.

  Each world has 3 decisions, a lookup in even-numbered worlds, and exactly half of
  the decisions irreversible. The lineage record is complete: nothing is missing and
  nothing is spurious.
- **Lookup errors.** Each call independently reports a grouping.
  - **Split rate e_s:** each true unit with more than one observation is reported as
    one unit per observation.
  - **Merge rate e_m:** each pair of true units is reported as one unit. A unit
    merged with another is reported merged, not split.
  - **Unchanged:** the record, truth and true grouping.
- **Cells.** (e_s, e_m) ∈ {(0, 0), (0.05, 0), (0.2, 0), (0, 0.2), (0.2, 0.2)}. Every
  cell uses the same base worlds.
- **Common random numbers.** Call k on a decision uses a stream seeded by SHA-256 of
  `salt|lookup|decision|k`. The stream draws one number per unit and one per pair of
  units, whatever the rates. The same call on the same decision therefore reports the
  same grouping to every arm.
- **Totals.** 10,000 base worlds, each scored under 5 cells, with 6,000 decisions per
  family per cell.
- **Seeds.** The confirmatory salt is `minority-prophet-dri6-v1-confirmatory`.
  Development uses `minority-prophet-dri6-development` only.

## 5. Arms

- **Frozen DRI-3 arms, unchanged.** Each settles on whatever a lookup reports:
  - agreement rule;
  - tiered rule;
  - always look.
- **Checked tiered rule.** The tiered rule, except after a look: it accepts the
  reported grouping only if every reported unit is joined by recorded shared
  identities inside it, and otherwise abstains.
- **Confirmed tiered rule (method under test).** The tiered rule, except after a
  look: it looks a second time, and settles only when both reports pass the check
  and give the same settlement. Otherwise it abstains.
- **Oracle reference.**

There is no human.

## 6. Scoring

Scoring follows DRI-3 (`experiments/dri3/scoring.py::score_decision`):
- correct settlement;
- false settlement, **flagged** if stamped "not robust" and **silent** otherwise;
- unneeded abstention;
- required abstention.

A decision with a lookup counts as decidable even when the lookup errs, so
abstaining there is an unneeded abstention. Results are kept per family and per
cell and are never pooled. Time is measured, not a criterion.

## 7. Endpoints

- **Primary, per family and cell:**
  - silent false settlements by the confirmed tiered rule and the tiered rule;
  - the paired comparison between them.
- **Reported, per family and cell:**
  - the checked tiered rule's paired comparison with the tiered rule;
  - false settlements made after a look, per arm;
  - extra looks, prevented false settlements and extra unneeded abstentions for each
    new arm against the tiered rule;
  - every outcome count for every arm.

## 8. Uncertainty and multiple testing

- **Zero-event bound.** With zero events in 6,000 decisions, the exact one-sided 95%
  upper bound is 0.000499.
- **Paired test.** Exact McNemar on paired per-decision silent-false-settlement
  indicators, with Holm correction at a family-wise α of 0.05 across every powered
  comparison.
- **Number of comparisons.** At most 20: 5 families × 4 erring cells.
- **Power rule.** A comparison runs only when the tiered rule makes at least 12
  silent false settlements in that family and cell. Otherwise it is reported as
  underpowered and is not a check.

## 9. Invalidation

- the runner detects a changed hash;
- the two executions differ;
- a contestant arm is shown to have read a hidden field;
- a lookup reports different groupings to different arms for the same call.

## 10. Success criterion

Supported only if all of the following hold:

1. **Truthful lookups (0, 0).** In every family, the confirmed tiered rule makes zero
   silent false settlements, with the 95% upper bound below 0.001.
2. **Implementation of the guarantee.** In every family and cell, neither the checked
   nor the confirmed tiered rule makes a silent false settlement on a decision where
   the tiered rule does not.
3. **Erring lookups.** In every powered comparison, the confirmed tiered rule makes
   significantly fewer silent false settlements than the tiered rule.
4. **Reproducibility.** Two complete executions give identical semantic results.

Items 1 and 2 check the implementation of consequences of DR2 and of the arms'
construction. They are not discoveries. Item 3 is the finding.

## 11. Frozen inputs and environment

- **Pinned by SHA-256 in the runner at the freeze commit:**
  - this protocol and `EXECUTION-CONFIG.json`;
  - `experiments/dri6/world.py`, `arms.py` and `scoring.py`;
  - the reused `experiments/dri5/world.py` and `experiments/dri4/world.py`;
  - the reused DRI-3 `world.py`, `arms.py` and `scoring.py`;
  - `experiments/dri2/stats.py`;
  - `provenance/dependence_robustness.py` and `provenance/decision_relative.py`.
- **Environment:** CPython 3.12, with no third-party packages beyond the repository.
- **Candidate record:** committed before the run.

## 12. Boundary and disclosure

- **Where the design came from.** DRI-4's result was seen before this design. DRI-5
  was frozen but its result had not been read. On 2026-09-15 the owner asked for the
  imperfect-lookup follow-up. The owner did not review the specific rates, arms or
  criterion before the freeze; Claude chose them and states them here.
- **Error model.** Errors are independent across calls. Correlated lookup errors
  would defeat confirmation and are not modelled. The rates are a stated model, not
  estimates.
- **Authorship.** Everything is authored in the same control domain as the engine.
- **Scope.** Synthetic worlds only. No real-world lookup-error, lineage or authority
  claim.
