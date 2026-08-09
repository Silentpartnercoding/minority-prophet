"""No-retuning LIR-2 transfer scorer for the recorded PHEME-R2 corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from experiments.lir1.llm_echo.score_confirmatory import root_pair_counts_by_case
from experiments.lir1.metrics import root_count_metrics, root_pair_metrics
from experiments.lir1.model import ClaimInstance, read_jsonl
from experiments.lir1.run_boundary import FRACTIONS
from experiments.lir1.run_pheme_confirmatory import f1_from_counts, percentile
from experiments.lir1.synthetic_fixture import hide_edges
from experiments.lir2.root_grouping import infer_roots


THRESHOLD = 0.75
INPUT_SHA256 = "1c3e9e08149021cdb81da02b96750d75e0f0dce1dd7432bf5f7613fb206a2266"
BOOTSTRAP_SEED = 20260808
BOOTSTRAP_SAMPLES = 10_000


def root_errors_by_case(
    claims: list[ClaimInstance], roots: dict[str, str]
) -> dict[str, int]:
    grouped: dict[str, list[ClaimInstance]] = defaultdict(list)
    for claim in claims:
        grouped[claim.case_id].append(claim)
    return {
        case_id: abs(
            len({claim.true_root_id for claim in rows})
            - len({roots[claim.claim_id] for claim in rows})
        )
        for case_id, rows in grouped.items()
    }


def bootstrap(
    claims: list[ClaimInstance], roots: dict[str, str]
) -> dict[str, Any]:
    pair_counts = root_pair_counts_by_case(claims, roots)
    errors = root_errors_by_case(claims, roots)
    case_ids = sorted(pair_counts)
    rng = random.Random(BOOTSTRAP_SEED)
    precision_values: list[float] = []
    recall_values: list[float] = []
    f1_values: list[float] = []
    mae_values: list[float] = []
    for _ in range(BOOTSTRAP_SAMPLES):
        sample = [case_ids[rng.randrange(len(case_ids))] for _ in case_ids]
        counts = [pair_counts[case_id] for case_id in sample]
        tp = sum(row[0] for row in counts)
        fp = sum(row[1] for row in counts)
        fn = sum(row[2] for row in counts)
        precision_values.append(tp / (tp + fp) if tp + fp else 0.0)
        recall_values.append(tp / (tp + fn) if tp + fn else 0.0)
        f1_values.append(f1_from_counts(tp, fp, fn))
        mae_values.append(sum(errors[case_id] for case_id in sample) / len(sample))
    return {
        "samples": BOOTSTRAP_SAMPLES,
        "seed": BOOTSTRAP_SEED,
        "intervals95": {
            "rootPrecision": {"lower": percentile(precision_values, 0.025), "upper": percentile(precision_values, 0.975)},
            "rootRecall": {"lower": percentile(recall_values, 0.025), "upper": percentile(recall_values, 0.975)},
            "rootF1": {"lower": percentile(f1_values, 0.025), "upper": percentile(f1_values, 0.975)},
            "rootCountMae": {"lower": percentile(mae_values, 0.025), "upper": percentile(mae_values, 0.975)},
        },
    }


def score_at(claims: list[ClaimInstance], fraction: float) -> tuple[dict[str, Any], dict[str, str]]:
    visible = hide_edges(claims, fraction)
    roots = infer_roots((claim.feature_view() for claim in visible), threshold=THRESHOLD)
    return ({
        "hiddenFraction": fraction,
        "rootPair": root_pair_metrics(claims, roots),
        "rootCount": root_count_metrics(claims, roots),
    }, roots)


def score(source: Path) -> dict[str, Any]:
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash != INPUT_SHA256:
        raise ValueError("source does not match the frozen PHEME-R2 input")
    claims = read_jsonl(source)
    rows = []
    primary_roots = None
    for fraction in FRACTIONS:
        row, roots = score_at(claims, fraction)
        rows.append(row)
        if fraction == 0.40:
            primary_roots = roots
    primary = next(row for row in rows if row["hiddenFraction"] == 0.40)
    if primary_roots is None:
        raise RuntimeError("primary roots missing")
    pair = primary["rootPair"]
    count = primary["rootCount"]
    supported = (
        pair["precision"] >= 0.99
        and pair["recall"] >= 0.45
        and pair["f1"] >= 0.60
        and count["meanAbsoluteError"] < 4.0
    )
    return {
        "schema": "minority-prophet.lir2-pheme-transfer.v1",
        "status": "transfer-complete",
        "threshold": THRESHOLD,
        "caseCount": len({claim.case_id for claim in claims}),
        "claimCount": len(claims),
        "labelBoundary": "Recorded PHEME reply-tree roots; not causal evidence independence.",
        "criterion": {
            "minimumRootPrecision": 0.99,
            "minimumRootRecall": 0.45,
            "minimumRootF1": 0.60,
            "strictMaximumRootCountMae": 4.0,
            "supported": supported,
        },
        "knownLir1Comparator": {
            "rootPrecision": 0.9990288905074047,
            "rootRecall": 0.2255733894662983,
            "rootF1": 0.36804493457475823,
            "rootCountMae": 4.931034482758621,
        },
        "primary": primary,
        "primaryBootstrap": bootstrap(claims, primary_roots),
        "fractions": rows,
        "normalizedInputSha256": source_hash,
        "interpretationBoundary": "Prospective fixed-method transfer on a previously studied corpus, not a new independent dataset holdout.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = score(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "criterionSupported": result["criterion"]["supported"],
        "outputSha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
