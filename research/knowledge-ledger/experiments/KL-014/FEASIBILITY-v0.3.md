# KL-014 v0.3 — feasibility assessment, 2026-08-13

Written after probing OpenAlex under the frozen v0.3 rule, before computing any
endpoint. **Arm A as registered is not assemblable. Arm B is.** The reason is
worth more than the arm was.

## Arm A does not survive contact with the corpus

v0.3 registered arm A as *"multi-lab registered replication reports where the
number of independently executing sites is stated."* The registration assumed
those sites appear as **N separately published claims**.

They do not. A coordinated replication is published as **one work**. Many Labs 2
is a single OpenAlex record — one title, one DOI — containing roughly 125
independently collected samples. The Reproducibility Project: Psychology is one
paper covering 100 replications by different teams.

So the N genuinely independent observations exist **inside one artifact**. The
citation graph sees a single node. There is nothing for a root criterion to
count, and R1 and R2 cannot be distinguished on this corpus because they operate
on relations *between* works.

The corpus is real and findable — 4,432 works match "Many Labs" replication,
492,791 match "registered replication report". The problem is not availability.
It is that the unit of publication is not the unit of observation.

## Why this is the third instance of the same defect

This experiment has now hit the same wall three times, in three different places:

| version | the registered assumption | what was actually true |
|---|---|---|
| v0.1 | claims carry an evidence digest | they do not; it must be constructed, and the construction picks the answer |
| v0.2 | claims cite a resolvable primary source | 56% of verified claims cite none |
| v0.3 | independent observations are separately published claims | a coordinated replication bundles N observations into one work |

Each time the model assumed a mapping from real evidence onto
`World = (parents, assert)` that the world does not supply. **The formalism has
no defined unit.** `formal/lean/` proves theorems about claims; nothing states
what a claim is when the evidence arrives as a 125-sample paper, an unattributed
news item, or a dataset reanalysis.

That is not a defect in any one preregistration. It is the same gap as U1 (root
identity undefined) reaching further than U1 is currently written to reach.
U1 asks when two roots are the same root. This asks a prior question: **what is
one claim?**

## Arm B is assemblable

Works reanalysing one named cohort are separately published and findable —
106,625 works reference UK Biobank. O(p)=1 is defensible from the reuse
statement. Arm B can be run.

But arm B alone cannot validate a criterion. v0.3 says so explicitly: *"Arm A
alone can be passed by a criterion that never merges anything. Arm B is the
counter-test."* The inverse holds equally — **arm B alone is passed by a
criterion that merges everything.** Running it by itself would produce a number
that looks like a result and is not one.

## What is NOT being done

- Arm B is not being run alone and reported as a v0.3 result. That would be
  reporting the half of a two-armed design that survived, which is the failure
  mode the two-armed design exists to prevent.
- Arm A is not being redefined mid-flight to something assemblable. Loosening a
  frozen frame after seeing it fail is retrofitting.
- No endpoint has been computed.

## What a v0.4 would need

A registered **unit-of-claim rule**: what constitutes one claim when a single
publication reports many independent observations. Candidates worth pinning are
the per-sample records some coordinated projects deposit separately, and
independently published replication attempts of one original finding — the
latter needing a separate frame because identifying them is not metadata-only.

Until that rule exists, no citation corpus can test HRI-1, and KL-015 inherits
the block through its declared dependency.
