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

## What cannot be derived — and it is exactly one thing

Everything above is a fact about a procedure. This is not:

> **How many independent witnesses, against which class of error, is enough to
> act?**

No amount of analysis produces that number, because it is not a claim about the
world. It is a statement of which mistake you would rather make. Formally, the
**exchange rate between false-allow and false-deny**: how many wrongly-refused
true claims is one wrongly-admitted false claim worth?

That is irreducibly the owner's, and it would be illegitimate for anyone else to
choose it — a verifier that sets its own risk appetite has assumed the authority
of the party it is supposed to be checking.

Three things make it a smaller ask than it sounds:

1. **Its shape is already fixed by the canon.** Law 2 (uncertainty contracts
   authority) and Law 3 (reversibility expands freedom) mean the threshold is
   not one number but a function of stakes: near-zero for cheap reversible
   probes, high for irreversible ones. What is missing is calibration, not
   structure.
2. **It is per error class, not global.** "Two independent checks against
   analysis error, one against fabrication" is a complete and usable answer.
3. **It must be published before the sample** (`A3`), which means it is written
   once and then constrains everything, rather than being renegotiated per case.

## Status

Table populated. Four contested entries assigned conservatively and flagged for
signature. One genuine gap, which is a preference rather than a fact and is
therefore not ours to close.

Unknown procedures raise rather than defaulting to TEXT: an unassigned procedure
is a refusal with a stated reason, not a silent downgrade.
