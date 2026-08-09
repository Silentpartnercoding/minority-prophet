# KL-001 v0.4 — design notes, resolving BL-061 and BL-062

Not a registration. A registration is frozen and pinned before results exist, and
this document explains why v0.4's cannot be written against the corpora we have.

## The integrity problem that shapes everything below

The v0.3 run is complete and its numbers are known: **1 defective repository
rescued, 3 clean repositories refused certification, 23% of clean repositories
affected.** Any endpoint written now against corpus v2 would be chosen by someone
who has already seen how it comes out.

That is not preregistration. It is model selection wearing preregistration's
clothes, and it is a worse failure than the two it would be fixing, because the
existing defects at least announce themselves in the numbers.

So v0.4 splits in two, and the split is the point:

| | status | corpus | what it can support |
|---|---|---|---|
| **Exploratory re-analysis** | done, below | v1 and v2, already seen | description; hypothesis generation |
| **Confirmatory run** | not yet registered | **frozen-v3, generated after the pin** | a result |

The exploratory figures below are reported as description. They are not evidence
for the intervention and must not be quoted as a finding.

## BL-061 — the endpoint books the benefit and cannot see the cost

The registered primary endpoint is the false-clean rate: the share of *defective*
repositories receiving a clean verdict. It counts defective repositories only. So
when the dual ledger converts a verdict to `not_established`:

- if the repository was defective, the endpoint records an improvement
- if the repository was clean, the endpoint records **nothing at all**

A one-sided endpoint cannot come out against the intervention. The only way to
score badly is to change nothing, and even that reads as neutral.

**Exploratory measurement** (already-seen data, description only):

    corpus v2:  rescued 1 defective  |  refused 3 of 13 clean  (23%)
                trade ratio 1 : 3
    corpus v1:  rescued 0            |  refused 0 of 11 clean   (0%)

Whether 1:3 is a good trade is a judgement, not a measurement, and the honest
reading cuts both ways: `not_established` is arguably the *correct* verdict for
"I could not read part of this repository" even when the repository is clean. It
is a refusal to certify, not a false positive. But a refusal has a cost to whoever
must act on it, and an endpoint that never books that cost is not measuring the
intervention — it is advertising it.

**Proposed for v0.4, to be registered before frozen-v3 exists:**

Two co-primary endpoints, both of which must be satisfied:

1. `falseCleanRate` — strictly lower than the baseline arm.
2. `cleanRefusalRate` — the share of *clean* repositories not certified clean —
   at or below a ceiling **fixed in the registration**.

The ceiling is an owner decision, not a measurement, and it must be set before
frozen-v3 is generated. Setting it after would reintroduce exactly the problem
this section exists to fix. A starting proposal is **10%**, which the v0.3 result
would have failed at 23% — deliberately chosen so the endpoint has teeth rather
than ratifying what already happened.

## BL-062 — the 95%-preservation target cannot fail

The registered target is "preserve 95% of true positives". Both arms run the
identical scanner and differ only in aggregation, so recall is identical **by
construction**, not by result. Measured: 81.7% and 81.7% on v1, 79.3% and 79.3%
on v2 — exactly equal, both times, to the digit.

A target that is satisfied by the structure of the experiment carries no
information. It is the same defect this programme removed from two LIN-000 tests,
and it survived here because a number that comes out at 100% looks like a pass.

**Proposed for v0.4:** retire it as a research endpoint and replace it with an
**invariant assertion**:

    recall(dual) == recall(baseline)      exactly, not within a tolerance

This can fail, for a real and useful reason: if the two arms ever stop sharing a
scanner — through a refactor, a caching bug, or a well-meant "improvement" to one
arm — the identity breaks and the comparison silently stops being a comparison.
That is worth catching. What it is not is evidence that the dual ledger preserves
recall, and v0.4 must not present it as such.

The distinction is the whole lesson: **an assertion that cannot fail is
decoration; the same assertion re-scoped to something that can fail is a
regression test.** The number does not change. The claim it supports does.

## What frozen-v3 must satisfy before v0.4 runs

- generated **after** `PROTOCOL-COMMIT-v0.4.txt` is pinned
- passes `scripts/check_effect_reachability.py` against v0.4's declaration —
  BL-060, now enforced, which v0.2 would have failed
- contains enough clean repositories for `cleanRefusalRate` to have a usable
  denominator. v2's 13 makes the rate move in steps of 7.7 points, so a
  10% ceiling is decided by one repository. This needs stating in the
  registration as a power consideration, or the ceiling is noise.
- multi-defect files, as v2 has, so the taxonomy limitation stays exercised

## Open, and deliberately not resolved here

The defect-class taxonomy remains unregistered. The `(file, kind)` key is
injective on v1 and v2 — 0 of 135 planted defects collide — so recall is not
inflated today, but that is a property of these corpora and not of the metric. A
corpus with two same-kind defects in one file would score 1/1 where the truth is
1/2, silently. frozen-v3 should either avoid the case or register how it is
counted, and the choice belongs in the registration rather than in a generator.
