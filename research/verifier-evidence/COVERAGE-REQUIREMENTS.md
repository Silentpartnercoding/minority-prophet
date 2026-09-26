# Coverage requirements for completeness claims

These are public research notes on CMP-1 and CMP-2: what a completeness claim
must name and what independent omission-detection basis a deciding verifier
must appraise before reporting completeness as established. An earlier private
review branch omitted them. The current, still-unfiled private review draft,
`draft-he-agentproto-verifier-evidence-00`, includes revised CMP-1/CMP-2 text.
The notes below explain the research boundary; they are not the authoritative
text of that draft, and neither has been submitted to a standards body.

## Provenance, stated accurately

`not_established` appears in this repository's public history on **2026-08-07**
(`f6904c0`) and `unestablished` on **2026-08-25** (`a6572d5`). The distinction
between a check that ran and failed and one that could not run is therefore
dated here before the adjacent drafts.

The requirements below are **not**. `material party`, `revealing mechanism` and
the coverage framing first appear on **2026-09-16** to **2026-09-18**
(`1ba14f7`, `76cd467`) — contemporaneous with
`draft-sergeev-claim-boundaries-00` (2026-09-16), not earlier than it. They were
reached independently, and no claim of priority over that draft is made for
them.

What is not contemporaneous with anything is the composition at the end of
CMP-2, which applies the exercised-check requirement to CMP-2 itself.

---

## CMP-1: Coverage domain

A result claiming completeness over a stated coverage domain, including a claim
of independent observation of that complete domain, MUST name that domain and
the mechanism by which an omission within it would be revealed. Independently
checking one identified artifact does not by itself claim completeness of a
wider event or artifact history.

A result that does not name both does not support a completeness claim, whatever the
number of individually valid artifacts it presents. Validity of disclosed
artifacts is a property of those artifacts and carries no information about
records that were not disclosed.

A record may be absent for more than one reason: it was never created, it was
created but not observed, it was observed but not recorded, or it was recorded
and later removed. CMP-1 requires the revealing mechanism to be named; it does
not require that mechanism to separate these causes. A profile whose mechanism
can separate them SHOULD say which it separates, because a relying party that
must act on the difference cannot infer it from the fact of absence.

## CMP-2: Material-party detection

Where the mechanism that would reveal an omission is operated by a material
party, or its inputs are selected by a material party, that mechanism alone is
same-party regardless of the number of independently valid artifacts presented.
Unless an independent basis has been appraised for this result, the evaluator
MUST NOT report the completeness claim as verified. Lack of an independent
omission-detection basis alone does not establish a violation. A violation of a
separately completed predicate check remains reportable.

A predicate reported as a violation asserts that its check ran and its
condition did not hold. A completeness appraisal left unestablished says the
available record cannot settle whether an omission remains. These are separate
checks and verdicts.

CMP-2 is bounded by what counts as an independent basis. A profile may name a
domain and mechanism under CMP-1 yet still be unable to establish completeness
under CMP-2. An independent basis is a constraint on the record set that was not
under the sole control of a material party when the records were produced:

- an append-only log whose inclusion is witnessed by parties not material to the
  claim;
- a counterparty-held record that must reconcile with the disclosed set; or
- a substrate that cannot produce the effect without emitting a record a
  material party cannot suppress.

Naming an independent basis is necessary but does not establish that it
constrained the record set for this result. Before reporting a completeness
claim as verified, the deciding verifier must establish the basis's authority,
its binding to this result and coverage domain, the extent of its coverage,
and the relevant time, and retain evidence of those checks. A basis for a
different scope or time leaves this result's completeness claim unestablished.

### CMP-2 is itself subject to the exercised-check requirement

A profile in which CMP-2 returns unestablished for **every** result has not
tested CMP-2. It has a check with one reachable outcome, which the exercised
rejection requirement forbids reporting as implemented. A conforming profile
MUST be able to exhibit both a result that CMP-2 leaves unestablished and one
that it does not.

This is the part with no counterpart elsewhere. A coverage requirement that
always fires looks maximally conservative and is in fact untested, and nothing
in a report of its verdicts would reveal that.

---

## Relationship to adjacent work

`draft-sergeev-claim-boundaries-00` (2026-09-16) defines reporting outcomes:
what a verdict should say when evidence does not support the asserted claim,
including *downgrade*, which this work did not have and has adopted — see
[`ADOPTED-EXTERNAL.md`](ADOPTED-EXTERNAL.md).

CMP-1 and CMP-2 do not replace that general reporting vocabulary. They set
conditions for a completeness reading of a particular result: naming the
domain and mechanism does not by itself establish that an independent basis
covered that result. A profile can satisfy one requirement and not the other.

The separation of a detector's independence from its field of view was stated
publicly by Bradley B on the IETF agentproto list on 2026-09-16, and is the
reason `detector_sees_undisclosed` is documented here as a coverage axis
distinct from who operates the detector.

## Status

This note is public research material, not an Internet-Draft submission. The
broader verifier-evidence draft remains private and unfiled. No independent
party has implemented CMP-1 or CMP-2 as specified in that draft, and no
reviewer's comments imply endorsement.
