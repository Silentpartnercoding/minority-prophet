#!/usr/bin/env python3
"""KL-002 first gate, and the repair for the defect it measured.

Read-only, deterministic, no inference. Writes probe/first-gate.json.
Exit 1 while the gate does not hold under the rule that was in force.
"""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3]))          # repository root, for knowledge_ledger

from src.aggregate import confidence, inflation_table  # noqa: E402
from src.roots import RULES, build_index, distinct_roots  # noqa: E402

P_ROOT = 0.7
POPULATIONS = ("laundered", "stripped", "chained", "independent")


def evaluate(group: dict, index: dict) -> dict:
    docs = group["documents"]
    out = {"trueOriginCount": group["trueOriginCount"], "groundTruth": group["groundTruth"],
           "documents": len(docs), "byRule": {}}
    for rule in RULES:
        k = len(distinct_roots(docs, rule, index))
        out["byRule"][rule] = {
            "distinctRoots": k,
            "confidence": round(confidence(k, P_ROOT), 12),
            "overcountsBy": k - group["trueOriginCount"],
            "correct": k == group["trueOriginCount"],
        }
    return out


def main() -> int:
    fixture = json.loads((HERE / "fixtures/laundered-source.json").read_text())
    index = build_index(*(fixture[name] for name in POPULATIONS))
    results = {name: evaluate(fixture[name], index) for name in POPULATIONS}

    gate_holds = results["laundered"]["byRule"]["byte_identity"]["distinctRoots"] == 1

    false_conf = results["laundered"]["byRule"]["byte_identity"]["confidence"]
    true_conf = results["independent"]["byRule"]["byte_identity"]["confidence"]

    # Which rule is correct on which population -- the enumerated table that
    # replaces a rate, because the outcome is a total function of the fixture.
    correctness = {rule: {name: results[name]["byRule"][rule]["correct"] for name in POPULATIONS}
                   for rule in RULES}
    fully_correct = [rule for rule, row in correctness.items() if all(row.values())]

    # The asymmetry that matters more than correctness. Over-counting MANUFACTURES
    # independence: a false claim gains witnesses it does not have, and the system
    # becomes confidently wrong. Under-counting DISCARDS evidence: the system
    # abstains when it could have concluded. Only one of those creates a false
    # belief, so a rule that is never over-counting is safe in a way a merely
    # accurate one is not.
    direction = {}
    for rule in RULES:
        over = [n for n in POPULATIONS if results[n]["byRule"][rule]["overcountsBy"] > 0]
        under = [n for n in POPULATIONS if results[n]["byRule"][rule]["overcountsBy"] < 0]
        direction[rule] = {
            "overcountsOn": over, "undercountsOn": under,
            "neverOvercounts": not over,
            "reading": ("never manufactures independence" if not over
                        else "manufactures independence on: " + ", ".join(over)),
        }

    result = {
        "schema": "minority-prophet.kl002-first-gate.v2",
        "gate": "Twenty paraphrases of one false source must remain one root.",
        "gateHoldsUnderByteIdentity": gate_holds,
        "populations": results,
        "correctnessByRule": correctness,
        "rulesCorrectOnEveryPopulation": fully_correct,
        "errorDirection": direction,
        "whyNoRuleIsFullyCorrect": (
            "ancestry is wrong on `stripped` by refusing all twenty rather than finding the one. "
            "That is the fail-closed trade stated in knowledge_ledger/ancestry.py: it never mints a "
            "root it has not been shown, so it under-counts where the others over-count. Only "
            "over-counting creates a false belief; under-counting creates an abstention."
        ),
        "falseClaimOutscoresTrueClaim": false_conf > true_conf,
        "confidenceGap": round(false_conf - true_conf, 12),
        "inflationTable": inflation_table(20, P_ROOT),
        "perRootAccuracyDeclared": P_ROOT,
        "theRepair": {
            "rule": "ancestry",
            "module": "knowledge_ledger/ancestry.py",
            "sharedWith": "KL-005, which reached the same mechanism from syndication",
            "whatIsActuallyNew": "not the walk, which KL-005 already had, but the treatment of a "
                                 "document declaring NO ancestry. byte_identity and declared_origin "
                                 "both read silence as originality, which is how laundering works. "
                                 "ancestry refuses: an undeclared document is unattributable, not a root.",
            "costAccepted": "a genuine original that never recorded its provenance is discarded with "
                            "the laundered copies. An origin claim that costs nothing to make is worth "
                            "nothing, so the cost is the point.",
            "notSolved": "ancestry still trusts a declared edge. A document that lies about its parent "
                         "is believed, and ADV-001's under-declared search space is untouched. This "
                         "narrows the attack from free to auditable; it does not remove it.",
        },
        "boundaries": [
            "The population is authored and is not a sample. No rate is reported and none is derivable.",
            "The normalizer is deliberately generous; a stricter one yields MORE byte-identity roots, never fewer.",
            "The `chained` population contains no lie. Every document truthfully names what it was copied from, and declared_origin is still wrong on it because it reads one hop.",
        ],
    }
    (HERE / "probe/first-gate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("gateHoldsUnderByteIdentity", "correctnessByRule",
                       "rulesCorrectOnEveryPopulation", "errorDirection")}, indent=2))
    return 0 if gate_holds else 1


if __name__ == "__main__":
    raise SystemExit(main())
