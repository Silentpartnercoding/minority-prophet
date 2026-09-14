"""Bounded truth — a claim is valid *inside* the system that measured it.

Recorded in `canon/ORIGINS.md` as one of three ideas that never landed. It comes
from the tea-wheel conversation, and the distinction it protects is between
*bounding reality* and *claiming the boundary is reality*. A good boundary says
these distinctions are reproducible within this representation. A bad one says
these are the distinctions that exist.

The failure it exists to catch is silent transport: a result established with one
vocabulary, one instrument and one protocol gets restated somewhere else without
the boundary travelling with it, and nobody notices that the evidence stayed
behind. Nothing about the restatement is dishonest. The sentence is simply doing
work it was never measured to do.

**The default for an untested transport is UNTESTED, never inherited validity.**
That is the whole module. Validity does not propagate by default and must be
re-established in each ontology, which is the same asymmetry `ASSAYER.md` §5
applies to evidence: presence can be shown, absence cannot.

The case worth naming separately is `INEXPRESSIBLE`. The tea wheel's defect was
not that it gave wrong answers -- it was that a tea departing from the expected
trajectory produced *no* evidence rather than contrary evidence, because the
vocabulary had no cell for it. A target ontology that cannot state the claim has
not disagreed with it. Collapsing those two into "not supported" is how a
representation starts controlling the observations it was meant to describe.

Deliberately exposes no score. `canon/susceptibility.py` carries the same refusal
for the same reason: replacing "confidence 0.87" with "portability 0.62" rebuilds
the black box under a new name, and that trap was called in advance in the same
conversation that produced this one.

This module decides nothing. Per `canon/PLACEMENT.md`, Minority Prophet reports
standing and takes no action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Standing(StrEnum):
    """What is known about a claim in a *particular* ontology.

    There is no member meaning "true everywhere". That is the point: the type
    cannot express the thing the module exists to prevent.
    """

    ESTABLISHED = "established"
    #: Different ontology, no evidence either way. The default, and the common case.
    UNTESTED = "untested"
    #: Tested there, and it did not hold.
    CONTRADICTED = "contradicted"
    #: The target vocabulary cannot state the claim, so it produced no evidence.
    #: Not the same as disagreement, and must never be reported as such.
    INEXPRESSIBLE = "inexpressible"


@dataclass(frozen=True)
class Ontology:
    """A declared measurement system: what may be said, with what, and when.

    All three parts matter. Two studies sharing a vocabulary but not an instrument
    are not measuring the same thing, and the tea wheel fused a vocabulary, a
    schedule and a theory while announcing only the first.
    """

    name: str
    #: The terms in which an observation may be recorded. Everything outside this
    #: set is not merely unobserved -- it is unreportable.
    vocabulary: frozenset[str]
    instrument: str = ""
    protocol: str = ""

    def can_express(self, terms: frozenset[str]) -> bool:
        return terms <= self.vocabulary

    def missing(self, terms: frozenset[str]) -> frozenset[str]:
        return terms - self.vocabulary


@dataclass(frozen=True)
class BoundedClaim:
    """A statement, the ontology that established it, and nothing implied beyond."""

    statement: str
    established_in: Ontology
    #: The vocabulary terms the statement actually uses. These are what must exist
    #: in a target ontology for the claim to even be stateable there.
    terms: frozenset[str]
    evidence: str = ""

    def __post_init__(self) -> None:
        if not self.statement:
            raise ValueError("a bounded claim needs a statement")
        if not self.terms:
            raise ValueError(
                "a bounded claim must name the terms it uses; a claim whose "
                "vocabulary is unrecorded cannot be transported honestly, which "
                "is the failure this module exists to prevent"
            )
        unstateable = self.established_in.missing(self.terms)
        if unstateable:
            raise ValueError(
                f"claim uses terms absent from the ontology that supposedly "
                f"established it: {sorted(unstateable)}"
            )


@dataclass(frozen=True)
class Transport:
    """What is known about one claim in one target ontology."""

    claim: BoundedClaim
    target: Ontology
    standing: Standing
    #: Populated for INEXPRESSIBLE: the terms the target cannot state.
    untranslatable: frozenset[str] = frozenset()
    #: What would have to be done to establish the claim in the target.
    what_would_establish: str = ""
    note: str = ""

    @property
    def carries(self) -> bool:
        """One bit, for callers that only need one. Everything above is the reason
        it is not the only thing returned."""
        return self.standing is Standing.ESTABLISHED

    def report(self) -> str:
        head = (f"{self.claim.statement!r}\n"
                f"  established in : {self.claim.established_in.name}\n"
                f"  asked about    : {self.target.name}\n"
                f"  standing       : {self.standing}")
        if self.standing is Standing.INEXPRESSIBLE:
            return (f"{head}\n"
                    f"  untranslatable : {', '.join(sorted(self.untranslatable))}\n"
                    f"  The target cannot state this claim, so it produced no evidence\n"
                    f"  about it. That is not disagreement and must not be reported as\n"
                    f"  such.")
        if self.what_would_establish:
            return f"{head}\n  to establish   : {self.what_would_establish}"
        return head if not self.note else f"{head}\n  note           : {self.note}"


def transport(
    claim: BoundedClaim,
    target: Ontology,
    contradicted_by: str = "",
) -> Transport:
    """Ask what is known about `claim` in `target`. Never generalises.

    `contradicted_by` is supplied only when the claim was actually tested in the
    target and failed. Absence of it means untested, not supported -- the caller
    cannot accidentally pass an empty string and get a supportive answer.
    """
    if target == claim.established_in:
        return Transport(claim, target, Standing.ESTABLISHED,
                         note="same ontology; this is where the evidence is")

    missing = target.missing(claim.terms)
    if missing:
        return Transport(
            claim, target, Standing.INEXPRESSIBLE, untranslatable=missing,
            what_would_establish=(
                f"extend {target.name} to express {', '.join(sorted(missing))}, "
                f"then measure; until then it has no cell for this claim"
            ),
        )

    if contradicted_by:
        return Transport(claim, target, Standing.CONTRADICTED, note=contradicted_by)

    differences = []
    if target.instrument != claim.established_in.instrument:
        differences.append(
            f"instrument ({claim.established_in.instrument or 'unstated'} "
            f"-> {target.instrument or 'unstated'})")
    if target.protocol != claim.established_in.protocol:
        differences.append(
            f"protocol ({claim.established_in.protocol or 'unstated'} "
            f"-> {target.protocol or 'unstated'})")
    what_differs = "; ".join(differences) or "a different declared ontology"

    return Transport(
        claim, target, Standing.UNTESTED,
        what_would_establish=(
            f"re-measure in {target.name}. It is stateable there but was not "
            f"tested there, and {what_differs} separates the two."
        ),
    )


@dataclass(frozen=True)
class Survey:
    """One claim against several ontologies. Reports each; combines none."""

    transports: tuple[Transport, ...] = field(default_factory=tuple)

    @property
    def established_in(self) -> tuple[str, ...]:
        return tuple(t.target.name for t in self.transports if t.carries)

    @property
    def untested_in(self) -> tuple[str, ...]:
        return tuple(t.target.name for t in self.transports
                     if t.standing is Standing.UNTESTED)

    def report(self) -> str:
        return "\n\n".join(t.report() for t in self.transports)


def survey(claim: BoundedClaim, targets: list[Ontology] | tuple[Ontology, ...]) -> Survey:
    """Transport one claim into each target. No aggregate is produced, on purpose."""
    return Survey(tuple(transport(claim, t) for t in targets))


__all__ = [
    "Standing", "Ontology", "BoundedClaim", "Transport", "Survey",
    "transport", "survey",
]
