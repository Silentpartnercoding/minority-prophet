"""Metrics and benchmark harness."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter_ns
from typing import Callable, Iterable

from aggregation import AggregationResult, majority_vote, weighted_vote

from .world import SyntheticWorld


Aggregator = Callable[[Iterable[object]], AggregationResult]


@dataclass(frozen=True)
class Metrics:
    method: str
    worlds: int
    truth_accuracy: float
    minority_truth_recovery: float
    brier_score: float
    abstention_rate: float
    mean_compute_microseconds: float


def evaluate(
    worlds: Iterable[SyntheticWorld],
    methods: dict[str, Aggregator] | None = None,
) -> list[dict[str, object]]:
    """Evaluate methods on the same materialized set of worlds."""
    suite = methods or {"majority": majority_vote, "weighted": weighted_vote}
    materialized = tuple(worlds)
    if not materialized:
        raise ValueError("at least one world is required")

    reports: list[dict[str, object]] = []
    for name, method in suite.items():
        correct = 0
        minority_correct = 0
        minority_total = 0
        abstentions = 0
        squared_error = 0.0
        elapsed_ns = 0
        for world in materialized:
            started = perf_counter_ns()
            result = method(world.claims)
            elapsed_ns += perf_counter_ns() - started
            correct += result.belief == world.truth
            abstentions += result.belief is None
            squared_error += (result.probability_true - float(world.truth)) ** 2
            if world.minority_truth:
                minority_total += 1
                minority_correct += result.belief == world.truth

        metric = Metrics(
            method=name,
            worlds=len(materialized),
            truth_accuracy=correct / len(materialized),
            minority_truth_recovery=(minority_correct / minority_total if minority_total else 0.0),
            brier_score=squared_error / len(materialized),
            abstention_rate=abstentions / len(materialized),
            mean_compute_microseconds=elapsed_ns / len(materialized) / 1_000,
        )
        reports.append(asdict(metric))
    return reports
