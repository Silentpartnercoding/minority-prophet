"""AID-1 world: every named support criterion has a family that can fail it.

Claude named the policy, the four arms, and the five support criteria before
any world existed. This world is written by the adversarial review, not by
the author of the policy. It contains the six families the spec asked for,
constructed so the criteria can lose rather than so the policy can look cheap.

The load-bearing hole is in the policy itself: two witnesses who check
`ancestry_complete` on an empty ancestry record are granted independence
against every error class, including fabrication. Backing is never consulted
once that box is ticked. A hidden pair that can fill in a form is therefore
indistinguishable from two honest attesters, and at adoption rate 1 they
restore the exact defect the policy claimed to close.

Families:

- **honest_unattestable** — genuine independents who went to the world and
  left nothing. They cannot attest. The policy discounts them forever. Every
  settlement it loses here is a correct one.
- **hidden_source** — DR3's case. Two copies of one hidden parent, nothing
  recorded. They can fill the same form the honest attesters fill, at the
  same rate α. At α = 1 the policy grants them independence.
- **adversary_attests** — the copies always declare REALITY and complete
  ancestry, with no backing and no holdable identity. `attested` and
  `attested_declared_only` both take the short-circuit. Theatre.
- **robust_correct** — six backed independents, nothing hidden. Reflexive
  discounting is pure loss; at α = 1 the policy should match the ladder.
- **minority_suppression** — the true side is two unattestable witnesses;
  the false side is two backed attesters. Ladder ties and abstains. Using
  the policy to settle is the attack the scope comment forbids.
- **mixed_attestation** — attestable, unattestable, and hidden copies in
  one decision. A rule that only works when everyone is attested or no one
  is has not been tested.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import random
from collections.abc import Iterable, Mapping
from typing import Any

from aggregation.independence_axes import DepthBasis, WitnessDepth, WitnessIdentity
from aggregation.attested_independence import Witness
from canon.proximity import ErrorClass

FAMILIES = (
    "honest_unattestable",
    "hidden_source",
    "adversary_attests",
    "robust_correct",
    "minority_suppression",
    "mixed_attestation",
)
DEPENDENCE_FAMILIES = ("hidden_source",)
THEATRE_FAMILIES = ("adversary_attests",)
SUPPRESSION_FAMILIES = ("minority_suppression",)
COST_TRAP_FAMILIES = ("honest_unattestable", "robust_correct")

SETTLED_TRUE = "settled_true"
SETTLED_FALSE = "settled_false"
ABSTAIN = "abstain"
SETTLED = (SETTLED_TRUE, SETTLED_FALSE)
REVERSIBLE = "low_reversible"


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


@dataclasses.dataclass(frozen=True)
class Source:
    source_id: str
    accuracy: float
    component: str | None
    can_attest: bool
    always_attest: bool
    claimed: WitnessDepth
    depth_basis: DepthBasis
    identity: WitnessIdentity
    ancestry: frozenset[str]
    markers: frozenset[str]
    role: str


@dataclasses.dataclass(frozen=True)
class RealizedWitness:
    source_id: str
    vote: bool
    unit: str
    adopted: bool
    witness: Witness
    role: str


@dataclasses.dataclass(frozen=True)
class Decision:
    decision_id: str
    truth: bool
    threshold: int
    decision_class: str
    witnesses: tuple[RealizedWitness, ...]
    reference: str
    mixed: bool


@dataclasses.dataclass(frozen=True)
class Campaign:
    campaign_id: str
    family: str
    sources: tuple[Source, ...]
    focus_group: tuple[str, ...]
    decisions: tuple[Decision, ...]


def _honest_attestable(source_id: str, accuracy: float) -> Source:
    return Source(
        source_id,
        accuracy,
        None,
        True,
        False,
        WitnessDepth.REALITY,
        DepthBasis.DEVICE_ATTESTED,
        WitnessIdentity.VERIFIED,
        frozenset(),
        frozenset(),
        "attestable",
    )


def _honest_unattestable(source_id: str, accuracy: float) -> Source:
    return Source(
        source_id,
        accuracy,
        None,
        False,
        False,
        WitnessDepth.REALITY,
        DepthBasis.DECLARED,
        WitnessIdentity.ANONYMOUS,
        frozenset(),
        frozenset(),
        "unattestable",
    )


def _hidden_copy(source_id: str, accuracy: float, *, always_attest: bool) -> Source:
    return Source(
        source_id,
        accuracy,
        "hidden:u",
        True,
        always_attest,
        WitnessDepth.REALITY,
        DepthBasis.DECLARED,
        WitnessIdentity.ANONYMOUS,
        frozenset(),
        frozenset(),
        "hidden",
    )


def _layout(config: Mapping[str, Any], family: str, rng: random.Random) -> tuple[tuple[Source, ...], tuple[str, ...]]:
    accuracies = tuple(config["source_accuracies"])
    high = max(accuracies)
    mid = accuracies[len(accuracies) // 2]
    n_ind = config["independents_per_campaign"]
    if family == "honest_unattestable":
        sources = tuple(_honest_unattestable(f"u{i}", high) for i in range(5))
        return sources, ()
    if family == "hidden_source":
        group = tuple(_hidden_copy(f"g{i}", rng.choice(accuracies), always_attest=False) for i in range(2))
        rest = tuple(_honest_attestable(f"i{i}", rng.choice(accuracies)) for i in range(n_ind))
        return group + rest, tuple(s.source_id for s in group)
    if family == "adversary_attests":
        group = tuple(_hidden_copy(f"g{i}", rng.choice(accuracies), always_attest=True) for i in range(2))
        rest = tuple(_honest_attestable(f"i{i}", rng.choice(accuracies)) for i in range(n_ind))
        return group + rest, tuple(s.source_id for s in group)
    if family == "robust_correct":
        sources = tuple(_honest_attestable(f"i{i}", high) for i in range(6))
        return sources, ()
    if family == "minority_suppression":
        majority = tuple(_honest_attestable(f"m{i}", mid) for i in range(2))
        minority = tuple(_honest_unattestable(f"n{i}", high) for i in range(2))
        return majority + minority, tuple(s.source_id for s in minority)
    if family == "mixed_attestation":
        hidden = tuple(_hidden_copy(f"g{i}", rng.choice(accuracies), always_attest=False) for i in range(2))
        attestable = tuple(_honest_attestable(f"a{i}", rng.choice(accuracies)) for i in range(2))
        silent = tuple(_honest_unattestable(f"u{i}", high) for i in range(2))
        return hidden + attestable + silent, tuple(s.source_id for s in hidden)
    raise ValueError(f"unknown family {family}")


def _adopts(source: Source, alpha: float, rng: random.Random) -> bool:
    if source.always_attest:
        return True
    if not source.can_attest:
        return False
    return rng.random() < alpha


def _realize(source: Source, vote: bool, adopted: bool) -> RealizedWitness:
    return RealizedWitness(
        source_id=source.source_id,
        vote=vote,
        unit=source.component or source.source_id,
        adopted=adopted,
        witness=Witness(
            name=source.source_id,
            claimed=source.claimed,
            depth_basis=source.depth_basis,
            identity=source.identity,
            ancestry=source.ancestry,
            markers=source.markers,
            ancestry_complete=adopted,
        ),
        role=source.role,
    )


def _ordinary_votes(
    sources: tuple[Source, ...], truth: bool, rng: random.Random, config: Mapping[str, Any]
) -> dict[str, bool]:
    faulty = {
        component: rng.random() < config["component_fault_rate"]
        for component in sorted({s.component for s in sources if s.component})
    }
    votes = {}
    for source in sources:
        if source.component and faulty[source.component]:
            votes[source.source_id] = not truth
        else:
            votes[source.source_id] = truth if rng.random() < source.accuracy else not truth
    return votes


def _forced_minority_votes(sources: tuple[Source, ...], truth: bool) -> dict[str, bool]:
    votes = {}
    for source in sources:
        votes[source.source_id] = truth if source.role == "unattestable" else (not truth)
    return votes


def _count_units(realized: tuple[RealizedWitness, ...], side: bool) -> int:
    return len({item.unit for item in realized if item.vote is side})


def reference_settlement(realized: tuple[RealizedWitness, ...], threshold: int) -> str:
    n_true = _count_units(realized, True)
    n_false = _count_units(realized, False)
    if n_true >= threshold and n_true > n_false:
        return SETTLED_TRUE
    if n_false >= threshold and n_false > n_true:
        return SETTLED_FALSE
    return ABSTAIN


def is_mixed(realized: tuple[RealizedWitness, ...]) -> bool:
    adopted = {item.adopted for item in realized}
    return True in adopted and False in adopted


def _decision(
    config: Mapping[str, Any],
    campaign: str,
    index: int,
    sources: tuple[Source, ...],
    family: str,
    alpha: float,
    rng: random.Random,
) -> Decision:
    truth = True if family == "minority_suppression" else bool(rng.getrandbits(1))
    if family == "minority_suppression":
        votes = _forced_minority_votes(sources, truth)
    else:
        votes = _ordinary_votes(sources, truth, rng, config)
    realized = tuple(
        _realize(source, votes[source.source_id], _adopts(source, alpha, rng)) for source in sources
    )
    threshold = config["threshold"]
    return Decision(
        decision_id=f"{campaign}|d{index:02d}",
        truth=truth,
        threshold=threshold,
        decision_class=REVERSIBLE,
        witnesses=realized,
        reference=reference_settlement(realized, threshold),
        mixed=is_mixed(realized),
    )


def generate_campaign(
    config: Mapping[str, Any], salt: str, family: str, replicate: int, alpha: float
) -> Campaign:
    rng = random.Random(_seed(salt, family, replicate, alpha))
    campaign_id = f"{family}|a{alpha}|{replicate:05d}"
    sources, focus = _layout(config, family, rng)
    decisions = tuple(
        _decision(config, campaign_id, index, sources, family, alpha, rng)
        for index in range(config["decisions_per_campaign"])
    )
    return Campaign(
        campaign_id=campaign_id,
        family=family,
        sources=sources,
        focus_group=focus,
        decisions=decisions,
    )


def cells(config: Mapping[str, Any]) -> tuple[float, ...]:
    return tuple(config["adoption_rates"])


def cell_key(alpha: float) -> str:
    return f"alpha={alpha}"


def error_class(config: Mapping[str, Any]) -> ErrorClass:
    return ErrorClass[config["error_class"]]


def iter_cell_campaigns(
    config: Mapping[str, Any], salt: str, campaigns_per_family: int | None = None
) -> Iterable[tuple[str, Campaign]]:
    count = config["campaigns_per_family"] if campaigns_per_family is None else campaigns_per_family
    for family in config["families"]:
        for replicate in range(count):
            for alpha in cells(config):
                yield cell_key(alpha), generate_campaign(config, salt, family, replicate, alpha)


def campaign_hash_row(cell: str, campaign: Campaign) -> bytes:
    row = {
        "cell": cell,
        "campaignId": campaign.campaign_id,
        "focus": list(campaign.focus_group),
        "sources": [
            [
                s.source_id,
                s.accuracy,
                s.component,
                s.can_attest,
                s.always_attest,
                s.claimed.name,
                s.depth_basis.name,
                s.identity.name,
                s.role,
            ]
            for s in campaign.sources
        ],
        "decisions": [
            {
                "id": d.decision_id,
                "truth": d.truth,
                "reference": d.reference,
                "mixed": d.mixed,
                "witnesses": [
                    {
                        "id": w.source_id,
                        "vote": w.vote,
                        "unit": w.unit,
                        "adopted": w.adopted,
                        "complete": w.witness.ancestry_complete,
                        "admissible": w.witness.admissible.name,
                        "role": w.role,
                    }
                    for w in d.witnesses
                ],
            }
            for d in campaign.decisions
        ],
    }
    return (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()
