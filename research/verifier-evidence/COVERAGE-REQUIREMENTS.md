# Coverage requirements for a claim of independent observation

Two requirements, CMP-1 and CMP-2, on what a verifier result must name before
it may be read as supporting a claim of independent observation.

They were written for an Internet-Draft and then cut from it, because adjacent
work was published the same week and restating it would have been duplication.
On re-reading, they are not a restatement: the adjacent work defines a reporting
vocabulary, and these are requirements on what a result must name. They are
published here so the work exists, is dated, and can be cited.

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

A result claiming independent observation MUST name the coverage domain over
which completeness is asserted, and MUST name the mechanism by which an omission
within that domain would be revealed.

A result that names neither does not support a completeness claim, whatever the
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
party, or where its inputs are selected by a material party, the result is
same-party regardless of the number of independently valid artifacts it
presents, and the evaluator MUST report the claim as unestablished rather than
as failed.

Unestablished and failed are distinct signals and a relying party acts
differently on each. A claim reported as failed asserts that the check ran and
the condition did not hold. A claim reported as unestablished asserts that the
record cannot settle the question.

CMP-2 is bounded by what counts as an independent basis, and a profile that
cannot state one for any result has not satisfied CMP-1. An independent basis is
a constraint on the record set that was not under the sole control of a material
party when the records were produced:

- an append-only log whose inclusion is witnessed by parties not material to the
  claim;
- a counterparty-held record that must reconcile with the disclosed set; or
- a substrate that cannot produce the effect without emitting a record a
  material party cannot suppress.

Naming one, and stating how a later verifier establishes it held, satisfies
CMP-1 and takes the result out of CMP-2.

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

CMP-1 and CMP-2 are a different kind of statement. They do not define what to
report; they define what a result must name before a completeness reading is
available at all. A profile can satisfy one and not the other.

The separation of a detector's independence from its field of view was stated
publicly by Bradley B on the IETF agentproto list on 2026-09-16, and is the
reason `detector_sees_undisclosed` is documented here as a coverage axis
distinct from who operates the detector.

## Status

Not submitted to any standards body. No independent party has implemented these
requirements or reproduced anything in this file.
