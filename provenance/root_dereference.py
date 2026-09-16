"""Dereference a root's evidence instead of shape-matching it.

`resolvable_reference` checks that a root names something with the FORM of a
dereferenceable reference, and says so in its own docstring: "This checks SHAPE,
NOT EXISTENCE. A well-formed DOI that was never registered passes." That is the
second of the two failure classes in
`research/adversarial-weighting/two_failure_classes.py` -- root emptiness, where
the graph reports the right number of roots and they are hollow.

The move here is the one DRI-7 validated on an unauthored corpus: do not read
the record, go look at the thing. There, 358 records each carried a perfectly
formed 40-character SHA, every one passed a shape check, and 102 pointed at
nothing that existed.

THREE VALUES, NEVER TWO. `unverifiable` is not `absent`. A resolver that is
offline, rate-limited or not configured has not shown a reference to be missing,
and collapsing that into either pass or fail is the defect DRI-7 exists to name:
one direction manufactures false confidence, the other manufactures false
alarms. The caller decides what a host that cannot answer is allowed to conclude.

NO NETWORK BY DEFAULT. Verification that silently performs I/O turns an audit
into a crawler and makes results depend on when you ran them. A resolver must be
passed in explicitly; with none, every checkable reference returns
`unverifiable` with the reason stated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from .graph import WARRANT_KEY, resolvable_reference

VERIFIED = "verified"
ABSENT = "absent"
UNVERIFIABLE = "unverifiable"
NO_REFERENCE = "no_reference"


class Resolver(Protocol):
    """Answers whether a reference exists. True / False / None for 'cannot say'."""
    def __call__(self, form: str, reference: str) -> bool | None: ...


@dataclass(frozen=True)
class Dereference:
    state: str
    form: str | None
    reference: str | None
    reason: str | None

    @property
    def hollow(self) -> bool:
        """Only `absent` is a demonstrated hollow root. `unverifiable` is not."""
        return self.state == ABSENT


def _first_reference(evidence: dict[str, Any]) -> tuple[str | None, str | None]:
    form = resolvable_reference(evidence)
    if form is None:
        return None, None
    for key, value in evidence.items():
        if key == WARRANT_KEY or not isinstance(value, str):
            continue
        candidate = value.strip()
        from .graph import _RESOLVABLE_FORMS
        for name, pattern in _RESOLVABLE_FORMS:
            if name == form and pattern.match(candidate):
                return form, candidate
    return form, None


def dereference_root(evidence: dict[str, Any], resolver: Resolver | None = None) -> Dereference:
    """Does this root's reference actually resolve?

    Returns one of four states. `no_reference` is kept distinct from `absent`
    because a root that names nothing is already refused by
    `UnattributedRootError`; conflating the two would report that older gate's
    work as this one's.
    """
    form, reference = _first_reference(evidence)
    if form is None:
        return Dereference(NO_REFERENCE, None, None,
                           "names no reference with a dereferenceable form")
    if reference is None:
        return Dereference(UNVERIFIABLE, form, None,
                           f"a {form} form was detected but its value could not be recovered")
    if resolver is None:
        return Dereference(UNVERIFIABLE, form, reference,
                           "no resolver configured; shape was checked, existence was not")
    answer = resolver(form, reference)
    if answer is True:
        return Dereference(VERIFIED, form, reference, None)
    if answer is False:
        return Dereference(ABSENT, form, reference, "the reference does not resolve")
    return Dereference(UNVERIFIABLE, form, reference,
                       "the resolver could not answer; this is not evidence of absence")


def audit_roots(nodes, resolver: Resolver | None = None) -> dict:
    """Dereference every root in a graph and report the distribution.

    Reports the DISTRIBUTION rather than a pass rate, because a gate whose
    outcome has only ever held one value has not been tested however many roots
    it has seen. `hollow` counts only demonstrated absence.
    """
    counts = {VERIFIED: 0, ABSENT: 0, UNVERIFIABLE: 0, NO_REFERENCE: 0}
    hollow = []
    for node in nodes:
        if not node.is_root:
            continue
        result = dereference_root(node.evidence, resolver)
        counts[result.state] += 1
        if result.hollow:
            hollow.append(node.node_id)
    checkable = counts[VERIFIED] + counts[ABSENT]
    return {
        "roots": sum(counts.values()),
        "states": counts,
        "checkable": checkable,
        "hollowRate": round(counts[ABSENT] / checkable, 3) if checkable else None,
        "hollowRoots": sorted(hollow),
        "distinctStatesObserved": sum(1 for v in counts.values() if v),
        "boundary": (
            "`unverifiable` is not `absent`: a resolver that cannot answer has not shown a "
            "reference to be missing. hollowRate is over what was actually checkable. "
            "This addresses root emptiness only; count inflation is a separate defence "
            "(knowledge_ledger/ancestry.py) and neither substitutes for the other."
        ),
    }
