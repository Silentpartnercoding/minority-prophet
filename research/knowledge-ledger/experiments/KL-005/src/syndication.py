"""KL-005 first gate: wire copies and circular citations cannot count as
independent confirmation.

Root collapse over a citation graph. A report's root is the original-reporting
document it ultimately descends from; wire copies inherit their parent's root,
and a citation cycle resolves to no original at all rather than to an arbitrary
member of the cycle.
"""

from __future__ import annotations


def resolve_root(report_id: str, reports: dict) -> str | None:
    """Walk `derivedFrom` to an original. Returns None on a cycle.

    A cycle means every member's claim to originality rests on another member's,
    so none of them is an original. Returning None rather than a cycle member is
    the fail-closed choice: it refuses to mint an origin that does not exist.
    """
    seen = set()
    current = report_id
    while True:
        if current in seen:
            return None  # circular citation: no original exists
        seen.add(current)
        parent = reports[current].get("derivedFrom")
        if parent is None:
            return current
        if parent not in reports:
            return None  # dangling ancestor: unresolvable, not independent
        current = parent


def independent_origins(report_ids, reports) -> set[str]:
    """Distinct original-reporting roots. Wire copies collapse onto their parent."""
    roots = set()
    for rid in report_ids:
        root = resolve_root(rid, reports)
        if root is not None:
            roots.add(root)
    return roots
