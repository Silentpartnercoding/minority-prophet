# KL-016 v0.2 — design notes

Not a registration. It explains why v0.2 asks a different question from v0.1,
and why the difference is not a retreat to an easier one.

## v0.1 failed twice, and only one failure was measured

**The measured failure** was ancestry: three of four cases fell below the 50%
threshold, li-crossing at 5.5%. That is recorded in
`AMENDMENT-v0.1-ancestry-threshold.md` and it stopped the experiment.

**The unmeasured failure is worse, and was found while drafting this.** v0.1
asked whether aggregation *preserved a dissenting position* at the cutoff. For
these conjectures **there is usually no published dissent before the
refutation.** Nobody wrote "I believe Hedetniemi is false" in 2018. The dissent
and the refutation arrive in the same paper.

So even with perfect citation data, v0.1 would have measured the preservation of
something that was not there. The endpoint could not move — the same shape as
BL-060's failure, and as `frozen-v3`'s, arriving by a third route. **The ancestry
threshold stopped v0.1 for the less interesting of its two defects.**

Recording this because it is the second time in this programme that a design
error was found by a person asking a question rather than by any check
(`CLAIMS.md` C4), and because a reader who sees only the amendment would
conclude the design was sound and the corpus merely poor.

## What v0.2 asks instead

Not *"was the dissent preserved?"* — there was no dissent. Instead:

> At the moment before a conjecture is resolved, how much of its apparent
> support is independent, and how much descends from other support?

This is the copying-pressure question the programme has always been about, asked
of **real literature** rather than a generated world. It does not require a
dissenter to exist. It requires only a body of citing work and a resolution
date, both of which are present.

## Why the primary endpoint is mechanical, deliberately

The primary measure is the citation graph alone: distinct roots among pre-cutoff
citing works, over the raw count. **No judgement about what any work says.**

KL-014 is blocked because its measure requires human labelling of "the same
underlying observation", and `HRI1-BLOCKER-20260816.md` shows no metadata source
can supply that. Designing a primary endpoint that needs a labeller would
reproduce that blocker in a new experiment. The semantic question — how much
apparent support is *conditional dependence* rather than confirming evidence —
is real and is registered as a **secondary** endpoint with a labelling protocol,
an agreement threshold fixed in advance, and an unassignable path if agreement
fails.

## The distinction the owner asked to have settled

In mathematics, a work citing conjecture `C` may be doing one of two opposite
things:

| | what it is |
|---|---|
| **Confirming evidence** | verifies `C` in cases not previously verified |
| **Conditional dependent** | assumes `C` and derives something else |

A conditional dependent is **not support for `C`**. It is a work derived *from*
`C`. Counting it as support is the citation-as-endorsement error, and it inflates
apparent support with works whose authors took no position at all.

This matters more than copying for these cases. A copied confirmation at least
descends from an observation. A conditional dependent descends from an
*assumption* — so if conditional dependents dominate, the apparent support was
never evidence in the first place, which is a stronger claim than that it was
duplicated.

The primary endpoint does not attempt this classification. The secondary one
does, and reports UNASSIGNABLE rather than guessing if labellers disagree.

## What cannot be fixed, and is disclosed rather than solved

**Every case is known to us because it was resolved.** There is no way to sample
conjectures blind to their resolution, since an unresolved conjecture has no
resolution to compare against. Selection on the outcome is therefore permanent
here.

The consequence is registered: the interesting comparison — do refuted
conjectures show thinner independent support than proved ones? — is
**hypothesis-generating only**, at n=7, with no statistic permitted. Registered
in advance so that a difference cannot later be presented as confirmatory, and
so that no difference is also recorded.

## Why mertens is excluded although it passed

`mertens` (1985, 57.3%) cleared the threshold in v0.1's screening and is **not**
carried into v0.2. Retaining the single case that survived a screen is selecting
on the outcome of that screen. v0.1 is stopped; its case list goes with it.

## Feasibility, checked before freezing

All seven v0.2 cases clear the registered 50% threshold — 56.5% to 62.9%, against
a modern ceiling of 62.6%. See `FEASIBILITY-v0.2-probe.json`, produced by the
same instrument as v0.1's and reproducing v0.1's numbers unchanged on re-run.

The failure of v0.1 was the **era**, not the field. Mathematics is the
best-documented field measured: 62.6% against medicine's 47.6% and psychology's
38.7%.
