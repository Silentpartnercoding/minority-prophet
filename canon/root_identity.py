"""U1 — what counts as one evidence root.

The failed approach was to look for an equivalence relation on sources. Ancestry
is transitive and unbounded, so "shares an ancestor" has a transitive closure
that swallows the corpus and drives the effective witness count to 1.

The fix is the doctrine of remoteness borrowed from tort and criminal law.
Cause-in-fact is unbounded; **proximate cause** is a declared cut, and an
intervening independent act (``novus actus interveniens``) breaks the chain.
Two sources sharing an ancestor remain independent witnesses if each
re-established the claim through a channel not passing through that ancestor.

Dependence is therefore a graph relation relative to a proposition, not an
equivalence, and the count is a **maximum independent set**, not a quotient.

Three properties, all pinned by tests:

* it reduces to the quotient count when dependence really is transitive,
* it returns 2 on the ``A—B—C`` path that broke the quotient definition,
* the greedy variant is a sound *lower* bound on the exact count.

The remaining exposure is stated plainly in ``effective_witnesses``: undetected
edges inflate the count. That is not fixed here and is not fixable by counting.
It is what R3 margin sufficiency exists to absorb.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Hashable, Iterable, Sequence


@dataclass(frozen=True)
class Witness:
    """A source asserting a proposition, with its recorded ancestry."""

    name: str
    ancestry: frozenset[str] = frozenset()
    #: idiosyncratic markers -- the trout in the milk. Shared markers are
    #: positive evidence of copying; absence proves nothing (ASSAYER A5).
    markers: frozenset[str] = frozenset()


def shares_ancestry(a: Witness, b: Witness) -> bool:
    """Cause-in-fact. Unbounded, and useless on its own."""
    return bool(a.ancestry & b.ancestry)


def shares_markers(a: Witness, b: Witness) -> bool:
    """Trout test: a shared idiosyncratic error has no innocent explanation."""
    return bool(a.markers & b.markers)


def proximately_dependent(
    a: Witness,
    b: Witness,
    *,
    rederived: Callable[[Witness, Witness], bool] | None = None,
) -> bool:
    """Two witnesses are proximately dependent when they share ancestry **and**
    the chain was not cut by an intervening independent re-derivation.

    A shared marker is treated as decisive: it is direct evidence that no
    re-derivation occurred, whatever the provenance record claims.
    """
    if shares_markers(a, b):
        return True
    if not shares_ancestry(a, b):
        return False
    if rederived is not None and rederived(a, b):
        return False        # novus actus interveniens -- chain cut
    return True


def _independent(group: Sequence[Witness], dep: Callable[[Witness, Witness], bool]) -> bool:
    return not any(dep(x, y) for x, y in combinations(group, 2))


def effective_witnesses(
    witnesses: Iterable[Witness],
    dep: Callable[[Witness, Witness], bool] = proximately_dependent,
    *,
    exact: bool = True,
) -> int:
    """Number of genuinely independent witnesses: a maximum independent set.

    Soundness is machine-checked as ``RootIdentity.independent_card_le_lineages``
    -- an independent set holds at most one member per true lineage, so this
    cannot over-report independence **relative to the dependence graph it is
    given**.

    It can over-report relative to *reality*, because an adversary who launders
    provenance and scrubs idiosyncratic markers removes edges, and a sparser
    graph admits a larger independent set. No counting rule closes that; only
    detection does, and detection can only ever report "no dependence trace
    found" (ASSAYER A5). Margin sufficiency R3 is what absorbs the residual.

    ``exact=False`` uses a greedy pass -- always a *lower* bound, so
    conservative in the safe direction.
    """
    items = list(witnesses)
    if not items:
        return 0

    if not exact:
        chosen: list[Witness] = []
        for w in items:
            if all(not dep(w, c) for c in chosen):
                chosen.append(w)
        return len(chosen)

    for size in range(len(items), 0, -1):
        for group in combinations(items, size):
            if _independent(group, dep):
                return size
    return 0
