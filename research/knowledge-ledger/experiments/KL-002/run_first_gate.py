#!/usr/bin/env python3
"""KL-002 first gate: twenty paraphrases of one false source must remain one root.

Read-only, deterministic, no inference. Writes probe/first-gate.json.
"""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from src.aggregate import confidence, inflation_table  # noqa: E402
from src.roots import RULES, distinct_roots  # noqa: E402

P_ROOT = 0.7


def evaluate(group: dict) -> dict:
    docs = group["documents"]
    out = {"trueOriginCount": group["trueOriginCount"], "groundTruth": group["groundTruth"],
           "documents": len(docs), "byRule": {}}
    for rule in RULES:
        k = len(distinct_roots(docs, rule))
        out["byRule"][rule] = {
            "distinctRoots": k,
            "confidence": round(confidence(k, P_ROOT), 12),
            "overcountsBy": k - group["trueOriginCount"],
        }
    return out


def main() -> int:
    fixture = json.loads((HERE / "fixtures/laundered-source.json").read_text())
    laundered = evaluate(fixture["laundered"])
    independent = evaluate(fixture["independent"])

    gate_holds = laundered["byRule"]["byte_identity"]["distinctRoots"] == 1

    # The comparison that matters: does a false claim laundered through
    # paraphrase outscore a genuinely multi-sourced true claim?
    false_conf = laundered["byRule"]["byte_identity"]["confidence"]
    true_conf = independent["byRule"]["byte_identity"]["confidence"]

    result = {
        "schema": "minority-prophet.kl002-first-gate.v1",
        "gate": "Twenty paraphrases of one false source must remain one root.",
        "gateHolds": gate_holds,
        "laundered": laundered,
        "independent": independent,
        "falseClaimOutscoresTrueClaim": false_conf > true_conf,
        "confidenceGap": round(false_conf - true_conf, 12),
        "inflationTable": inflation_table(20, P_ROOT),
        "perRootAccuracyDeclared": P_ROOT,
        "boundaries": [
            "The population is authored and is not a sample. No rate is reported and none is derivable; every number here is a total function of the fixture and the two declared rules.",
            "The normalizer is deliberately generous. A stricter one yields MORE byte-identity roots, never fewer, so the reported failure is the best case for byte identity.",
            "declared_origin holding at one root is not evidence that origins are truthfully declared. It relocates the trust assumption from the text to the declaration; ADV-001's under-declared search space is untouched by this gate.",
        ],
    }
    (HERE / "probe/first-gate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "inflationTable"}, indent=2))
    return 0 if gate_holds else 1


if __name__ == "__main__":
    raise SystemExit(main())
