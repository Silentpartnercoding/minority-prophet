# Rung assignments — the table, filled in

`proximity.py` defines the ladder. `rungs.py` populates it: **24 procedures
across four domains.** This document records what was derivable, what is
genuinely contested, and the one thing that cannot be derived at all.

The earlier claim that rung assignment was "an owner decision" was mostly wrong.
*How far back toward the world did this procedure go* is a question about the
procedure. It has an answer, and deferring it to the owner was work avoidance
dressed as deference.

## What was derivable — 20 of 24

Assigned in `canon/rungs.py` with a one-line rationale each. Representative:

| Procedure | Rung | Why |
|---|---|---|
| original experiment · physical inventory count · witnessed directly | REALITY | The world was consulted |
| independent replication, different method · third-party confirmation · interviewed a primary participant | METHOD | A channel that does not pass through the shared record |
| direct replication, same protocol | REPLICATION | New measurement; a biased protocol biases both runs identically |
| reanalysis from raw data · recalculation from ledgers | RAW | Pipeline redone, measurement inherited |
| reanalysis from published figures · meta-analysis of published effects | ANALYSIS | Only the arithmetic is new |
| citation · wire reprint · narrative review · reliance on a prior auditor | TEXT | Restatement |

Two assignments are worth stating out loud because they are load-bearing and
unwelcome:

**Meta-analysis sits at ANALYSIS, not near the world.** It aggregates numbers
other people produced. A meta-analysis of fifty studies sharing one flawed
instrument inherits the flaw fifty times and reports increased confidence. The
ladder says so structurally.

**Model reasoning over provided context sits at TEXT.** No contact occurred.
Reasoning is not observation. This is the bootstrap, and a ladder that rewarded
it would be worthless.

## The four "contested" entries were not close calls — they were a missing parameter

Owner review resolved all four at once, and the resolution is structural.

**A rung is not a property of a procedure. It is a property of a
`(procedure, proposition)` pair.** The same act reaches different depths
depending on what is being measured:

| Procedure | Proposition is about… | Rung |
|---|---|---|
| retrieved-original-document | the document itself | **REALITY** — the artifact *is* the world for that claim |
| retrieved-original-document | events the document describes | RAW |
| second-model-query | model behaviour | **REALITY** — a model was actually observed |
| second-model-query | reality | TEXT — and correlated, same control domain |
| peer-review | whether process was followed | **METHOD** |
| peer-review | the world | TEXT |
| different-lab-same-protocol | reproducibility of the protocol | **REALITY** |
| different-lab-same-protocol | the world | REPLICATION |

The owner's formulation: *"the original document should be original 1 of 1, but
you can have multiple independent witnesses of it — it depends on the context in
which you're measuring."* Implemented in `canon/targets.py`; undefined
`(procedure, target)` pairs are refused rather than guessed.

## Witnessing and attesting are different axes

The second correction. *"Peer review is NOT a witness, it's a testament — it has
more rigor than someone re-reading the text."*

Both halves are true and the single-axis ladder could express neither. Peer
review adds no observation of the world, and is plainly more than one more
person reading. Same for a second lab: it is replication, and *some action was
taken* by a separate party.

So attestation gets its own axis — NONE, SELF, INTERNAL, INDEPENDENT,
ADVERSARIAL — and the two compose without mixing:

* **Witness depth sets `N_eff`.** How many independent observations exist.
* **Attestation never adds a witness.** It reduces the *margin* required on top
  of `N_eff`, because margin exists to absorb **undetected** dependence (R3),
  and an independent party putting its name on the chain is precisely what makes
  silent laundering less likely.

Two consequences, both pinned as tests:

- **Self-attestation and internal attestation reduce nothing.** Vouching for
  yourself is the bootstrap; vouching from inside the same control domain is
  internal replication. Only a party that could have said otherwise counts.
- **A testament lowers the floor, it never removes it.** Margin saturates at 1
  regardless of how strong the attestation is. No amount of review substitutes
  for having looked.

This also gives adversarial review a formal position it did not have: it is the
strongest attestation, because a party trying to find fault and failing tells
you something a party trying to confirm never can.

## What cannot be derived — retracted

*This section previously claimed one irreducible gap: the false-allow /
false-deny exchange rate, said to be owed by the owner. That was wrong, and
owner review is what showed it. Retracted rather than silently deleted, per
`PROGRAM.md`.*

The argument for a threshold assumed a gate with **two** outcomes. Forced to
answer `allow` or `deny` on every case, something must adjudicate the
undetermined middle, and that something is a preference expressed as a number.

Give the gate a third outcome and the requirement disappears. The owner's
objection — the laws already pin the extremes, the gate can reroute, human
escalation exists, and every case differs — is correct, and together those
remove the need for a threshold entirely.

`canon/precedent.py` implements it:

* **Determined by law, no preference involved.** Bounds not establishable (L8),
  authority expanded (L1), unresolved authenticated conflict (L7), world state
  unverified, or zero independent witnesses against the governing error class →
  `DENY`. These hold on day one against an empty case book.
* **Determined by precedent.** A case that dominates an allowed precedent on
  *every* axis is allowed; a case dominated by a denied precedent on every axis
  is denied. Dominance is a partial order — at least as many witnesses against
  every error class, at least as reversible, no more tail risk, no more loss.
  **Nothing is traded against anything**, because trading off is precisely the
  step that needs a preference. A thousand extra witnesses never buys
  irreversibility.
* **Everything else escalates.** Not guessed.

This is the same borrowing that produced proximate cause. No legislature sets a
numeric threshold for negligence; cases are decided, reasons are recorded, and
the determined region grows. The preference still enters — through decided
cases — but it enters **visibly**, attached to facts, attributed to a person,
and open to being overturned. A number fixed in advance has none of those
properties, and is worse for exactly that reason.

Two honest consequences, both pinned as tests:

* **Cold start.** With no case law, everything undetermined escalates. That is
  correct behaviour rather than a defect.
* **The escalation rate replaces the threshold, and it is measured rather than
  chosen.** If it settles low, the system works. If it settles high, the answer
  is more precedent or better evidence — never a looser number.

One subtlety worth stating: being *worse* than an allowed precedent does not
produce a denial. It produces an escalation. The gate never extrapolates past
what it was actually told.

