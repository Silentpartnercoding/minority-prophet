"""Select the frozen PHEME parent threshold using development cases only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .infer import infer_parents, roots_from_parents
from .metrics import parent_metrics, root_count_metrics, root_pair_metrics
from .model import read_jsonl
from .synthetic_fixture import hide_edges


THRESHOLDS = tuple(round(0.40 + 0.05 * step, 2) for step in range(10))


def select_threshold(rows: list[dict[str, object]]) -> float:
    selected = max(
        rows, key=lambda row: (float(row["parentF1"]), float(row["threshold"]))
    )
    return float(selected["threshold"])


def run(source: Path) -> dict[str, object]:
    all_claims = read_jsonl(source)
    claims = [claim for claim in all_claims if claim.split == "development"]
    observed = hide_edges(claims, 0.40)
    hidden_claim_ids = {
        truth.claim_id
        for truth, visible in zip(claims, observed, strict=True)
        if truth.observed_parents and not visible.observed_parents
    }
    rows: list[dict[str, object]] = []
    for threshold in THRESHOLDS:
        parents = infer_parents((claim.feature_view() for claim in observed), threshold=threshold)
        roots = roots_from_parents(parents)
        parent = parent_metrics(claims, parents, evaluate_claim_ids=hidden_claim_ids)
        rows.append({
            "threshold": threshold,
            "parentF1": parent["f1"],
            "parentPrecision": parent["precision"],
            "parentRecall": parent["recall"],
            "rootPair": root_pair_metrics(claims, roots),
            "rootCount": root_count_metrics(claims, roots),
        })
    selected = select_threshold(rows)
    return {
        "schema": "minority-prophet.lir1-pheme-threshold.v1",
        "status": "development-only",
        "claimBoundary": "Threshold selection on hidden edges in development cases; no confirmatory cases scored.",
        "normalizedInputSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "hiddenFraction": 0.40,
        "developmentCases": len({claim.case_id for claim in claims}),
        "developmentClaims": len(claims),
        "hiddenDevelopmentEdges": len(hidden_claim_ids),
        "thresholds": list(THRESHOLDS),
        "selectionRule": "maximum exact-parent F1; ties select higher threshold",
        "selectedThreshold": selected,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = run(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
