"""Select the frozen LIR-2 root-grouping threshold on open LIR-1E data."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from experiments.lir1.metrics import aggregation_accuracy, root_count_metrics, root_pair_metrics
from experiments.lir1.model import ClaimInstance, read_jsonl
from experiments.lir1.synthetic_fixture import hide_edges
from experiments.lir2.root_grouping import infer_roots


THRESHOLDS = (0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)


def reversal_count(claims: list[ClaimInstance], roots: dict[str, str]) -> int:
    grouped: dict[str, list[ClaimInstance]] = defaultdict(list)
    for claim in claims:
        grouped[claim.case_id].append(claim)
    reversals = 0
    for rows in grouped.values():
        truth = rows[0].content_truth == "true"
        raw = [bool(row.channel_metadata["asserted_value"]) for row in rows]
        collapsed: dict[str, bool] = {}
        for row in rows:
            collapsed.setdefault(roots[row.claim_id], bool(row.channel_metadata["asserted_value"]))
        raw_ones = sum(raw)
        root_ones = sum(collapsed.values())
        raw_correct = raw_ones != len(raw) - raw_ones and ((raw_ones > len(raw) - raw_ones) == truth)
        root_correct = root_ones != len(collapsed) - root_ones and ((root_ones > len(collapsed) - root_ones) == truth)
        if raw_correct and not root_correct:
            reversals += 1
    return reversals


def candidate(claims: list[ClaimInstance], threshold: float) -> dict[str, Any]:
    visible = hide_edges(claims, 0.40)
    roots = infer_roots((row.feature_view() for row in visible), threshold=threshold)
    pairs = root_pair_metrics(claims, roots)
    aggregation = aggregation_accuracy(claims, roots)
    eligible_cases = int(aggregation["eligible_cases"])
    answered = int(aggregation["inferred_answered"])
    correct = int(round(float(aggregation["inferred_accuracy"]) * answered))
    reversals = reversal_count(claims, roots)
    eligible = pairs["precision"] == 1.0 and reversals == 0
    return {
        "threshold": threshold,
        "eligible": eligible,
        "falseReversals": reversals,
        "coverage": answered / eligible_cases if eligible_cases else 0.0,
        "allCaseCorrectYield": correct / eligible_cases if eligible_cases else 0.0,
        "rootPair": pairs,
        "rootCount": root_count_metrics(claims, roots),
        "aggregation": aggregation,
    }


def tune(paths: list[Path]) -> dict[str, Any]:
    claims = [claim for path in paths for claim in read_jsonl(path)]
    if len({claim.case_id for claim in claims}) != 48:
        raise ValueError("LIR-2 development requires exactly 48 distinct cases")
    rows = [candidate(claims, threshold) for threshold in THRESHOLDS]
    eligible = [row for row in rows if row["eligible"]]
    selected = max(eligible, key=lambda row: (
        row["coverage"], row["rootPair"]["recall"], row["allCaseCorrectYield"], row["threshold"]
    )) if eligible else None
    return {
        "schema": "minority-prophet.lir2-development-selection.v1",
        "status": "selected" if selected else "no-eligible-candidate",
        "caseCount": 48,
        "hiddenFraction": 0.40,
        "selectionRule": "eligible precision=1 and zero false reversals; maximize coverage, root recall, all-case yield, then threshold",
        "candidates": rows,
        "selected": selected,
        "inputs": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claims", required=True, nargs=2, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = tune(args.claims)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "outputSha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "selectedThreshold": result["selected"]["threshold"] if result["selected"] else None,
        "status": result["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
