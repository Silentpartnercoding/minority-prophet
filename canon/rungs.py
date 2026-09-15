"""Rung assignments — which real procedures reach which depth.

`proximity.py` defines the ladder. This file populates it. The assignment is
mostly *derivable*: "how far back toward the world did this procedure go" is a
question about the procedure, not a matter of taste. Everything derivable is
assigned here so it stops being mistaken for an owner decision.

Four entries once carried `contested=True`, described as owner decisions awaiting
a signature. **They were not close calls, and none of them needed a signature.**
Owner review resolved all four at once and structurally: *a rung is not a
property of a procedure. It is a property of a `(procedure, proposition)` pair.*
Retrieving the original document is REALITY for a claim about the document and
RAW for a claim about the events it describes; a second lab is REALITY for a
claim about the protocol's reproducibility and REPLICATION for a claim about the
world. That table lives in `canon/targets.py`, which refuses undefined pairs
rather than guessing.

A second axis fell out of the same review: *peer review is not a witness, it is a
testament.* Attestation -- NONE, SELF, INTERNAL, INDEPENDENT, ADVERSARIAL -- is
tracked separately and **never adds a witness**; it lowers the margin required on
top of `N_eff`, because margin absorbs undetected dependence and an independent
party signing the chain makes silent laundering less likely.

So `contested` is retained as a field and is now empty. Placements below are the
target-free default; when the proposition is known, `canon/targets.py` governs.

Nothing here sets a threshold. How many independent witnesses are *enough* is
not a fact about a procedure and cannot be derived from one -- see
`RUNG-ASSIGNMENTS.md` §"What cannot be derived".
"""

from __future__ import annotations

from dataclasses import dataclass

from canon.proximity import Rung


@dataclass(frozen=True)
class Assignment:
    procedure: str
    rung: Rung
    rationale: str
    contested: bool = False
    alternative: Rung | None = None


SCIENCE: tuple[Assignment, ...] = (
    Assignment("original-experiment", Rung.REALITY,
               "The world was consulted directly."),
    Assignment("independent-replication-different-method", Rung.METHOD,
               "New instrument or protocol, so systematic method error does not "
               "carry across."),
    Assignment("direct-replication-same-protocol", Rung.REPLICATION,
               "New measurement, but a biased protocol biases both runs "
               "identically."),
    Assignment("different-lab-same-protocol", Rung.REPLICATION,
               "Changing who runs a protocol does not change the protocol. "
               "Placed at REPLICATION, not METHOD. Not contested: the choice was inert, because divergence takes the shallower of two re-entries, so promoting this to METHOD changed no verdict at any error class. REALITY when the proposition is about the protocol -- see canon/targets.py.",
               contested=False),
    Assignment("reanalysis-from-raw-data", Rung.RAW,
               "Pipeline redone from the raw record; measurement is inherited."),
    Assignment("reanalysis-from-published-figures", Rung.ANALYSIS,
               "Only the arithmetic is redone."),
    Assignment("meta-analysis-of-published-effects", Rung.ANALYSIS,
               "Aggregation over numbers others produced. No new contact."),
    Assignment("peer-review", Rung.TEXT,
               "Reviewers read. They do not re-measure and rarely recompute. Not contested: one label covering two procedures. METHOD when the proposition is whether process was followed, TEXT when it is about the world. Its rigour is carried on the attestation axis as INDEPENDENT, not by moving it down the ladder.",
               contested=False),
    Assignment("citation", Rung.TEXT, "Restatement."),
    Assignment("systematic-narrative-review", Rung.TEXT,
               "Summarises published claims."),
)

DOCUMENTARY: tuple[Assignment, ...] = (
    Assignment("witnessed-directly", Rung.REALITY, "Saw it."),
    Assignment("interviewed-primary-participant", Rung.METHOD,
               "A channel to the world that does not pass through the record."),
    Assignment("retrieved-original-document", Rung.RAW,
               "Back to the raw record, but the world was not observed. Best-"
               "evidence, not eyewitness. Not contested: REALITY when the proposition is about the document itself -- the artifact is the world for that claim -- and RAW for events it describes.",
               contested=False),
    Assignment("wire-story-reprint", Rung.TEXT, "Verbatim carriage."),
    Assignment("quoting-another-outlet", Rung.TEXT, "Restatement."),
)

AUDIT: tuple[Assignment, ...] = (
    Assignment("physical-inventory-count", Rung.REALITY, "Counted the things."),
    Assignment("third-party-confirmation", Rung.METHOD,
               "Independent channel outside the entity's own records."),
    Assignment("recalculation-from-ledgers", Rung.RAW,
               "Raw records recomputed; the records themselves are inherited."),
    Assignment("review-of-management-schedule", Rung.ANALYSIS,
               "Management's own summary, rechecked."),
    Assignment("reliance-on-prior-auditor-report", Rung.TEXT, "Hearsay."),
)

AGENTIC: tuple[Assignment, ...] = (
    Assignment("tool-call-observing-live-state", Rung.REALITY,
               "The system state was actually read."),
    Assignment("second-tool-different-provider", Rung.METHOD,
               "Independent path to the same world state."),
    Assignment("model-reasoning-over-given-context", Rung.TEXT,
               "No contact. Reasoning is not observation -- this is the "
               "bootstrap, and the ladder must not reward it."),
    Assignment("second-model-reviewing-first-model", Rung.TEXT,
               "Off-ladder in the dangerous direction: overlapping training "
               "data means shared priors, so agreement is correlated rather "
               "than merely uninformative. Treated as TEXT and additionally "
               "flagged as same-control-domain. Not contested: the line is shared ancestry, not depth. Disjoint training corpora are independent at every error class; an overlapping corpus is independent at none but TRANSCRIPTION. Record the corpus as ancestry and proximity.independent_for answers it.",
               contested=False),
)

ALL: tuple[Assignment, ...] = SCIENCE + DOCUMENTARY + AUDIT + AGENTIC

BY_NAME: dict[str, Assignment] = {a.procedure: a for a in ALL}


def rung_of(procedure: str) -> Rung:
    """Rung for a named procedure. Unknown procedures are refused, not guessed."""
    try:
        return BY_NAME[procedure].rung
    except KeyError:
        raise KeyError(
            f"unassigned procedure {procedure!r}: assign it in canon/rungs.py "
            "and publish before drawing a sample (ASSAYER A3). Unknown != TEXT."
        ) from None


def contested() -> tuple[Assignment, ...]:
    """The assignments that genuinely need an owner signature."""
    return tuple(a for a in ALL if a.contested)
