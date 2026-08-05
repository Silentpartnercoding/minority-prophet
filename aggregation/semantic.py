"""Finite semantic aggregation experiments inspired by ultraproduct semantics.

This is not an implementation of a literal ultraproduct.  It is a finite proxy
that (1) counts evidence roots rather than copies and (2) selects a submitted,
constraint-satisfying model rather than voting on propositions independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Callable, Iterable, Protocol


Assignment = tuple[bool, ...]
Constraint = Callable[[Assignment], bool]


class ModelClaim(Protocol):
    assignment: Assignment
    root_id: str | None
    confidence: float
    competence: float


@dataclass(frozen=True)
class SemanticResult:
    assignment: Assignment | None
    proposition_probabilities: tuple[float, ...]
    consistent: bool | None
    support_margin: float
    roots_used: int
    method: str


def _probabilities(assignments: list[Assignment]) -> tuple[float, ...]:
    if not assignments:
        return ()
    return tuple(
        sum(float(assignment[index]) for assignment in assignments) / len(assignments)
        for index in range(len(assignments[0]))
    )


def proposition_majority(
    claims: Iterable[ModelClaim], constraint: Constraint
) -> SemanticResult:
    """Vote independently on each proposition, ignoring lineage."""
    materialized = list(claims)
    probabilities = _probabilities([claim.assignment for claim in materialized])
    assignment = tuple(probability > 0.5 for probability in probabilities)
    tied = any(probability == 0.5 for probability in probabilities)
    return SemanticResult(
        None if tied else assignment,
        probabilities,
        None if tied else constraint(assignment),
        0.0,
        len(materialized),
        "proposition_majority",
    )


def evidence_root_vote(
    claims: Iterable[ModelClaim], constraint: Constraint
) -> SemanticResult:
    """Count each attributable evidence root once, then vote proposition-wise."""
    roots: dict[str, ModelClaim] = {}
    for claim in claims:
        if claim.root_id is not None:
            roots.setdefault(claim.root_id, claim)
    probabilities = _probabilities([claim.assignment for claim in roots.values()])
    if not probabilities:
        return SemanticResult(None, (), None, 0.0, 0, "evidence_root_vote")
    assignment = tuple(probability > 0.5 for probability in probabilities)
    tied = any(probability == 0.5 for probability in probabilities)
    return SemanticResult(
        None if tied else assignment,
        probabilities,
        None if tied else constraint(assignment),
        0.0,
        len(roots),
        "evidence_root_vote",
    )


def semantic_coalition(
    claims: Iterable[ModelClaim],
    constraint: Constraint,
    *,
    abstain_margin: float = 0.05,
) -> SemanticResult:
    """Select a supported, submitted, logically valid model.

    Duplicate root IDs contribute once.  Candidate models must have been
    submitted by an attributable root and satisfy the public constraint.  A
    candidate is scored by confidence/competence-weighted agreement with all
    roots.  Close contests abstain.
    """
    roots: dict[str, ModelClaim] = {}
    for claim in claims:
        if claim.root_id is not None:
            roots.setdefault(claim.root_id, claim)
    rooted = list(roots.values())
    candidates = sorted(
        {claim.assignment for claim in rooted if constraint(claim.assignment)}
    )
    if not candidates:
        return SemanticResult(None, (), None, 0.0, len(rooted), "semantic_coalition")

    def weight(claim: ModelClaim) -> float:
        return max(0.0, min(1.0, claim.confidence)) * max(
            0.0, min(1.0, claim.competence)
        )

    def score(candidate: Assignment) -> float:
        return sum(
            weight(claim)
            * sum(a == b for a, b in zip(candidate, claim.assignment, strict=True))
            / len(candidate)
            for claim in rooted
        )

    ranked = sorted(((score(candidate), candidate) for candidate in candidates), reverse=True)
    best_score, best = ranked[0]
    runner_up = ranked[1][0] if len(ranked) > 1 else 0.0
    total_weight = sum(weight(claim) for claim in rooted) or 1.0
    margin = (best_score - runner_up) / total_weight

    score_total = sum(exp(item[0]) for item in ranked)
    probabilities = tuple(
        sum(exp(candidate_score) for candidate_score, candidate in ranked if candidate[index])
        / score_total
        for index in range(len(best))
    )
    if margin < abstain_margin:
        return SemanticResult(
            None, probabilities, None, margin, len(rooted), "semantic_coalition"
        )
    return SemanticResult(
        best, probabilities, True, margin, len(rooted), "semantic_coalition"
    )
