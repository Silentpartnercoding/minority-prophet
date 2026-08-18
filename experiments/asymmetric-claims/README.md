# Asymmetric claims

A universal claim — *every* member of a scope has property P — is falsified by
**one** counterexample, whatever the confirming count. This directory holds the
artifacts for that claim shape, which no experiment in this repository had
previously used.

## Why it needed its own directory

Every synthetic world in the programme is a symmetric binary proposition where
more roots is the right answer. On those worlds a counting aggregator and an
asymmetric rule never disagree, so nothing exercised the difference. Giving the
repository a universal claim to evaluate produced `CE-14` immediately: two
shipped verdict paths, one input, opposite sides.

Reproduce it:

```sh
PYTHONPATH=. python3 audit/ce14_asymmetric_claims.py
```

## What is here

| File | What it is | Status |
|---|---|---|
| `false-candidate-vectors.json` | Required admission decisions for three false-candidate fault classes and two true-candidate controls | **specification only — no implementation under test** |

`tests/test_asymmetric_claims.py` pins both the CE-14 divergence and this file's
structure.

## What is scored, and what was cut

The vectors began as section 6 of a proposed Riemann Hypothesis falsification
benchmark, where search agents evaluated zeta numerically and seven fault classes
described how a candidate counterexample could be bogus.

Four of them — wrong precision, cancellation, truncation, drift — are faults in
*that computation*. They are caught by recomputing the result correctly, which is
a verifier's job, and this repository contains no numerical verifier and plans
none. **A vector specifying required behaviour for a subsystem that does not
exist cannot pass or fail, so it is not a test.** They are recorded under
`droppedClasses` with their reason rather than deleted, and would return as
verifier conformance vectors in that component if it is ever built.

Three survive, because the evidence layer can decide them from the report alone:

- **duplication** (FP5) — the report may be perfectly correct; there is simply
  only one of it. **Copying is not evidence of falsity.** A duplicated candidate
  is collapsed to one root and escalated like any other unverified candidate,
  never refused for being duplicated. Refusing on duplication alone discards a
  genuine lone counterexample, which is the failure this project exists to
  prevent.
- **fabrication** (FP6, FP7) — no observation exists behind the report. Either no
  reproducible artifact is attached (FP6), or the record's own digest does not
  bind the values it reports (FP7). Both are `REFUSE`.

That distinction is what the four dropped classes were worth: **observability
does not imply refusal.** FP5 is fully observable and must never be refused; FP6
and FP7 are observable and must always be. Getting this backwards was a real
error during construction, caught by the suite rather than by review.

## Two things this directory deliberately does not do

**It reports no rate.** Each vector is a named case with a required decision,
scored pass or fail. A percentage over a handful of authored fault types would
be a fact about which faults were authored. `KL-001/DESIGN-v0.4.md` cancelled
`frozen-v3` for exactly that — *"the rates were not measured; they were chosen
and read back"* — and the reasoning transfers unchanged.

**It does not claim copy discounting helps here.** Measured, in
`test_ce14_copy_collapse_cannot_reach_an_absence_conclusion`: one record and
twenty records of the same opposing root produce the identical conclusion,
differing only in `repeatedRecordsCollapsed`. The absence rule never reads the
margin, so the repository's central mechanism is **inert** on this claim shape.
That is a scope statement, not a defect — but a benchmark built on universal
claims cannot exercise copy discounting through the verdict, and must not be
presented as though it does.
