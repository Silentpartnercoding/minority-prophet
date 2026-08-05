"""Public aggregation baselines."""

from .baselines import AggregationResult, majority_vote, weighted_vote
from .semantic import (
    SemanticResult,
    evidence_root_vote,
    proposition_majority,
    semantic_coalition,
)

__all__ = [
    "AggregationResult",
    "SemanticResult",
    "evidence_root_vote",
    "majority_vote",
    "proposition_majority",
    "semantic_coalition",
    "weighted_vote",
]
