# AID-1 — preregistration, protocol v1

**Status: FROZEN, protocol v1, 2026-09-17. NOT RUN.** Frozen before any
confirmatory campaign is generated or scored. The policy, the four arms, and
the five support criteria were named in
`research/attested-independence/AID-1-DESIGN-DRAFT.md` before this world
existed. This file is the world and the criterion, written by the adversarial
review, not by the author of the policy.

No confirmatory outcome had been computed when this was frozen. Same control
domain as AID-1-OBS and the closed DRI series. Not independent validation.

## 1. Identifier

AID-1, protocol v1. First confirmatory experiment of the attested-independence
series. Not DRI-12.

## 2. Why this exists

The DRI series closed on a theorem: no rule reading the record can tell
independent evidence from dependence the record does not carry. The adopted
policy refuses to convert that silence into independence. That is sound in
one direction and not free. The spec asked what it costs, and asked someone
other than the policy's author to write the world.

The policy has a hole the spec did not treat as a family of its own. Two
witnesses who tick `ancestry_complete` on an empty ancestry record are
granted independence against every error class, including fabrication.
Backing is not consulted once the box is ticked. A hidden pair that can fill
in a form is then the same object as two honest attesters. At adoption
rate 1 the policy restores the defect it exists to close, while honest
witnesses who cannot produce an artifact stay discounted forever.

## 3. Policy and arms, named before this world

Copied from the spec, not chosen here.

1. **`ladder`** — `canon.proximity.independent_for` unchanged. Baseline.
2. **`attested`** — the adopted policy, at each adoption rate. Primary.
3. **`attested_declared_only`** — declared depth honoured at face value.
   Named as the failure mode to exhibit, not a candidate.
4. **`refuse_all_unrecorded`** — abstain whenever any pair lacks recorded
   shared ancestry. Cost ceiling.

Settlement is an `N_eff` vote against `FABRICATION`, the error a hidden
shared source produces. A side wins when its independent count meets the
threshold and strictly beats the other side; otherwise the decision
abstains. The reference grouping uses true causal units: a hidden pair is
one unit.

Adoption rate `α` is the probability that a witness who *can* fill the form
ticks `ancestry_complete`. Witnesses who cannot attest never tick it.
Adversaries who always attest tick it at every `α`.

## 4. Questions

Copied from the spec:

1. Under adoption rate `α`, what share of decisions the ladder settles
   become unanswerable?
2. Of the settlements lost, what share were correct under the reference
   grouping?
3. In the hidden-source family, how many silent false settlements does the
   policy prevent?
4. Is there an `α` below which the policy costs more correct settlements
   than it prevents false ones?
5. With an adversary free to declare any depth and any completeness, does
   the policy still discount the witnesses it must?

The adoption curve is reported. Naming a preferred `α` after seeing it is
the selection error this programme made twice.

## 5. Scope

Reversible decisions, threshold 2. The policy is applied as
`Use.PERMIT_ACTION` — the use it permits. The minority-suppression family
exists so that applying it there is a measured outcome, not a comment in
the doctrine file.

## 6. Generated worlds

400 campaigns per family, 12 decisions, `α ∈ {0.0, 0.5, 1.0}`.

| Family | What is true | What can fail |
|---|---|---|
| `honest_unattestable` | Five genuine independents who left no artifact, hold no key, and cannot be found | Cost bound. Every lost settlement is a correct one. |
| `hidden_source` | Two copies of one hidden parent, nothing recorded. They fill the same form as the honest attesters, at the same `α`. Layout is two copies plus three independents at threshold 2: collapsing the pair turns a 3–2 settle into a 1–2 settle the other way, not an abstention. | Prevention at every `α`. At `α = 1` the complete-box short-circuit restores independence. At `α = 0` the collapse still acts. |
| `adversary_attests` | The copies always declare `REALITY` and complete ancestry, no backing, no holdable identity | Theatre. `attested_declared_only` must be worse than `attested`. The short-circuit makes them the same. |
| `robust_correct` | Six backed independents, nothing hidden | Reflexive discounting. At `α = 1` the policy should match the ladder. |
| `minority_suppression` | True side is two unattestable witnesses; false side is two backed attesters. Ladder 2–2, abstains | Scope. Settling here deletes the contrary claim. |
| `mixed_attestation` | Attestable, unattestable, and hidden copies in one decision | A rule that only works when everyone is attested or no one is. |

Critical share is measured by collapsing the family's focus group in the
ladder settlement. `honest_unattestable` and `robust_correct` have an empty
focus.

## 7. Scoring

Ladder outcomes are the baseline. Unneeded abstention = abstain when the
reference settled. A hidden-source cell is powered when the ladder makes at
least 12 margin-critical silent false settlements. Holm-corrected across
powered hidden-source cells.

A true contrary claim survives when the decision is not settled against it.

## 8. Success criterion

Fail-closed: no powered hidden-source cell ⇒ not supported.

**The policy is supported only if all hold:**

1. **Prevention.** In every powered cell of `hidden_source`, prevents at
   least 40% of the ladder's margin-critical silent false settlements,
   significantly. Same floor as DRI-9 through DRI-11.
2. **Cost bound.** At `α = 1.0`, in every family and cell, correct
   settlements lost (unneeded abstentions) do not exceed silent false
   settlements prevented.
3. **Not theatre.** In every `adversary_attests` cell, `attested_declared_only`
   has strictly more silent false settlements than `attested`. Equality
   fails. If backing is ornamental, the policy is rejected regardless of
   its other numbers.
4. **Cheaper than refusing.** In every powered hidden-source cell, strictly
   more correct settlements than `refuse_all_unrecorded`, at no worse
   critical prevention.
5. **Does not suppress.** In every `minority_suppression` cell, the true
   contrary claim survives at the same rate as under the ladder. Any loss
   fails the experiment outright.

**Reported, not criteria:** the adoption curve, and the share of decisions
with mixed attestation.

**Kill.** If no adoption rate exists at which the policy prevents more than
it costs, the policy is dead and the remaining option is C: count the
unattested witnesses and publish the exposure.

## 9. Frozen inputs

Pinned by the runner: this protocol, `CONFIRMATORY-CONFIG.json`,
`experiments/aid3run/world.py`, `arms.py`, `scoring.py`,
`aggregation/attested_independence.py`, `aggregation/independence_axes.py`,
`canon/proximity.py`, `canon/independent_set.py`, `experiments/dri2/stats.py`.

## 10. Disclosure

- Written after the DRI series closed and after AID-1-OBS, in response to a
  spec that named the policy and the criteria. Development salt only for
  construction tests. Confirmatory salt unread.
- Rates stated, not measured. Real attestation adoption is unmeasured and
  is not what this experiment establishes.
- Same control domain. Not A2-independent validation.
- No authority claim.
- AID-1-OBS stays observational. This protocol does not restick it.
- The complete-box short-circuit is not an invention of this world. It is
  `aggregation/attested_independence.py` lines 148–149, and
  `tests/test_attested_independence.py` already pins it as intended
  behaviour.
