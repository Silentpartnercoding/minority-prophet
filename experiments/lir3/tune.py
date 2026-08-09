"""Select the frozen LIR-3 configuration on the disjoint development split."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.lir1.metrics import root_count_metrics, root_pair_metrics
from experiments.lir1.model import ClaimInstance, read_jsonl
from experiments.lir1.synthetic_fixture import hide_edges
from experiments.lir2.root_grouping import infer_roots as infer_lir2_roots
from experiments.lir3.provenance_parent import CONFIGURATIONS, Configuration, infer_roots


HIDDEN_FRACTION = 0.40
MINIMUM_PRECISION = 0.99


def candidate(claims: list[ClaimInstance], configuration: Configuration) -> dict[str, Any]:
    visible = hide_edges(claims, HIDDEN_FRACTION)
    roots = infer_roots(
        (claim.feature_view() for claim in visible), configuration=configuration
    )
    pair = root_pair_metrics(claims, roots)
    count = root_count_metrics(claims, roots)
    return {
        "configuration": {
            "id": configuration.identifier,
            "authorMinScore": configuration.author_min_score,
            "authorMargin": configuration.author_margin,
            "fallback": configuration.fallback,
        },
        "eligible": pair["precision"] >= MINIMUM_PRECISION,
        "rootPair": pair,
        "rootCount": count,
    }


def tune(source: Path) -> dict[str, Any]:
    claims = read_jsonl(source)
    if any(claim.split != "development" for claim in claims):
        raise ValueError("LIR-3 tuning accepts only development rows")
    rows = [candidate(claims, configuration) for configuration in CONFIGURATIONS]
    eligible = [row for row in rows if row["eligible"]]
    selected = max(
        eligible,
        key=lambda row: (
            row["rootPair"]["recall"],
            row["rootPair"]["f1"],
            -row["rootCount"]["meanAbsoluteError"],
            row["configuration"]["authorMinScore"],
            row["configuration"]["authorMargin"],
            row["configuration"]["id"],
        ),
    ) if eligible else None
    visible = hide_edges(claims, HIDDEN_FRACTION)
    baseline_roots = infer_lir2_roots(
        (claim.feature_view() for claim in visible), threshold=0.75
    )
    return {
        "schema": "minority-prophet.lir3-development-selection.v1",
        "status": "selected" if selected else "no-eligible-candidate",
        "caseCount": len({claim.case_id for claim in claims}),
        "claimCount": len(claims),
        "hiddenFraction": HIDDEN_FRACTION,
        "selectionRule": (
            "require root precision >=0.99; maximize recall, F1, minimize root-count MAE, "
            "then prefer stricter score, margin, and lexical configuration id"
        ),
        "candidates": rows,
        "selected": selected,
        "lir2SameCaseComparator": {
            "rootPair": root_pair_metrics(claims, baseline_roots),
            "rootCount": root_count_metrics(claims, baseline_roots),
        },
        "normalizedInputSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = tune(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "status": result["status"],
        "selected": result["selected"],
        "outputSha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
