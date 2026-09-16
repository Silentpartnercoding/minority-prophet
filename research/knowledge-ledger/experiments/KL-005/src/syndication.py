"""KL-005 first gate: wire copies and circular citations cannot count as
independent confirmation.

Root collapse over a citation graph. A report's root is the original-reporting
document it ultimately descends from; wire copies inherit their parent's root,
and a citation cycle resolves to no original at all rather than to an arbitrary
member of the cycle.

The walk itself now lives in `knowledge_ledger.ancestry`, shared with KL-002,
which reached the same mechanism from the source-laundering side. It is kept
shared rather than duplicated so the two experiments cannot drift into
disagreeing about what a root is -- which is the thing they both measure.

KL-005's local rule stays here: a report with no `derivedFrom` IS an original,
because in news a first-hand report is exactly a document with no antecedent.
KL-002's population is the opposite -- an undeclared paraphrase -- so it passes
`require_origin_claim=True` and refuses silence. Same walk, different default,
and the difference is a property of the domain rather than of the code.
"""

from __future__ import annotations


def resolve_root(report_id: str, reports: dict) -> str | None:
    """Walk `derivedFrom` to an original. Returns None on a cycle.

    Delegates to the shared walk. `require_origin_claim=False` keeps KL-005's
    domain rule: a report with no antecedent is a first-hand report.
    """
    from knowledge_ledger.ancestry import resolve_root as shared
    return shared(report_id, reports, require_origin_claim=False)


def independent_origins(report_ids, reports) -> set[str]:
    """Distinct original-reporting roots. Wire copies collapse onto their parent."""
    roots = set()
    for rid in report_ids:
        root = resolve_root(rid, reports)
        if root is not None:
            roots.add(root)
    return roots
