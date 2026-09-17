# DRI-10 — preregistration, protocol v1

**Status: FROZEN, protocol v1, 2026-09-16. NOT RUN.** Frozen before any
confirmatory campaign is generated or scored. The runner pins this file, the
configuration, the implementation, reused DRI-9/DRI-8/DRI-3/DRI-2 files and the
engine by SHA-256, and refuses to run if any of them changed. No confirmatory
outcome had been computed when this was frozen.

Design rationale: `research/decision-relative-independence/DRI-10-DESIGN-DRAFT.md`.
Implementation: `experiments/dri10/`. Predecessor: DRI-9-V1, rejected.
Related proof: ledger DR3.

This protocol was written after DRI-9's confirmatory was public. The named
method and the world are a response to that record, not a clean hold-out.
The confirmatory salt below was not used in development. Same control domain
as DRI-9. Not independent validation of DRI-9, and not a resticker of it.

## 1. Identifier

DRI-10, protocol v1.

## 2. Why this exists

DRI-9 named a ladder, watched bait win as a reported arm, and proposed to name
bait and rerun the same generator. Relabeling that `semanticResult` with
`method_under_test=bait` is already supported, 65/65. That is not a new
experiment.

DRI-9's world was the bait story. Hidden families shared one unmarked component;
that component was the marked channel; the decoy planted zero markers, so
`marker_leak` never fired and bait's "no harm" pass was free.

DRI-10 names bait, because that is the confirmatory DRI-9 deferred, and changes
the world so the name can lose.

## 3. Questions

1. When the mark *is* the hidden component, does bait still prevent a quarter of
   the margin-critical silent errors? (Positive control. If this fails, the
   instrument was broken, not tested.)
2. When the hidden pair is unmarked, does bait still look like a detector?
   If prevention there is within 15 points of the marked family at the same
   pickup and the low leak, the mark is not what did the work.
3. When independent sources share a marked library, or only a leaky
   environmental token, does bait keep the baseline's correct settlements and
   refrain from collapsing the library?

## 4. Scope: reversible decisions

Same owner decision as DRI-9 §4. Irreversible decisions use `lookup_grouping`,
which ignores belief. They are tallied without a pass mark. That immunity is a
code path (`experiments/dri9/rule.py::settle`), not a property of the world.

## 5. Generated worlds

- **Campaigns.** 500 per family, 6–8 sources answering 12 decisions, alternating
  irreversible (threshold 3) and reversible (threshold 2).
- **Knobs.** Each source has an optional hidden error component and an optional
  marker carrier. The marked channel is chosen per family. A source whose
  carrier equals the marked channel picks up at `pickup`; everyone else at
  `leak`. Leak fires in every family.
- **Families.**
  - `marked_hidden_pair` — hidden pair, carrier = hidden component = marked
    channel. DRI-9's bait story. Floor family.
  - `unmarked_hidden_pair` — hidden pair, empty carrier, marked channel
    `env:public`. They share errors and carry the token only by leak.
    Mechanism contrast.
  - `common_carrier` — no shared error. Three sources share carrier
    `lib:shared`, which is marked. They err independently. Merging them is
    wrong.
  - `leaky_independents` — no shared error, no shared carrier, marked channel
    `env:public`. Markers exist. This is the harm test DRI-9's decoy could
    not run.
- **Cells.** Pickup ∈ {0.5, 0.9} × leak ∈ {0.02, 0.20}. Timing jitter is fixed
  at 0.1; this experiment is not about the clock.
- **Nothing is placed** on an enumerated pivotal table. Critical share is
  measured by `rule.is_pivotal` against the family's focus group.

## 6. Arms

Same instruments as DRI-9. **bait is the method under test**, named here, before
the confirmatory salt is touched. ladder, reflection, ablation, fragile
refusal and the oracle are reported.

Timing stays out of the ladder (`ladder_signals = ["bait", "coerror"]`), as in
DRI-9, so the reported ladder is the same AND-gate, not a new favourite.

## 7. Scoring

DRI-3 outcomes. Margin-critical when `is_pivotal` says believing any subset of
the focus group changes the settlement or its stamp.

A comparison is powered when the baseline makes at least
`minimum_critical_silent_for_test` silent false settlements on margin-critical
reversible decisions in that family and cell.

## 8. Endpoints

- **Primary:** silent false settlements on reversible decisions, bait against
  baseline, on `marked_hidden_pair`; the share of margin-critical baseline
  errors prevented; the marked-minus-unmarked prevention gap at leak 0.02.
- **Harm:** correct settlements and silent false settlements on
  `common_carrier` and `leaky_independents`; false merges on `common_carrier`.
- **Reported:** every other arm; irreversible tallies; unmarked-family
  prevention at leak 0.20 (contamination regime, no pass mark).

## 9. Uncertainty

Exact McNemar, Holm-corrected at family-wise α 0.05 across powered floor
comparisons.

## 10. Success criterion

Supported only if **all** hold. If the floor family has **no** powered cell,
the result is **not** supported. Quiet is not a pass.

On reversible decisions:

1. **Effect floor.** On `marked_hidden_pair`, bait prevents at least 25% of the
   baseline's margin-critical silent false settlements in every powered cell,
   and does so significantly.
2. **The mark did the work.** At leak 0.02, for each pickup, bait's prevented
   share on `marked_hidden_pair` exceeds its share on `unmarked_hidden_pair` by
   at least 15 points. Both cells must be powered or this check fails.
3. **No harm.** On `common_carrier` and `leaky_independents`, bait does not
   make significantly more silent false settlements than the baseline, and
   keeps at least 95% of the baseline's correct settlements.
4. **Library.** On `common_carrier`, bait's false merges are at most 0.1 per
   campaign. Collapsing a shared library is a fail, even if settlements move
   little.
5. **Cost.** On `marked_hidden_pair`, bait keeps at least 95% of the baseline's
   correct settlements and spends at most 100 interventions per prevented
   error (bait spends 0; this is so a later instrument cannot hide here).
6. **Reproducibility.** Two executions give identical semantic results.

## 11. Frozen inputs and environment

Pinned by SHA-256 in the runner: this protocol and `EXECUTION-CONFIG.json`;
`experiments/dri10/world.py`, `arms.py`, `scoring.py`;
`experiments/dri9/rule.py`; `experiments/dri8/world.py`;
`experiments/dri3/world.py`; `experiments/dri2/stats.py`;
`provenance/dependence_robustness.py` and `provenance/decision_relative.py`.
CPython 3.12, no third-party packages beyond the repository. The candidate
record is committed before the run.

## 12. Boundary and disclosure

- DRI-9's confirmatory was public before this protocol was written. The world
  and the named method are a response to that record. Development salt
  `minority-prophet-dri10-development` may be used for construction tests only.
  No confirmatory salt is to be evaluated before this file is frozen.
- Rates are stated, not measured on anything real.
- Families, instruments and arms are authored in the same control domain as
  the engine. This is not A2-independent validation.
- Bait still assumes something to plant. This world can make that something
  the wrong object. It cannot show that a real upstream can be marked.
- No authority claim.
- DRI-9-V1 stays rejected. A supported DRI-10 would not rewrite it.
