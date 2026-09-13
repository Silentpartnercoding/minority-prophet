"""Adapt benchmark claims to the evidence-root verdict.

`benchmark.world` records lineage but the default suite never used it, so
`python -m benchmark` printed only the two baselines. Both score zero on these
worlds, which is the correct and intended result: 95 copies of one rumour
outvote 3 independent observers every time. Printed alone, two rows of zeroes
read as a broken program rather than as the finding.

This module resolves each claim to its evidence root and calls
`aggregation.root_vote.verdict`, the function the compiled proofs are about, so
the comparison appears next to the baselines that fail.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from aggregation.baselines import AggregationResult
from aggregation.root_vote import Verdict, verdict

from .world import Claim


@dataclass(frozen=True)
class _Rooted:
    """The `RootedClaim` shape, built from a benchmark claim."""

    value: bool
    root_id: str | None
    independence_basis: str | None = None
    witness_depth: str | None = None
    attestation: str | None = None
    witness_identity: str | None = None
    depth_basis: str | None = None


def resolve_root(claim: Claim, by_id: dict[str, Claim]) -> str | None:
    """Walk the copy chain to the evidence it ultimately rests on.

    An independent observation is its own root. A copy inherits the root of what
    it copied, however long the chain. A chain whose origin is not itself a
    recorded claim resolves to that origin id, which is how 95 repeaters collapse
    to the single rumour they all descend from.
    """
    seen: set[str] = set()
    current = claim
    while True:
        if current.copied_from is None:
            return current.evidence_id
        if current.claim_id in seen:
            return None  # a cycle is not a root; fail closed rather than guess
        seen.add(current.claim_id)
        parent = by_id.get(current.copied_from)
        if parent is None:
            return current.copied_from
        current = parent


def dependence_aware_vote(claims: Iterable[Claim]) -> AggregationResult:
    """Count distinct evidence roots per side instead of counting agents."""
    materialized = tuple(claims)
    by_id = {claim.claim_id: claim for claim in materialized}
    rooted = tuple(
        _Rooted(
            value=claim.value,
            root_id=resolve_root(claim, by_id),
            independence_basis="attested" if claim.independent else "inferred",
            attestation="attested" if claim.independent else "declared",
        )
        for claim in materialized
    )

    result = verdict(rooted)
    true_roots = float(len(result.support_true))
    false_roots = float(len(result.support_false))
    total = true_roots + false_roots
    belief = None if result.verdict is Verdict.ABSTAIN else result.verdict is Verdict.TRUE
    probability = 0.5 if total == 0 else true_roots / total
    return AggregationResult(
        belief=belief,
        probability_true=probability,
        support_true=true_roots,
        support_false=false_roots,
        method="dependence_aware",
    )
