# Attested independence — rejected policy record

<!-- mp-status: {"id":"attested-independence-policy","class":"rejected_policy","asOf":"2026-09-18","replacement":"recorded_dependence_robust_settlement","immutable":false,"theorems":["DR3"],"researchRecords":["AID-1-V1","AID-2-V1","AID-3-V1","AID-4-V1"],"describesMechanisms":["attested_independence_point_policy","attested_independence_bounds_policy"],"recommendedMechanisms":["recorded_dependence_robust_settlement"]} -->

**Status: rejected and superseded as policy.** AID-1 through AID-4 rejected
every counting-time policy proposed by this document: attested-depth deflation,
its bounds repair as tested, collapse-robust margin, and priced exposure. The
negative result and the surviving copy-time emission seam are recorded in
[`ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md`](../experiments/ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md).
The implementation remains as hash-pinned research code and is not a recommended
default.

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

## The three policies that were proposed

None of them detects anything. Detection is proved impossible; these are
different attempted ways of behaving while blind. All were later rejected.

**A. Unattested witnesses do not earn independence from silence.** Originally
adopted and implemented; rejected by AID-1 and AID-3. Absence of recorded
shared ancestry counts as evidence of independence only when someone has
attested that the ancestry record is complete. Otherwise independence must be
earned the way the ladder already earns it everywhere else — by declared
re-entry depth that its backing actually supports.

**B. Margin, not merger.** Require a margin wide enough that an undetected echo
could not have flipped the settlement. This is the existing R3 mechanism, and
`canon/targets.py::required_margin` already lowers that margin for independent
attestation. This proposal was later implemented for AID-4 and rejected: it
never vindicated the true minority in the test where the baseline did.

**C. Price it.** Accept the blindness, count the unattested witnesses, and
report the exposure as a declared number rather than as silence.
`unattested_exposure` implemented that proposal. AID-4 rejected it as a warning:
it was a coin flip where powered and anti-correlated when pooled.

A and C were composable in the tested implementation: A changed the count, and
C reported what A discounted. That composition did not rescue either policy.

## The point rule that was tested

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

The tested policy is never more permissive than the ladder. Where the ladder
answers "not independent", so does this. It differs only by refusing to convert
silence into independence, and it is pinned that way by an exhaustive test.

## The original scope and why it failed

`aggregation/independence_axes.py` already contains the argument against
deflating counts, and it is right:

> Undercounting is safe when `N_eff` is used to permit an action and dangerous
> when it is used to refuse one: an adversary who can strip identity from
> evidence deflates the count and suppresses a true claim.

That was the original rationale for scoping the policy, not current permission
to use it:

- **Originally claimed permitted:** counting that decides whether to settle and
  act. Fewer witnesses means less action, which is the safe direction.
- **Originally forbidden:** counting that decides whether a contrary or minority claim
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

The proposed structural replacement was `witness_bounds`, which returns the
range the record supports: a lower bound counting only independence that was
earned, and an upper bound counting independence wherever the record cannot
rule it out.
Evaluate the decision at both ends. If it comes out the same way, settle it. If
it differs, the evidence does not determine the decision — refuse and escalate,
rather than choosing the end that suits. A single number cannot serve both a
permit decision and a survival decision, because those require opposite
conservatism, and that is exactly what AID-1 demonstrated. AID-2 and AID-3 then
rejected the bounds policy as tested: the range repaired the first suppression
case but did not create knowledge of shared origin and retained other harms.
That does not refute the broader requirement to report uncertainty; it does
refute presenting this implementation as a validated decision policy.

`effective_witnesses_for` and `witness_bounds` remain to reproduce and inspect
the experiments. Neither is the canonical default.

## What the experiments did not establish

- It does not detect hidden shared sources. DR3 forbids that, and nothing here
  contradicts it.
- It does not make an unattested witness worthless. The witness still counts
  against transcription errors if it has earned a depth; it simply stops being
  granted independence by the record's silence.
- They do not establish that attestation is obtainable in a real deployment.
  The 2026-09-16 census found no record in the searched corpora stating a depth
  and no searched boundary format able to carry one; the vendor-neutral contract
  then gained optional fields. A slot is a precondition, not adoption evidence.
- They measured synthetic cost, not a real adoption rate or field cost. Those
  measurements were sufficient to reject the proposed policies under their
  frozen criteria, not to estimate a deployment frequency.
