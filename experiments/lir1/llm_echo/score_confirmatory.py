"""Frozen confirmatory scorer for the controlled LIR-1E echo corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from experiments.lir1.infer import infer_parents, roots_from_parents
from experiments.lir1.metrics import aggregation_accuracy, parent_metrics, root_count_metrics, root_pair_metrics
from experiments.lir1.model import ClaimInstance, read_jsonl
from experiments.lir1.run_boundary import FRACTIONS
from experiments.lir1.run_pheme_confirmatory import f1_from_counts, percentile
from experiments.lir1.synthetic_fixture import hide_edges
from experiments.lir1.llm_echo.score_development import hidden_ids, source_adherence, usage_summary


THRESHOLD = 0.85
BOOTSTRAP_SEED = 20260808
BOOTSTRAP_SAMPLES = 10_000


def root_pair_counts_by_case(
    claims: list[ClaimInstance], predicted_roots: dict[str, str]
) -> dict[str, tuple[int, int, int]]:
    grouped: dict[str, list[ClaimInstance]] = defaultdict(list)
    for claim in claims:
        grouped[claim.case_id].append(claim)
    result = {}
    for case_id, rows in grouped.items():
        tp = fp = fn = 0
        for left, right in combinations(rows, 2):
            true_same = left.true_root_id == right.true_root_id
            predicted_same = predicted_roots[left.claim_id] == predicted_roots[right.claim_id]
            if true_same and predicted_same:
                tp += 1
            elif not true_same and predicted_same:
                fp += 1
            elif true_same and not predicted_same:
                fn += 1
        result[case_id] = (tp, fp, fn)
    return result


def aggregation_outcomes_by_case(
    claims: list[ClaimInstance], predicted_roots: dict[str, str]
) -> dict[str, dict[str, tuple[int, int]]]:
    grouped: dict[str, list[ClaimInstance]] = defaultdict(list)
    for claim in claims:
        grouped[claim.case_id].append(claim)
    result = {}
    for case_id, rows in grouped.items():
        truth = rows[0].content_truth == "true"
        methods: dict[str, dict[str, bool]] = {
            "majority": {row.claim_id: bool(row.channel_metadata["asserted_value"]) for row in rows},
            "declared": {},
            "inferred": {},
        }
        for row in rows:
            value = bool(row.channel_metadata["asserted_value"])
            methods["declared"].setdefault(row.true_root_id or row.claim_id, value)
            methods["inferred"].setdefault(predicted_roots[row.claim_id], value)
        case = {}
        for method, votes in methods.items():
            ones = sum(votes.values())
            zeros = len(votes) - ones
            answered = int(ones != zeros)
            correct = int(answered and ((ones > zeros) == truth))
            case[method] = (correct, answered)
        result[case_id] = case
    return result


def bootstrap_primary(
    claims: list[ClaimInstance], predicted_roots: dict[str, str]
) -> dict[str, Any]:
    root_counts = root_pair_counts_by_case(claims, predicted_roots)
    aggregation = aggregation_outcomes_by_case(claims, predicted_roots)
    case_ids = sorted(root_counts)
    rng = random.Random(BOOTSTRAP_SEED)
    root_values: list[float] = []
    survival_values: list[float] = []
    undefined = 0
    for _ in range(BOOTSTRAP_SAMPLES):
        sample = [case_ids[rng.randrange(len(case_ids))] for _ in case_ids]
        counts = [root_counts[case_id] for case_id in sample]
        root_values.append(f1_from_counts(
            sum(row[0] for row in counts), sum(row[1] for row in counts), sum(row[2] for row in counts)
        ))
        accuracies = {}
        for method in ("majority", "declared", "inferred"):
            correct = sum(aggregation[case_id][method][0] for case_id in sample)
            answered = sum(aggregation[case_id][method][1] for case_id in sample)
            accuracies[method] = correct / answered if answered else 0.0
        denominator = accuracies["declared"] - accuracies["majority"]
        if denominator > 0:
            survival_values.append((accuracies["inferred"] - accuracies["majority"]) / denominator)
        else:
            undefined += 1
    survival_interval = {
        "definedSamples": len(survival_values),
        "undefinedSamples": undefined,
        "lower95": percentile(survival_values, 0.025) if survival_values else None,
        "upper95": percentile(survival_values, 0.975) if survival_values else None,
    }
    return {
        "samples": BOOTSTRAP_SAMPLES,
        "seed": BOOTSTRAP_SEED,
        "rootPairF1": {
            "lower95": percentile(root_values, 0.025),
            "upper95": percentile(root_values, 0.975),
        },
        "declaredAdvantageSurvival": survival_interval,
    }


def metrics_at(
    truth: list[ClaimInstance], fraction: float, *, ablation: str | None = None
) -> tuple[dict[str, Any], dict[str, str]]:
    visible = hide_edges(truth, fraction)
    hidden = hidden_ids(truth, visible)
    features = []
    for claim in visible:
        feature = claim.feature_view()
        if ablation == "no-text":
            feature["text"] = None
        elif ablation == "no-time":
            feature["timestamp"] = None
        features.append(feature)
    parents = infer_parents(features, threshold=THRESHOLD)
    roots = roots_from_parents(parents)
    return ({
        "hiddenFraction": fraction,
        "hiddenEdgeCount": len(hidden),
        "parent": parent_metrics(truth, parents, evaluate_claim_ids=hidden),
        "rootPair": root_pair_metrics(truth, roots),
        "rootCount": root_count_metrics(truth, roots),
        "aggregation": aggregation_accuracy(truth, roots),
    }, roots)


def score(
    claims_path: Path, responses_path: Path, requests_path: Path, labels_path: Path
) -> dict[str, Any]:
    truth = read_jsonl(claims_path)
    if {row.split for row in truth} != {"confirmatory"}:
        raise ValueError("confirmatory scorer refuses non-confirmatory claims")
    rows = []
    primary_roots = None
    for fraction in FRACTIONS:
        metrics, roots = metrics_at(truth, fraction)
        rows.append(metrics)
        if fraction == 0.40:
            primary_roots = roots
    if primary_roots is None:
        raise RuntimeError("registered primary fraction is absent")
    primary = next(row for row in rows if row["hiddenFraction"] == 0.40)
    bootstrap = bootstrap_primary(truth, primary_roots)
    lower_survival = bootstrap["declaredAdvantageSurvival"]["lower95"]
    complete_cases = len({row.case_id for row in truth})
    supported = (
        complete_cases >= 30
        and primary["rootPair"]["f1"] >= 0.60
        and lower_survival is not None
        and lower_survival > 0.25
    )
    no_text, _ = metrics_at(truth, 0.40, ablation="no-text")
    no_time, _ = metrics_at(truth, 0.40, ablation="no-time")
    return {
        "schema": "minority-prophet.lir1e-confirmatory-result.v1",
        "status": "confirmatory-complete",
        "threshold": THRESHOLD,
        "caseCount": complete_cases,
        "claimCount": len(truth),
        "primaryFraction": 0.40,
        "criterion": {
            "minimumCases": 30,
            "minimumRootPairF1": 0.60,
            "strictMinimumSurvivalLower95": 0.25,
            "supported": supported,
        },
        "primary": primary,
        "primaryBootstrap": bootstrap,
        "fractions": rows,
        "ablationsAtPrimary": {"noText": no_text, "noTime": no_time},
        "sourceAdherence": source_adherence(requests_path, responses_path, labels_path),
        "usage": usage_summary(responses_path),
        "billing": {"mode": "subscription", "incrementalUsdRecorded": 0},
        "inputs": {
            "claimsSha256": hashlib.sha256(claims_path.read_bytes()).hexdigest(),
            "responsesSha256": hashlib.sha256(responses_path.read_bytes()).hexdigest(),
            "requestsSha256": hashlib.sha256(requests_path.read_bytes()).hexdigest(),
            "constructionLabelsSha256": hashlib.sha256(labels_path.read_bytes()).hexdigest(),
        },
        "interpretationBoundary": "Constructed record-root recovery under frozen conditions; not proof of causal evidence independence or general truth inference.",
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
