"""Authority debt: walk a chain of "who says so" until it reaches something, or does not.

Layer eight of `canon/decomposition.py` asks who or what may declare, transform, or
act on a claim. Answering it once gives a name. Answering it repeatedly gives a
chain, and the chain either terminates in something that carries its own weight or
it does not.

Four terminations carry weight, and they are not equivalent:

    EVIDENCE     an observation of the world
    MECHANISM    a repeatable procedure that can be run again
    JUDGMENT     an accountable person deciding under stated uncertainty
    UNKNOWN      an honest admission that nobody knows

`UNKNOWN` is a *good* termination. A chain that ends in "nobody knows, and we say
so" is sound; what is unsound is a chain that never ends, or one that ends only
because someone senior said so. Deference is the one link that carries no weight
of its own: it borrows from whatever it points at, so a chain of pure deference
borrows from nothing.

Two failures are reported separately because they are different diseases:

    debt        the fraction of the walk that is bare deference
    a loop      the chain eats its own tail and terminates in nothing at all

A loop is not high debt. It is the absence of a foundation, and reporting it as a
percentage would let it average away against sound links. It gets its own field.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Ground(StrEnum):
    """What a link rests on. Only DEFERENCE carries no weight of its own."""

    EVIDENCE = "evidence"
    MECHANISM = "mechanism"
    JUDGMENT = "judgment"
    UNKNOWN = "unknown"
    DEFERENCE = "deference"


#: The four that terminate a walk. UNKNOWN is among them on purpose.
TERMINAL: frozenset[Ground] = frozenset(
    {Ground.EVIDENCE, Ground.MECHANISM, Ground.JUDGMENT, Ground.UNKNOWN}
)


@dataclass(frozen=True)
class Link:
    """One step of "who says so"."""

    name: str
    ground: Ground
    #: Who this defers to. Required for DEFERENCE, forbidden otherwise: a link
    #: that stands on its own has nothing to point at.
    defers_to: str | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if self.ground is Ground.DEFERENCE and not self.defers_to:
            raise ValueError(f"{self.name}: deference must name who it defers to")
        if self.ground is not Ground.DEFERENCE and self.defers_to:
            raise ValueError(
                f"{self.name}: {self.ground} stands on its own and cannot also defer"
            )


@dataclass(frozen=True)
class Walk:
    """The result of following one chain to wherever it goes."""

    path: tuple[str, ...]
    terminated_in: Ground | None       #: None exactly when the walk found a loop
    deference_steps: int
    loop_at: str | None = None
    dangling_at: str | None = None     #: deferred to a name that does not exist

    @property
    def is_loop(self) -> bool:
        return self.loop_at is not None

    @property
    def debt(self) -> float:
        """Fraction of the walk that is bare deference. Never the whole story:
        a loop has debt 1.0, and so does a long chain that does terminate soundly
        at the very end. `is_loop` is what separates them."""
        return self.deference_steps / len(self.path) if self.path else 0.0

    def report(self) -> str:
        head = " -> ".join(self.path)
        if self.is_loop:
            return (f"{head}\n  LOOP at {self.loop_at}: the chain eats its own tail "
                    f"and terminates in nothing. This is not support.")
        if self.dangling_at:
            return (f"{head}\n  DANGLING at {self.dangling_at}: deferred to a name "
                    f"that is not in the chain. Unresolvable, not grounded.")
        return (f"{head}\n  terminates in {self.terminated_in}; "
                f"{self.deference_steps} of {len(self.path)} steps are bare deference "
                f"(debt {self.debt:.0%})")


def walk(chain: dict[str, Link], start: str) -> Walk:
    """Follow deference from `start` until something carries its own weight.

    Returns rather than raises on a loop or a dangling reference: both are
    findings about the chain, and a traversal that throws cannot report them
    alongside the sound part of the walk.
    """
    if start not in chain:
        raise KeyError(f"{start!r} is not in the chain")

    path: list[str] = []
    seen: set[str] = set()
    node = start
    while True:
        if node in seen:
            path.append(node)
            return Walk(tuple(path), None, sum(
                1 for n in path if chain[n].ground is Ground.DEFERENCE), loop_at=node)
        seen.add(node)
        path.append(node)
        link = chain[node]
        if link.ground in TERMINAL:
            return Walk(tuple(path), link.ground,
                        sum(1 for n in path if chain[n].ground is Ground.DEFERENCE))
        nxt = link.defers_to
        if nxt not in chain:
            return Walk(tuple(path), None,
                        sum(1 for n in path if chain[n].ground is Ground.DEFERENCE),
                        dangling_at=nxt)
        node = nxt


__all__ = ["Ground", "Link", "Walk", "walk", "TERMINAL"]
