"""Run the frozen PHEME confirmatory edge-hiding evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

from .infer import infer_parents, roots_from_parents
from .metrics import parent_metrics, root_count_metrics, root_pair_metrics
from .model import ClaimInstance, read_jsonl
from .run_boundary import FRACTIONS
from .synthetic_fixture import hide_edges


THRESHOLD = 0.80
BOOTSTRAP_SEED = 20260808
BOOTSTRAP_SAMPLES = 10_000
THRESHOLD_COMMIT = "7e49622304d1e0c6cdaea45047de80397ccbceb6"


def f1_from_counts(tp: int, fp: int, fn: int) -> float:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    index = round((len(ordered) - 1) * probability)
    return ordered[index]


def parent_counts_by_case(
    claims: list[ClaimInstance], predictions: dict[str, str | None]
) -> list[tuple[int, int, int]]:
    grouped: dict[str, list[ClaimInstance]] = defaultdict(list)
    for claim in claims:
        grouped[claim.case_id].append(claim)
    counts: list[tuple[int, int, int]] = []
    for case_id in sorted(grouped):
        case_claims = grouped[case_id]
        true_edges = {
            (claim.claim_id, claim.observed_parents[0])
            for claim in case_claims
            if claim.observed_parents
        }
        predicted_edges = {
            (claim.claim_id, predictions[claim.claim_id])
            for claim in case_claims
            if predictions[claim.claim_id] is not None
        }
        counts.append((
            len(true_edges & predicted_edges),
            len(predicted_edges - true_edges),
            len(true_edges - predicted_edges),
        ))
    return counts


def bootstrap_parent_f1(counts: list[tuple[int, int, int]]) -> dict[str, float | int]:
    rng = random.Random(BOOTSTRAP_SEED)
    values: list[float] = []
    for _ in range(BOOTSTRAP_SAMPLES):
        sample = [counts[rng.randrange(len(counts))] for _ in counts]
        values.append(f1_from_counts(
            sum(item[0] for item in sample),
            sum(item[1] for item in sample),
            sum(item[2] for item in sample),
        ))
    return {
        "samples": BOOTSTRAP_SAMPLES,
        "seed": BOOTSTRAP_SEED,
        "lower95": percentile(values, 0.025),
        "upper95": percentile(values, 0.975),
    }


def run(source: Path) -> dict[str, object]:
    claims = [claim for claim in read_jsonl(source) if claim.split == "confirmatory"]
    rows: list[dict[str, object]] = []
    for fraction in FRACTIONS:
        observed = hide_edges(claims, fraction)
        parents = infer_parents(
            (claim.feature_view() for claim in observed), threshold=THRESHOLD
        )
        roots = roots_from_parents(parents)
        parent = parent_metrics(claims, parents)
        rows.append({
            "hiddenFraction": fraction,
            "parent": parent,
            "parentF1CaseBootstrap95": bootstrap_parent_f1(
                parent_counts_by_case(claims, parents)
            ),
            "rootPair": root_pair_metrics(claims, roots),
            "rootCount": root_count_metrics(claims, roots),
        })
    primary = next(row for row in rows if row["hiddenFraction"] == 0.40)
    supported = float(primary["parent"]["f1"]) > 0.50  # type: ignore[index]
    return {
        "schema": "minority-prophet.lir1-pheme-confirmatory.v1",
        "status": "confirmatory-complete",
        "claimBoundary": "Recovery of recorded PHEME reply-tree lineage, not causal evidence independence.",
        "threshold": THRESHOLD,
        "thresholdCommit": THRESHOLD_COMMIT,
        "normalizedInputSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "confirmatoryCases": len({claim.case_id for claim in claims}),
        "confirmatoryClaims": len(claims),
        "criterion": "exact-parent F1 > 0.50 at 40% hidden edges",
        "criterionSupported": supported,
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
