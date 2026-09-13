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
    """Weight each vote by declared confidence and known domain competence.

    **This is a baseline and its naivety is deliberate. Do not "fix" it.**

    It exists to represent what a reasonable person does, and to lose. Both of
    its inputs are `DepthBasis.DECLARED` on the independence ladder, whose own
    comment in `aggregation/independence_axes.py` reads: *"I was there." Free,
    therefore worthless alone.* So this weights by exactly what the corpus says
    carries no weight, and it scores 0.000 on the benchmark. That is the
    doctrine being demonstrated, not a defect to repair.

    Two real defects live nearby and are not repaired here either, because
    repairing them inside a baseline would make it stop being one:

    * A negative weight is silently clamped to zero, an implementation choice
      with no formal justification.
    * A zero-weight root is counted at full strength by the formal aggregator
      and at zero here, so the same corpus can yield two verdicts depending on
      which aggregator reads it.

    Both are recorded in `audit/falsify.py::weight_boundary_probe`, and the
    second must be reconciled before any weighted theorem is stated. Taken
    apart layer by layer in `canon/decompositions/weight.py`, where three
    layers -- lineage, authority and falsifiers -- come back empty.
    """
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
