#!/usr/bin/env python3
"""KL-001 first check FC1. Registered in PREREGISTRATION-FC1.md before this
script existed; the four worlds and four expectations are transcribed from
the registration, not invented here."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO))

from knowledge_ledger.transaction import evaluate_transaction  # noqa: E402

EVALUATOR = REPO / "knowledge_ledger" / "transaction.py"
REGISTERED_HASH = "15dfd50051ef5da3db13d8e591f58537325ee50aa4e3573914f86e4ff3a3e21f"


def world(locations, records, proposition):
    return {
        "transactionId": "kl001-fc1",
        "claim": {"type": "absence", "proposition": proposition},
        "searchLedger": {"locations": locations},
        "evidenceLedger": {"records": records},
    }


REPO_PROP = "No hardcoded credential exists in the mandatory files of repository example-svc."
KL000_PROP = "No target-class defect exists in the declared components."

W1 = world(
    [{"id": "src/config.py", "status": "searched"},
     {"id": "README.md", "status": "searched"},
     {"id": ".env.example", "status": "not_searched"},
     {"id": "deploy/secrets.tpl", "status": "unavailable"}],
    [{"id": "finding-1", "rootId": "scanner-A", "side": "support"},
     {"id": "finding-2", "rootId": "scanner-A", "side": "support"},
     {"id": "finding-3", "rootId": "scanner-B", "side": "support"}],
    REPO_PROP,
)
W2 = json.loads(json.dumps(W1))
for loc in W2["searchLedger"]["locations"]:
    loc["status"] = "searched"
W3 = world(
    [{"id": "src/config.py", "status": "searched"},
     {"id": "README.md", "status": "searched"}],
    W1["evidenceLedger"]["records"],
    REPO_PROP,
)
W4 = world(
    [{"id": "loc-1", "status": "searched"},
     {"id": "loc-2", "status": "searched"},
     {"id": "loc-3", "status": "not_searched"},
     {"id": "loc-4", "status": "unavailable"}],
    [{"id": "rec-1", "rootId": "r1", "side": "support"},
     {"id": "rec-2", "rootId": "r1", "side": "support"},
     {"id": "rec-3", "rootId": "r2", "side": "support"}],
    KL000_PROP,
)

evaluator_hash = hashlib.sha256(EVALUATOR.read_bytes()).hexdigest()
receipts = {name: evaluate_transaction(w) for name, w in
            (("W1", W1), ("W2", W2), ("W3", W3), ("W4", W4))}

STRUCTURAL_FIELDS = ("conclusion", "search", "evidence")
w1_structure = {f: receipts["W1"][f] for f in STRUCTURAL_FIELDS}
w4_structure = {f: receipts["W4"][f] for f in STRUCTURAL_FIELDS}

# W4 must sit inside KL-000's declared exhaustive bounds.
w4_in_bounds = (
    1 <= len(W4["searchLedger"]["locations"]) <= 4
    and 0 <= len(W4["evidenceLedger"]["records"]) <= 3
    and all(r["rootId"] in {"r1", "r2", "r3"} for r in W4["evidenceLedger"]["records"])
    and all(loc["status"] in {"searched", "unavailable", "failed", "not_searched"}
            for loc in W4["searchLedger"]["locations"])
)

expectations = {
    "E1": receipts["W1"]["conclusion"] == "not_established"
          and receipts["W1"]["reason"] == "The declared search space was not exhaustively searched.",
    "E2": receipts["W2"]["conclusion"] == "absent_within_declared_scope",
    "E3": receipts["W3"]["conclusion"] == "absent_within_declared_scope",
    "E4": w1_structure == w4_structure
          and receipts["W1"]["contentDigest"] != receipts["W4"]["contentDigest"],
}

result = {
    "check": "KL-001 FC1",
    "preregistration": "PREREGISTRATION-FC1.md, committed before this script existed",
    "evaluatorUnderTest": {
        "path": "knowledge_ledger/transaction.py",
        "sha256": evaluator_hash,
        "matchesRegistration": evaluator_hash == REGISTERED_HASH,
    },
    "worlds": {"W1": W1, "W2": W2, "W3": W3, "W4": W4},
    "receipts": receipts,
    "w4InsideKl000Bounds": w4_in_bounds,
    "expectations": expectations,
    "verdict": (
        "a" if all(expectations.values()) and w4_in_bounds
        and evaluator_hash == REGISTERED_HASH else "b-or-invalid"
    ),
    "verdictStatement": (
        "(a) FC1 is I2 restated: the evaluator refused the incomplete repository "
        "for exactly the reason it refuses any incomplete-coverage world, the "
        "structural twin inside KL-000's enumeration produced an identical "
        "structural receipt, and the check adds no new evidence about the "
        "evaluator. KL-001's named first gate was already paid by KL-000."
        if all(expectations.values()) and w4_in_bounds else
        "One or more expectations failed; the divergence is the finding (verdict b) "
        "or the run is invalid (hash/bounds)."
    ),
}

out = HERE / "results"
out.mkdir(exist_ok=True)
target = out / "fc1-result.json"
target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"expectations": expectations,
                  "w4InsideKl000Bounds": w4_in_bounds,
                  "evaluatorMatches": evaluator_hash == REGISTERED_HASH,
                  "verdict": result["verdict"]}, indent=2))
print(f"written: {target}")
