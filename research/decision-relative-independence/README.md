# Decision-relative independence

Status: **proposed research primitive with constructed falsification fixtures.**
The executable adapter and fixtures do not establish that a model can discover
the correct causal cut in real systems. No existing Minority Prophet theorem is
extended by this document.

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

### DRI-1A candidate result

The declared-policy arm ran 8,192 frozen synthetic worlds and **failed** its
joint preregistered criterion. This is a noncanonical candidate diagnostic: its
pre-run record omitted uncertainty, multiple-testing, lifecycle, and environment
fields required by the repository's canonical standard. The relevant-cut policy was materially more
accurate than every fixed cut and recovered all registered minority reversals,
but a globally deepest cut bought a lower false-settlement rate by abstaining on
40.23% of worlds. Several coarse baselines could not be matched to the oracle's
zero-abstention operating point, so the registered matched comparison failed.
The deterministic five-cut assessment remained below 0.7 ms p99 on the test
machine. See `results/dri1a-v1/README.md` for the complete bounded result.

The next open question is DRI-1B: can blinded humans or models select the right
cut on externally authored cases? DRI-1A cannot answer it because its rules
engine received the explicit failure-domain label.

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
