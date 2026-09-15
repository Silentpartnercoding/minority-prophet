# Decision-relative independence

Status: **proposed research primitive with constructed falsification fixtures
and one adverse preregistered test.** DRI-1A (run 2026-08-25, not canonical) did
not support its joint policy-value criterion; see
[Result so far](#result-so-far-dri-1a). The executable adapter and fixtures do
not establish that a model can discover the correct causal cut in real systems.
No existing Minority Prophet theorem is extended by this document.

## Claim

Evidence independence is not a context-free Boolean attached to an agent. It is
the absence of a *material* shared failure cause under a stated decision model.
The same observations may therefore be sufficiently independent for one
question and insufficiently independent for another without changing their
underlying lineage.

Examples:

- three machines may be adequate replication for machine-specific tool
  compatibility while remaining one controller for operator consensus;
- three sensors may be separate devices while sharing one upstream component;
- ten agents may be separate processes while repeating one information source.

This does not make independence subjective. It makes the causal and policy
assumptions explicit, auditable and falsifiable.

## Operational formalization

Let:

- `E` be an unchanged finite set of observations about one proposition;
- `C` be a declared set of candidate lineage cuts;
- `r_c(e)` be the recorded root of observation `e` at cut `c`, or `⊥` when
  unknown;
- `v(e) ∈ {0,1}` be the observation's assertion;
- `F_c(E)` be the existing Minority Prophet root verdict after replacing each
  observation's root with `r_c(e)`;
- `τ_D ≥ 1` be the minimum winning-root count declared for decision `D`.

For side `b`, the roots visible at cut `c` are:

```text
S_b^c(E) = { r_c(e) | e ∈ E, v(e)=b, r_c(e)≠⊥ }
```

The decision is settled at cut `c` only when `F_c(E)` is decisive and its
winning side has at least `τ_D` roots. Otherwise it is `unsettled`. Unknown roots
use the existing `abstain_if_decisive` policy: they are never silently promoted
to independent evidence.

An alternative cut `c'` is **decision-material** relative to selected cut `c`
when it changes the disposition:

```text
M_D(c,c') := disposition_D(c) ≠ disposition_D(c')
```

where the disposition is one of `settled_true`, `settled_false`, or
`unsettled`. A root-count change that does not cross the declared threshold is
reported as count-sensitive, not verdict-material.

The **proximal root** is the root at the selected cut: the nearest recorded
causal boundary declared relevant to the decision's failure domain. The
**ultimate lineage** remains available for audit and for decisions using a
different cut.

## Required context

Every assessment declares:

- the exact proposition and decision ID;
- the failure domain being guarded against;
- the selected independence cut;
- the minimum winning-root count;
- consequence and reversibility labels;
- how the cut was selected (`preregistered`, rules engine, model, human review,
  declaration, or unknown);
- any alternative cuts used for sensitivity analysis.

The adapter does not infer these values. Selecting the wrong failure domain or
cut remains a trusted policy error.

## Invariants

1. **Full-lineage preservation.** Evaluating a proximal cut cannot delete,
   rewrite or merge the underlying multi-resolution record.
2. **Explicit cut.** No output may be described as an independent count without
   naming the cut that produced it.
3. **No self-certification promotion.** Distinct declared root IDs do not become
   attested independence merely because they differ.
4. **Unknown stays unknown.** Missing roots fail closed when they could change
   the disposition.
5. **Minority preservation.** Collapse changes evidential mass, not visibility;
   a contrary independently rooted observation remains present even when it
   does not settle the proposition.
6. **Materiality is counterfactual.** A cut is material only relative to a
   declared alternative and decision threshold.
7. **Evidence is not authority.** Settlement is an evidence assessment, not
   permission to act. Gate and runtime policy remain separate.

## Architectural placement

| Layer | Responsibility |
|---|---|
| Minority Prophet | Benchmark whether the correct decision-relative cut preserves materially independent minority evidence and avoids false settlement. |
| Provenance / Knowledge Ledger | Preserve complete ancestry, identities at multiple cuts, assurance basis, time and contradictions. |
| AgentWEX | Transport minimized observations and expose multi-resolution counts; never invent the decision context. |
| Strategic governor | Declare the relevant failure domain, cut, sufficiency threshold, consequence and stopping rule. |
| Border / Gate | Bind the assessment to one proposed action and enforce proceed, deny or escalate policy. |

This primitive is the bridge between static epistemics (what depends on what?)
and strategic epistemics (which dependency can materially change this
decision?). It is not a new identity system or a universal voting rule.

## Executable fixtures

`benchmark/decision-relative-independence-v0.1.json` contains three constructed
counterexamples:

1. three machines under one controller;
2. a copied majority and an independently sourced minority;
3. three sensors sharing one upstream component.

`provenance.decision_relative.assess_decision` evaluates the same evidence at
multiple declared cuts. The fixtures pass only when a cut change can convert a
settled result into an unresolved one where the shared failure domain is
material.

Run:

```bash
python -m pytest -q tests/test_decision_relative_independence.py
```

## Research experiment

Before product enforcement, preregister a benchmark that presents systems with
the same lineage graph under multiple decisions. Compare:

1. agent headcount;
2. one fixed global root definition;
3. an oracle policy selecting the preregistered relevant cut;
4. a model or rules engine asked to select the cut from the decision context.

Measure false settlement, unnecessary abstention, minority preservation,
selected-cut accuracy, calibration, latency and sensitivity-report accuracy.
Score cut selection separately from aggregation so a correct vote cannot hide
an incorrect causal model.

## Next: DRI-3 (draft)

All 14 of the DRI-2 method's false settlements were stacked dependence on
which every cut agreed. [`DRI-3-DESIGN-DRAFT.md`](DRI-3-DESIGN-DRAFT.md) drafts a
test of whether settling only on a robust settlement
(`provenance/dependence_robustness.py`) is immune to that class, and what it
costs. Not frozen, not run.
## Result: DRI-2 v2 (final)

DRI-2 v2 reran the unchanged v1 method on 12,624 fresh synthetic worlds with no
human and speed measured but not a criterion, and was **supported**: all 44
checks passed. The method crossed as often as always abstaining and far more
often than headcount or any fixed cut, with almost no unneeded abstentions. Its
criterion was fixed after v1 was known. Full record:
[`results/dri2-v2/`](../../results/dri2-v2/README.md),
[`research/records/DRI-2-V2.json`](../records/DRI-2-V2.json).

## Result: DRI-2 v1

DRI-2 withheld the failure domain on 12,624 frozen synthetic worlds and was
**rejected**: the decision-sensitivity guided method crossed as often as always
escalating and far more often than headcount or any fixed cut, with almost no
excess human calls, but failed its frozen time criterion. Full record:
[`results/dri2-v1/`](../../results/dri2-v1/README.md),
[`research/records/DRI-2-V1.json`](../records/DRI-2-V1.json). Its speed checks were
misplaced; with them set aside, all 44 other registered checks passed. See the
[`post-result note`](../../results/dri2-v1/POST-RESULT-NOTE.md), which leaves the verdict unchanged.

## Result so far: DRI-1A

DRI-1A tested the declared-policy arm on 8,192 frozen synthetic worlds, with the
failure domain *supplied* to the selector. Full record:
[`results/dri1a-v1/`](../../results/dri1a-v1/README.md),
[`research/records/DRI-1A-V1.json`](../records/DRI-1A-V1.json).

Its frozen criterion required false settlement at least 15 points lower than
**every** fixed cut, including after abstention matching. It was not met:

| Fixed cut | False-settlement reduction by the relevant cut | Against the 0.15 bar |
|---|---:|---|
| Agent headcount | 30.21 points | met |
| Machine | 22.67 points | met |
| Controller | 13.07 points | short by 1.93 |
| Evidence origin | 13.06 points | short by 1.94 |
| Upstream component | −5.75 points | short by 20.75 |

The upstream-component cut settled falsely less often only by abstaining on
40.23% of worlds, and it had the lowest correct-settlement rate of any method
(56.51% against the relevant cut's 90.99%). Three of the fixed cuts could not be
abstention-matched within the frozen tolerance, which also fails the criterion.
The favourable descriptive numbers are recorded in the result and are not a
rescued claim.

Against this document's kill criteria below:

- *one fixed, simpler policy matches on false settlement and abstention* — **not
  triggered**: no fixed cut matched on both;
- *systems cannot select the relevant cut above a trivial baseline* — **not
  tested**: the cut was supplied; this is DRI-1B, which has not run;
- metadata availability, false escalations from sensitivity analysis, and expert
  agreement on cuts — **not tested**;
- *joint failure domains dominate* — **not represented**: every DRI-1A world had
  exactly one failure domain.

What DRI-1A adds to the design of any successor: false settlement read alone
rewards abstention, so the next test must score correct settlement, abstention
and false settlement together. A refusal never counts as crossing. Handing over
to a human is part of crossing only at the junction where a human is genuinely
needed; stopping before that point, when the system could have carried on, is a
stall and counts as a failure. In deployment the system should still fail safe;
the test measures whether it navigates the critical path.

## Relation to the canon's independence model

`canon/proximity.py`, `canon/U1-PROXIMATE-ROOTS.md` and
`aggregation/independence_axes.py` (2026-09-07 to 2026-09-14) answer a related
but different question. They do **not** supersede this document or
`provenance/decision_relative.py`, and neither side cited the other until this
section.

- **This document asks which kind of shared cause to group observations by** for
  one decision: the same machine, controller, evidence origin or upstream
  component. It selects one cut.
- **The canon asks how far each witness went toward the world, and against which
  class of error they are independent.** Witness depth runs from observing the
  world to restating text; an error entering at one rung is invisible to any
  witness that joined above it. It reports the independent count for every error
  class (`independence_profile`) and names the least-defended one
  (`weakest_link`), without selecting. Separately, `IndependenceAxes` records per
  root how well the depth is backed, who vouched, and whether the observer can
  be identified.

Both say independence is not a single number. They slice it in different
directions: this document by what is shared sideways, the canon by depth toward
the world.

### Proposed mapping

**Proposed, not established.** Nothing in the repository tests this mapping.

| DRI-1A failure domain | Cut | Nearest canon concept | Canon error class | Existing evidence | Fit |
|---|---|---|---|---|---|
| `copied_source` | `evidence_origin` | witness depth at the text and analysis rungs; U1's shared-marker test | `TRANSCRIPTION`, `ANALYSIS` | HEO-1, canonical, supported | close |
| `shared_upstream_component` | `upstream_component` | re-measurement by the same method or instrument | `INSTRUMENT`, `SYSTEMATIC_METHOD` | none canonical | close |
| `machine_local` | `machine` | no direct rung; nearest is the processing pipeline | `PROCESSING` | none | loose |
| `shared_controller` | `controller` | **not on the depth ladder**: control domain (`Attestation.INTERNAL`) | none; control is not an error class | HVI-1, canonical, supported | orthogonal |
| — | `agent` | none; counts records | — | — | n/a |

### How they interact

1. **Selecting versus profiling.** Reading the canon's profile at the error class
   that matches a declared failure domain is the proposed counterpart of this
   document's relevant-cut policy. Always acting on `weakest_link` is the
   proposed counterpart of always taking the coarsest cut.
2. **What DRI-1A suggests about the second.** The coarsest fixed cut in DRI-1A
   was the safest on false settlement and the least decisive of all methods. If
   the counterpart holds, a policy that acts only on the weakest error class
   inherits that trade, which is the false-denial failure the canon itself warns
   against. This is untested, and the mechanisms differ: DRI-1A merges roots at a
   coarse cut, while the canon counts a maximum independent set per error class.
3. **Control is a separate axis.** HVI-1's matched boundary case kept eight
   separately controlled roots carrying one adverse claim as eight, with 75.72%
   decision error. Separate control with shallow depth is not independent
   evidence, so the controller cut cannot stand in for the depth ladder, or the
   reverse.
4. **Joint independence is open in both.** This document's single-cut model
   cannot represent joint failure domains. The canon evaluates error classes one
   at a time, and `IndependenceAxes` composes per-root properties by partial
   order and meet. Neither answers whether a set of observations is independent
   with respect to controller and evidence origin at once.
5. **Who chooses is the same unsolved step.** The strategic governor declares the
   cut here (`canon/PLACEMENT.md`); rung assignments must be published by the
   owner before any sample under `ASSAYER.md` A3. DRI-1B would test whether that
   choice can be made from the decision context, and has not run.

The successor experiment that would compare these directly is drafted, not
frozen, in [`DRI-2-DESIGN-DRAFT.md`](DRI-2-DESIGN-DRAFT.md).

## Falsification and kill criteria

Reject or sharply narrow the proposal if any of the following survives matched
testing:

- one fixed, simpler root policy matches decision-relative policy on false
  settlement and abstention;
- systems cannot select the preregistered relevant cut above a trivial baseline;
- root metadata needed for useful cuts cannot be obtained without adoption
  friction or self-reporting that destroys its evidentiary value;
- sensitivity analysis produces enough false escalations to erase the avoided
  errors or latency benefit;
- reasonable experts cannot specify failure domains and cuts consistently;
- joint failure domains dominate real cases and the current single-cut model
  cannot represent them without unsafe over-counting.

The last condition is an explicit open limit. Multi-cut independence is not
implemented here: independently satisfying controller and source counts does
not prove the existence of observations jointly independent across both.
