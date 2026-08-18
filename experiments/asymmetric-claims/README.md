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
| `false-candidate-vectors.json` | Required admission decisions for seven false-candidate fault classes and two true-candidate controls | **specification only — no implementation under test** |

`tests/test_asymmetric_claims.py` pins both the CE-14 divergence and this file's
structure.

## The three fault kinds, and why the distinction is load-bearing

- **numerical** (FP1–FP4) — the computation is wrong. Not observable from the
  report; only recomputation settles it. Required decision before verification
  is `ESCALATE`, never `REFUSE`. A layer that refuses these is guessing.
- **duplication** (FP5) — the report may be perfectly correct; there is simply
  only one of it. **Copying is not evidence of falsity.** A duplicated candidate
  is collapsed to one root and escalated like any other unverified candidate,
  never refused for being duplicated. Refusing on duplication alone discards a
  genuine lone counterexample, which is the failure this project exists to
  prevent.
- **fabrication** (FP6–FP7) — no observation exists behind the report. Observable
  from the report alone, so `REFUSE`.

That split is the file's main content. Five of the seven fault classes are
caught by recomputation rather than by anything this project contributes, and
saying so is more useful than a score that blurs them together.

## Two things this directory deliberately does not do

**It reports no rate.** Each vector is a named case with a required decision,
scored pass or fail. A percentage over seven authored fault types would be a
fact about which faults were authored. `KL-001/DESIGN-v0.4.md` cancelled
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
