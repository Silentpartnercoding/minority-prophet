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

Failures are reported separately because they are different diseases:

    debt        the fraction of the walk that is deference of any kind
    a loop      the chain eats its own tail and terminates in nothing at all

A loop is not high debt. It is the absence of a foundation, and reporting it as a
percentage would let it average away against sound links. It gets its own field.

## Which authority is being borrowed

The project's private origins record carries a guard from the conversation that
produced this module
which the first version stated in prose and did not enforce. **The conclusion is not
that everyone is clueless.** Institutions accumulate expertise, procedure and
collective memory that no individual has, so institutional competence and individual
omniscience are different things. The failure is *coordination* authority being
mistaken for *epistemic* authority, not the existence of authority.

Treating every deference as equally weightless gets this backwards twice over.

A clinician deferring to a guideline that is itself grounded in trials walks
`clinician -> guideline -> trials`, terminates in EVIDENCE, and reports two thirds
bare deference. The number says disease and the chain is healthy: those deferences
borrowed from something real and the walk proves it by reaching it.

The inverse is worse. A chain of pure title-deference that bottoms out in a senior
person's opinion terminates in JUDGMENT, which is terminal, and reports as sound —
the exact thing the paragraph above calls unsound.

Neither can be fixed by looking at the shape of the chain, which is all `walk` sees.
Loops and dangling references are structural. *What kind of authority a link borrows*
is a fact about the link, and has to be declared:

    EPISTEMIC     claims to know something
    COORDINATION  claims to decide who may act

So `Authority` is a second axis on a deferring link, and JUDGMENT must name who is
accountable. Then three things become checkable rather than assertable:

  * **Borrowed competence.** Epistemic deference on a walk that does reach ground is
    not bare — it borrowed, and the borrowing is honoured. Those steps are named in
    the report so the discount is auditable rather than silent.
  * **Mistaken authority.** Coordination authority appearing in a chain about what is
    *true* is the named failure. It is never discounted, and it is reported on its own
    field rather than folded into a percentage, for the same reason a loop is.
  * **Ungrounded judgment.** JUDGMENT that names nobody accountable does not terminate
    the walk soundly. "Someone senior said so" stops being a valid foundation.

Undeclared deference stays bare. The honest prior for a link that does not say what
it is borrowing is that it is borrowing nothing, and a guard that defaults to
generous would be worth less than no guard.

Deliberately no legitimacy score. `canon/susceptibility.py` refuses an aggregate for
the reason this corpus keeps rediscovering: replacing one number with another rebuilds
the black box under a new name. `debt` is retained unchanged as "how much of this walk
was deference"; `bare_debt` is "how much of it borrowed from nothing"; and the two
findings that are not fractions at all keep their own fields.
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


class Authority(StrEnum):
    """What kind of authority a deference borrows.

    A title changes who is allowed to act. It does not change the truth value of a
    proposition, and the whole point of this enum is that the two cannot be written
    down as the same thing.
    """

    EPISTEMIC = "epistemic"        # claims to know
    COORDINATION = "coordination"  # claims to decide who may act


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
    #: What kind of authority is being borrowed. Optional, and its absence is a
    #: finding rather than a default: undeclared deference is treated as bare.
    defers_as: Authority | None = None
    #: For JUDGMENT only: who is accountable, and under what stated uncertainty.
    #: A judgment naming nobody is seniority, not a foundation.
    accountable: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        if self.ground is Ground.DEFERENCE and not self.defers_to:
            raise ValueError(f"{self.name}: deference must name who it defers to")
        if self.ground is not Ground.DEFERENCE and self.defers_to:
            raise ValueError(
                f"{self.name}: {self.ground} stands on its own and cannot also defer"
            )
        if self.defers_as is not None and self.ground is not Ground.DEFERENCE:
            raise ValueError(
                f"{self.name}: only a deference borrows authority; "
                f"{self.ground} carries its own"
            )
        if self.accountable and self.ground is not Ground.JUDGMENT:
            raise ValueError(
                f"{self.name}: accountability is what makes a JUDGMENT terminal "
                f"and means nothing on {self.ground}"
            )


@dataclass(frozen=True)
class Walk:
    """The result of following one chain to wherever it goes."""

    path: tuple[str, ...]
    terminated_in: Ground | None       #: None exactly when the walk found a loop
    deference_steps: int
    loop_at: str | None = None
    dangling_at: str | None = None     #: deferred to a name that does not exist
    #: Deferences to coordination authority: a title standing in for a reason.
    #: Its own field, never averaged into a percentage.
    mistaken_authority: tuple[str, ...] = ()
    #: Terminated in JUDGMENT that named nobody accountable.
    ungrounded_judgment: str | None = None
    #: Epistemic deferences that the walk went on to ground. Named so the discount
    #: below is auditable instead of silent.
    borrowed_competence: tuple[str, ...] = ()
    #: Deferences that never said what they were borrowing.
    undeclared_deference: tuple[str, ...] = ()

    @property
    def is_loop(self) -> bool:
        return self.loop_at is not None

    @property
    def is_grounded(self) -> bool:
        """Whether the walk reached something that carries its own weight.

        A JUDGMENT naming nobody accountable does not, which is the guard: a chain
        that ends only because someone senior said so has not ended.
        """
        return (
            self.terminated_in is not None
            and not self.is_loop
            and self.dangling_at is None
            and self.ungrounded_judgment is None
        )

    @property
    def debt(self) -> float:
        """Fraction of the walk that is deference of any kind. Never the whole story:
        a loop has debt 1.0, and so does a long chain that does terminate soundly
        at the very end. `is_loop` is what separates them."""
        return self.deference_steps / len(self.path) if self.path else 0.0

    @property
    def bare_debt(self) -> float:
        """Fraction of the walk that borrowed from nothing.

        The difference from `debt` is the guard. Deference to declared competence on
        a walk that reaches ground has borrowed from something real and is not
        counted here; deference to coordination authority, and deference that never
        said what it was borrowing, are.
        """
        if not self.path:
            return 0.0
        bare = self.deference_steps - len(self.borrowed_competence)
        return bare / len(self.path)

    def report(self) -> str:
        head = " -> ".join(self.path)
        if self.is_loop:
            return (f"{head}\n  LOOP at {self.loop_at}: the chain eats its own tail "
                    f"and terminates in nothing. This is not support.")
        if self.dangling_at:
            return (f"{head}\n  DANGLING at {self.dangling_at}: deferred to a name "
                    f"that is not in the chain. Unresolvable, not grounded.")

        lines = [head]
        if self.ungrounded_judgment:
            lines.append(
                f"  UNGROUNDED JUDGMENT at {self.ungrounded_judgment}: terminates in "
                f"a judgment that names nobody accountable. That is seniority, not a "
                f"foundation, and the walk is not grounded.")
        else:
            lines.append(
                f"  terminates in {self.terminated_in}; "
                f"{self.deference_steps} of {len(self.path)} steps are deference "
                f"(debt {self.debt:.0%}, bare {self.bare_debt:.0%})")
        if self.mistaken_authority:
            lines.append(
                f"  MISTAKEN AUTHORITY: {', '.join(self.mistaken_authority)} "
                f"borrow authority over who may act and are being read as authority "
                f"over what is true. A title cannot settle a proposition.")
        if self.borrowed_competence:
            lines.append(
                f"  borrowed competence, not counted as bare: "
                f"{', '.join(self.borrowed_competence)} defer to declared expertise "
                f"that this walk goes on to ground.")
        if self.undeclared_deference:
            lines.append(
                f"  undeclared: {', '.join(self.undeclared_deference)} do not say "
                f"what they borrow, and are counted as bare.")
        return "\n".join(lines)


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
            return _finish(chain, path, None, loop_at=node)
        seen.add(node)
        path.append(node)
        link = chain[node]
        if link.ground in TERMINAL:
            return _finish(chain, path, link.ground)
        nxt = link.defers_to
        if nxt not in chain:
            return _finish(chain, path, None, dangling_at=nxt)
        node = nxt


def _finish(
    chain: dict[str, Link],
    path: list[str],
    terminated_in: Ground | None,
    loop_at: str | None = None,
    dangling_at: str | None = None,
) -> Walk:
    """Classify the deferences on a completed walk.

    Separated from the traversal because the classification depends on where the
    walk *ended* — epistemic deference only counts as borrowed once the thing it
    borrowed from has actually been reached.
    """
    deferences = [n for n in path if chain[n].ground is Ground.DEFERENCE]

    last = chain[path[-1]]
    ungrounded_judgment = (
        path[-1]
        if terminated_in is Ground.JUDGMENT and not last.accountable
        else None
    )
    reached_ground = (
        terminated_in is not None
        and loop_at is None
        and dangling_at is None
        and ungrounded_judgment is None
    )

    mistaken = tuple(
        n for n in deferences if chain[n].defers_as is Authority.COORDINATION
    )
    undeclared = tuple(n for n in deferences if chain[n].defers_as is None)
    # Epistemic deference is only *borrowed* competence if the walk went on to
    # reach something. A chain that promises expertise and never arrives at it has
    # borrowed nothing, so the discount is withheld rather than given on trust.
    borrowed = tuple(
        n for n in deferences if chain[n].defers_as is Authority.EPISTEMIC
    ) if reached_ground else ()

    return Walk(
        path=tuple(path),
        terminated_in=terminated_in,
        deference_steps=len(deferences),
        loop_at=loop_at,
        dangling_at=dangling_at,
        mistaken_authority=mistaken,
        ungrounded_judgment=ungrounded_judgment,
        borrowed_competence=borrowed,
        undeclared_deference=undeclared,
    )


__all__ = ["Ground", "Authority", "Link", "Walk", "walk", "TERMINAL"]
