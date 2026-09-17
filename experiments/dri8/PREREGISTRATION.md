# DRI-8 — preregistration, protocol v1

**Status: FROZEN, protocol v1, 2026-09-16. NOT RUN.** Frozen before any
confirmatory campaign is generated or scored. The runner pins this file, the
configuration, the implementation, the reused DRI-3 files and the engine by
SHA-256, and refuses to run if any of them has changed. When this was frozen, no
comparative outcome had been computed on any DRI-8 campaign. Development runs
checked construction invariants, determinism and runtime only.

Design rationale: `research/decision-relative-independence/DRI-8-DESIGN-DRAFT.md`.
Implementation: `experiments/dri8/`. Related proof:
`formal/lean/MinorityProphetCore/DependenceRobustness.lean`, ledger DR3.

## 1. Identifier

DRI-8, protocol v1.

## 2. Questions

1. **Time.** Does a co-error track record prevent silent false settlements caused
   by dependence the record does not carry?
2. **Intervention.** Does active probing prevent more of them, and at what cost?
3. **Harm.** What does learning cost when it merges sources that are in fact
   independent?
4. **Combined failure.** Does either survive missing lineage and a lookup that is
   wrong the same way on every call?

## 3. Hypotheses

- **Null:** neither learning method changes silent false settlements.
- **Target:** section 10.
- **Stated expectation:** probing prevents more than history does, history is
  weak at the low feedback rate, and the decoy family is where learning can do
  harm. The criterion is not narrowed to where this expectation predicts success.

## 4. Generated worlds

- **Campaigns.** 500 per family, each with 6 persistent sources answering 12
  decisions in order: 6,000 decisions per family per cell. Decisions alternate
  irreversible (threshold 3) and reversible (threshold 2).
- **Sources.** Each has an accuracy drawn from the configuration and may draw on
  an upstream component with a per-decision fault state. When a component is
  faulty, every source drawing on it errs together; otherwise each source errs
  independently at its own rate.
- **Dependence.**
  - **hidden:** shared by sources 0–1 (`shared_upstream_pair`) or 0–2
    (`shared_upstream_trio`), recorded at **no** cut, with content fingerprints
    that differ per source and decision.
  - **recorded:** shared by sources 3 and 4, at the upstream-component cut, and
    truly one unit.
  - `coincident_independents` has no hidden component; its sources 0 and 1 carry
    the lowest accuracy, so they err together by chance. This is the decoy.
- **Missing lineage.** DRI-4's model applied to the recorded link, at
  m ∈ {0, 0.25}.
- **Cells.** m × feedback r ∈ {1.0, 0.25} × probe budget b ∈ {2, 10} per
  campaign: 8 cells, each scoring the same campaigns.
- **Lookup.** Returns the grouping the lineage system knows: recorded dependence
  included, the hidden component never. It is wrong the same way on every call,
  which is the correlated lookup error DRI-6 excluded.
- **Probes.** `probe_result` puts a tracer through one source's upstream and
  reports whether another source's next report carries it: probability
  `probe_detect` when they share a component, `probe_leak` otherwise. Results
  come from a stream seeded by campaign, pair and probe index, so every arm that
  spends its nth probe on a pair sees the same answer.
- **Seeds.** Campaigns: SHA-256 of `salt|family|replicate`. Degradation, probes
  and feedback use separate streams under the same salt. The confirmatory salt is
  `minority-prophet-dri8-v1-confirmatory`; development uses
  `minority-prophet-dri8-development` only.

## 5. Arms

- **tiered rule** — the DRI-3 rule over the five lineage cuts. Baseline.
- **content tiered rule** — the same, plus the content cut. A control: content is
  independent per source here.
- **track record** — the tiered rule plus a co-error history. A pair is merged
  once it has been wrong together on at least
  `track_record_coerror_threshold` of at least
  `track_record_minimum_joint_decisions` decisions whose outcome was revealed,
  which happens at rate r.
- **probe (method under test)** — the tiered rule plus active probing. For each
  candidate pair on the winning side, the arm first asks whether merging that
  pair would change this decision's settlement or its "not robust" stamp. If not,
  it spends nothing. If so, it spends probes on that pair until it has
  `probe_positives_to_merge` positives or exhausts its per-pair attempts or the
  campaign budget. On reaching that many positives the pair is merged from then
  on.
- **oracle reference.**

A learned merge is an identity at a `learned` cut carried by every source: a
merged group shares one label, every other source has its own. It therefore takes
part in both the robustness assessment and the across-cuts agreement check.

## 6. Scoring

Per decision, as in DRI-3: correct settlement; false settlement, **flagged** when
stamped and **silent** otherwise; unneeded abstention; required abstention. A
lookup is always available, so abstaining where the true grouping settles is
unneeded.

**The margin split.** A decision is **margin-critical** when merging the whole
true hidden group would change the settlement or its stamp; otherwise it is
slack, and the hidden dependence cannot move it. Every endpoint is reported for
both.

Results are kept per family and per cell and are never pooled.

## 7. Endpoints

- **Primary:** silent false settlements, probe arm against tiered rule, paired
  per decision.
- **Reported:** the same for the track-record arm; margin-critical against slack;
  probes and looks; learned merges split into true and false; every outcome count
  for every arm.

## 8. Uncertainty and multiple testing

- **Paired test.** Exact McNemar on paired per-decision silent-false-settlement
  indicators, Holm-corrected at a family-wise α of 0.05 across every powered
  comparison.
- **Prevention comparisons.** At most 8: 2 families × 4 cells at the generous
  budget. A comparison runs only when the tiered rule makes at least 12 silent
  false settlements in that family and cell; otherwise it is reported as
  underpowered and is not a check.
- **Harm comparisons.** Every cell of the decoy family, for both learning arms,
  as a one-sided concern: a check fails only if the arm is significantly worse.

## 9. Invalidation

- the runner detects a changed hash;
- the two executions differ;
- a hidden component is found recorded at any cut, or reachable through the
  lookup;
- an arm spends more probes than its budget;
- a contestant arm is shown to have read a hidden field.

## 10. Success criterion

Supported only if all hold:

1. **Prevention.** In `shared_upstream_pair` and `shared_upstream_trio`, at probe
   budget 10, the probe arm makes significantly fewer silent false settlements
   than the tiered rule in every powered comparison.
2. **No harm.** In `coincident_independents`, neither learning arm makes
   significantly more silent false settlements than the tiered rule, in any cell.
3. **Cost ceiling.** In every family and cell, the probe arm keeps at least 90%
   of the tiered rule's correct settlements.
4. **Reproducibility.** Two complete executions give identical semantic results.

The track-record arm is reported against the same endpoints and is not required
to pass. Whether time alone suffices is the finding, not the pass mark.

## 11. Frozen inputs and environment

- **Pinned by SHA-256 in the runner at the freeze commit:** this protocol and
  `EXECUTION-CONFIG.json`; `experiments/dri8/world.py`, `arms.py` and
  `scoring.py`; the reused `experiments/dri3/world.py`; `experiments/dri2/stats.py`;
  `provenance/dependence_robustness.py` and `provenance/decision_relative.py`.
- **Environment:** CPython 3.12, no third-party packages beyond the repository.
- **Candidate record:** committed before the run.

## 12. Boundary and disclosure

- **Where the design came from.** DRI-4 through DRI-7 were all seen before this
  design, and DRI-7's finding that a record-only check never varies is part of
  its motivation. On 2026-09-16 the owner asked for the open questions to be
  attacked and proposed the intervention idea in their own words. The owner did
  not review these rates, arms or criterion before the freeze; Claude chose them
  and states them here.
- **Probing is an assumption about the world.** A tracer through a source's
  upstream is not a property of the record. Where the upstream cannot be touched,
  this method does not exist, whatever the result says.
- **The tracer model is synthetic.** Detection and coincidence rates are stated,
  not measured on anything real.
- **Authorship.** Families, probe model and arms are authored in the same control
  domain as the engine.
- **Scope.** Synthetic campaigns only. No real-world rate, and no authority
  claim.
