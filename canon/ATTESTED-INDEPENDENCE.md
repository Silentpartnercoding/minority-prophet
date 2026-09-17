# Attested independence — silence never grants independence

**Status: policy, adopted for counting that permits action on reversible
decisions. Its cost is unmeasured and is the subject of
`research/attested-independence/AID-1-DESIGN-DRAFT.md`.**

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
4. Where the record shows no shared ancestry, **the absence carries nothing**
   and the pair must clear the same divergence test as in (3).

**Revised 2026-09-17 after AID-1.** Rule 4 previously granted independence when
both witnesses attested that their ancestry record was complete. That was
wrong, and the experiment measured how wrong: an adversary that simply said the
words was granted full independence with no backing at all, while witnesses who
attested completeness in good faith and were mistaken prevented nothing.

The error was conceptual, not clerical. A witness can attest to the path it took
and what backs that. It cannot attest to what it does not know it shares — two
reporters may honestly believe they have no common source while drinking from
one well. Asking for that certificate reinstated the very defect this document
exists to remove: our code used to infer independence from silence in the
record, and taking a witness's word for that silence is the same inference with
the claim moved into someone else's mouth.

Shared origin must therefore be found by comparing witnesses against each other,
or by intervening upstream and watching what comes back. It cannot be obtained
by asking each witness separately about an absence. `ancestry_complete` is still
recorded, because what a party claimed is worth keeping, and it is not honoured.

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

**That scoping failed, and could not have worked.** AID-1 settled 720 of 720
decisions against a true contrary claim carried by unattestable witnesses, with
the guard in place and the caller declaring its purpose honestly the whole time.
A caller deciding whether to act says `PERMIT_ACTION` truthfully while the same
deflated count deletes the claim. No declaration can repair a number that is
wrong in one direction or the other.

The structural replacement is `witness_bounds`, which returns the range the
record supports: a lower bound counting only independence that was earned, and
an upper bound counting independence wherever the record cannot rule it out.
Evaluate the decision at both ends. If it comes out the same way, settle it. If
it differs, the evidence does not determine the decision — refuse and escalate,
rather than choosing the end that suits. A single number cannot serve both a
permit decision and a survival decision, because those require opposite
conservatism, and that is exactly what the experiment demonstrated.

`effective_witnesses_for` remains for callers that genuinely only permit, and
still refuses `DECIDE_SURVIVAL`. It is no longer the honest default; the bounds
are.

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
  unanswered. A census run 2026-09-16 found that no record in this estate stated
  a depth and that no published format had anywhere to put one; the
  vendor-neutral contract was given optional fields for it the same day
  (`contracts/authority-evidence-v0.2`). A slot is a precondition, not an
  answer: the instance count is still zero.
- It does not state its own cost. How many decisions become unanswerable under
  this policy is measurable, unmeasured, and specified as the successor
  experiment.
