# AID-1 — preregistration, protocol v1

**Status: FROZEN, protocol v1. NOT RUN.** Frozen before any confirmatory
campaign is generated or scored. The policy, the arms and the criteria were
named in
[`research/attested-independence/AID-1-DESIGN-DRAFT.md`](../../research/attested-independence/AID-1-DESIGN-DRAFT.md)
before this world existed. This file is the world, written by someone other than
the author of the policy it tests.

No confirmatory outcome had been computed when this was frozen. Development
salt only. Same control domain as the policy. Not independent validation.

## 1. Identifier

AID-1, protocol v1. Code in `experiments/aid1run/`.

## 2. What is under test

`aggregation/attested_independence.py`, adopted as
`canon/ATTESTED-INDEPENDENCE.md`, for counting that permits action on reversible
decisions. The policy detects nothing; DR3 proves detection impossible. The open
question is its price, and the price is measurable.

## 3. Arms, named in section 4 of the spec before this world existed

1. **`ladder`** — `canon.proximity.independent_for`, unchanged. Baseline.
2. **`attested`** — the adopted policy, `effective_witnesses_for` with
   `Use.PERMIT_ACTION`, at each adoption rate.
3. **`attested_declared_only`** — the same policy with backing ignored. Built by
   setting each witness's backing to `DEVICE_ATTESTED` / `BONDED`, which makes
   `admissible_depth` return the claim itself. The arm therefore runs the
   policy's own code with `admissible_depth` neutralised and nothing else
   changed, so a null result here is a statement about the backing machinery and
   not about a reimplementation of it. Named in advance as the failure mode to
   exhibit.
4. **`refuse_all_unrecorded`** — refuse whenever any pair lacks recorded
   ancestry. Trivially safe upper bound on cost.

Every arm answers by the same pipeline: count each side's effective witnesses
against the decision's error class through `canon/independent_set.py`, then
settle with `provenance.dependence_robustness.settle_counts`. Only the
independence relation varies.

## 4. Scope

Reversible decisions, per the owner's standing scope decision. Irreversible
decisions are generated and tallied without a pass mark.

## 5. Generated world

Six families, nine variants, `campaigns_per_variant` campaigns each, 12
decisions per campaign, alternating irreversible/reversible. Cells are the
adoption rate `alpha ∈ {0.0, 0.25, 0.5, 0.75, 1.0}` crossed with the error class
`∈ {FABRICATION, INSTRUMENT, TRANSCRIPTION}`. The error class is not an input to
generation, so the same world is scored against all three and the comparison is
paired by construction.

| Family | Variant | What is true | What it is built to break |
|---|---|---|---|
| `nobody_can_attest` | `unfindable_honest` | Five honest witnesses who went to the world; no artifact, no key, unfindable. Nothing hidden. | The policy grants them `TEXT` and settles nothing. Pure cost, no error prevented, at every `alpha` including 1.0. Decides criterion 2. |
| `adversary_attests_freely` | `declares_completeness` | Three witnesses echoing one fabricator. Declared `REALITY`, declared complete ancestry, no backing, `ANONYMOUS`. The spec's wording, verbatim. | The completeness clause returns before any depth is consulted, so the policy grants them full independence. Ceremony added to the same blindness. |
| | `claims_bonded_identity` | The same adversaries claiming `BONDED` with nothing behind it. | `IndependenceAxes.honoured_identity` degrades an unreferenced bond to `NAMED`; `Witness.admissible` never calls it. The free claim buys `REALITY`. |
| | `declares_depth_only` | The same adversaries declaring depth but not completeness. | The strain where the backing machinery does bite, so criterion 3 is a real test rather than a foregone one. |
| `hidden_shared_source` | `unaware` | Four witnesses on one hidden source, nothing recorded connecting them, three genuine independents. The group attests completeness in good faith and is wrong. | The policy's only benefit disappears: an honest but mistaken completeness claim is indistinguishable from a true one. |
| | `aware` | The same, but the group knows its record is incomplete and never attests completeness. | The only construction in the whole world where the policy can prevent anything. |
| `baseline_already_right` | `nothing_hidden` | Three witnesses who are right, one who is wrong, everyone attestable, nothing hidden. | Reflexive discounting is punished. At `alpha = 1.0` a working policy pays nothing here; at `alpha = 0` it loses every settlement. |
| `minority_suppression` | `count_decides_survival` | Three attestable majority witnesses asserting the false value against three unattestable witnesses carrying the true one. All six genuinely independent. | The baseline ties and the claim survives; the policy deflates the minority to one and settles against it. Suppression increases with `alpha`. |
| `mixed_attestation` | `mixed` | One decision holding an artifact-attested pair on a hidden source, a recorded-ancestry pair sharing a marker, an unattestable witness, a witness that states no depth at all, and a device-attested witness. | A rule that only works when every witness is attested or none is. |

Each witness carries its own recorded lineage token, so no observation is
unattributed and the record is never trivially non-robust. What the record does
not carry is any token connecting two witnesses of one hidden source. That is
DR3's case and it is what makes the baseline's false settlements silent.

## 6. Construction choices made against the policy, and why

These are the places where section 5 left a choice. Each was made so the policy
could lose, and each is stated here rather than discovered later.

1. **The unattestable are genuinely unattestable.** In `nobody_can_attest` and
   for the minority in `minority_suppression`, `attestable` is `False`, so no
   adoption rate reaches them. A world in which every witness becomes attested
   at `alpha = 1.0` would have no cost to measure at full adoption, which is the
   cell criterion 2 is stated on.
2. **The hidden group is split into `aware` and `unaware`.** Building only
   `aware` would flatter the policy; building only `unaware` would make
   criterion 1 unwinnable by construction. Both exist, the family row aggregates
   them because the criteria are stated per family, and `variants` in the
   semantic result reports them apart.
3. **The adversary has three strains, not one.** Only
   `declares_completeness` is the spec's literal wording. `declares_depth_only`
   was added so the backing machinery has a case it can win, which is the
   condition for criterion 3 being a test rather than a formality.
   `claims_bonded_identity` was added because `Witness` skips the
   `honoured_identity` check that `IndependenceAxes` performs, and an
   unreferenced self-declared bond is precisely "no identity that can be held".
4. **The minority decision is called with `Use.PERMIT_ACTION`.** The policy
   raises `ScopeViolation` on `Use.DECIDE_SURVIVAL`, and a protocol test pins
   that it does. But the use is caller-declared and nothing in a record
   distinguishes the two: a caller settling whether to act declares
   `PERMIT_ACTION` truthfully while the same count deletes a claim. Scoring the
   family through the declared-forbidden path would test the assertion rather
   than the scope, which section 5 explicitly asked not to do.
5. **`TRANSCRIPTION` is kept as a cell.** At the bottom error class every
   admissible depth clears the divergence test, so the policy costs nothing and
   prevents nothing. Dropping it would overstate the price; keeping it bounds
   the claim.
6. **The ladder places an unstated claim at `TEXT`.** The legacy ladder has no
   `UNSTATED` rung. Reading a witness that says nothing as hearsay is the
   default the policy exists to refuse, so the baseline must make it.

## 7. Criteria, copied verbatim from section 6 of the frozen spec

> Scored on reversible decisions, by the owner's standing scope decision.
> Powered cells only, Holm-corrected across arms, fail closed when underpowered.
> Two executions must be semantically identical.
>
> **The policy is supported only if all hold:**
>
> 1. **It prevents what it exists to prevent.** In every powered cell of the
>    hidden-source family, at least 40% of the baseline's margin-critical silent
>    false settlements are prevented — the same floor DRI-9 through DRI-11 used,
>    so the number is not chosen for this run.
> 2. **Cost is bounded by benefit.** Correct settlements lost do not exceed
>    silent false settlements prevented, in every family and cell, at adoption
>    rate `α = 1.0`.
> 3. **It is not theatre.** `attested_declared_only` must do materially worse
>    than `attested` in the freely-attesting family — otherwise the backing is
>    ornamental and the policy is rejected regardless of its other numbers.
> 4. **It is cheaper than refusing.** Strictly more correct settlements than
>    `refuse_all_unrecorded`, at no worse prevention, in every powered cell.
> 5. **It does not suppress.** In the minority-suppression family, the true
>    contrary claim survives at the same rate as under the baseline. Any loss
>    here fails the experiment outright, whatever the other results, because it
>    is the attack the policy's own scope was written to prevent.
>
> **Reported, not criteria:** the adoption curve — cost and prevention at each
> `α` — and the share of decisions with mixed attestation.

Nothing above is renumbered, softened or added to. The verdict is `supported`
only if every check passes; otherwise it is `not supported`.

## 8. Operationalisation, where section 6 gave no number

Two phrases in section 6 are not numbers and had to be made computable. Both
choices are recorded here, before execution, and neither may move afterwards.

- **"margin-critical"** — a decision where the true causal grouping decides the
  answer: `settlement_over_units` over the true units differs from the same
  settlement with every witness counted separately. Computed in `world.py`, so
  the world and the scoring cannot drift apart.
- **"silent"** — a false settlement that the recorded ancestry alone settles the
  same way, by `assess_dependence_robustness`. Where the record shows possible
  dependence, the settlement is flagged instead and somebody could have looked.
- **"materially worse"** (criterion 3) — `attested_declared_only` makes strictly
  more silent false settlements than `attested`, the McNemar difference is
  significant after Holm correction at `familywise_alpha`, and the excess is at
  least `theatre_margin = 0.10` of the baseline's silent false settlements in
  that family.
- **"survives at the same rate"** (criterion 5) — read as *no loss*: the
  policy's surviving count may not fall below the baseline's in any cell of the
  minority family. Powering is not required; section 6 says any loss fails the
  experiment outright.
- **"powered"** — a cell where the baseline makes at least
  `minimum_critical_silent_for_test = 12` margin-critical silent false
  settlements, the DRI-11 threshold. Fail closed: no powered hidden-source cell,
  or no powered freely-attesting cell, is `not supported`.

Holm correction is applied jointly across `attested`,
`attested_declared_only`, `refuse_all_unrecorded` in every powered cell and
across the theatre-versus-policy comparisons, as one family of tests.

## 9. Reused machinery, and one deliberate departure

Reused rather than rebuilt, because a previous experiment in this series
silently dropped machinery from an earlier one:

- `experiments/dri3/world.py` — settlement outcomes (`settlement_over_units`,
  `SETTLED`, the reversible/irreversible classes and their thresholds). The
  reference settlement is DRI-3's, unchanged, including its legacy
  `independence_basis` stamp.
- `experiments/dri2/stats.py` — `holm`, `mcnemar_exact`.
- `provenance/dependence_robustness.py` — whether a settlement is silent or
  flagged by the record.
- `provenance/decision_relative.py` — `DecisionEvidence` and the root-vote
  kernel beneath it.
- `canon/independent_set.py` — exact `N_eff`, reached through both independence
  modules rather than reimplemented.

**Departure:** arm settlements are computed as `settle_counts` over each side's
`N_eff`, not through `experiments/dri9/rule.py`. The DRI-9 rule settles over
lineage cuts and a learned belief; this experiment's arms differ only in a
pairwise independence relation, and the policy's own public entry point is
`effective_witnesses_for`. Routing it through the DRI-9 rule would have measured
that rule rather than the policy. `Belief` and `lookup_grouping` have no
counterpart here because no arm learns anything — the policy detects nothing by
construction.

## 10. What this experiment cannot answer

- Whether attestation is obtainable at all. The census in `experiments/aid1/`
  found zero records in this estate stating a witness depth. Every adoption rate
  here is synthetic and none of them is a measurement.
- Whether the reference grouping is the right one. It is stipulated by the
  generator.
- Anything about irreversible decisions.

## 11. Disclosure

- Written after the policy and its criteria were frozen, by an author who did
  not write the policy. Development salt only for construction tests.
  Confirmatory salt named in `EXECUTION-CONFIG.json` and unread.
- Same control domain. Not A2-independent validation.
- Every rate in this world is stated, not measured.
- No authority claim.
- The construction tests in `tests/test_aid1_protocol.py` pin the six families
  to the cases section 5 asked for. Where a construction test disagreed with the
  world, the world was fixed; no criterion was moved.
