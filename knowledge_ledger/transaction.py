"""Deterministic transaction evaluator for the knowledge-ledger seed.

This is a conformance reference, not a truth engine. It evaluates only the
declared search space and evidence roots supplied in one transaction.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


TERMINAL_SEARCH_STATUSES = {"searched", "unavailable"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def verify_content_digest(result: dict[str, Any]) -> bool:
    unsigned = {key: value for key, value in result.items() if key != "contentDigest"}
    expected = f"sha256:{hashlib.sha256(canonical_bytes(unsigned)).hexdigest()}"
    return result.get("contentDigest") == expected


def evaluate_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    claim = payload["claim"]
    locations = payload["searchLedger"]["locations"]
    evidence = payload["evidenceLedger"]["records"]
    if not locations:
        raise ValueError("The declared search space must not be empty.")

    ids = [location["id"] for location in locations]
    if len(ids) != len(set(ids)):
        raise ValueError("Search-location identifiers must be unique.")
    if any(location["status"] not in TERMINAL_SEARCH_STATUSES for location in locations):
        search_complete = False
    else:
        search_complete = all(location["status"] == "searched" for location in locations)

    root_sides: dict[str, str] = {}
    for record in evidence:
        root_id = record["rootId"]
        side = record["side"]
        if side not in {"support", "oppose"}:
            raise ValueError("Evidence sides must be support or oppose.")
        previous = root_sides.setdefault(root_id, side)
        if previous != side:
            raise ValueError("One root cannot support opposing sides.")

    supporting = sorted(root for root, side in root_sides.items() if side == "support")
    opposing = sorted(root for root, side in root_sides.items() if side == "oppose")
    margin = abs(len(supporting) - len(opposing))
    conversions = margin // 2 + 1 if margin else 1
    repeated_collapsed = len(evidence) - len(root_sides)

    if claim["type"] == "absence":
        if opposing:
            conclusion = "present"
            reason = "At least one distinct counterexample root was recorded."
        elif search_complete:
            conclusion = "absent_within_declared_scope"
            reason = "Every declared location was searched and no counterexample root was recorded."
        else:
            conclusion = "not_established"
            reason = "The declared search space was not exhaustively searched."
    else:
        conclusion = "supported" if len(supporting) > len(opposing) else "not_established"
        reason = "The conclusion follows only from the declared root counts."

    result = {
        "schema": "minority-prophet.knowledge-transaction.v0.1",
        "transactionId": payload["transactionId"],
        "claim": claim,
        "search": {
            "declared": len(locations),
            "searched": sum(location["status"] == "searched" for location in locations),
            "unavailable": sum(location["status"] == "unavailable" for location in locations),
            "complete": search_complete,
        },
        "evidence": {
            "records": len(evidence),
            "distinctRoots": len(root_sides),
            "repeatedRecordsCollapsed": repeated_collapsed,
            "supportingRoots": supporting,
            "opposingRoots": opposing,
            "margin": margin,
            "conversionsToReverse": conversions,
        },
        "conclusion": conclusion,
        "reason": reason,
        "limits": [
            "Root identity and independence are declared operationally, not proved semantically.",
            "This result applies only to the declared search space.",
        ],
    }
    result["contentDigest"] = f"sha256:{hashlib.sha256(canonical_bytes(result)).hexdigest()}"
    return result
