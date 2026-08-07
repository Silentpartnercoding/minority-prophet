"""KL-000 ablated baselines B1-B4.

Each is a deliberately defective evaluator that removes exactly one property the
dual ledger is claimed to provide. They exist to answer a question the primary
result cannot answer about itself: *would this checker notice if the evaluator
were wrong?*

If any of B1-B4 passes the invariant suite, the suite is vacuous and the run is
invalidated -- regardless of how cleanly the real evaluator passed. That is
preregistered in `preregistration.json` as an invalidation condition.

Each baseline emits the same receipt shape as the real evaluator, including a
self-consistent contentDigest, so that it fails on the property being ablated
rather than on a structural mismatch the checker would catch for the wrong
reason.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

TERMINAL = {"searched", "unavailable"}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def _finish(result: dict[str, Any]) -> dict[str, Any]:
    result["contentDigest"] = "sha256:" + hashlib.sha256(_canonical(result)).hexdigest()
    return result


def _common(payload: dict[str, Any]) -> tuple[list, list, bool, int, int]:
    locations = payload["searchLedger"]["locations"]
    records = payload["evidenceLedger"]["records"]
    if not locations:
        raise ValueError("The declared search space must not be empty.")
    ids = [loc["id"] for loc in locations]
    if len(ids) != len(set(ids)):
        raise ValueError("Search-location identifiers must be unique.")
    if any(loc["status"] not in TERMINAL for loc in locations):
        complete = False
    else:
        complete = all(loc["status"] == "searched" for loc in locations)
    searched = sum(loc["status"] == "searched" for loc in locations)
    unavailable = sum(loc["status"] == "unavailable" for loc in locations)
    return locations, records, complete, searched, unavailable


def _side_map(records: list[dict[str, Any]]) -> dict[str, str]:
    sides: dict[str, str] = {}
    for record in records:
        if record["side"] not in {"support", "oppose"}:
            raise ValueError("Evidence sides must be support or oppose.")
        previous = sides.setdefault(record["rootId"], record["side"])
        if previous != record["side"]:
            raise ValueError("One root cannot support opposing sides.")
    return sides


def _shell(payload, locations, records, complete, searched, unavailable,
           distinct, collapsed, supporting, opposing, conclusion, reason):
    margin = abs(len(supporting) - len(opposing))
    return _finish({
        "schema": "minority-prophet.knowledge-transaction.v0.1",
        "transactionId": payload["transactionId"],
        "claim": payload["claim"],
        "search": {
            "declared": len(locations),
            "searched": searched,
            "unavailable": unavailable,
            "complete": complete,
        },
        "evidence": {
            "records": len(records),
            "distinctRoots": distinct,
            "repeatedRecordsCollapsed": collapsed,
            "supportingRoots": supporting,
            "opposingRoots": opposing,
            "margin": margin,
            "conversionsToReverse": margin // 2 + 1 if margin else 1,
        },
        "conclusion": conclusion,
        "reason": reason,
    })


def b1_head_count(payload: dict[str, Any]) -> dict[str, Any]:
    """Ablation: no root collapse at all. Every record is its own witness.

    Expected to fail I1 and I10: adding one copy raises distinctRoots.
    """
    locations, records, complete, searched, unavailable = _common(payload)
    _side_map(records)
    supporting = sorted(r["id"] for r in records if r["side"] == "support")
    opposing = sorted(r["id"] for r in records if r["side"] == "oppose")
    if payload["claim"]["type"] == "absence":
        if opposing:
            conclusion = "present"
        elif complete:
            conclusion = "absent_within_declared_scope"
        else:
            conclusion = "not_established"
    else:
        conclusion = "supported" if len(supporting) > len(opposing) else "not_established"
    return _shell(payload, locations, records, complete, searched, unavailable,
                  len(records), 0, supporting, opposing, conclusion,
                  "Records counted individually.")


def b2_source_count(payload: dict[str, Any]) -> dict[str, Any]:
    """Ablation: roots collapse correctly, but the search ledger is ignored.

    Expected to fail I2: absence is concluded from evidence alone.
    """
    locations, records, complete, searched, unavailable = _common(payload)
    sides = _side_map(records)
    supporting = sorted(r for r, s in sides.items() if s == "support")
    opposing = sorted(r for r, s in sides.items() if s == "oppose")
    if payload["claim"]["type"] == "absence":
        conclusion = "present" if opposing else "absent_within_declared_scope"
    else:
        conclusion = "supported" if len(supporting) > len(opposing) else "not_established"
    return _shell(payload, locations, records, complete, searched, unavailable,
                  len(sides), len(records) - len(sides), supporting, opposing,
                  conclusion, "Coverage not consulted.")


def b3_evidence_without_coverage(payload: dict[str, Any]) -> dict[str, Any]:
    """Ablation: absence permitted whenever any supporting root exists.

    Expected to fail I2, and more aggressively than B2: it concludes absence
    even at zero coverage as long as one root supports the claim.
    """
    locations, records, complete, searched, unavailable = _common(payload)
    sides = _side_map(records)
    supporting = sorted(r for r, s in sides.items() if s == "support")
    opposing = sorted(r for r, s in sides.items() if s == "oppose")
    if payload["claim"]["type"] == "absence":
        if opposing:
            conclusion = "present"
        elif supporting:
            conclusion = "absent_within_declared_scope"
        else:
            conclusion = "not_established"
    else:
        conclusion = "supported" if len(supporting) > len(opposing) else "not_established"
    return _shell(payload, locations, records, complete, searched, unavailable,
                  len(sides), len(records) - len(sides), supporting, opposing,
                  conclusion, "Supporting roots treated as sufficient for absence.")


def b4_search_without_collapse(payload: dict[str, Any]) -> dict[str, Any]:
    """Ablation: coverage handled correctly, but margin counts records.

    Expected to fail I1: margin and conversionsToReverse move when a copy is
    added, so a copy changes the decision's safety budget.
    """
    locations, records, complete, searched, unavailable = _common(payload)
    sides = _side_map(records)
    supporting_records = [r for r in records if r["side"] == "support"]
    opposing_records = [r for r in records if r["side"] == "oppose"]
    supporting = sorted({r["rootId"] for r in supporting_records})
    opposing = sorted({r["rootId"] for r in opposing_records})
    if payload["claim"]["type"] == "absence":
        if opposing:
            conclusion = "present"
        elif complete:
            conclusion = "absent_within_declared_scope"
        else:
            conclusion = "not_established"
    else:
        conclusion = ("supported" if len(supporting_records) > len(opposing_records)
                      else "not_established")
    margin = abs(len(supporting_records) - len(opposing_records))
    return _finish({
        "schema": "minority-prophet.knowledge-transaction.v0.1",
        "transactionId": payload["transactionId"],
        "claim": payload["claim"],
        "search": {
            "declared": len(locations),
            "searched": searched,
            "unavailable": unavailable,
            "complete": complete,
        },
        "evidence": {
            "records": len(records),
            "distinctRoots": len(sides),
            "repeatedRecordsCollapsed": len(records) - len(sides),
            "supportingRoots": supporting,
            "opposingRoots": opposing,
            "margin": margin,
            "conversionsToReverse": margin // 2 + 1 if margin else 1,
        },
        "conclusion": conclusion,
        "reason": "Margin computed over records rather than roots.",
    })


BASELINES = {
    "B1-head-count": b1_head_count,
    "B2-source-count": b2_source_count,
    "B3-evidence-without-coverage": b3_evidence_without_coverage,
    "B4-search-without-collapse": b4_search_without_collapse,
}
