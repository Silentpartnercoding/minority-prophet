"""The truth spectrum — how far a claim has actually climbed, and what blocks it.

Recorded in the project's private origins record as one of three ideas that never
landed. Eight
levels, from raw state to invariant relationship, from the tea-wheel conversation.
The wheel itself sits at BOUNDED_ONTOLOGY, possibly CALIBRATED, and the value of
saying so is that most things called findings are NAMED_OBSERVATION wearing
MECHANISM's clothes.

**This is not `canon/proximity.py` and the two must not be confused.** Proximity
grades a *witness*: how far back toward the world did this particular re-teller
go. The spectrum grades a *claim*: how much has been established about it by
anyone. A single original experiment is REALITY on the proximity ladder and
OBSERVATION on this one. They are different axes and neither substitutes for the
other.

**Not a score.** The level is the highest rung whose requirement is met *and*
every lower requirement with it, because the ladder is cumulative -- a mechanistic
story for a phenomenon nobody has reproduced is not level six, it is level one
with an unsupported story attached. So there is no averaging and no partial
credit, and `assess` returns the first unmet requirement by name. Anyone who
wants a number can read `level.value`; the reason that is not the only return is
`canon/susceptibility.py`, and the reason *that* exists was called in advance in
this same conversation: escape one scalar and you will invent another.

Climbing is the useful output. A claim that reports "blocked at CALIBRATED because
no second observer has used the vocabulary" has been handed its next experiment.

This module decides nothing. Per `canon/PLACEMENT.md` it reports standing only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Level(IntEnum):
    """Higher is more established. Cumulative: each requires all below it."""

    RAW_STATE = 0                 # the world, whether or not anyone looked
    OBSERVATION = 1               # somebody looked
    NAMED_OBSERVATION = 2         # and wrote it down in words
    BOUNDED_ONTOLOGY = 3          # in a declared vocabulary, so notes can be compared
    CALIBRATED = 4                # and different observers agree using it
    INSTRUMENT_CORRESPONDENCE = 5 # and the labels track something an instrument reads
    MECHANISM = 6                 # and there is an account of why
    INVARIANT = 7                 # and it survives changing the representation


#: What each level requires, in the order it must be satisfied. Phrased as the
#: question a reviewer would ask, so an unmet one reads as an instruction.
REQUIREMENT: dict[Level, str] = {
    Level.OBSERVATION: "somebody observed it",
    Level.NAMED_OBSERVATION: "the observation was recorded in words",
    Level.BOUNDED_ONTOLOGY: "a vocabulary was declared, so two observers can compare notes",
    Level.CALIBRATED: "independent observers applied that vocabulary and agreed",
    Level.INSTRUMENT_CORRESPONDENCE: "the labels were shown to track an instrument reading",
    Level.MECHANISM: "there is a mechanistic account of why it happens",
    Level.INVARIANT: "the conclusion survived a change of representation",
}


@dataclass(frozen=True)
class Support:
    """What has actually been done for a claim. Every field defaults to False,
    because the honest prior for unevidenced work is that it was not done."""

    observed: bool = False
    recorded_in_words: bool = False
    vocabulary_declared: bool = False
    independent_observers_agreed: bool = False
    instrument_correspondence_shown: bool = False
    mechanism_given: bool = False
    survived_representation_change: bool = False

    def met(self, level: Level) -> bool:
        return {
            Level.OBSERVATION: self.observed,
            Level.NAMED_OBSERVATION: self.recorded_in_words,
            Level.BOUNDED_ONTOLOGY: self.vocabulary_declared,
            Level.CALIBRATED: self.independent_observers_agreed,
            Level.INSTRUMENT_CORRESPONDENCE: self.instrument_correspondence_shown,
            Level.MECHANISM: self.mechanism_given,
            Level.INVARIANT: self.survived_representation_change,
        }[level]


@dataclass(frozen=True)
class Standing:
    """Where a claim sits, what stops it climbing, and what was claimed too early."""

    claim: str
    level: Level
    #: The first unmet requirement. Empty only at INVARIANT.
    binding_constraint: str = ""
    next_level: Level | None = None
    #: Requirements satisfied *above* the binding constraint. These are the
    #: dangerous ones: work that has been done and does not count yet, and which
    #: a summary will happily present as though it did.
    claimed_beyond: tuple[str, ...] = ()

    def report(self) -> str:
        lines = [f"{self.claim!r}",
                 f"  level          : {self.level.value} {self.level.name}"]
        if self.binding_constraint:
            lines.append(f"  blocked by     : {self.binding_constraint}")
            lines.append(f"  next           : {self.next_level.name}")
        else:
            lines.append("  nothing further on this ladder")
        if self.claimed_beyond:
            lines.append("  does not count yet, and a summary will imply it does:")
            lines.extend(f"    - {c}" for c in self.claimed_beyond)
        return "\n".join(lines)


def assess(claim: str, support: Support) -> Standing:
    """Place a claim on the ladder. The level is the last consecutively met rung."""
    if not claim:
        raise ValueError("a claim needs a statement to be placed")

    ladder = [lvl for lvl in Level if lvl is not Level.RAW_STATE]
    level = Level.RAW_STATE
    binding: Level | None = None
    for lvl in ladder:
        if support.met(lvl):
            level = lvl
        else:
            binding = lvl
            break

    if binding is None:
        return Standing(claim=claim, level=Level.INVARIANT)

    # Anything satisfied above the break is real work that does not yet count --
    # a mechanism for something two observers have never agreed on, for instance.
    beyond = tuple(
        REQUIREMENT[lvl] for lvl in ladder
        if lvl > binding and support.met(lvl)
    )
    return Standing(
        claim=claim,
        level=level,
        binding_constraint=REQUIREMENT[binding],
        next_level=binding,
        claimed_beyond=beyond,
    )


__all__ = ["Level", "REQUIREMENT", "Support", "Standing", "assess"]
