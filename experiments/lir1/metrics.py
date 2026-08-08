"""LIR-1 parent, root, and aggregation metrics."""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import Iterable

from .model import ClaimInstance


def _prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def parent_metrics(
    claims: Iterable[ClaimInstance], predictions: dict[str, str | None]
) -> dict[str, float | int]:
    exact = {claim.claim_id: claim.observed_parents[0] if claim.observed_parents else None for claim in claims}
    evaluable = {
        claim.claim_id
        for claim in claims
        if claim.label_basis in {"constructed_exact", "explicit_edge", "adjudicated_lineage"}
        and claim.label_scope in {"direct_parent", "record_root"}
    }
    predicted_edges = {(child, parent) for child, parent in predictions.items() if child in evaluable and parent}
    true_edges = {(child, parent) for child, parent in exact.items() if child in evaluable and parent}
    values = _prf(len(predicted_edges & true_edges), len(predicted_edges - true_edges), len(true_edges - predicted_edges))
    return {"evaluable": len(evaluable), **values}


def root_pair_metrics(
    claims: Iterable[ClaimInstance], predicted_roots: dict[str, str]
) -> dict[str, float | int]:
    grouped: dict[tuple[str, str], list[ClaimInstance]] = defaultdict(list)
    for claim in claims:
        if claim.true_root_id is not None:
            grouped[(claim.dataset, claim.case_id)].append(claim)
    tp = fp = fn = pairs = 0
    for case_claims in grouped.values():
        for left, right in combinations(case_claims, 2):
            true_same = left.true_root_id == right.true_root_id
            predicted_same = predicted_roots[left.claim_id] == predicted_roots[right.claim_id]
            pairs += 1
            if true_same and predicted_same:
                tp += 1
            elif not true_same and predicted_same:
                fp += 1
            elif true_same and not predicted_same:
                fn += 1
    return {"pairs": pairs, **_prf(tp, fp, fn)}


def root_count_metrics(
    claims: Iterable[ClaimInstance], predicted_roots: dict[str, str]
) -> dict[str, float | int]:
    grouped: dict[tuple[str, str], list[ClaimInstance]] = defaultdict(list)
    for claim in claims:
        if claim.true_root_id is not None:
            grouped[(claim.dataset, claim.case_id)].append(claim)
    errors: list[int] = []
    for case_claims in grouped.values():
        true_count = len({claim.true_root_id for claim in case_claims})
        predicted_count = len({predicted_roots[claim.claim_id] for claim in case_claims})
        errors.append(abs(predicted_count - true_count))
    return {
        "cases": len(errors),
        "meanAbsoluteError": sum(errors) / len(errors) if errors else 0.0,
        "maxAbsoluteError": max(errors, default=0),
    }


def aggregation_accuracy(
    claims: Iterable[ClaimInstance], predicted_roots: dict[str, str]
) -> dict[str, float | int]:
    grouped: dict[tuple[str, str], list[ClaimInstance]] = defaultdict(list)
    for claim in claims:
        grouped[(claim.dataset, claim.case_id)].append(claim)

    correct = Counter()
    answered = Counter()
    brier_sum = Counter()
    for case_claims in grouped.values():
        truth_values = {claim.content_truth for claim in case_claims}
        if len(truth_values) != 1 or truth_values <= {"unresolved", "not_applicable"}:
            continue
        truth = truth_values.pop() == "true"
        methods: dict[str, dict[str, bool]] = {
            "majority": {claim.claim_id: bool(claim.channel_metadata["asserted_value"]) for claim in case_claims},
            "declared": {},
            "inferred": {},
        }
        for claim in case_claims:
            value = bool(claim.channel_metadata["asserted_value"])
            if claim.true_root_id is not None:
                methods["declared"].setdefault(claim.true_root_id, value)
            methods["inferred"].setdefault(predicted_roots[claim.claim_id], value)
        for method, votes in methods.items():
            ones = sum(votes.values())
            zeros = len(votes) - ones
            probability = ones / len(votes)
            brier_sum[method] += (probability - float(truth)) ** 2
            if ones == zeros:
                continue
            answered[method] += 1
            correct[method] += (ones > zeros) == truth

    result: dict[str, float | int] = {"eligible_cases": len(grouped)}
    for method in ("majority", "declared", "inferred"):
        result[f"{method}_answered"] = answered[method]
        result[f"{method}_accuracy"] = correct[method] / answered[method] if answered[method] else 0.0
        result[f"{method}_brier"] = brier_sum[method] / len(grouped) if grouped else 0.0
    majority = float(result["majority_accuracy"])
    declared = float(result["declared_accuracy"])
    inferred = float(result["inferred_accuracy"])
    result["declared_advantage_survival"] = (
        (inferred - majority) / (declared - majority) if declared > majority else None
    )
    return result
