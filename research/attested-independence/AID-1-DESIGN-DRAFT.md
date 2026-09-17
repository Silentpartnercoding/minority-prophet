# AID-1 — what attestation costs

*First experiment of the attested-independence series. It was drafted as
"DRI-12", which was wrong: numbering it into the closed series implies it
inherits that series' question, and it does not. Renamed 2026-09-16, before any
record was enrolled.*

**Status: SPECIFICATION ONLY. No world, no run, no verdict.** The measurement
and its criteria are named here before any world exists, and the world is to be
written by someone other than the author of the policy. That separation is the
only thing that worked in this programme: DRI-9 was built by the instrument's
author and flattered it; DRI-10, written by the review, rejected the same
instrument on the first honest test; DRI-11 rejected both methods named for it.

This is the successor chapter to the decision-relative independence series, not
unfinished evidence from it. See
[`experiments/DECISION-RELATIVE-INDEPENDENCE-SERIES-CLOSURE.md`](../../experiments/DECISION-RELATIVE-INDEPENDENCE-SERIES-CLOSURE.md).

## 1. Why this is a different kind of experiment

Every experiment from DRI-5 to DRI-11 asked the same question: *is there an
observable that reveals dependence the record does not carry?* The answers were
content (no), probes (barely, expensively), marks (no), co-error (no), two
signals agreeing (no), and fragility (no). DR3 says why: the record admits two
groupings, so no rule reading it can choose between them.

AID-1 stops asking for an instrument. The policy in
[`canon/ATTESTED-INDEPENDENCE.md`](../../canon/ATTESTED-INDEPENDENCE.md) does
not detect anything — it refuses to convert the record's silence into
independence. That is provably safe in the direction that matters and obviously
not free. **The only open question about it is its price**, and unlike every
question in the series before it, the price is directly measurable.

## 2. The policy under test, named before the world

Copied from the adopted policy, not chosen here. For two witnesses and an error
class: a shared marker is decisive; a witness with no admissible depth is
independent of nothing; where ancestry is shared the ladder's divergence test
stands; where no ancestry is recorded, the absence counts only if both witnesses
attested that their ancestry record is complete, and otherwise the pair must
clear the same divergence test.

`admissible_depth` is what makes the policy non-trivial: declaring depth is
free, so a declared depth is granted only what its backing or the witness's own
exposure supports.

## 3. Questions

1. **The headline.** Under an attestation adoption rate `α`, what share of
   decisions that the current ladder settles become unanswerable?
2. **Are the lost settlements the right ones?** Of the settlements lost, what
   share were correct under the reference grouping? A policy that only loses
   decisions it was getting wrong is free; one that loses correct ones is
   buying safety with answers.
3. **Does it buy anything where it matters?** In families with a hidden shared
   source and nothing recorded — DR3's case, which no instrument in this series
   touched — how many silent false settlements does it prevent?
4. **What adoption rate is enough?** Is there an `α` below which the policy
   costs more correct settlements than it prevents false ones?
5. **Can it be gamed cheaply?** With an adversary free to declare any depth and
   any completeness, does the policy still discount the witnesses it must?

## 4. Arms

1. `ladder` — `canon.proximity.independent_for` unchanged. Baseline.
2. `attested` — the adopted policy, at each adoption rate.
3. `attested_declared_only` — the same policy with backing ignored, so declared
   depth is honoured at face value. Named in advance as the **failure mode to
   exhibit**, not a candidate: if it performs comparably to `attested`, the
   backing machinery is doing no work and the policy is theatre.
4. `refuse_all_unrecorded` — refuse whenever any pair lacks recorded ancestry.
   The trivially safe upper bound on cost; nothing may be called expensive
   without being compared to it.

## 5. What the world must contain, requested of the adversarial author

The policy must be able to lose:

- **A family where nobody can attest.** Honest witnesses who genuinely went to
  the world but leave no artifact, hold no key, and cannot be found. The policy
  discounts them, and every settlement it loses there is a real cost with no
  corresponding error prevented.
- **A family where the adversary attests freely.** Declared `REALITY`, declared
  complete ancestry, no backing, no identity that can be held. If the policy
  counts these, it is worse than the ladder, because it has added ceremony to
  the same blindness.
- **DR3's case with a real hidden source**, where the current ladder returns
  independent for every error class and settles falsely. This is the only family
  where the policy can prevent anything.
- **A family where the baseline is already right and nothing is hidden**, so a
  policy that discounts reflexively is punished — the trap DRI-10 lacked and
  DRI-11 used to reject refusal.
- **A minority-suppression family.** A true contrary claim carried by
  unattested witnesses, with the count used to decide whether that claim
  survives. The policy is scoped to forbid this use; the world must contain the
  case so that the scope is tested rather than asserted.
- **Mixed attestation within one decision**, since a rule that only works when
  every witness is attested or none is has not been tested at all.

## 6. Criteria, stated before any world exists

Scored on reversible decisions, by the owner's standing scope decision. Powered
cells only, Holm-corrected across arms, fail closed when underpowered. Two
executions must be semantically identical.

**The policy is supported only if all hold:**

1. **It prevents what it exists to prevent.** In every powered cell of the
   hidden-source family, at least 40% of the baseline's margin-critical silent
   false settlements are prevented — the same floor DRI-9 through DRI-11 used,
   so the number is not chosen for this run.
2. **Cost is bounded by benefit.** Correct settlements lost do not exceed silent
   false settlements prevented, in every family and cell, at adoption rate
   `α = 1.0`.
3. **It is not theatre.** `attested_declared_only` must do materially worse than
   `attested` in the freely-attesting family — otherwise the backing is
   ornamental and the policy is rejected regardless of its other numbers.
4. **It is cheaper than refusing.** Strictly more correct settlements than
   `refuse_all_unrecorded`, at no worse prevention, in every powered cell.
5. **It does not suppress.** In the minority-suppression family, the true
   contrary claim survives at the same rate as under the baseline. Any loss here
   fails the experiment outright, whatever the other results, because it is the
   attack the policy's own scope was written to prevent.

**Reported, not criteria:** the adoption curve — cost and prevention at each
`α` — and the share of decisions with mixed attestation. The curve is the
practical output of this experiment and will be tempting to treat as its
result; it is descriptive, and naming a preferred `α` after seeing it would be
the selection error this programme made twice.

## 7. Kill criterion for the policy, and for the chapter

If no adoption rate exists at which the policy prevents more than it costs, the
policy is dead and the honest remaining option is C: count the unattested
witnesses and publish the exposure as a number. That outcome is a result, not a
failure, and it fires the programme's own fourth kill criterion — root metadata
that cannot be obtained without adoption friction or self-reporting that
destroys its evidentiary value.

## 8. Disclosure

- Written after the DRI series closed, by the author of the policy it tests.
  Only a world written by someone else can say whether the criteria above are
  the ones that bite.
- Same control domain either way. Not independent validation.
- Every rate in it will be synthetic. Real attestation adoption is unmeasured
  and is not what this experiment establishes.
- No authority claim.
