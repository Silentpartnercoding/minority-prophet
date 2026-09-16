# DRI-9 — preregistration, protocol v1

**Status: FROZEN, protocol v1, 2026-09-16. NOT RUN.** Frozen before any
confirmatory campaign is generated or scored. The runner pins this file, the
configuration, the implementation, the reused DRI-3 and DRI-8 files and the
engine by SHA-256, and refuses to run if any of them changed. No confirmatory
outcome had been computed when this was frozen. Development runs are disclosed in
section 12: they were extensive, and they shaped the design.

Design rationale: `research/decision-relative-independence/DRI-9-DESIGN-DRAFT.md`.
Implementation: `experiments/dri9/`. Related proof: ledger DR3.

## 1. Identifier

DRI-9, protocol v1.

## 2. Why this exists

DR3 proves no rule reading only the record can separate independent sources from
two sharing an unrecorded origin. DRI-8 probed for that dependence and reported a
small effect. A measurement taken afterwards, recorded in
`results/dri8-v1/POST-RESULT-NOTE.md`, showed why: its arms wrote a learned merge
as one extra cut and left the record's own identities in place, so the five cuts
describing the disguise outvoted it. Merging the true hidden group changed **0
settlements in 720 decisions** there.

DRI-9 fixes that first. `experiments/dri9/rule.py::believe` makes a believed
merge rewrite every cut for those sources, because believing two sources are one
means their separate recorded identities stop being evidence of independence.
Both the generator and the arms import that module, so the rule being tested and
the situations being counted are the same function — the other failure in DRI-8,
where the world was built against plain root counting while the rule settled over
six cuts.

## 3. Questions

1. Does an instrument that reaches outside the record prevent silent false
   settlements caused by dependence the record does not carry?
2. What does believing wrongly cost, where the sources are in fact independent?
3. Is a combination of weak signals better than its best single signal?

## 4. Scope: reversible decisions

**Owner decision, 2026-09-16.** The criterion is scored on reversible decisions
only. In this world the irreversible path settles when the record is robust and
otherwise looks, and the lookup is blind to what an arm believes, so belief
cannot move it: on the development world, believing the focus group changed **0
of 360** irreversible decisions per family against **233 and 279** reversible
ones. Irreversible decisions are tallied and reported without a pass mark. What
belief must clear before acting on an irreversible decision is deliberately left
open for a successor.

## 5. Generated worlds

- **Campaigns.** 500 per family, 6 sources answering 12 decisions in order,
  alternating irreversible (threshold 3) and reversible (threshold 2): 3,000
  reversible decisions per family per cell.
- **Families.** `shared_upstream_pair` and `shared_upstream_trio`, where the
  focus group shares an upstream component recorded at **no** cut, with
  independent content; `coincident_independents`, the decoy, whose equally sized
  group shares only low accuracy. Believing the decoy's group is wrong, and costs
  a root on its own side.
- **Nothing is placed.** An earlier draft positioned decisions on an enumerated
  table of pivotal vote shapes; that table modelled a single-cut root count and
  disagreed with the rule everywhere. Decisions are sampled, and the share where
  belief could change the answer is measured by `rule.is_pivotal`, not
  engineered.
- **Cells.** Bait pickup ∈ {0.5, 0.9} × timing jitter ∈ {0.1, 0.5}.
- **Observables outside the record.** Bait markers carried by a marked
  component's members at the cell's pickup rate and by anyone else at
  `marker_leak`; arrival order, consistent within a component group and shuffled
  between groups; cut response, `cut_together` for members of one component and
  `cut_alone` otherwise. Every stream is keyed by campaign, so arms asking the
  same question get the same answer.

## 6. Arms

- **tiered rule** — baseline: the record, believed as written.
- **fragile refusal** — free; abstains when believing any two winning-side
  sources were one would change the answer.
- **bait** — believes a pair seen carrying the same marker
  `marker_cooccurrences_to_merge` times.
- **reflection** — believes a pair whose arrival order is consistent enough.
- **ablation** — spends a cut from a small budget, believes a pair that changes
  together, and abstains on the decision it spent.
- **ladder — the method under test.** Believes a pair when
  `ladder_score_to_merge` of its declared signals agree.
- **oracle reference.**

**Timing is excluded from the ladder, decided before the run.** On the
development world the reflection arm made 476 and 586 false merges and cut
correct settlements from 155 to 77 and 240 to 100. `ladder_signals` is therefore
`["bait", "coerror"]`, and with the threshold at 2 the ladder requires both.
Reflection still runs as its own arm so the failure is recorded rather than
deleted.

## 7. Scoring

DRI-3 outcomes: correct settlement; false settlement, flagged when stamped and
silent otherwise; unneeded abstention; required abstention.

A decision is **margin-critical** when `rule.is_pivotal` says believing any
subset of the focus group changes the settlement or its stamp. The effect floor
is measured there, because preventing errors that could not have happened is not
prevention.

## 8. Endpoints

- **Primary:** silent false settlements on reversible decisions, ladder against
  baseline, paired per decision, and the share of margin-critical baseline errors
  prevented.
- **Reported:** the same for every other arm; true and false merges; interventions
  spent; correct settlements and abstentions, including how many abstentions fall
  on decisions the baseline got silently wrong; all irreversible tallies.

## 9. Uncertainty and multiple testing

Exact McNemar on paired per-decision indicators, Holm-corrected at a family-wise
α of 0.05 across powered comparisons. A comparison is powered when the baseline
makes at least `minimum_critical_silent_for_test` silent false settlements on
margin-critical decisions in that family and cell; otherwise it is reported as
underpowered and is not a check.

## 10. Success criterion

Supported only if all hold, on reversible decisions:

1. **Effect floor.** In both hidden families, the ladder prevents at least 25% of
   the baseline's margin-critical silent false settlements, in every powered cell.
2. **Significance.** In every powered cell, significantly fewer silent false
   settlements than the baseline.
3. **No harm.** In the decoy family, no arm makes significantly more silent false
   settlements than the baseline, and the ladder's false merges do not exceed its
   true merges.
4. **Cost ceiling.** The ladder keeps at least 95% of the **baseline's** correct
   settlements — the incumbent rule is the thing it must not make worse — and
   spends at most 100 interventions per prevented error.
5. **Reproducibility.** Two executions give identical semantic results.

## 11. Frozen inputs and environment

Pinned by SHA-256 in the runner: this protocol and `EXECUTION-CONFIG.json`;
`experiments/dri9/rule.py`, `world.py`, `arms.py`, `scoring.py`; the reused
`experiments/dri8/world.py` and `experiments/dri3/world.py`;
`experiments/dri2/stats.py`; `provenance/dependence_robustness.py` and
`provenance/decision_relative.py`. CPython 3.12, no third-party packages beyond
the repository. The candidate record is committed before the run.

## 12. Boundary and disclosure

- **Development evidence shaped this design, extensively.** Four things were
  decided on development runs and are stated rather than hidden: the belief
  semantics (after measuring that the DRI-8 form changed nothing); dropping the
  shape-table placement (after measuring that it disagreed with the rule);
  scoping to reversible decisions (after measuring 0 of 360 on the irreversible
  path); and excluding timing from the ladder (after measuring its false merges).
  No confirmatory salt was touched.
- **The method under test may well lose.** On the development world, bait alone
  prevented more silent false settlements than the ladder (27 and 18 remaining
  against 65 and 68, from a baseline of 85 and 87). The ladder was named first and
  is kept named, because a preregistration rewritten whenever the favourite
  underperforms is not one. If bait wins again on the confirmatory salt, that is
  the finding: a combination can be more cautious and less useful than its best
  ingredient.
- **Probing is an assumption about the world.** Bait assumes something to plant,
  ablation assumes something you may break, reflection assumes a trustworthy
  clock. Where those do not hold, the arm does not exist.
- **Rates are stated, not measured** on anything real, and the families,
  instruments and arms are authored in the same control domain as the engine.
- **No authority claim.**
