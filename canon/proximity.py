"""The proximity ladder — how far back toward the world a witness actually went.

`U1-PROXIMATE-ROOTS.md` established that shared ancestry is cut by an
intervening independent re-derivation. That treated re-derivation as a boolean.
It is not. Re-running the arithmetic in a paper is worth something; it is not
worth what re-running the experiment is worth, and neither is worth what an
independent measurement is worth.

**The currency is contact with the world, not effort.** A year of careful
re-reading buys nothing. A glance at a second thermometer buys a great deal.
Any grading scheme keyed to diligence rewards the wrong thing and is trivially
gamed by anyone willing to look busy.

The chain, from the owner's own Law 9 (`World → Measurement → Interpretation →
Decision`), extended to the point where claims are merely repeated:

    0 REALITY      went to the world independently
    1 METHOD       re-measured, materially different method or instrument
    2 REPLICATION  re-measured, same method and instrument
    3 RAW          recomputed from the raw data
    4 ANALYSIS     recomputed from the published figures
    5 TEXT         re-read, restated, reformatted, summarised

A witness's **re-entry depth** is the lowest rung it actually reached. Two
witnesses **diverge** at the shallowest rung either of them reached
independently -- the deeper the divergence, the more genuinely separate they are.

The consequence that matters: **independence is not a scalar.** It is always
relative to a class of error. Two analysts working from the same published table
are fully independent with respect to arithmetic mistakes and not independent at
all with respect to a miscalibrated instrument. A single "independence score"
hides exactly the distinction that decides whether a claim survives.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable

from canon.independent_set import (
    DEFAULT_BUDGET,
    CountingBudgetExceeded,
    maximum_independent_set_size,
)


class Rung(IntEnum):
    """Lower is closer to the world, and stronger."""

    REALITY = 0
    METHOD = 1
    REPLICATION = 2
    RAW = 3
    ANALYSIS = 4
    TEXT = 5


class ErrorClass(IntEnum):
    """The rung at which each class of error enters the chain.

    An error introduced at rung *r* is invisible to any witness that re-entered
    the chain above *r* -- it was already baked in before they arrived.
    """

    FABRICATION = 0        # the world was never consulted
    SYSTEMATIC_METHOD = 1  # the method itself is biased
    INSTRUMENT = 2         # miscalibration, random measurement error
    PROCESSING = 3         # the pipeline from raw data mangles it
    ANALYSIS = 4           # wrong test, arithmetic slip, coding bug
    TRANSCRIPTION = 5      # a digit changed on the way to the page


@dataclass(frozen=True)
class Source:
    """A witness, with the deepest rung it independently reached."""

    name: str
    reentry: Rung
    ancestry: frozenset[str] = frozenset()
    markers: frozenset[str] = frozenset()


def divergence(a: Source, b: Source) -> Rung:
    """The shallowest rung at which the two paths separate.

    Both must have gone at least as deep as the divergence point for the
    separation to be real, so the divergence is the *worse* of the two
    re-entries -- the numerically larger, shallower rung.
    """
    return Rung(max(a.reentry, b.reentry))


def independent_for(a: Source, b: Source, error: ErrorClass) -> bool:
    """Are `a` and `b` independent with respect to this class of error?

    Only if both re-entered the chain at or below the rung where the error is
    introduced. A shared idiosyncratic marker is decisive regardless -- it is
    direct evidence of copying, and copying defeats any claimed re-entry.
    """
    if a.markers & b.markers:
        return False
    if not (a.ancestry & b.ancestry):
        return True
    return divergence(a, b) <= error


def effective_witnesses_for(
    sources: Iterable[Source],
    error: ErrorClass,
    *,
    budget: int = DEFAULT_BUDGET,
) -> int:
    """`N_eff` against one class of error. There is no error-free `N_eff`.

    Exact or refused: raises ``CountingBudgetExceeded`` rather than
    approximating, because an approximate count is attacker-selectable.
    """
    return maximum_independent_set_size(
        list(sources), lambda a, b: not independent_for(a, b, error), budget=budget
    )


def independence_profile(sources: Iterable[Source]) -> dict[str, int]:
    """`N_eff` against every error class.

    This is the honest report. A claim supported by six witnesses may have six
    independent checks on arithmetic and one on whether the instrument was
    plugged in, and only the profile shows it.
    """
    items = list(sources)
    return {e.name: effective_witnesses_for(items, e) for e in ErrorClass}


def weakest_link(sources: Iterable[Source]) -> tuple[str, int]:
    """The error class the evidence is least defended against."""
    profile = independence_profile(sources)
    name = min(profile, key=lambda k: profile[k])
    return name, profile[name]
