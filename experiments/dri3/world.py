"""DRI-3 world generator. DRAFT: not frozen, and never run on confirmatory seeds.

Each world holds three independent decisions. Every decision carries observations
with identities at five lineage cuts, and a hidden true causal grouping that a
lookup returns when the world allows lookups. Half of each family's worlds allow
lookups; the other half do not.

Families 1 to 6 carry all of their true dependence in recorded identities, so the
true grouping is always one of the readings `assess_dependence_robustness`
considers. Family 7 carries a dependence that no identity records; it is the
declared boundary.

Decision classes alternate by a fixed pattern so that exactly half of each
family's decisions are irreversible.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from provenance.decision_relative import (
    CutAssessment,
    DecisionContext,
    DecisionEvidence,
    assess_decision,
)
from provenance.dependence_robustness import assess_dependence_robustness

CUTS = ("agent", "machine", "controller", "evidence_origin", "upstream_component")
CUT_INDEX = {cut: index for index, cut in enumerate(CUTS)}
FAMILIES = (
    "single_domain",
    "joint_domain",
    "separate_control_shared_origin",
    "three_stacked",
    "side_asymmetric",
    "decoy_shared_identity",
    "unrecorded_dependence",
)
RECORDED_FAMILIES = FAMILIES[:6]
CONDITIONS = ("lookup_available", "lookup_unavailable")
IRREVERSIBLE = "high_irreversible"
REVERSIBLE = "low_reversible"
SETTLED = ("settled_true", "settled_false")
UNIT_CUT = "causal_unit"


@dataclass(frozen=True)
class Decision:
    decision_id: str
    truth: bool
    threshold: int
    decision_class: str
    accuracy: float
    amplification: int
    copy_cut: str
    evidence: tuple[DecisionEvidence, ...]
    units: tuple[tuple[str, str], ...]
    lookup_available: bool
    reference: str
    cut_settlements: tuple[tuple[str, str], ...]
    record_settles_reference: bool
    """True when the record alone robustly settles the way the true grouping does."""


@dataclass(frozen=True)
class World:
    world_id: str
    family: str
    condition: str
    replicate: int
    decisions: tuple[Decision, ...]


def _context(proposition: str, cut: str, cuts: tuple[str, ...], threshold: int) -> DecisionContext:
    return DecisionContext(
        decision_id=proposition,
        proposition_id=proposition,
        failure_domain="undisclosed",
        independence_cut=cut,
        minimum_winning_roots=threshold,
        cut_selection_basis="unknown",
        candidate_cuts=cuts,
    )


def assess_cuts(evidence: tuple[DecisionEvidence, ...], threshold: int) -> dict[str, CutAssessment]:
    proposition = evidence[0].proposition_id
    result = assess_decision(evidence, _context(proposition, CUTS[0], CUTS, threshold))
    by_cut = {result.selected.independence_cut: result.selected, **dict(result.alternatives)}
    return {cut: by_cut[cut] for cut in CUTS}


def settlements_at_cuts(evidence: tuple[DecisionEvidence, ...], threshold: int) -> dict[str, str]:
    return {cut: assessed.settlement for cut, assessed in assess_cuts(evidence, threshold).items()}


def settlement_over_units(
    evidence: tuple[DecisionEvidence, ...], units: Iterable[tuple[str, str]], threshold: int
) -> str:
    unit_of = dict(units)
    regrouped = tuple(
        DecisionEvidence(
            observation_id=item.observation_id,
            proposition_id=item.proposition_id,
            value=item.value,
            roots={UNIT_CUT: unit_of[item.observation_id]},
            basis={UNIT_CUT: "attested"},
        )
        for item in evidence
    )
    return assess_decision(
        regrouped, _context(evidence[0].proposition_id, UNIT_CUT, (UNIT_CUT,), threshold)
    ).selected.settlement


def decision_classes(replicate: int) -> tuple[str, str, str]:
    """Fixed pattern: over any four consecutive replicates, exactly half of the
    decisions are irreversible, balanced across both lookup conditions."""
    if (replicate // 2) % 2 == 0:
        return (IRREVERSIBLE, REVERSIBLE, IRREVERSIBLE)
    return (REVERSIBLE, IRREVERSIBLE, REVERSIBLE)


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


Identity = Callable[[int, int, str], str]
Unit = Callable[[int], str]


def _layout(rng: random.Random, family: str, values: list[bool]) -> tuple[str, Identity, Unit]:
    """How identities are recorded at each cut, and the true causal unit of each root.

    Below the copy cut every copy of a root is distinct; at or above it the copies
    share an identity.
    """

    def base(copy_cut: str) -> Identity:
        copy_index = CUT_INDEX[copy_cut]

        def identity(root: int, copy: int, cut: str) -> str:
            suffix = f"r{root}" if CUT_INDEX[cut] >= copy_index else f"r{root}c{copy}"
            return f"{cut}:{suffix}"

        return identity

    def per_root(root: int) -> str:
        return f"u{root}"

    if family == "single_domain":
        copy_cut = rng.choice(CUTS[1:])
        plain = base(copy_cut)

        def identity(root: int, copy: int, cut: str) -> str:
            if CUT_INDEX[cut] > CUT_INDEX[copy_cut]:
                return f"{cut}:g{root // 2}"
            return plain(root, copy, cut)

        return copy_cut, identity, per_root

    if family == "joint_domain":
        copy_cut = rng.choice(("machine", "controller", "evidence_origin"))
        plain = base(copy_cut)

        def identity(root: int, copy: int, cut: str) -> str:
            return f"{cut}:g{root // 2}" if cut == "upstream_component" else plain(root, copy, cut)

        return copy_cut, identity, lambda root: "u01" if root in (0, 1) else f"u{root}"

    if family == "separate_control_shared_origin":
        copy_cut = rng.choice(("machine", "controller"))
        plain = base(copy_cut)

        def identity(root: int, copy: int, cut: str) -> str:
            if cut == "upstream_component":
                return f"{cut}:g{root // 2}"
            if CUT_INDEX[cut] >= CUT_INDEX["evidence_origin"] and root <= 2:
                return f"{cut}:origin"
            return plain(root, copy, cut)

        return copy_cut, identity, lambda root: "u012" if root <= 2 else f"u{root}"

    if family == "three_stacked":
        copy_cut = rng.choice(("machine", "controller"))
        plain = base(copy_cut)

        def identity(root: int, copy: int, cut: str) -> str:
            if cut == "evidence_origin" and root in (0, 1):
                return f"{cut}:o01"
            if cut == "upstream_component" and root in (2, 3):
                return f"{cut}:g23"
            return plain(root, copy, cut)

        def unit(root: int) -> str:
            if root in (0, 1):
                return "u01"
            if root in (2, 3):
                return "u23"
            return f"u{root}"

        return copy_cut, identity, unit

    if family == "side_asymmetric":
        copy_cut = "machine"
        plain = base(copy_cut)
        true_roots = [root for root, value in enumerate(values) if value]
        false_roots = [root for root, value in enumerate(values) if not value]
        pair_true = tuple(true_roots[:2]) if len(true_roots) >= 2 else ()
        pair_false = tuple(false_roots[:2]) if len(false_roots) >= 2 else ()

        def identity(root: int, copy: int, cut: str) -> str:
            if cut == "evidence_origin" and root in pair_true:
                return f"{cut}:shared_true"
            if cut == "controller" and root in pair_false:
                return f"{cut}:shared_false"
            return plain(root, copy, cut)

        def unit(root: int) -> str:
            if root in pair_true:
                return "u_true_pair"
            if root in pair_false:
                return "u_false_pair"
            return f"u{root}"

        return copy_cut, identity, unit

    if family == "decoy_shared_identity":
        copy_cut = "machine"
        plain = base(copy_cut)

        def identity(root: int, copy: int, cut: str) -> str:
            return f"{cut}:g{root % 2}" if cut == "upstream_component" else plain(root, copy, cut)

        return copy_cut, identity, per_root

    if family == "unrecorded_dependence":
        copy_cut = "machine"
        return copy_cut, base(copy_cut), lambda root: "u01" if root in (0, 1) else f"u{root}"

    raise ValueError(f"unknown family: {family}")


def _decision(
    rng: random.Random,
    config: Mapping[str, Any],
    family: str,
    world_id: str,
    index: int,
    decision_class: str,
    lookup_available: bool,
) -> Decision:
    truth = bool(rng.getrandbits(1))
    accuracy = rng.choice(tuple(config["independent_root_accuracies"]))
    amplification = rng.choice(tuple(config["erroneous_root_amplifications"]))
    roots = rng.choice(tuple(config["roots_per_decision"]))
    values = [truth if rng.random() < accuracy else not truth for _ in range(roots)]
    copy_cut, identity, unit = _layout(rng, family, values)
    threshold = config["decision_classes"][decision_class]
    proposition = f"{world_id}|d{index}"
    evidence: list[DecisionEvidence] = []
    units: list[tuple[str, str]] = []
    for root in range(roots):
        copies = 1 if values[root] == truth else amplification
        for copy in range(copies):
            observation = f"{proposition}|r{root}|c{copy}"
            evidence.append(
                DecisionEvidence(
                    observation_id=observation,
                    proposition_id=proposition,
                    value=values[root],
                    roots={cut: identity(root, copy, cut) for cut in CUTS},
                    basis={cut: "attested" for cut in CUTS},
                )
            )
            units.append((observation, unit(root)))
    frozen = tuple(evidence)
    cut_settlements = settlements_at_cuts(frozen, threshold)
    reference = settlement_over_units(frozen, units, threshold)
    robustness = assess_dependence_robustness(frozen, threshold, CUTS)
    return Decision(
        decision_id=proposition,
        truth=truth,
        threshold=threshold,
        decision_class=decision_class,
        accuracy=accuracy,
        amplification=amplification,
        copy_cut=copy_cut,
        evidence=frozen,
        units=tuple(units),
        lookup_available=lookup_available,
        reference=reference,
        cut_settlements=tuple((cut, cut_settlements[cut]) for cut in CUTS),
        record_settles_reference=robustness.robust and robustness.settlement == reference,
    )


def generate_world(config: Mapping[str, Any], salt: str, family: str, replicate: int) -> World:
    condition = CONDITIONS[replicate % 2]
    classes = decision_classes(replicate)
    if len(classes) != config["decisions_per_world"]:
        raise ValueError("decision class pattern does not match decisions_per_world")
    world_id = f"{family}|{replicate:05d}"
    rng = random.Random(_seed(salt, family, replicate))
    decisions = tuple(
        _decision(rng, config, family, world_id, index, decision_class, condition == CONDITIONS[0])
        for index, decision_class in enumerate(classes)
    )
    return World(world_id=world_id, family=family, condition=condition, replicate=replicate, decisions=decisions)


def iter_worlds(
    config: Mapping[str, Any], salt: str, worlds_per_family: int | None = None
) -> Iterable[World]:
    count = config["worlds_per_family"] if worlds_per_family is None else worlds_per_family
    for family in config["families"]:
        for replicate in range(count):
            yield generate_world(config, salt, family, replicate)


def world_hash_row(world: World) -> bytes:
    row = {
        "worldId": world.world_id,
        "condition": world.condition,
        "decisions": [
            {
                "id": d.decision_id,
                "truth": d.truth,
                "class": d.decision_class,
                "threshold": d.threshold,
                "reference": d.reference,
                "evidence": [
                    {"id": item.observation_id, "value": item.value, "roots": dict(item.roots)}
                    for item in d.evidence
                ],
                "units": [list(pair) for pair in d.units],
            }
            for d in world.decisions
        ],
    }
    return (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()
