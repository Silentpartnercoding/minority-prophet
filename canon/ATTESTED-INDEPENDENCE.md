# Attested independence — silence never grants independence

**Status: policy, adopted for counting that permits action on reversible
decisions. Its cost is unmeasured and is the subject of
`research/decision-relative-independence/DRI-12-DESIGN-DRAFT.md`.**

Implementation: `aggregation/attested_independence.py`.
Tests: `tests/test_attested_independence.py`.

## The defect this fixes, which is ours

`canon/proximity.py` decides independence like this:

```python
if a.markers & b.markers:
    return False
if not (a.ancestry & b.ancestry):
    return True
return divergence(a, b) <= error
```

The middle line reads "the record shows no shared ancestry" and returns
"independent". That is a **positive claim of absence**, which `ASSAYER.md` A5
forbids in reports and which no part of this system is allowed to make
internally either. It is also the precise shape of the case the whole
decision-relative independence series failed to solve by observation: two
witnesses drawing on one hidden source, with nothing recorded that connects
them, are granted full independence against *every* class of error — including
fabrication, the one that hidden shared source produces.

Ledger DR3 (`no_record_rule_is_immune`) proves that no rule reading the record
can tell that case apart from two genuine independents. The proof does not
license the current answer. Given two indistinguishable possibilities, the code
picks the favourable one and asserts it. The honest move under the same proof is
to fail closed.

## The three available policies

None of them detects anything. Detection is proved impossible; these are
different ways of behaving well while blind.

**A. Unattested witnesses do not earn independence from silence.** Adopted, and
implemented. Absence of recorded shared ancestry counts as evidence of
independence only when someone has attested that the ancestry record is
complete. Otherwise independence must be earned the way the ladder already
earns it everywhere else — by declared re-entry depth that its backing actually
supports.

**B. Margin, not merger.** Require a margin wide enough that an undetected echo
could not have flipped the settlement. This is the existing R3 mechanism, and
`canon/targets.py::required_margin` already lowers that margin for independent
attestation. Policy B is stated here and not implemented, because the owner's
standing decision is that the belief threshold that allows action is settled
later; for now the criterion is on reversible decisions.

**C. Price it.** Accept the blindness, count the unattested witnesses, and
report the exposure as a declared number rather than as silence.
`unattested_exposure` exists for exactly this, and it is what an assay must
publish whenever policy A is *not* applied.

A and C compose: A changes the count, C reports what A had to discount.

## The rule, exactly

For two witnesses and one class of error:

1. A shared idiosyncratic marker is decisive. Not independent. Unchanged — the
   trout still outranks the paperwork.
2. A witness whose admissible depth is `UNSTATED` is independent of nothing. It
   has made no claim about how far it went, and silence is recorded as silence
   rather than defaulted to the bottom rung.
3. Where the record *does* show shared ancestry, the ladder's answer stands:
   independent for this error class when the pair's divergence is at or below
   the rung the error enters at.
4. Where the record shows no shared ancestry:
   - if **both** witnesses have attested that their ancestry record is complete,
     the absence is informative and they are independent;
   - otherwise the absence carries nothing, and the pair must clear the same
     divergence test as in (3).

"Admissible depth" is not the depth claimed. It is
`aggregation.independence_axes.admissible_depth`, already in the repository:
the shallower of what was claimed and what the claim's backing or the witness's
own exposure supports. A bare `REALITY` claim from an unfindable source is
granted `TEXT`, which is what a bare assertion has always been worth. That is
what makes the policy resistant to the obvious attack — declaring depth is free,
so an adversary declares it, and a policy keyed to declarations alone would
reward exactly the witness it needs to discount.

The policy is never more permissive than the ladder. Where the ladder answers
"not independent", so does this. It differs only by refusing to convert silence
into independence, and it is pinned that way by an exhaustive test.

## Where this may be used, and where it must not

`aggregation/independence_axes.py` already contains the argument against
deflating counts, and it is right:

> Undercounting is safe when `N_eff` is used to permit an action and dangerous
> when it is used to refuse one: an adversary who can strip identity from
> evidence deflates the count and suppresses a true claim.

So the policy is scoped, not universal:

- **Permitted:** counting that decides whether to settle and act. Fewer
  witnesses means less action, which is the safe direction.
- **Forbidden:** counting that decides whether a contrary or minority claim
  survives. Stripping attestation from an inconvenient witness must not be a way
  to delete it. Invariant 5 in
  `research/decision-relative-independence/README.md` — minority preservation —
  governs there, and `effective_witness_bounds` remains the honest instrument:
  report the range the record supports and escalate when the answer depends on
  where inside it the truth lies.

A counting call that cannot say which of the two it is doing does not get to use
this policy.

## What it does not do

- It does not detect hidden shared sources. DR3 forbids that, and nothing here
  contradicts it.
- It does not make an unattested witness worthless. The witness still counts
  against transcription errors if it has earned a depth; it simply stops being
  granted independence by the record's silence.
- It does not establish that attestation is obtainable. Whether declared, backed
  depth can be collected from real witnesses without adoption friction or
  self-reporting that destroys its evidentiary value is the fourth kill
  criterion of the decision-relative independence programme, and it is
  unanswered.
- It does not state its own cost. How many decisions become unanswerable under
  this policy is measurable, unmeasured, and specified as the successor
  experiment.
