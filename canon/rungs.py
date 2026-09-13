"""Rung assignments — which real procedures reach which depth.

`proximity.py` defines the ladder. This file populates it. The assignment is
mostly *derivable*: "how far back toward the world did this procedure go" is a
question about the procedure, not a matter of taste. Everything derivable is
assigned here so it stops being mistaken for an owner decision.

Entries carry `contested=True` where a competent reviewer could reasonably place
them one rung either way. Those are the only ones needing a signature, and they
must be fixed and published before any sample is drawn (`ASSAYER.md` A3).

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
               "Placed at REPLICATION, not METHOD.",
               contested=True, alternative=Rung.METHOD),
    Assignment("reanalysis-from-raw-data", Rung.RAW,
               "Pipeline redone from the raw record; measurement is inherited."),
    Assignment("reanalysis-from-published-figures", Rung.ANALYSIS,
               "Only the arithmetic is redone."),
    Assignment("meta-analysis-of-published-effects", Rung.ANALYSIS,
               "Aggregation over numbers others produced. No new contact."),
    Assignment("peer-review", Rung.TEXT,
               "Reviewers read. They do not re-measure and rarely recompute.",
               contested=True, alternative=Rung.ANALYSIS),
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
               "evidence, not eyewitness.",
               contested=True, alternative=Rung.METHOD),
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
               "flagged as same-control-domain.",
               contested=True, alternative=None),
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
