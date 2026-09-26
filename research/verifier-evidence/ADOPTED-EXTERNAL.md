# Externally originated improvements adopted into this model

This file records ideas taken from outside this programme that are **better than
what we had**, who originated them, and what changed here as a result.

It exists because the alternative — quietly improving and later being unable to
say where a distinction came from — is the provenance failure this repository
studies. A borrowed idea with no named source becomes, within one revision, an
idea that appears to be ours.

Nothing here is a claim that these authors endorse this repository or have
reviewed it. Each entry cites public, dated material.

An entry here means a specific improvement was taken from outside. It does not
mean the surrounding idea originated outside. Where this repository reached
something first, the date is in [`PROVENANCE.md`](../../PROVENANCE.md) and is
stated in the entry.

---

## 1. Independence and completeness are two axes, not one

**Bradley B, IETF agentproto list, 2026-09-16.** Replying to Iman Schrock:

> "Independence constrains who attests. Completeness constrains what they see.
> A detector that is independent of the effecting party, and is fed only what
> that party discloses, satisfies the first and fails the second."

**What we had.** One notion, "same-party evidence", which conflated *who is
looking* with *how much they can see*. Our CMP-2 draft text said a result is
same-party where the revealing mechanism is operated by, or its inputs selected
by, a material party — folding both failures into one verdict.

**Why theirs is better.** The two failures have different repairs. An
independence failure is fixed by changing who attests. A completeness failure is
not: a perfectly independent detector fed a curated set still cannot see an
omission. Collapsing them hides which repair is needed.

**Changed here.** `evaluate_single_use` in `vectors.py` already took
`detector_sees_undisclosed` as a separate parameter from who operates the
detector, which is the right shape by accident rather than by design. The
parameter is now named and documented as the *coverage* axis, distinct from the
independence axis, with this attribution.

---

## 2. Three reporting outcomes, not two

**Mikhail Sergeev, `draft-sergeev-claim-boundaries-00` Section 11, 2026-09-16.**

> **Downgrade to the supportable claim:** "Report the strongest claim on the
> dimension at issue that the evidence does support […] 'Invocation established;
> execution asserted only' is actionable; 'invalid' is not."
>
> **Unsupported:** "The relevant assessment ran over the evidence evaluated, and
> that evidence failed it."
>
> **Not established:** "The assessment did not run, the evidence was not
> available, or the premise was outside the evaluation's scope. […] It does not
> establish the negation of the claim either."

**What we had, and when.** Two outcomes, `unestablished` and `failed`, plus
`established`. `unverifiable` appears in this repository's public history on
**2026-08-05** (`e1403a7`) and `not_established` on **2026-08-07** (`f6904c0`),
six weeks before the draft cited above. The distinction was reached here
independently and is dated in [`PROVENANCE.md`](../../PROVENANCE.md). Nothing
below is an account of learning it from someone else.

**What theirs adds.** A third move we did not have: *downgrade*.
Rather than reporting only that the asserted claim is not supported, report the
strongest claim the evidence **does** support. That is strictly more useful to a
relying party, and it is the difference between a verdict and a diagnosis.

Sergeev also states the reason the split matters in a form worth keeping:

> "Collapsing 'not established' into 'unsupported', or either into 'refuted',
> destroys information a relying party needs: 'we checked and it failed' and 'we
> could not check' call for different decisions."

**Changed here.** `vectors.py` gains `DOWNGRADED` alongside the existing
outcomes, and `evaluate_single_use` returns the strongest supportable claim
rather than only the failure of the asserted one. Tests pin all four outcomes.

---

## 3. A verdict is over a named basis, not over all evidence

**Mikhail Sergeev, agentproto list, 2026-09-17**, on his Section 11:

> "Every record in an evaluated set can verify while records that would have
> changed the outcome were never delivered. A verdict over a named evidence basis
> is a verdict over that basis, not over all evidence that exists."

**What we had.** `EXTERNAL-REPRODUCTIONS.json` requires each entry to state what
it does **not** discharge, which is the same instinct applied to reproductions.
We had no equivalent requirement for a verdict to name the basis it ranged over.

**Changed here.** `results.json` now carries `evidenceBasis` per vector, naming
what the verdict ranged over. Not a large change; it makes the scope of each
result explicit rather than implied by the file it sits in.

---

## What this changed in the draft under review

An earlier private review branch narrowed the proposed Internet-Draft to
exercised rejection and omitted the completeness requirements. It was not
submitted or published as an Internet-Draft. The current, still-unfiled private
review draft, `draft-he-agentproto-verifier-evidence-00`, includes both
EXR-1/EXR-2 and revised CMP-1/CMP-2 requirements.

That inclusion does not claim priority over adjacent work. Bradley B's public
independence-versus-completeness distinction and Mikhail Sergeev's published
reporting vocabulary are attributed above. The revised CMP text addresses a
narrower question: what domain and omission-detection mechanism a completeness
claim names, and what independent basis the deciding verifier actually
appraises for that particular result. It does not make every independently
checked observation a completeness claim or turn an unestablished completeness
claim into a failed predicate check.

The author's draft remains under review. Approval of its private wording does
not file or publish it. No named reviewer is implied to endorse this repository
or the draft.
