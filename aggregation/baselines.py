"""Transparent reference baselines for binary claims."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


class ClaimLike(Protocol):
    value: bool
    confidence: float
    competence: float


@dataclass(frozen=True)
class AggregationResult:
    belief: bool | None
    probability_true: float
    support_true: float
    support_false: float
    method: str


def _finish(true_mass: float, false_mass: float, method: str) -> AggregationResult:
    total = true_mass + false_mass
    probability = 0.5 if total == 0 else true_mass / total
    belief = None if true_mass == false_mass else true_mass > false_mass
    return AggregationResult(belief, probability, true_mass, false_mass, method)


def majority_vote(claims: Iterable[ClaimLike]) -> AggregationResult:
    """Count agents equally, intentionally ignoring confidence and lineage."""
    values = [claim.value for claim in claims]
    return _finish(float(sum(values)), float(len(values) - sum(values)), "majority")


def weighted_vote(claims: Iterable[ClaimLike]) -> AggregationResult:
    """Weight each vote by declared confidence and known domain competence."""
    true_mass = 0.0
    false_mass = 0.0
    for claim in claims:
        weight = max(0.0, min(1.0, claim.confidence)) * max(
            0.0, min(1.0, claim.competence)
        )
        if claim.value:
            true_mass += weight
        else:
            false_mass += weight
    return _finish(true_mass, false_mass, "weighted")
