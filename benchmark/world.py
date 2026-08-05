"""Deterministic synthetic worlds with independent truth and copied falsehood."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterable


@dataclass(frozen=True)
class Claim:
    claim_id: str
    agent_id: str
    value: bool
    confidence: float
    competence: float
    source_id: str
    copied_from: str | None
    evidence_id: str | None

    @property
    def independent(self) -> bool:
        return self.copied_from is None and self.evidence_id is not None


@dataclass(frozen=True)
class SyntheticWorld:
    world_id: str
    truth: bool
    claims: tuple[Claim, ...]
    independent_truth_count: int
    copied_false_count: int

    @property
    def minority_truth(self) -> bool:
        true_claims = sum(claim.value == self.truth for claim in self.claims)
        return true_claims < len(self.claims) - true_claims


def generate_world(
    *,
    seed: int,
    world_index: int = 0,
    independent_truth_count: int = 3,
    copied_false_count: int = 95,
    independent_accuracy: float = 0.98,
) -> SyntheticWorld:
    """Generate one benchmark world without consulting global random state."""
    if independent_truth_count < 1 or copied_false_count < 0:
        raise ValueError("world populations must be non-negative and include an observer")
    if not 0.0 <= independent_accuracy <= 1.0:
        raise ValueError("independent_accuracy must be between 0 and 1")

    rng = Random((seed << 32) + world_index)
    truth = bool(rng.getrandbits(1))
    world_id = f"mp-{seed}-{world_index:05d}"
    claims: list[Claim] = []

    for index in range(independent_truth_count):
        observed = truth if rng.random() < independent_accuracy else not truth
        claims.append(
            Claim(
                claim_id=f"{world_id}-ind-{index}",
                agent_id=f"observer-{index}",
                value=observed,
                confidence=0.90 + rng.random() * 0.09,
                competence=independent_accuracy,
                source_id=f"instrument-{index}",
                copied_from=None,
                evidence_id=f"evidence-{world_id}-{index}",
            )
        )

    false_value = not truth
    origin_id = f"{world_id}-rumor-origin"
    for index in range(copied_false_count):
        claims.append(
            Claim(
                claim_id=f"{world_id}-copy-{index}",
                agent_id=f"repeater-{index}",
                value=false_value,
                confidence=0.72 + rng.random() * 0.25,
                competence=0.50,
                source_id="social-feed",
                copied_from=origin_id if index == 0 else f"{world_id}-copy-{rng.randrange(index)}",
                evidence_id=None,
            )
        )

    rng.shuffle(claims)
    return SyntheticWorld(
        world_id,
        truth,
        tuple(claims),
        independent_truth_count,
        copied_false_count,
    )


def generate_worlds(*, count: int, seed: int, **kwargs: object) -> Iterable[SyntheticWorld]:
    if count < 1:
        raise ValueError("count must be positive")
    for index in range(count):
        yield generate_world(seed=seed, world_index=index, **kwargs)
