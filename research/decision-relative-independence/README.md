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

## Observation: DRI-7, the same rules on a corpus nobody authored

**Not preregistered, and not a result in the sense of the sections below.** The
corpus is historical and the analysis was performed before the write-up existed.
It is recorded as an *exploratory* record for that reason, and the repository's
own record tooling refuses to pin a protocol for it.

DRI-1 through DRI-6 generate their worlds. That is the right way to establish a
mechanism and the wrong way to establish a rate, because a rate measured on an
authored corpus reads back the setting that authored it. DRI-7 runs the same
rules against 642 records written over six weeks by a production job-control
plane, for purposes unrelated to this research.

- **Record-only is not inaccurate; it is non-falsifiable.** It accepted 642 of
  642 records across two corpora that share no identifier scheme. No input
  present could make it return false: the defect lies entirely outside what it
  inspects. A check whose outcome has only ever held one value has not been
  tested, whatever its sample size.
- **Looking twice removed 100% of the silent failures**, on both corpora,
  because the first look removed none. That is the top of DRI-6's 68–100% band,
  reached on data with no author.
- **The DRI-6 gap is the one that bites.** DRI-6 recorded "a lookup wrong the
  same way every time" as not covered. Record-only is the limiting case of it —
  a check whose answer is constant regardless of input — and it is what was
  running in production.
- **Content addressing recovered 82% of what location lost.** Absent referents
  were mostly retrievable by hash from a store already present; they were not
  lost, they were addressed by a path that did not survive.
- **What makes a check untested is that its outcome never varies.** A negative
  control shows the second way to build one: a sibling table of 2,299 rows is
  genuinely clean and seven more hold zero rows, so a check aimed at those eight
  reports a sound system — truthfully, and worthlessly, since zero-over-zero and
  zero-over-2,299 print the same — while 102 absent referents sit in a ninth.
  Report the denominator; audit outcome distribution, not pass rate.
- **Boundaries:** one host, one control plane; 235 of 358 records name
  repositories absent from this host and are *unverifiable*, not clean; the two
  corpora are independent in identifier scheme and code path, not in root cause.

Refuted by exhibiting a single record that record-only rejects. Full write-up:
[`experiments/dri7/OBSERVATIONAL-REPORT.md`](../../experiments/dri7/OBSERVATIONAL-REPORT.md),
[`research/records/DRI-7-V1.json`](../records/DRI-7-V1.json). Rerun:
`python3 experiments/dri7/measure.py`.

## Result: DRI-9 v1, belief that acts, and a favourite that lost

DRI-8's arms could discover a shared source and then not act on it: a learned
merge was one identity among six cuts and was outvoted by the five describing the
disguise. DRI-9 makes belief override the record's identities at every cut, and
asks which instrument earns that belief. Criterion on reversible decisions, by
owner decision. **Rejected**, 58 of 65.

- **The named method lost.** The ladder, which required two signals to agree,
  cleared its 25% effect floor in **1 of 8** powered cells. It was the most precise
  arm — 0 to 6 false merges, not one correct settlement lost — and the least
  useful. Combining weak signals cost more than it bought.
- **The simplest instrument won inside a world built for it.** Bait — plant a
  marker upstream, see who carries it — cleared the floor in **8 of 8** at
  34–77%, scaling with pickup rate, and raised correct settlements in the trio
  family from 1,273 to 1,622. It is a reported arm. The decoy planted no
  markers, so the harm clause did not test it. Naming it on that generator
  and rerunning is not the next experiment; DRI-10 is.
- **Prevention alone is not a measure.** Reflection cleared the floor while making
  6,497–8,782 false merges per cell and collapsing correct settlements from 3,000
  to about 1,300 in the decoy family.
- **Refusing is blind to trios.** Fragile refusal prevented half the pair family's
  errors and exactly none in the trio, because it tests pairs.

A dated post-result note corrects three claims made around this result: the decoy
family planted no markers, so bait's "no harm" there was not a test; the
margin-critical filter was an identity in all eight cells; and relabelling the
same result as bait returns 65/65, which is why a successor must not simply
rename the method on this generator. The verdict is unchanged. See
[`POST-RESULT-NOTE.md`](../../results/dri9-v1/POST-RESULT-NOTE.md).

Full record: [`results/dri9-v1/`](../../results/dri9-v1/README.md),
[`research/records/DRI-9-V1.json`](../records/DRI-9-V1.json). Design:
[`DRI-9-DESIGN-DRAFT.md`](DRI-9-DESIGN-DRAFT.md). Adversary note on the
proposed sequel: [`#204`](https://github.com/Silentpartnercoding/minority-prophet/pull/204).

## Candidate: DRI-10 v1, bait against a world that can reject it

Frozen, not run. Error component and marker carrier are separate knobs.
`marked_hidden_pair` is DRI-9's bait story, kept as a positive control.
`unmarked_hidden_pair`, `common_carrier` and `leaky_independents` exist so
that story is not the whole world. Bait is named before the confirmatory
salt. Quiet (no powered floor cell) is a fail. Same control domain as DRI-9;
written after that confirmatory was public.

Protocol: [`experiments/dri10/PREREGISTRATION.md`](../../experiments/dri10/PREREGISTRATION.md).
Design: [`DRI-10-DESIGN-DRAFT.md`](DRI-10-DESIGN-DRAFT.md).
Run, after the candidate record is committed:

```text
PYTHONPATH=. python -m experiments.dri10.run_confirmatory --output results/dri10-v1/result.json
```

## Result: DRI-8 v1, intervention, and a criterion that asked too little

DR3 says no rule reading the record can separate independent sources from two
sharing an unrecorded origin. DRI-8 stopped reading and acted: a tracer through
one source's upstream, observed in another's next report, spent only where merging
the pair would change that decision's outcome.

It was **supported** on all 49 checks, and the result is thinner than that sounds.

- **The mechanism is real.** Probing prevented silent false settlements that no
  record-only rule can prevent, by stamping them "not robust".
- **The scale is not.** 80 of 2,281 in the pair family, 10 of 3,084 in the trio,
  with correct settlements unchanged in every arm.
- **The price is high.** 16 to 468 probes per error prevented, and a larger budget
  bought a worse rate.
- **Time is weaker.** Passive co-error history did nothing at all in the trio
  family, needed full feedback elsewhere, and merged independent sources an order
  of magnitude more often than probing did.
- **The criterion is the lesson.** It asked for significance and set no minimum
  effect, so 6,000 paired decisions per cell made a 0.3% difference "significant".
  A successor must state the effect it will accept before it runs.
- **A disclosed defect.** The margin-critical endpoint merges the whole hidden
  group, which never flips a trio decision although merging a pair sometimes does.
  It reads 0 for that family and is unmeasured there; the frozen protocol was not
  edited.

A dated post-result note records why the effect was small: a learned merge was
outvoted by the record's own identities, so the arm could find the dependence and
not act on it — see
[`POST-RESULT-NOTE.md`](../../results/dri8-v1/POST-RESULT-NOTE.md).

Full record: [`results/dri8-v1/`](../../results/dri8-v1/README.md),
[`research/records/DRI-8-V1.json`](../records/DRI-8-V1.json). Design:
[`DRI-8-DESIGN-DRAFT.md`](DRI-8-DESIGN-DRAFT.md).

## Result: DRI-6 v1, imperfect lookups

Every earlier experiment assumed a truthful lookup. DRI-6 let each lookup miss or
invent dependence, independently per call, and was **supported** on all 77 checks.

- **Harm:** with erring lookups, every silent false settlement the tiered rule made
  came after a look.
- **Record check:** checking a report against the record caught no missed
  dependence (DR3 again), and only some invented dependence.
- **Confirmation:** looking twice and settling only when both reports agree removed
  68–100% of those errors in every powered comparison, at 2.9–42.6 extra looks per
  prevented false settlement against missed dependence. Against invented dependence
  it cost many unneeded abstentions.
- **Not covered:** a lookup wrong the same way every time.

Full record: [`results/dri6-v1/`](../../results/dri6-v1/README.md),
[`research/records/DRI-6-V1.json`](../records/DRI-6-V1.json). Design:
[`DRI-6-DESIGN-DRAFT.md`](DRI-6-DESIGN-DRAFT.md).

## Result: DRI-5 v1, and why the record alone cannot be enough

DRI-4 showed protection eroding as lineage goes missing. Ledger DR3
(`no_record_rule_is_immune`) proves no rule that reads only the record can be immune:
one record can come from two groupings that settle differently. Protection needs an
observable the loss does not remove.

DRI-5 tested one, an exact content fingerprint counted as possible dependence, on
360,000 synthetic decisions, and was **rejected** on 4 of 193 checks.

- **Forgotten copies:** in the trap family, where the lost dependence is copying,
  exact content removed every silent and every irreversible false settlement.
- **Shared components or origins:** content carries no trace of them, and recovery
  was partial.
- **Paraphrase:** rewording half of copies largely defeated it.
- **Why it was rejected:** four recovery comparisons at 25% missing were not
  significant.

Full record: [`results/dri5-v1/`](../../results/dri5-v1/README.md),
[`research/records/DRI-5-V1.json`](../records/DRI-5-V1.json). Design:
[`DRI-5-DESIGN-DRAFT.md`](DRI-5-DESIGN-DRAFT.md).

## Result: DRI-4 v1, and the proof

DRI-3's zero silent false settlements were guaranteed by construction, so the
guarantee is now proved: `robust_settlement_is_true` (ledger DR2) in
`formal/lean/MinorityProphetCore/DependenceRobustness.lean`. When the engine reports
one settlement, every reading the record allows gives it, including the true
grouping whenever every real dependence is recorded.

DRI-4 tested that assumption on 240,000 fresh synthetic decisions and was
**rejected** on 2 of 67 checks.

- **Complete record:** the tiered rule made zero silent false settlements in every
  family, including a repaired side-asymmetric trap on which the old agreement
  rule settled every decision falsely.
- **Incomplete record:** as true shared identities went missing, protection eroded.
  The rule prevented 33–87% of the old rule's silent errors at 10% missing and
  10–26% at 50%, and never did worse.
- **Why it was rejected:** two comparisons at 10% missing were not significant.

Imperfect lookups remain the follow-up. Full record:
[`results/dri4-v1/`](../../results/dri4-v1/README.md),
[`research/records/DRI-4-V1.json`](../records/DRI-4-V1.json). Design:
[`DRI-4-DESIGN-DRAFT.md`](DRI-4-DESIGN-DRAFT.md).

## Result: DRI-3 v1

All 14 of the DRI-2 method's false settlements were stacked dependence on which
every cut agreed. DRI-3 tested the engine fix
(`provenance/dependence_robustness.py`) under the owner's tiered cost rule on
42,000 fresh synthetic decisions and was **supported**. It made zero silent false
settlements and zero irreversible false settlements in six recorded-dependence
families, where the old agreement rule settled falsely 780 times. The cost was
extra looks where lineage exists, and lost settlements where it does not.
Unrecorded dependence remains undetectable, and the side-asymmetric family did not
produce its intended case. The reversible scorecard chose forced looks, but every
false settlement it prevented came from one family, so that policy is not adopted
for real use until tested further. Full record:
[`results/dri3-v1/`](../../results/dri3-v1/README.md),
[`research/records/DRI-3-V1.json`](../records/DRI-3-V1.json). Design:
[`DRI-3-DESIGN-DRAFT.md`](DRI-3-DESIGN-DRAFT.md).

## Result: DRI-2 v2 (final)

DRI-2 v2 reran the unchanged v1 method on 12,624 fresh synthetic worlds with no
human and speed measured but not a criterion, and was **supported**: all 44
checks passed. The method had as few false settlements as always abstaining and far fewer than headcount or any fixed cut, with almost no unneeded abstentions. Its
criterion was fixed after v1 was known. Full record:
[`results/dri2-v2/`](../../results/dri2-v2/README.md),
[`research/records/DRI-2-V2.json`](../records/DRI-2-V2.json).

## Result: DRI-2 v1

DRI-2 withheld the failure domain on 12,624 frozen synthetic worlds and was
**rejected**: the decision-sensitivity guided method had as few false settlements as always
escalating and far fewer than headcount or any fixed cut, with almost no
excess human calls, but failed its frozen time criterion. Full record:
[`results/dri2-v1/`](../../results/dri2-v1/README.md),
[`research/records/DRI-2-V1.json`](../records/DRI-2-V1.json). Its speed checks were
misplaced; with them set aside, all 44 other registered checks passed. See the
[`post-result note`](../../results/dri2-v1/POST-RESULT-NOTE.md), which leaves the verdict unchanged. Terminology notes for both DRI-2 versions:
[`dri2-v1`](../../results/dri2-v1/TERMINOLOGY-NOTE.md),
[`dri2-v2`](../../results/dri2-v2/TERMINOLOGY-NOTE.md).

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
and false settlement together. A refusal never counts as completing a decision. Handing over
to a human is part of completing the run only at the junction where a human is genuinely
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
