"""Aggregation baselines and the evidence-root verdict.

Use `aggregation.root_vote.verdict` for anything provenance-aware. It is the
function that corresponds to `F` in formal/PROOFS.md and to the compiled proofs
in formal/lean/.

`semantic.evidence_root_vote` is RETAINED VERBATIM and is NOT that function.
Its sha256 is bound by `results/los-inspired-v0.1.manifest.json` as canonical
evidence for EXPERIMENT-001, so it cannot be corrected in place without
falsifying a canonical record. Its known defects are recorded as CE-11 and
CE-12 in formal/COUNTEREXAMPLES.md: it resolves duplicate root IDs
first-writer-wins (making it order-dependent exactly when side separation
fails) and silently discards claims with no root. Do not use it for new work
and do not describe it as the aggregator the theorems are about.
"""

from .baselines import AggregationResult, majority_vote, weighted_vote
from .root_vote import (
    RootVerdict,
    RootedClaim,
    UnattributedPolicy,
    Verdict,
    tolerated_root_errors,
    verdict,
)
from .semantic import (
    SemanticResult,
    evidence_root_vote,
    proposition_majority,
    semantic_coalition,
)

__all__ = [
    "AggregationResult",
    "RootVerdict",
    "RootedClaim",
    "SemanticResult",
    "UnattributedPolicy",
    "Verdict",
    "evidence_root_vote",
    "majority_vote",
    "proposition_majority",
    "semantic_coalition",
    "tolerated_root_errors",
    "verdict",
    "weighted_vote",
]
