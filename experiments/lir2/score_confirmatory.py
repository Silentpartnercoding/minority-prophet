"""Frozen confirmatory scorer for LIR-2 precision-constrained root coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from experiments.lir1.llm_echo.score_confirmatory import (
    aggregation_outcomes_by_case,
    metrics_at as lir1_metrics_at,
    root_pair_counts_by_case,
)
from experiments.lir1.llm_echo.score_development import source_adherence, usage_summary
from experiments.lir1.metrics import aggregation_accuracy, root_count_metrics, root_pair_metrics
from experiments.lir1.model import ClaimInstance, read_jsonl
from experiments.lir1.run_pheme_confirmatory import f1_from_counts, percentile
from experiments.lir1.synthetic_fixture import hide_edges
from experiments.lir2.root_grouping import infer_roots


THRESHOLD = 0.75
LIR1_BASELINE_THRESHOLD = 0.85
BOOTSTRAP_SEED = 20260808
BOOTSTRAP_SAMPLES = 10_000
REQUESTS_SHA256 = "55ee08cbd2bf4362b8ac1584abb2da41e0c9fb9a49da3dd28bf45084b8a61b49"
LABELS_SHA256 = "13b2b9348b7f97d5f6fe9d08d7e7cb4ebf3646d21a21ff6dc7018df8a8eb6eca"


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall, f1_from_counts(tp, fp, fn)


def bootstrap_metrics(
    claims: list[ClaimInstance], roots: dict[str, str]
) -> dict[str, Any]:
    root_counts = root_pair_counts_by_case(claims, roots)
    outcomes = aggregation_outcomes_by_case(claims, roots)
    case_ids = sorted(root_counts)
    rng = random.Random(BOOTSTRAP_SEED)
    values: dict[str, list[float]] = {
        "rootPrecision": [], "rootRecall": [], "rootF1": [],
        "coverage": [], "accuracyAnswered": [], "allCaseCorrectYield": [],
    }
    for _ in range(BOOTSTRAP_SAMPLES):
        sample = [case_ids[rng.randrange(len(case_ids))] for _ in case_ids]
        counts = [root_counts[case_id] for case_id in sample]
        precision, recall, f1 = _prf(
            sum(row[0] for row in counts), sum(row[1] for row in counts), sum(row[2] for row in counts)
        )
        correct = sum(outcomes[case_id]["inferred"][0] for case_id in sample)
        answered = sum(outcomes[case_id]["inferred"][1] for case_id in sample)
        values["rootPrecision"].append(precision)
        values["rootRecall"].append(recall)
        values["rootF1"].append(f1)
        values["coverage"].append(answered / len(sample))
        values["accuracyAnswered"].append(correct / answered if answered else 0.0)
        values["allCaseCorrectYield"].append(correct / len(sample))
    return {
        "samples": BOOTSTRAP_SAMPLES,
        "seed": BOOTSTRAP_SEED,
        "intervals95": {
            key: {"lower": percentile(series, 0.025), "upper": percentile(series, 0.975)}
            for key, series in values.items()
        },
    }


def score(
    claims_path: Path, responses_path: Path, requests_path: Path, labels_path: Path
) -> dict[str, Any]:
    if hashlib.sha256(requests_path.read_bytes()).hexdigest() != REQUESTS_SHA256:
        raise ValueError("request file does not match the frozen LIR-2 holdout")
    if hashlib.sha256(labels_path.read_bytes()).hexdigest() != LABELS_SHA256:
        raise ValueError("label file does not match the frozen LIR-2 holdout")
    claims = read_jsonl(claims_path)
    case_count = len({claim.case_id for claim in claims})
    if case_count != 36 or len(claims) != 432:
        raise ValueError("LIR-2 requires exactly 36 complete cases and 432 claims")
    visible = hide_edges(claims, 0.40)
    roots = infer_roots((claim.feature_view() for claim in visible), threshold=THRESHOLD)
    pair = root_pair_metrics(claims, roots)
    aggregation = aggregation_accuracy(claims, roots)
    answered = int(aggregation["inferred_answered"])
    correct = int(round(float(aggregation["inferred_accuracy"]) * answered))
    coverage = answered / case_count
    all_case_yield = correct / case_count
    criterion = {
        "minimumCases": 30,
        "zeroFalseRootMerges": pair["precision"] == 1.0,
        "minimumRootRecall": 0.80,
        "minimumCoverage": 0.80,
        "minimumAccuracyAnswered": 0.80,
        "minimumAllCaseCorrectYield": 0.65,
    }
    criterion["supported"] = (
        case_count >= 30
        and criterion["zeroFalseRootMerges"]
        and pair["recall"] >= criterion["minimumRootRecall"]
        and coverage >= criterion["minimumCoverage"]
        and aggregation["inferred_accuracy"] >= criterion["minimumAccuracyAnswered"]
        and all_case_yield >= criterion["minimumAllCaseCorrectYield"]
    )
    baseline, _ = lir1_metrics_at(claims, 0.40)
    return {
        "schema": "minority-prophet.lir2-confirmatory-result.v1",
        "status": "confirmatory-complete",
        "threshold": THRESHOLD,
        "caseCount": case_count,
        "claimCount": len(claims),
        "hiddenFraction": 0.40,
        "criterion": criterion,
        "rootPair": pair,
        "rootCount": root_count_metrics(claims, roots),
        "aggregation": aggregation,
        "coverage": coverage,
        "abstentions": case_count - answered,
        "correctAnswered": correct,
        "allCaseCorrectYield": all_case_yield,
        "bootstrap": bootstrap_metrics(claims, roots),
        "lir1ParentBaselineSameCases": baseline,
        "sourceAdherence": source_adherence(requests_path, responses_path, labels_path),
        "usage": usage_summary(responses_path),
        "billing": {"mode": "subscription", "incrementalUsdRecorded": 0},
        "inputs": {
            "claimsSha256": hashlib.sha256(claims_path.read_bytes()).hexdigest(),
            "responsesSha256": hashlib.sha256(responses_path.read_bytes()).hexdigest(),
            "requestsSha256": REQUESTS_SHA256,
            "constructionLabelsSha256": LABELS_SHA256,
        },
        "interpretationBoundary": "Constructed record-root coverage under frozen conditions; not causal evidence independence or real-world truth performance.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claims", required=True, type=Path)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--requests", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = score(args.claims, args.responses, args.requests, args.labels)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "criterionSupported": result["criterion"]["supported"],
        "outputSha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
