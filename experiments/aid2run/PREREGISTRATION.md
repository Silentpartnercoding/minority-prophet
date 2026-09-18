# AID-2 — preregistration, protocol v1

**Status: FROZEN, protocol v1. NOT RUN.** Frozen before any confirmatory
campaign is generated or scored. The primary method, the arms and the criteria
were named in
[`research/attested-independence/AID-2-DESIGN-DRAFT.md`](../../research/attested-independence/AID-2-DESIGN-DRAFT.md)
before this world existed. This file is the world, written by someone other than
the author of the policy it tests.

No confirmatory outcome had been computed when this was frozen. Development salt
only. Same control domain as the policy. Not independent validation.

## 1. Identifier

AID-2, protocol v1. Code in `experiments/aid2run/`.

## 2. What is under test

`aggregation/attested_independence.py` as repaired on `research/aid2-repair`,
and specifically `witness_bounds`, which returns `WitnessBounds(lower, upper)`:
`lower` counts only independence that was earned, `upper` counts independence
wherever the record cannot rule it out.

AID-1 rejected the policy, 61 of 111 checks, and the failure that mattered was
suppression. The diagnosis was that a single number cannot serve two decisions
that need opposite conservatism. The repair is the range, and the discipline is
to evaluate a decision at both ends and settle only when the answer is the same
at both. AID-1 could not test that, because its arms asked for a point estimate.
This world's arms ask for the range.

The open question is whether the range does what the number could not, and
whether it does so by answering or merely by refusing.

## 3. Arms, named in section 3 of the spec before this world existed

1. **`ladder`** — `canon.proximity.independent_for`, unchanged. Baseline. Reads
   the *claimed* depth: the ladder has no backing test.
2. **`attested_bounds`** — **the primary.** For each decision, each side's
   `witness_bounds`; the settlement evaluated at the lower end and at the upper
   end; settled only if both ends give the same disposition, otherwise refused.
3. **`attested_point`** — the same repaired policy through
   `effective_witnesses_for` with `Use.PERMIT_ACTION`. It differs from the
   primary in exactly one thing, a number where the primary has a range, so the
   gap between them is what the range buys.
4. **`attested_declared_only`** — the primary with backing neutralised, by
   setting each witness's backing to `DEVICE_ATTESTED` / `BONDED`, which makes
   `admissible_depth` return the claim itself. It is the **bounds** rule, not
   the point rule: the theatre arm must differ from the primary in backing
   alone, or criterion 3 confounds "the backing machinery is ornamental" with
   "the range is ornamental". Computed by the policy's own code rather than by a
   reimplementation of it.
5. **`refuse_all_unrecorded`** — refuse whenever any pair lacks recorded
   ancestry. Trivially safe upper bound on cost.

Every arm answers by the same pipeline and settles with
`provenance.dependence_robustness.settle_counts`. Only what is handed to that
function varies.

## 4. Scope

Reversible decisions, per the owner's standing scope decision. Irreversible
decisions are generated and tallied without a pass mark.

## 5. Generated world

Six families, thirteen variants, `campaigns_per_variant` campaigns each, 12
decisions per campaign, alternating irreversible/reversible. Cells are the
adoption rate `alpha ∈ {0.0, 0.25, 0.5, 0.75, 1.0}` crossed with the error class
`∈ {FABRICATION, INSTRUMENT, TRANSCRIPTION}`. The error class is not an input to
generation, so the same world is scored against all three and the comparison is
paired by construction.

| Family | Variant | What is true | What it is built to break |
|---|---|---|---|
| `nobody_can_attest` | `unfindable_honest` | Five honest witnesses who went to the world; no artifact, no key, unfindable. Nothing hidden. | The range is wide at every decision and the primary refuses all of them against fabrication. Nothing is prevented, because nothing is wrong. Pure cost, arriving as refusal rather than abstention, which looks identical in a ledger and is not. |
| `adversary_attests_freely` | `declares_completeness` | Three witnesses echoing one fabricator. Declared `REALITY`, declared complete ancestry, no backing, `ANONYMOUS`. | Kept from AID-1 although the repair removed the completeness clause. A world that drops the case a repair claims to have fixed cannot show that it fixed it. |
| | `claims_bonded_identity` | The same adversaries claiming `BONDED` with nothing to point at. | Kept for the same reason. `honoured_identity` is wired in now and degrades the claim to `NAMED`, worth `PROCEDURAL` backing, floor `RAW`. |
| | `declares_depth_only` | The same adversaries declaring depth but not completeness. | The strain where the backing machinery bites, so criterion 3 is a real test rather than a foregone one. |
| | `device_attested_fabricator` | **New.** Three copies of one fabricator, each carrying a device attestation, nothing recorded connecting them. Two honest witnesses who cannot attest and are recorded as filing through one clerk. | The lower bound. `independent_for` asks only that both witnesses clear the error class and that their recorded ancestries are disjoint, so the bound that is supposed to count only *earned* independence counts three copies of one source as three. The honest pair collapses to one at both ends. The range is not wide here — it is pinned, and pinned on a falsehood. |
| `hidden_shared_source` | `unaware` | Four witnesses on one hidden source, nothing recorded connecting them, three genuine independents. The group attests completeness in good faith and is wrong. | DR3's case. Since the repair, identical in the policy's eyes to `aware`; a protocol test pins that, which is how the repair is shown to have landed. |
| | `aware` | The same, but the group knows its record is incomplete and never attests completeness. | As above. |
| | `device_attested_echoes` | **New.** The hidden group carries the device attestation; the honest independents cannot attest at all. | Inverts who the policy protects. Both ends count four sources where there is one, and deflate the honest independents. The family criterion 1 is scored on now contains a construction in which the primary prevents nothing. |
| `baseline_already_right` | `nothing_hidden` | Three witnesses who are right, one who is wrong, everyone attestable to an artifact, nothing hidden. | Reflexive discounting is punished. Criterion 6 is scored here. Artifact backing tops out at `METHOD`, so against fabrication the ends disagree on every decision and the primary refuses everything the baseline gets right; one class up the same population settles completely. |
| `minority_suppression` | `count_decides_survival` | Three attestable majority witnesses asserting the false value against three unattestable witnesses carrying the true one. All six genuinely independent. | AID-1's construction, where the single count settled 720 of 720 against the true claim. The range is expected to refuse instead, and the gap between `attested_bounds` and `attested_point` here is the repair's central claim. |
| | `recorded_kinship_decoy` | **New.** The same six, all genuinely independent, but the majority is device-attested and the minority is recorded as citing one registry and cannot attest. | `_ladder_view` runs the ladder at *admissible* depth, so the policy's discount is applied at the upper end too — the end that is supposed to count independence wherever the record cannot rule it out. Recorded kinship then defeats the minority at both ends at once, the range agrees, and the rule settles against a true claim that the baseline, the theatre arm and refusal all preserve. |
| `mixed_attestation` | `mixed` | One decision holding an artifact-attested pair on a hidden source, a recorded-ancestry pair sharing a marker, an unattestable witness, a witness that states no depth at all, and a device-attested witness. | A rule that only works when every witness is attested or none is. The `UNSTATED` witness is the one place `lower` and `upper` disagree per witness rather than per pair. |
| | `interior_disagreement` | **New.** Two device-attested copies of one source and two unattestable witnesses on the false side; one device-attested and two unattestable witnesses on the true side. | The rule *as the specification words it*. It reads the diagonal corners `(lower, lower)` and `(upper, upper)`; the box is bounded by the other two corners. Here the true side ranges over 1..3 and the false side over 2..4, both read corners settle false, and `(3, 2)` settles true. The rule settles anyway, and settles wrongly. |

Each witness carries its own recorded lineage token, so no observation is
unattributed and the record is never trivially non-robust. What the record does
not carry is any token connecting two witnesses of one hidden source. That is
DR3's case and it is what makes the baseline's false settlements silent.

## 6. Construction choices made against the policy, and why

These are the places where section 5 left a choice. Each was made so the primary
could lose, and each is stated here rather than discovered later.

1. **The unattestable are genuinely unattestable.** In `nobody_can_attest`, for
   the minority in both `minority_suppression` variants, and for the honest
   witnesses in the two new device-attested strains, `attestable` is `False`, so
   no adoption rate reaches them. A world in which every witness becomes attested
   at `alpha = 1.0` would have no cost to measure at full adoption, which is the
   cell criteria 2 and 6 are stated on.
2. **The three AID-1 adversary strains are kept although two of them are now
   dead.** `declares_completeness` and `claims_bonded_identity` existed to
   exhibit the two defects AID-1 disclosed, both since repaired. Deleting them
   would leave the repair unmeasured in the successor; keeping them costs two
   variants and turns the repair's own claim into a protocol test.
3. **The device-attested strains are new and are the point of this world.**
   AID-1's world could not make the primary lose, because at every depth the
   policy discounted, the two ends of the range diverged and the rule refused —
   which is safe. A range is dangerous where it is *narrow* and wrong. The only
   way to narrow it is to give the adversary the backing the policy honours, so
   three variants do exactly that. This is the single largest departure from
   AID-1's world and it is deliberate.
4. **`baseline_already_right` is deliberately left at one variant.** A
   device-attested variant would let the primary settle everything in half of the
   family and refuse everything in the other half, putting a frozen criterion on
   a knife edge whose position is a property of my variant mix rather than of the
   policy. Criterion 6 is instead answered across the three error classes, which
   already span the case where attestation reaches the depth the class requires
   and the case where it cannot. The family stays as AID-1 built it.
5. **The recorded kinship in `recorded_kinship_decoy` and
   `device_attested_fabricator` is a decoy, and a protocol test asserts it.** No
   two witnesses sharing a recorded ancestry token in those variants share a
   causal unit. Recorded shared ancestry is not proof of dependence — that is
   precisely why the ladder applies a divergence test rather than merging — so a
   world in which every recorded kinship were real would be testing nothing.
6. **The minority decision is called with `Use.PERMIT_ACTION`.** The point arm
   raises `ScopeViolation` on `Use.DECIDE_SURVIVAL`, and a protocol test pins
   that it still does. AID-1 established that the guard cannot hold, because the
   use is caller-declared. Scoring the family through the declared-forbidden
   path would test the assertion rather than the scope.
7. **`TRANSCRIPTION` is kept as a cell.** At the bottom error class every
   admissible depth clears the divergence test, the two ends of the range
   coincide, and every arm is identical by construction. Dropping it would
   overstate the price; keeping it bounds the claim, and it is the control that
   distinguishes a rule that refuses *because the evidence is thin* from one that
   refuses always.
8. **The ladder places an unstated claim at `TEXT`.** The legacy ladder has no
   `UNSTATED` rung. Reading a witness that says nothing as hearsay is the default
   the policy exists to refuse, so the baseline must make it.

## 7. Criteria, copied verbatim from section 6 of the frozen spec

> Scored on reversible decisions. Powered cells only, Holm-corrected across
> arms, fail closed when underpowered. Two executions must be semantically
> identical.
>
> **The primary is supported only if all hold:**
>
> 1. **It prevents what it exists to prevent.** In every powered cell of the
>    hidden-source family, at least 40% of the baseline's margin-critical silent
>    false settlements are prevented.
> 2. **Cost is bounded by benefit, where benefit is possible.** At `α = 1.0`,
>    correct settlements lost do not exceed silent false settlements prevented,
>    in every family where the baseline makes at least one margin-critical silent
>    false settlement. Where it makes none, cost is reported and is not a pass
>    mark.
> 3. **It is not theatre.** `attested_declared_only` does materially worse than
>    the primary in the freely-attesting family, in cells where the arms can
>    differ at all.
> 4. **It is not worse than refusing.** Strictly more correct settlements than
>    `refuse_all_unrecorded`, with margin-critical prevention no more than 10
>    percentage points below refusal's, in every powered cell.
> 5. **It does not suppress.** In the minority-suppression family, the true
>    contrary claim survives at least as often as under the baseline, in every
>    cell. Any loss fails the experiment outright, whatever else holds.
> 6. **It is not refusal with extra steps.** In `baseline_already_right` at
>    `α = 1.0`, the primary settles at least half of what the baseline settles. A
>    rule that refuses whenever the range is wide fails here, and should.
>
> **Reported, not criteria:** the adoption curve; the gap between
> `attested_bounds` and `attested_point`; and the share of decisions where the
> two ends of the range disagreed.

Nothing above is renumbered, softened or added to. The verdict is `supported`
only if every check passes; otherwise it is `not supported`.

## 8. Operationalisation, where section 6 gave no number

Four phrases in section 6 are not numbers and had to be made computable. All are
recorded here, before execution, and none may move afterwards.

- **"margin-critical"** — a decision where the true causal grouping decides the
  answer: `settlement_over_units` over the true units differs from the same
  settlement with every witness counted separately. Computed in `world.py`, so
  the world and the scoring cannot drift apart.
- **"silent"** — a false settlement that the recorded ancestry alone settles the
  same way, by `assess_dependence_robustness`. Where the record shows possible
  dependence, the settlement is flagged instead and somebody could have looked.
- **"materially worse"** (criterion 3) — `attested_declared_only` makes strictly
  more silent false settlements than the primary, the McNemar difference is
  significant after Holm correction at `familywise_alpha`, and the excess is at
  least `theatre_margin = 0.10` of the baseline's silent false settlements in
  that family. Identical to AID-1's reading, so it is not a new choice.
- **"in cells where the arms can differ at all"** (criterion 3) — computed from
  the world rather than asserted: a cell qualifies when at least one reversible
  decision in it produces different terminals under different arms. AID-1 found
  criterion 3 unmeasurable at `TRANSCRIPTION` for exactly this reason and the
  spec repaired the criterion in advance; this is how the repair is applied.
- **"survives at least as often"** (criterion 5) — read as *no loss*: the
  primary's surviving count may not fall below the baseline's in any cell of the
  minority family. Powering is not required; section 6 says any loss fails the
  experiment outright.
- **"settles at least half of what the baseline settles"** (criterion 6) —
  counts *settlements*, correct or not. A rule that refuses everything is what
  the criterion exists to catch; a rule that settles wrongly is caught by
  criteria 1, 2 and 5.
- **"margin-critical prevention no more than 10 percentage points below
  refusal's"** (criterion 4) — each arm's prevention rate is its
  margin-critical silent false settlements prevented over the baseline's
  margin-critical silent false settlements in that cell, which is well defined
  because a powered cell has at least 12 of them.
- **"powered"** — a cell where the baseline makes at least
  `minimum_critical_silent_for_test = 12` margin-critical silent false
  settlements, the DRI-11 threshold. Fail closed: no powered hidden-source cell,
  or no powered freely-attesting cell, is `not supported`.

Holm correction is applied jointly across `attested_bounds`, `attested_point`,
`attested_declared_only` and `refuse_all_unrecorded` in every powered cell, and
across the theatre-versus-primary comparisons, as one family of tests.

## 9. Reused machinery, and one deliberate departure

Reused rather than rebuilt, because a previous experiment in this series
silently dropped machinery from an earlier one:

- `experiments/dri3/world.py` — settlement outcomes (`settlement_over_units`,
  `SETTLED`, the reversible/irreversible classes and their thresholds). The
  reference settlement is DRI-3's, unchanged, including its legacy
  `independence_basis` stamp.
- `experiments/dri2/stats.py` — `holm`, `mcnemar_exact`.
- `provenance/dependence_robustness.py` — `settle_counts`, and whether a
  settlement is silent or flagged by the record.
- `provenance/decision_relative.py` — `DecisionEvidence` and the root-vote
  kernel beneath it.
- `canon/independent_set.py` — exact `N_eff`, reached through both independence
  modules rather than reimplemented.
- `experiments/aid1run/world.py` — the generation machinery, the six families
  and their construction, adapted. The arms are new; AID-1's arms asked for a
  point estimate, which is the reason this experiment exists.

**Departure:** `arms.range_settlements` reimplements the monotone corner
argument that `assess_dependence_robustness` already makes, because that
function takes evidence and this one takes a pair of `WitnessBounds`. It is used
for a reported diagnostic only and never substituted for the rule the spec
named; a protocol test pins it against brute force over the whole count box.

## 10. Two defects in the instrument, disclosed before the run

Both were found while building this world, on the development salt, and are
recorded here before the confirmatory salt is touched. Both are properties of the
repaired policy and of the primary method as the specification words it, not of
this world. The run measures the instrument **as specified**; repairing it here
would mean editing the artifact after a world was built to expose its specific
defects, which is the tuning this repository forbids.

1. **`lower` still infers independence from silence, above the depth floor.**
   `independent_for` grants independence to any two witnesses whose admissible
   depth clears the error class and whose recorded ancestries are disjoint. Two
   device-attested copies of one fabricator are exactly that, so the bound that
   the policy describes as counting only independence that was *earned* counts
   them as two. A device attestation earns depth; it says nothing about shared
   origin. This is the A5 defect the policy exists to remove, still present and
   now gated behind a depth check rather than removed.
   Exhibited by `device_attested_fabricator`, `device_attested_echoes` and
   `interior_disagreement`.
2. **`upper` is not the record's permissive reading.** `_ladder_view` runs the
   ladder at *admissible* depth, so a witness whose depth claim the policy
   discounts is discounted at both ends of the range. The record cannot rule out
   that an unbacked `REALITY` claim is true, and the upper bound rules it out
   anyway. Where such witnesses also share a recorded ancestry token, the pair
   collapses at both ends and the range agrees on deleting them.
   Exhibited by `recorded_kinship_decoy`.

A third observation concerns the primary method rather than the policy: the rule
reads the two diagonal corners of the count box and the box is bounded by the
other two, so both ends can agree on a settlement the range does not determine.
Exhibited by `interior_disagreement`, counted as `endsAgreeInteriorDoesNot`, and
reported rather than scored, since section 6 contains no criterion for it.

## 11. What this experiment cannot answer

- Whether attestation is obtainable at all. The census in `experiments/aid1/`
  found zero records in this estate stating a witness depth. Every adoption rate
  here is synthetic and none of them is a measurement.
- Whether the reference grouping is the right one. It is stipulated by the
  generator.
- Anything about irreversible decisions.
- Whether a different bounds rule would do better. Only the rule section 2 names
  is under test.

## 12. Disclosure

- Written after the policy, the primary method and the criteria were frozen, by
  an author who did not write the policy. Development salt only for construction
  tests. Confirmatory salt named in `EXECUTION-CONFIG.json` and unread; a
  protocol test asserts it is passed to nothing.
- **This is a re-test on a world family whose earlier results are known.** A pass
  here is weaker evidence than AID-1's failure was, and must be reported as such.
- Same control domain. Not A2-independent validation.
- Every rate in this world is stated, not measured.
- No authority claim.
- The construction tests in `tests/test_aid2_protocol.py` pin the six families to
  the cases section 5 asked for, and pin the primary arm to the range rather than
  to a point estimate. Where a construction test disagreed with the world, the
  world was fixed; no criterion was moved.
