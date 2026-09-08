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

## What is genuinely contested — 4 of 24

These are close calls where a competent reviewer could place them one rung
either way. They need a signature, and under `ASSAYER.md` A3 the signature must
land *before* any sample is drawn.

**1. `different-lab-same-protocol` — REPLICATION or METHOD?**
Assigned REPLICATION: changing who runs a protocol does not change the
protocol, and a biased protocol is biased in both labs. The case for METHOD is
that labs differ in unrecorded ways — reagents, calibration, local practice —
which sometimes does break systematic error. *Assigned conservatively.*

**2. `peer-review` — TEXT or ANALYSIS?**
Assigned TEXT: reviewers read, they do not re-measure, and they usually do not
recompute. The case for ANALYSIS is reviewers who genuinely check the
arithmetic. Consequential, because it decides whether peer review adds
independent witnesses or none. *Assigned conservatively, and it is the entry
most likely to be argued with in public.*

**3. `retrieved-original-document` — RAW or METHOD?**
Assigned RAW: obtaining the original record goes back past the summaries but
does not observe the world. Best-evidence, not eyewitness. The case for METHOD
is that retrieval through an independent archive is a genuinely separate channel.

**4. `second-model-reviewing-first-model` — TEXT or off-ladder?**
Assigned TEXT *and* flagged same-control-domain. The argument for off-ladder is
that it is worse than uninformative: overlapping training data means shared
priors, so two models agree *confidently on their shared errors*. That is
positive correlation, not absence of information, and the ladder's floor may not
be low enough to express it.

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
