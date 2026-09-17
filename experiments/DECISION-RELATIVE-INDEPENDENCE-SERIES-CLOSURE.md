# Decision-relative independence series closure

**Status:** DRI-1A through DRI-11 are complete. The series closes at the
question it was built to answer: whether a rule that reads the record can tell
independent evidence from dependence that the record does not carry.

It closes with an answer, not with exhaustion. The answer is no, it is proved
rather than measured, and the measurements say why every attempt to get around
the proof by observing behaviour also fails.

## Closed question

Can a decision-relative rule, reading a record of evidence, avoid settling
falsely when sources that look separate are not separate — and if the record is
silent, can any observable substitute for it?

## Result chain

1. **Choosing the cut was never established.** DRI-1A tested the declared-policy
   arm with the failure domain *supplied* and did not meet its frozen criterion;
   it is recorded as adverse and non-canonical. DRI-1B, which would test whether
   a system can select the cut from the decision context, is recorded in
   `research/decision-relative-independence/README.md` as not run.
2. **The method survived withholding the failure domain, on its second
   registration.** DRI-2 v1 was rejected on a frozen time criterion; DRI-2 v2
   reran the unchanged method on fresh worlds and was supported.
3. **Robustness over *recorded* dependence works, and is proved.** DRI-3 made
   zero silent and zero irreversible false settlements in six recorded-dependence
   families where the agreement rule settled falsely 780 times. The guarantee is
   now the Lean theorem `robust_settlement_is_true` (ledger DR2).
4. **It degrades exactly as the record degrades.** DRI-4 was rejected on 2 of 67
   checks: with a complete record, zero silent false settlements in every family;
   as true shared identities went missing, 33–87% of silent errors prevented at
   10% missing and 10–26% at 50%, never worse than the old rule, and two powered
   comparisons at 10% missing were not significant.
5. **No rule over the record alone can close that gap.** Ledger DR3,
   `no_record_rule_is_immune`: one record admits two groupings that settle
   differently, so any rule reading only the record is wrong under one of them.
   Everything after DRI-4 is an attempt to find an observable the loss does not
   remove.
6. **Content is not that observable.** DRI-5 was rejected on 4 of 193 checks. An
   exact fingerprint removed every silent false settlement where the lost
   dependence was copying, recovered only partially where it was a shared
   component or origin, and was largely defeated by paraphrasing half the copies.
7. **Asking twice is, where a lookup exists at all.** DRI-6 was supported on all
   77 checks: every silent false settlement came after a look, and confirming a
   second look removed 68–100% of them — at real cost in unneeded abstentions
   against invented dependence. Checking a report against the record caught no
   missed dependence, which is DR3 again.
8. **On an unauthored corpus the record-only check was not inaccurate but
   non-falsifiable.** DRI-7 (exploratory, not canonical) ran the same rules over
   642 production records: record-only accepted 642 of 642, because no input
   present could make it return false.
9. **Intervention reaches what reading cannot, at a price.** DRI-8 was supported
   on all 49 checks and the result is thinner than that sounds: probing prevented
   silent false settlements no record-only rule can prevent, but 0.3–3.5% of the
   baseline's, at 16–468 probes each. Its criterion set no minimum effect, which
   is the lesson it contributed to every successor.
10. **Belief had to override the record before any instrument could matter.**
    DRI-9 rebuilt belief so that a believed group shares one identity at every
    cut, and was rejected 58 of 65: the method named in advance cleared its
    effect floor in 1 of 8 powered cells. A dated post-result note retracts three
    claims made around that result.
11. **A mark is not dependence.** DRI-10, on a world written by the adversarial
    review, rejected bait 28 of 40: it collapsed a shared library that carries no
    shared error (correct settlements 2,830–2,866 → 1,389–2,194, with zero true
    merges) and prevented 0 of 1,005 and 0 of 988 where dependence carried no
    mark.
12. **Corroboration is not independence, and fragility is not evidence.**
    DRI-11 named both methods before the reviewer's world existed and rejected
    both, 66 of 134. Refusal prevented 0 of 925–961 critical errors on trios and
    refused all 2,400 decisions in a family the baseline settles correctly. The
    composite's two signals were satisfied by one shock: 342–439 false merges
    with zero true ones.

## Defensible conclusion

**Behaviour does not separate a shared source from a shared shock.** DRI-11
measured joint-error rates of 0.38–0.42 for genuinely dependent pairs against
**0.58** for an independent pair hit by one external shock: the innocents failed
together more often than the guilty. Every instrument in this series reads some
consequence of dependence — shared content, shared marks, shared timing, shared
errors, fragility of the answer — and each consequence is produced at least as
readily by a common shock, a shared library, or a close vote.

What survives is narrower and sound:

- Settling only on settlements robust to **recorded** possible dependence is
  correct, proved, and cheap (DRI-3, DR1/DR2).
- Where a lookup exists, confirming it with a second look removes most of the
  errors an erring lookup introduces (DRI-6).
- Intervening — planting something upstream and watching for it downstream —
  reaches dependence the record does not carry, at a measured price, and only
  where an upstream can be reached at all (DRI-8).
- Independence is never a scalar. It is relative to a class of error, and the
  proximity ladder reports it that way without weights (`canon/proximity.py`).

## What the series refutes

- That agreement among sources is evidence of their independence.
- That an idiosyncratic mark shared by two sources establishes a shared source.
- That two weak signals agreeing is stronger than one, when a single cause can
  satisfy both.
- That refusing whenever an answer is fragile is a safe default: it is blind to
  groups of three and costs every settlement in a world where answers are close
  and correct.
- That absence of a recorded dependence is evidence of independence. This one is
  a defect in our own code as well as a finding, and it is addressed separately
  in [`canon/ATTESTED-INDEPENDENCE.md`](../canon/ATTESTED-INDEPENDENCE.md).

## Why the series stops here

Not because a kill criterion fired. None of the six in
`research/decision-relative-independence/README.md` has been triggered by a
matched test: no fixed cut matched the decision-relative policy on both false
settlement and abstention, cut selection was never tested without an oracle, and
joint failure domains remain an explicit open limit.

It stops because the question it asked has an answer, and the answer is a
theorem. DR3 says a record carrying no shared identity cannot distinguish
independent observations from copies of one source. DRI-5, DRI-8, DRI-9, DRI-10
and DRI-11 then tried five distinct classes of observable — content, probes,
marks, co-error, and fragility — and each failed in a way the next one could
predict. Adding a sixth instrument to the same list is not a new experiment.

The residue is not an instrument problem. Where dependence is recorded, the
engine already handles it. Where it is not recorded, the only remaining moves are
about **records and incentives**: refuse to count a witness that has not declared
and backed how far it went, require a margin large enough that an undetected echo
could not have flipped the decision, or accept the blindness and price it. Those
are policy, and the first of them is now written down, implemented and tested.

Its cost is unmeasured, and that is the successor chapter:
[`AID-1-DESIGN-DRAFT.md`](../research/attested-independence/AID-1-DESIGN-DRAFT.md)
asks how many decisions become unanswerable when unattested witnesses stop
counting. It is a new chapter, not unfinished evidence from this series.

## What remains open

- Whether declared, backed witness depth can be obtained in real systems without
  adoption friction or self-reporting that destroys its evidentiary value. This
  is the programme's own fourth kill criterion and it is now the live question.
- Whether a system can select the relevant cut from the decision context
  (DRI-1B, not run).
- Joint independence across two cuts at once. Neither the single-cut model here
  nor the per-error-class profile in the canon answers it.
- Whether a common cause of *error* ought to count as dependence at all. DRI-11's
  shocked pair is two units in the reference grouping, so merging them scores as
  error; that is a modelling choice the result raises and does not settle.
- Every rate in this series is synthetic. No real-world frequency of shocks,
  marks, leaks or shared libraries has been measured.

## Canonical records

- `results/dri2-v1/canonical-manifest.json`
- `results/dri2-v2/canonical-manifest.json`
- `results/dri3-v1/canonical-manifest.json`
- `results/dri4-v1/canonical-manifest.json`
- `results/dri5-v1/canonical-manifest.json`
- `results/dri6-v1/canonical-manifest.json`
- `results/dri8-v1/canonical-manifest.json`
- `results/dri9-v1/canonical-manifest.json`
- `results/dri10-v1/canonical-manifest.json`
- `results/dri11-v1/canonical-manifest.json`

Non-canonical and exploratory: `results/dri1a-v1/` (adverse, not canonical),
`experiments/dri7/OBSERVATIONAL-REPORT.md` (exploratory).
