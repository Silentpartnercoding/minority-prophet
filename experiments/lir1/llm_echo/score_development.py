"""Score LIR-1E development cases and freeze the selected threshold."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from experiments.lir1.infer import infer_parents, roots_from_parents
from experiments.lir1.metrics import aggregation_accuracy, parent_metrics, root_count_metrics, root_pair_metrics
from experiments.lir1.model import ClaimInstance, read_jsonl
from experiments.lir1.synthetic_fixture import hide_edges


THRESHOLDS = (0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85)


def usage_summary(responses_path: Path) -> dict[str, Any]:
    grouped: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    counts: dict[str, int] = defaultdict(int)
    with responses_path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("status") != "valid":
                continue
            model = row["model"]
            counts[model] += 1
            for key, value in (row.get("usage") or {}).items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    grouped[model][key] += value
    return {
        model: {"calls": counts[model], "usage": dict(sorted(values.items()))}
        for model, values in sorted(grouped.items())
    }


def hidden_ids(truth: list[ClaimInstance], visible: list[ClaimInstance]) -> set[str]:
    return {
        original.claim_id
        for original, observed in zip(truth, visible, strict=True)
        if original.observed_parents and not observed.observed_parents
    }


def score(claims_path: Path, responses_path: Path) -> dict[str, Any]:
    truth = read_jsonl(claims_path)
    if {row.split for row in truth} != {"development"}:
        raise ValueError("development scorer refuses non-development claims")
    visible = hide_edges(truth, 0.40)
    hidden = hidden_ids(truth, visible)
    rows = []
    predictions_by_threshold = {}
    for threshold in THRESHOLDS:
        predictions = infer_parents((claim.feature_view() for claim in visible), threshold=threshold)
        predictions_by_threshold[threshold] = predictions
        rows.append({"threshold": threshold, **parent_metrics(truth, predictions, evaluate_claim_ids=hidden)})
    selected = max(rows, key=lambda row: (row["f1"], row["threshold"]))["threshold"]
    predictions = predictions_by_threshold[selected]
    roots = roots_from_parents(predictions)
    return {
        "schema": "minority-prophet.lir1e-development-result.v1",
        "status": "development-only-threshold-selection",
        "split": "development",
        "caseCount": len({row.case_id for row in truth}),
        "claimCount": len(truth),
        "hiddenFraction": 0.40,
        "hiddenEdgeCount": len(hidden),
        "thresholdSelection": {
            "objective": "maximum hidden-parent F1; ties choose higher threshold",
            "candidates": rows,
            "selected": selected,
        },
        "selectedMetrics": {
            "parent": parent_metrics(truth, predictions, evaluate_claim_ids=hidden),
            "rootPair": root_pair_metrics(truth, roots),
            "rootCount": root_count_metrics(truth, roots),
            "aggregation": aggregation_accuracy(truth, roots),
        },
        "usage": usage_summary(responses_path),
        "billing": {"mode": "subscription", "incrementalUsdRecorded": 0},
        "inputs": {
            "claimsSha256": hashlib.sha256(claims_path.read_bytes()).hexdigest(),
            "responsesSha256": hashlib.sha256(responses_path.read_bytes()).hexdigest(),
        },
        "interpretationBoundary": "Development estimates tune the method and are not confirmatory evidence.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claims", required=True, type=Path)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = score(args.claims, args.responses)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "outputSha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "selectedThreshold": result["thresholdSelection"]["selected"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
