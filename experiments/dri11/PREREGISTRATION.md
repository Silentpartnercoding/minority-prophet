# DRI-11 — preregistration, protocol v1

**Status: FROZEN, protocol v1, 2026-09-16. NOT RUN.** Frozen before any
confirmatory campaign is generated or scored. Methods were named in
`research/decision-relative-independence/DRI-11-DESIGN-DRAFT.md` before this
world existed. This file is the world and the criterion, written by the
adversarial review, not by the author of the methods.

No confirmatory outcome had been computed when this was frozen. Same control
domain as DRI-9 and DRI-10. Not independent validation.

## 1. Identifier

DRI-11, protocol v1.

## 2. Why this exists

DRI-10 rejected bait (28 of 40) on a world that separated error from mark.
The write-up then named **fragile refusal** as the next method because it
prevented 473–521 critical errors in every DRI-10 hidden family. Those families
were all pairs. DRI-9 already measured refusal at **0.00 in every trio cell**.
Naming refusal "the simplest thing that could work" after a pair-only world is
the same shape as naming bait after a world built for bait.

The secondary method — two signals, then refuse if fragile and unsupported —
is the DRI-9 ladder plus a fallback. DRI-10 showed the ladder never collapsed
a library. No experiment has contained two signals that agree because they
share a cause.

## 3. Methods, named before this world

Copied from the spec, not chosen here:

1. **Primary: `fragile_refusal`.** Refuse when believing any winning-side pair
   would change the settlement or its stamp. Otherwise answer.
2. **Secondary: `composite`.** Believe a pair when two declared signals
   (bait, co-error) agree. Otherwise, if the answer is fragile and no signal
   supports any winning-side pair, refuse. Otherwise answer.

## 4. Questions

1. Does refusal still clear 40% prevention when one of the dependence families
   is a trio?
2. Does its cost bound survive a family of fragile-but-correct decisions?
3. Does the composite beat refusal on cost without collapsing a library, and
   without merging two independents whose mark and co-error come from one shock?

## 5. Scope

Reversible decisions. Irreversible still uses `lookup_grouping` and ignores
belief. Tallied without a pass mark.

## 6. Generated worlds

400 campaigns per family, 12 decisions, pickup ∈ {0.5, 0.9} × leak ∈ {0.02, 0.20}.

| Family | What is true | What can fail |
|---|---|---|
| `unmarked_hidden_pair` | Hidden pair, mark is environmental | Refusal must prevent here |
| `unmarked_hidden_trio` | Hidden trio, mark is environmental | Refusal cannot see groups of three |
| `marked_hidden_pair` | Hidden pair, mark is the component | Composite's signals have a true target |
| `fragile_correct` | Baseline already right; winning pair is pivotal | Refusal's unneeded abstentions |
| `common_carrier` | Shared library, no shared error | Composite collapse |
| `shared_shock` | Two independents jointly wrong and jointly marked by one shock that is not an identity | Two signals agree for one reason |
| `robust_correct` | Six high-accuracy independents, not fragile | Reflexive refusal or merging |

`shared_shock` is the case the spec asked for if nothing else was built.
`unmarked_hidden_trio` is the case the spec omitted and DRI-9 already ran.

Critical share is measured by `is_pivotal` against the family's focus group.
`robust_correct` has an empty focus.

## 7. Scoring

DRI-3 outcomes. Unneeded abstention = abstain when the reference settled.
A cell is powered when the baseline makes at least 12 margin-critical silent
false settlements. Holm-corrected across both methods' powered comparisons.

## 8. Success criterion

Fail-closed: no powered dependence cell for the primary ⇒ not supported.

**Primary (`fragile_refusal`) is supported only if all hold:**

1. **Prevention.** In every powered cell of every dependence family — pair,
   trio, and marked pair — prevents at least 40% of the baseline's
   margin-critical silent false settlements, significantly.
2. **Cost bound.** In **every** family and cell, unneeded abstentions do not
   exceed the silent false settlements it prevented. On `fragile_correct` the
   baseline is already right, so the bound is zero unneeded abstentions unless
   it also prevented something.
3. **Correct settlements** stay within 80% of the baseline in every family.
4. **Reproducibility.** Two executions identical.

**Secondary (`composite`) is supported only if, in addition:**

5. In every powered dependence cell, strictly fewer unneeded abstentions than
   refusal, at no worse critical prevention.
6. On `common_carrier` and `shared_shock`, false merges do not exceed true
   merges, and correct settlements stay within 95% of the baseline.

The experiment verdict `supported` is the primary's verdict. The secondary is
reported separately and is not a consolation prize.

## 9. Frozen inputs

Pinned by the runner: this protocol, `EXECUTION-CONFIG.json`,
`experiments/dri11/world.py`, `arms.py`, `scoring.py`,
`experiments/dri9/rule.py`, `experiments/dri8/world.py`,
`experiments/dri3/world.py`, `experiments/dri2/stats.py`,
`provenance/dependence_robustness.py`, `provenance/decision_relative.py`.

## 10. Disclosure

- Written after DRI-9 and DRI-10, in response to a spec that named both
  methods after seeing DRI-10's pair-only scoreboard. Development salt only
  for construction tests. Confirmatory salt unread.
- Rates stated, not measured.
- Same control domain. Not A2-independent validation.
- No authority claim.
- DRI-9-V1 and DRI-10-V1 stay rejected.
