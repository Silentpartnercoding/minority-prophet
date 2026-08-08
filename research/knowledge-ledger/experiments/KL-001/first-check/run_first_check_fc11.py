#!/usr/bin/env python3
"""KL-001 first check FC1.1: the corrected E4'/E5' judgements, registered in
PREREGISTRATION-FC1.1.md before this script existed. Worlds W1-W4 are read
from FC1's committed result so they cannot drift from what FC1 ran."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO))

from knowledge_ledger.transaction import evaluate_transaction  # noqa: E402

REGISTERED_HASH = "15dfd50051ef5da3db13d8e591f58537325ee50aa4e3573914f86e4ff3a3e21f"
NAME_FREE_EVIDENCE = ("records", "distinctRoots", "repeatedRecordsCollapsed",
                      "margin", "conversionsToReverse")

fc1 = json.loads((HERE / "results" / "fc1-result.json").read_text())
worlds = fc1["worlds"]
evaluator_hash = hashlib.sha256(
    (REPO / "knowledge_ledger" / "transaction.py").read_bytes()
).hexdigest()

r1 = evaluate_transaction(worlds["W1"])
r4 = evaluate_transaction(worlds["W4"])

def name_free(receipt):
    return {
        "conclusion": receipt["conclusion"],
        "reason": receipt["reason"],
        "search": receipt["search"],
        "evidence": {k: receipt["evidence"][k] for k in NAME_FREE_EVIDENCE},
    }

e4_prime = name_free(r1) == name_free(r4)

diverging = []
for member in sorted(set(r1) | set(r4)):
    if r1.get(member) != r4.get(member):
        if member == "evidence":
            for k in sorted(set(r1["evidence"]) | set(r4["evidence"])):
                if r1["evidence"].get(k) != r4["evidence"].get(k):
                    diverging.append(f"evidence.{k}")
        elif member == "claim":
            for k in sorted(set(r1["claim"]) | set(r4["claim"])):
                if r1["claim"].get(k) != r4["claim"].get(k):
                    diverging.append(f"claim.{k}")
        else:
            diverging.append(member)
e5_expected = ["claim.proposition", "contentDigest",
               "evidence.opposingRoots", "evidence.supportingRoots"]
# opposingRoots are empty lists on both sides here, so they may legitimately
# NOT diverge; E5' requires the diverging set to be a subset of the named
# members and to include the two that must differ.
e5_prime = (set(diverging) <= set(e5_expected)
            and "evidence.supportingRoots" in diverging
            and "contentDigest" in diverging
            and "claim.proposition" in diverging)

result = {
    "check": "KL-001 FC1.1",
    "preregistration": "PREREGISTRATION-FC1.1.md, committed before this script existed",
    "worldsSource": "FC1's committed result (byte-fixed); re-evaluated fresh",
    "evaluatorUnderTest": {"sha256": evaluator_hash,
                            "matchesRegistration": evaluator_hash == REGISTERED_HASH},
    "E4prime_nameFreeStructuralIdentity": e4_prime,
    "nameFreeComparison": {"W1": name_free(r1), "W4": name_free(r4)},
    "E5prime_divergenceIsExactlyTheNames": e5_prime,
    "divergingMembers": diverging,
    "verdict": "a" if (e4_prime and e5_prime and evaluator_hash == REGISTERED_HASH) else "b-or-invalid",
    "verdictStatement": (
        "(a) confirmed under the corrected registration: the evaluator sees structure "
        "only; every name-free field is identical between the repository world and its "
        "enumerated twin, and the receipts diverge exactly on the echoed identifier "
        "strings and the digest they induce. FC1's check is I2 restated; KL-001's "
        "named first gate was already paid by KL-000. FC1's E4 failure stands in the "
        "record as a mis-registration."
        if e4_prime and e5_prime else
        "A name-free field diverged under renaming (verdict b) or the run is invalid."
    ),
}

target = HERE / "results" / "fc11-result.json"
target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({k: result[k] for k in
                  ("E4prime_nameFreeStructuralIdentity",
                   "E5prime_divergenceIsExactlyTheNames",
                   "divergingMembers", "verdict")}, indent=2))
print(f"written: {target}")
