"""`IndependenceBasis` decomposed into the two axes it was conflating.

`IndependenceBasis` ranks four values on one scale:

    UNKNOWN(0) < INFERRED(1) < DECLARED(2) < ATTESTED(3)

Those four values are not four points on one dimension. They are a diagonal
through a two-dimensional space, and collapsing them onto a single rank produces
comparisons that are not real:

* **ATTESTED vs DECLARED** differ only in *who vouched*. Neither says anything
  about whether anyone went and looked.
* **INFERRED vs the rest** differs only in *how far back toward the world* the
  root reached. It says nothing about who vouched.

Ranking those against each other forces an exchange rate between vouching and
looking, and there is no such rate. The visible consequence is an inversion:

> Under `BASIS_RANK`, a **notarised piece of hearsay** (`ATTESTED`, rank 3)
> outranks an **anonymous eyewitness** (`INFERRED`, rank 1) — a signed statement
> from someone who only read a document beats an unsigned report from someone
> who was in the room.

That is backwards, and no single ordering of four values can fix it, because the
error is the single ordering.

**This module is additive.** `IndependenceBasis`, `BASIS_RANK` and `verdict()`
are untouched, and the wire vocabulary shared byte-for-byte with
`invention_engine.models.IndependenceBasis` is preserved exactly. Decomposition
is offered alongside so callers can migrate deliberately.

The replacement for a total rank is a **partial order**: one root dominates
another only when it is at least as good on *both* axes. Incomparable pairs stay
incomparable rather than being forced into a false ranking — the same
no-trading-off rule the gate uses everywhere else.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, Sequence


class WitnessDepth(IntEnum):
    """How far back toward the world the root actually reached.

    Lower is closer to the world and stronger. `UNSTATED` is not a depth; it
    records that the legacy vocabulary never carried one.
    """

    REALITY = 0       # observed the world
    METHOD = 1        # re-measured by a materially different route
    REPLICATION = 2   # re-measured the same way
    RAW = 3           # recomputed from the raw record
    ANALYSIS = 4      # recomputed from published figures
    TEXT = 5          # read, restated, reasoned over
    UNSTATED = 6      # the source vocabulary did not say


class Attestation(IntEnum):
    """Who vouched, and how disinterested they were."""

    NONE = 0
    SELF = 1          # the source vouches for itself
    INTERNAL = 2      # same organisation or control domain
    INDEPENDENT = 3   # separate party with no stake
    ADVERSARIAL = 4   # a party actively trying to find fault


@dataclass(frozen=True)
class IndependenceAxes:
    """A root's independence, on both axes, with neither implying the other."""

    depth: WitnessDepth
    attestation: Attestation

    def dominates(self, other: "IndependenceAxes") -> bool:
        """Partial order. Never a score.

        Vouching does not buy depth and depth does not buy vouching, so a pair
        that is better on one axis and worse on the other is **incomparable**,
        and the caller must escalate rather than rank them.
        """
        return self.depth <= other.depth and self.attestation >= other.attestation

    def comparable_to(self, other: "IndependenceAxes") -> bool:
        return self.dominates(other) or other.dominates(self)


#: What each legacy value actually pins down, keyed by the wire string so this
#: module has no dependency on `root_vote` -- `root_vote` depends on this one.
#: `UNSTATED` marks the axis the legacy vocabulary was silent about: silence
#: recorded as silence, never defaulted (ASSAYER A5).
DECOMPOSITION: dict[str, IndependenceAxes] = {
    "attested": IndependenceAxes(WitnessDepth.UNSTATED, Attestation.INDEPENDENT),
    "declared": IndependenceAxes(WitnessDepth.UNSTATED, Attestation.SELF),
    "inferred": IndependenceAxes(WitnessDepth.TEXT, Attestation.NONE),
    "unknown": IndependenceAxes(WitnessDepth.UNSTATED, Attestation.NONE),
}


def decompose(basis) -> IndependenceAxes:
    """Lossy by necessity: three of the four legacy values carry no depth."""
    return DECOMPOSITION[getattr(basis, "value", basis)]


def minimal_axes(items: Iterable[IndependenceAxes]) -> tuple[IndependenceAxes, ...]:
    """The **weakest** elements: an antichain, not a single value.

    `weakest_basis` assumes a total order and returns one value. Under a partial
    order there may be several minimal elements that no ordering can rank
    against each other -- an anonymous eyewitness and a notarised hearsay are
    both weakest, in different ways.

    When this returns more than one element, any single "weakest" is a fiction,
    and the honest response is to escalate rather than to pick.
    """
    uniq = list(dict.fromkeys(items))
    return tuple(
        x for i, x in enumerate(uniq)
        if not any(j != i and x.dominates(y) and not y.dominates(x)
                   for j, y in enumerate(uniq))
    )


def weakest_is_well_defined(items: Iterable[IndependenceAxes]) -> bool:
    """False when the evidence set has no single weakest member."""
    return len(minimal_axes(items)) <= 1


def legacy_basis(axes: IndependenceAxes) -> str:
    """Project back onto the wire vocabulary. Lossy in the other direction.

    Depth cannot survive the round trip, because the legacy vocabulary has
    nowhere to put it. Preserved only for interoperability with
    `invention_engine`; new callers should carry both axes.
    """
    if axes.attestation >= Attestation.INDEPENDENT:
        return "attested"
    if axes.attestation >= Attestation.SELF:
        return "declared"
    if axes.depth <= WitnessDepth.TEXT:
        return "inferred"
    return "unknown"


def rank_inversion_witness() -> tuple[IndependenceAxes, IndependenceAxes]:
    """The concrete failure the single rank produces.

    Returns `(notarised_hearsay, anonymous_eyewitness)`. The legacy rank puts
    the first above the second. On the axes they are incomparable, which is the
    truthful answer: one has a better testament, the other actually saw it.
    """
    notarised_hearsay = IndependenceAxes(WitnessDepth.TEXT, Attestation.INDEPENDENT)
    anonymous_eyewitness = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE)
    return notarised_hearsay, anonymous_eyewitness
