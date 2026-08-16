# HRI-1 is blocked structurally, not for want of resources

Recorded after four attempts to find a corpus that supplies the ground truth
without human judgement. None can, and the reason is not incidental.

## The question

Does one distinct evidence root correspond to one distinct underlying
observation? Measuring it needs, for some population, an **independent** count
of real observations to compare the system's root count against.

## Why no metadata source can supply it

The over-count lives in exactly one population:

| | works, 2015–2024 |
|---|---:|
| articles | 60,820,558 |
| record **some** ancestry | 32,704,810 |
| record **no** ancestry | 28,115,748 |

A work that records its sources is read as derived. The system sees the
dependency and does not mint a spurious root. **The over-count occurs only among
works that record no ancestry** — and their true ancestry is, definitionally,
absent from the record. That is what "records no ancestry" means.

So the ground truth needed to measure the error is the very data whose absence
*constitutes* the error. **The missing data is the phenomenon.** No metadata
source can close that gap, because any metadata that could close it would, by
existing, remove the case from the population being measured.

## The four routes, and why each fails

| route | why it fails |
|---|---|
| **News corpora** | true observation count is a judgement about text |
| **Multi-lab replications** | the N independent observations are published as **one** work; the citation graph sees one node |
| **Preprint ↔ published pairs** | OpenAlex folds them into one work id, so they were never two roots |
| **Shared-dataset reuse** | if the dataset is cited the work is correctly derived, not a root; if it is not cited we are back to the unrecorded population |

The last row is the argument in miniature: every metadata route either finds the
dependency (in which case there is no error to measure) or does not (in which
case there is no ground truth).

## What this changes

This is not "we lack budget." It is a **property of the measurement**, and it
upgrades the earlier note from a limitation to a result:

> The only instrument that can measure this is one that reads what the metadata
> does not say. That means human judgement, and it means human judgement is not
> a workaround for a missing tool — it is the only possible tool.

It also sharpens what a human study buys. Raters are not being asked to
substitute for automation; they are being asked to **create ground truth that
does not otherwise exist**.

## The smallest study that answers it

- **200 propositions**, each with ≥3 claims, drawn from the unrecorded-ancestry
  population — the only population where the answer can differ from 1.
- **3 raters**, independent, blinded to every `mp-root-v1` identity.
- **Inter-rater floor 0.67**, stop-and-report on failure.
- Endpoint, decision rule, exclusions and blinding are already frozen in
  `preregistration-v0.1.json` and `v0.2.json`; nothing further needs registering.

That is the whole ask. Everything else in KL-014 is built and waiting.

## Until then

`flip_budget` remains publishable as a count of root-set units, which is what it
provably is, and **not** as an operational security budget. The measured bound
stands and is not affected by this: in the copy-dominant regime, over-count
≥ `u × N`, with `u` between 33% (medicine) and 74% (arts and humanities).
