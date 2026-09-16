"""Resolve a transaction's evidence roots from declared ancestry.

This is the layer the engine never had. `transaction.py` and `transaction_v2.py`
both take `record["rootId"]` as given, so the root rule KL-002 measured -- and the
repair it produced -- reached neither of them. This module closes that, and it
does so WITHOUT touching either evaluator.

Why not fix the evaluator. `knowledge_ledger/transaction.py` is pinned at
`preregistration.json` line 145 as the artifact under test in KL-000, which
reached `adversarial-passed` with an independent Rust reimplementation agreeing
on the conclusion distribution over all 110,840 receipts and on the canonical
digests of the two pinned receipts. Editing it moves those digests and
invalidates the reproduction. The evaluator is not where this belongs anyway:
KL-001's FC1 finding says the layer that decides what counts is where the risk
lives, and that layer is here.

What this does. Each evidence record names the document it came from. The root is
resolved by walking declared ancestry to an origin, exactly as KL-002 and KL-005
do. A record whose ancestry cannot establish an origin -- a cycle, a dangling
ancestor, or silence -- gets `rootId: None`.

Why `None` rather than dropping the record. `transaction_v2` already counts a
record with no rootId as `unattributed` and reports it separately, on the stated
grounds that "a dropped record is the difference between 'we found nothing' and
'we could not attribute what we found', and those are not the same receipt."
That distinction is exactly what unattributable ancestry needs, so this emits the
shape v2 already understands instead of inventing a second vocabulary.

What it does not do. This addresses ONE of the two failure classes named in
`research/adversarial-weighting/two_failure_classes.py`: count inflation, where
the graph reports more roots than exist. It does nothing for root emptiness,
where the count is right and the roots are hollow -- a fabricated root with nine
honest copies collapses to one root, which is structurally perfect and still
worth zero. That document says the two "need different defences that cannot
substitute for each other", and this is only the first.
"""

from __future__ import annotations

from .ancestry import resolve_root


def resolve_transaction_roots(payload: dict, documents: dict,
                              require_origin_claim: bool = True) -> dict:
    """Return a copy of `payload` with every record's rootId resolved by ancestry.

    `documents` maps a document id to `{"derivedFrom": ..., "isOriginal": ...}`.
    A record points at its document through `documentId`, falling back to the
    record's own `id` when the ledger names them the same.

    The input is not mutated: an evaluator that received the original payload and
    one that received the resolved payload must remain comparable, which is the
    whole point of doing this outside the evaluator.
    """
    resolved = {**payload}
    ledger = payload.get("evidenceLedger") or {}
    records = ledger.get("records") or []

    out = []
    for record in records:
        doc_id = record.get("documentId") or record.get("id")
        root = resolve_root(doc_id, documents, require_origin_claim) if doc_id else None
        out.append({**record, "rootId": root, "rootResolvedFrom": doc_id})

    resolved["evidenceLedger"] = {**ledger, "records": out}
    return resolved


def resolution_report(payload: dict, documents: dict,
                      require_origin_claim: bool = True) -> dict:
    """What resolution would change, without changing it.

    Reported as an explicit before/after because a root rule that silently
    rewrites its input is the thing this programme exists to refuse. `collapsed`
    is the count inflation removed; `unattributable` is the cost paid for it.
    """
    records = (payload.get("evidenceLedger") or {}).get("records") or []
    supplied = {r.get("rootId") for r in records if r.get("rootId")}
    after = resolve_transaction_roots(payload, documents, require_origin_claim)
    after_records = after["evidenceLedger"]["records"]
    resolved_roots = {r["rootId"] for r in after_records if r["rootId"]}
    unattributable = [r.get("documentId") or r.get("id")
                      for r in after_records if not r["rootId"]]
    return {
        "recordsConsidered": len(records),
        "suppliedDistinctRoots": len(supplied),
        "resolvedDistinctRoots": len(resolved_roots),
        "collapsed": len(supplied) - len(resolved_roots),
        "unattributable": sorted(x for x in unattributable if x),
        "note": ("`collapsed` is count inflation removed. `unattributable` is the cost: "
                 "evidence that named no resolvable origin and therefore joins no side. "
                 "Neither number speaks to root emptiness, which is a separate failure class."),
    }
