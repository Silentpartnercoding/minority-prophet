"""Does a settlement survive every combination of recorded possible dependence?

Agreement across a menu of independence cuts is not robustness. Each cut applies
one dependence reading to both sides of a decision at once. When dependencies
stack, every cut can overcount the same side, and all of them agree on a
settlement the evidence does not support.

DRI-2 found exactly this. In v1 and v2, every one of the decision-sensitivity
method's 14 false settlements was the same shape. The true causal units were tied
2-2, yet all five cuts settled the same way: the finer cuts split one side's
shared-component pair into two sources, and the coarsest cut also merged the other
side's independent sources. So every cut overcounted one side, and "the cuts agree,
so the choice of cut does not matter" settled a tie.

The reading this module applies instead: two observations *may* be one source if
they share an identity at any cut. Any combination of those possible merges is a
reading the record cannot rule out, including readings no single cut expresses,
such as one side's reports being one source while the other side's are independent.
A settlement is robust only when every such reading gives the same settlement.

The computation is exact and near-linear in the number of observations times
cuts. Each side's root count ranges
independently, from its connected components under shared identity to its
observation count. Any value in between is reachable by merging along the shared
identities one at a time. A block that mixes true and false observations can only
fail closed, as the root-vote kernel's side-separation check does. Nothing is
sampled or approximated.

What this cannot see: dependence that no recorded identity carries. Failure to
detect dependence is not evidence of independence, so a robust result is robust
only over what the record shows. An observation with no identity at any cut cannot
be bounded at all, and makes the result non-robust.

This is an adapter beside ``provenance.decision_relative``. It grants no authority
and does not choose what to do about a non-robust result; the caller decides
whether to look further or abstain.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from provenance.decision_relative import DecisionContextError, DecisionEvidence

SETTLED_TRUE = "settled_true"
SETTLED_FALSE = "settled_false"
UNSETTLED = "unsettled"


@dataclass(frozen=True)
class DependenceRobustness:
    """The settlements reachable under recorded possible dependence."""

    true_roots: tuple[int, int]
    """(fewest, most) independent roots the true side can have."""
    false_roots: tuple[int, int]
    """(fewest, most) independent roots the false side can have."""
    mixed_root_possible: bool
    """True when a true and a false observation share an identity, so one root
    could carry both values and the vote must fail closed."""
    unattributed: int
    """Observations with no identity at any considered cut."""
    reachable_settlements: frozenset[str]
    robust: bool
    """True only when every reading gives one settlement and nothing is unattributed."""
    settlement: str | None
    """The settlement every reading gives, or None when not robust."""


def settle_counts(true_roots: int, false_roots: int, minimum_winning_roots: int) -> str:
    """The root-vote settlement for given root counts on each side."""
    if true_roots > false_roots and true_roots >= minimum_winning_roots:
        return SETTLED_TRUE
    if false_roots > true_roots and false_roots >= minimum_winning_roots:
        return SETTLED_FALSE
    return UNSETTLED


def _components(indices: list[int], groups: Iterable[list[int]]) -> int:
    parent = {index: index for index in indices}

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for group in groups:
        members = [index for index in group if index in parent]
        for other in members[1:]:
            parent[find(other)] = find(members[0])
    return len({find(index) for index in indices})


def assess_dependence_robustness(
    evidence: Iterable[DecisionEvidence],
    minimum_winning_roots: int,
    candidate_cuts: Iterable[str] | None = None,
) -> DependenceRobustness:
    """Bound the settlement over every combination of recorded possible dependence.

    ``candidate_cuts`` limits which identities count as possible dependence. By
    default every cut present in the evidence counts.
    """
    records = tuple(evidence)
    if not records:
        raise DecisionContextError("at least one evidence record is required")
    if minimum_winning_roots < 1:
        raise ValueError("minimum_winning_roots must be at least 1")
    cuts = (
        tuple(dict.fromkeys(candidate_cuts))
        if candidate_cuts is not None
        else tuple(sorted({cut for item in records for cut in item.roots}))
    )

    unattributed = sum(
        1 for item in records if all(item.roots.get(cut) is None for cut in cuts)
    )
    groups: dict[tuple[str, str], list[int]] = {}
    for index, item in enumerate(records):
        for cut in cuts:
            root = item.roots.get(cut)
            if root is not None:
                groups.setdefault((cut, root), []).append(index)
    shared = [members for members in groups.values() if len(members) > 1]
    mixed = any(len({records[index].value for index in members}) > 1 for members in shared)

    true_indices = [index for index, item in enumerate(records) if item.value]
    false_indices = [index for index, item in enumerate(records) if not item.value]
    true_range = (_components(true_indices, shared), len(true_indices))
    false_range = (_components(false_indices, shared), len(false_indices))

    # Settlement is monotone in each side's count, so the corners decide it. True
    # is reachable iff the true side at its most and the false side at its fewest
    # settles true, and symmetrically for false. Every count box that is neither
    # all true nor all false contains an unsettled point: moving one root at a time
    # from a true point to a false one passes through a tie.
    most_true = settle_counts(true_range[1], false_range[0], minimum_winning_roots)
    most_false = settle_counts(true_range[0], false_range[1], minimum_winning_roots)
    reachable: set[str] = set()
    if most_true == SETTLED_TRUE:
        reachable.add(SETTLED_TRUE)
    if most_false == SETTLED_FALSE:
        reachable.add(SETTLED_FALSE)
    if most_false != SETTLED_TRUE and most_true != SETTLED_FALSE:
        reachable.add(UNSETTLED)
    if mixed:
        reachable.add(UNSETTLED)
    robust = unattributed == 0 and len(reachable) == 1
    return DependenceRobustness(
        true_roots=true_range,
        false_roots=false_range,
        mixed_root_possible=mixed,
        unattributed=unattributed,
        reachable_settlements=frozenset(reachable),
        robust=robust,
        settlement=next(iter(reachable)) if robust else None,
    )
