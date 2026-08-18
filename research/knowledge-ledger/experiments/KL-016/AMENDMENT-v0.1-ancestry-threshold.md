# KL-016 amendment v0.1 — the ancestry threshold the frozen spec omitted

`COLLECTION-SPEC-v0.1.json` stops the experiment if pre-cutoff ancestry "cannot
be reconstructed" for three or more of the four refuted cases, and never defines
that numerically. This sidecar registers the missing number. **The frozen spec is
not edited**; it is bound by `COLLECTION-COMMIT-v0.1.txt` and stays byte-identical.

Set by precedent at the owner's instruction, not by fresh judgement. Two
precedents apply and both point the same way.

## Precedent 1 — set the bar where the evidence fails (KL-001)

> "The ceiling is deliberately set where the current evidence fails, rather than
> where it passes, so the endpoint can come out against the intervention."
> — `KL-001/DESIGN-v0.4.md`, on the 15% `cleanRefusalRate` ceiling

The 15% ceiling was set knowing v0.3 had measured 23%, i.e. **knowing it would
fail**. A threshold chosen to be clearable is not a threshold.

## Precedent 2 — a threshold a negative control must fail (BL-060)

> "every declaration must also name a `negativeControl` population where the
> property is absent, and the probe must report *below* the minimum there. A
> probe that cannot distinguish the two is rejected as unfalsifiable."

So the number must separate a population that plainly has the property from one
that plainly lacks it, and be stated in those terms.

## The threshold

> **A case is reconstructable only if at least 50% of the works in its era
> record any ancestry.**

**Derivation, stated independently of which cases it admits.** The method
consumes recorded ancestry to separate copied support from independent support.
A work recording none becomes a root by default. If such works are the
*majority* of a case's era, then the majority of its confirming corpus is roots
by artefact of indexing rather than by evidence, and the root count measures
the index rather than the literature. That is
`KL-014/HRI1-BLOCKER-20260816.md` restated for this corpus: *the missing data is
the phenomenon.* Fifty percent is the point at which the artefact stops being a
minority contaminant and becomes the thing being counted.

**BL-060 separation, checked.** Negative control: mathematics 1910–1918, at
**5.5%** — a population where recorded ancestry is effectively absent. It falls
far below the threshold, as required. Positive control: the modern ceiling,
2005–2015 at **62.6%** — clears it. The threshold distinguishes them, so it is
not unfalsifiable in BL-060's sense.

**KL-001 direction, checked.** The bar is set above three of the four measured
cases. It is set where the evidence fails.

## Disclosed weakness

**This number was derived after the era coverages were measured.** That is the
defect KL-001's ceiling was designed to avoid, and it cannot be fully undone
here — the measurement had to happen before anyone knew a threshold was missing.

Three mitigations, none complete:

1. The rule is stated as a property of the *method's input* (the no-ancestry
   population must not be the majority), not as a property of any case. It would
   read identically had the numbers come out differently.
2. It is the **strict** direction. The incentive ran the other way: a lenient
   threshold would have let the experiment proceed, and this one halts it. A
   number chosen to serve the author would not be this one.
3. Both controls are pre-existing populations, not chosen for this amendment.

A reader who thinks 50% was reverse-engineered should note what it costs, and is
invited to propose a different rule with its own derivation.

## Evaluation of the registered stop rule

| case | era coverage | ≥50%? |
|---|---:|---|
| li-crossing | 5.5% | no |
| polya | 33.9% | no |
| euler-sum-of-powers | 42.6% | no |
| mertens | 57.3% | **yes** |

**Three of four refuted cases fail. The spec's stop rule fires.**

> "If it bites on three or more of the four refuted cases, the experiment is
> reported as unanswerable on this corpus and stops."

### KL-016 v0.1 is therefore reported UNANSWERABLE ON THIS CORPUS, and stops

`stopRule` also forbids the obvious escape: *"The case list is closed at seven.
It is not extended, substituted, or reweighted after any case has been scored."*
No case has been scored, but substituting easier conjectures is precisely what
`invalidationCondition` was written to prevent, and one surviving case is not an
experiment in any event.

## What this is, and is not

**It is a result, not a failure.** The registered condition anticipated exactly
this and fired on measurement rather than after a corpus had been built. It cost
one probe. Compare `frozen-v3`, which was cancelled only after its endpoint had
been shown to read back generator settings.

**It carries a reusable finding**, which is the durable output here: *a
lineage-aware method needs a literature that records lineage, and pre-1980
mathematics does not.* With the field comparison in `FEASIBILITY-v0.1.md`
(medicine 47.6%, psychology 38.7% against mathematics 62.6%) the constraint is
sharper still — **no field measured clears 50% before roughly 1980, and two do
not clear it today.** Any successor corpus must clear this bar first, and that
is now a one-command check rather than an argument.

**It does not retire the question.** Whether root-aware aggregation preserves
dissent that later overturned a consensus is unanswered, not answered
negatively. A corpus that could answer it must record ancestry for a majority of
its confirming literature. No such corpus has been identified.
