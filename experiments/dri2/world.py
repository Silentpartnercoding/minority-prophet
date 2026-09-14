"""DRI-2 world generator. DRAFT: not frozen, and never run on confirmatory seeds.

A world is a short sequence of decisions, revealed one at a time. Each decision
carries observations with identities at the five lineage cuts DRI-1A used, but
no contestant arm is told the failure domain. The true causal grouping of the
observations is hidden. A lineage probe reveals it, except in twin worlds, where
the probe is unavailable.

Each decision's junction type is fixed by construction and hidden from arms:

- ``settle``: every cut already settles the way the true causal grouping does;
- ``gather``: the cuts disagree with each other or with the true grouping, and
  the probe is available;
- ``hand_over``: the true grouping does not settle, or the cuts disagree and
  the probe is unavailable.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import random
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from provenance.decision_relative import (
    CutAssessment,
    DecisionContext,
    DecisionEvidence,
    assess_decision,
)

CUTS = ("agent", "machine", "controller", "evidence_origin", "upstream_component")
CUT_INDEX = {cut: index for index, cut in enumerate(CUTS)}
DOMAIN_CUT = {
    "machine_local": "machine",
    "shared_controller": "controller",
    "copied_source": "evidence_origin",
    "shared_upstream_component": "upstream_component",
}
FAMILIES = (
    "single_domain",
    "joint_domain",
    "separate_control_shared_origin",
    "genuinely_independent",
)
PATH_TYPES = ("no_handover", "one_handover", "twin")
SETTLE = "settle"
GATHER = "gather"
HAND_OVER = "hand_over"
SETTLED = ("settled_true", "settled_false")
UNIT_CUT = "causal_unit"


@dataclass(frozen=True)
class Decision:
    decision_id: str
    truth: bool
    threshold: int
    accuracy: float
    amplification: int
    domains: tuple[str, ...]
    evidence: tuple[DecisionEvidence, ...]
    units: tuple[tuple[str, str], ...]
    probe_available: bool
    reference: str
    cut_settlements: tuple[tuple[str, str], ...]
    junction: str


@dataclass(frozen=True)
class World:
    world_id: str
    family: str
    path_type: str
    replicate: int
    attempt: int
    probe_available: bool
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


def assess_cuts(
    evidence: tuple[DecisionEvidence, ...], threshold: int
) -> dict[str, CutAssessment]:
    """Root-vote assessment of the visible evidence at every cut."""
    proposition = evidence[0].proposition_id
    result = assess_decision(evidence, _context(proposition, CUTS[0], CUTS, threshold))
    by_cut = {result.selected.independence_cut: result.selected, **dict(result.alternatives)}
    return {cut: by_cut[cut] for cut in CUTS}


def settlements_at_cuts(evidence: tuple[DecisionEvidence, ...], threshold: int) -> dict[str, str]:
    return {cut: assessed.settlement for cut, assessed in assess_cuts(evidence, threshold).items()}


def settlement_over_units(
    evidence: tuple[DecisionEvidence, ...],
    units: Iterable[tuple[str, str]],
    threshold: int,
) -> str:
    """Settlement when observations are counted by their true causal unit."""
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
    proposition = evidence[0].proposition_id
    return assess_decision(
        regrouped, _context(proposition, UNIT_CUT, (UNIT_CUT,), threshold)
    ).selected.settlement


def classify(reference: str, cut_settlements: Mapping[str, str], probe_available: bool) -> str:
    if reference not in SETTLED:
        return HAND_OVER
    if all(value == reference for value in cut_settlements.values()):
        return SETTLE
    return GATHER if probe_available else HAND_OVER


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


def _domains(rng: random.Random, family: str) -> tuple[str, ...]:
    if family == "single_domain":
        return (rng.choice(tuple(DOMAIN_CUT)),)
    if family == "joint_domain":
        return (
            rng.choice(("machine_local", "shared_controller", "copied_source")),
            "shared_upstream_component",
        )
    if family == "separate_control_shared_origin":
        return (rng.choice(("machine_local", "shared_controller")), "copied_source")
    if family == "genuinely_independent":
        return ()
    raise ValueError(f"unknown family: {family}")


def _identity(family: str, domains: tuple[str, ...], root: int, copy: int, cut: str) -> str:
    """The identifier an observation carries at one cut.

    A cut at or coarser than the copy domain's cut sees copies as one root; finer
    cuts see every copy as distinct. Coarser cuts also merge causal roots, as in
    DRI-1A: roots 0/1 and 2/3 share an identity, which erases independent evidence.
    """
    index = CUT_INDEX[cut]
    if family == "genuinely_independent":
        return f"{cut}:r{root}"
    copy_index = CUT_INDEX[DOMAIN_CUT[domains[0]]]
    base = f"r{root}" if index >= copy_index else f"r{root}c{copy}"
    if family == "single_domain":
        return f"{cut}:g{root // 2}" if index > copy_index else f"{cut}:{base}"
    if index == CUT_INDEX["upstream_component"]:
        return f"{cut}:g{root // 2}"
    if (
        family == "separate_control_shared_origin"
        and index >= CUT_INDEX["evidence_origin"]
        and root <= 2
    ):
        return f"{cut}:origin"
    return f"{cut}:{base}"


def _unit(family: str, root: int) -> str:
    """The true causal unit, which only the lineage probe reveals.

    joint_domain: roots 0 and 1 share an upstream component. No single cut
    expresses this, because the upstream cut also merges roots 2 and 3.
    separate_control_shared_origin: roots 0 to 2 are separately controlled but
    repeat one source; the evidence-origin cut expresses it exactly.
    """
    if family == "joint_domain" and root in (0, 1):
        return "u01"
    if family == "separate_control_shared_origin" and root <= 2:
        return "u012"
    return f"u{root}"


def _decision(
    rng: random.Random,
    config: Mapping[str, Any],
    family: str,
    world_id: str,
    index: int,
) -> Decision:
    truth = bool(rng.getrandbits(1))
    accuracy = rng.choice(tuple(config["independent_root_accuracies"]))
    amplification = rng.choice(tuple(config["erroneous_root_amplifications"]))
    decision_class = rng.choice(tuple(sorted(config["decision_classes"])))
    threshold = config["decision_classes"][decision_class]
    domains = _domains(rng, family)
    # An even number of causal roots can tie, which leaves the true grouping
    # unsettled: the information needed exists only with a human. With a fixed
    # five roots that never happens and no native hand-over junction exists.
    roots = rng.choice(tuple(config["roots_per_decision"]))
    proposition = f"{world_id}|d{index}"
    evidence: list[DecisionEvidence] = []
    units: list[tuple[str, str]] = []
    for root in range(roots):
        correct = rng.random() < accuracy
        value = truth if correct else not truth
        copies = 1 if correct or family == "genuinely_independent" else amplification
        for copy in range(copies):
            observation = f"{proposition}|r{root}|c{copy}"
            evidence.append(
                DecisionEvidence(
                    observation_id=observation,
                    proposition_id=proposition,
                    value=value,
                    roots={cut: _identity(family, domains, root, copy, cut) for cut in CUTS},
                    basis={cut: "attested" for cut in CUTS},
                )
            )
            units.append((observation, _unit(family, root)))
    frozen_evidence = tuple(evidence)
    cut_settlements = settlements_at_cuts(frozen_evidence, threshold)
    reference = settlement_over_units(frozen_evidence, units, threshold)
    return Decision(
        decision_id=proposition,
        truth=truth,
        threshold=threshold,
        accuracy=accuracy,
        amplification=amplification,
        domains=domains,
        evidence=frozen_evidence,
        units=tuple(units),
        probe_available=True,
        reference=reference,
        cut_settlements=tuple((cut, cut_settlements[cut]) for cut in CUTS),
        junction=classify(reference, cut_settlements, True),
    )


def _accepts(family: str, path_type: str, decisions: tuple[Decision, ...]) -> bool:
    junctions = [decision.junction for decision in decisions]
    if path_type == "no_handover":
        return HAND_OVER not in junctions
    if path_type == "one_handover":
        return junctions.count(HAND_OVER) == 1
    if path_type == "twin":
        if family == "genuinely_independent":
            return HAND_OVER not in junctions
        return HAND_OVER not in junctions and GATHER in junctions
    raise ValueError(f"unknown path type: {path_type}")


def with_probe(world: World, available: bool) -> World:
    """The same world with the lineage probe made available or unavailable."""
    decisions = tuple(
        dataclasses.replace(
            decision,
            probe_available=available,
            junction=classify(decision.reference, dict(decision.cut_settlements), available),
        )
        for decision in world.decisions
    )
    return dataclasses.replace(world, probe_available=available, decisions=decisions)


def generate_world(
    config: Mapping[str, Any], salt: str, family: str, path_type: str, replicate: int
) -> World:
    """Deterministic rejection sampling until the world matches its path type.

    A twin is accepted with the probe available and then has it removed, so every
    gather junction in it becomes a hand-over.
    """
    world_id = f"{family}|{path_type}|{replicate:04d}"
    for attempt in range(config["max_attempts"]):
        rng = random.Random(_seed(salt, family, path_type, replicate, attempt))
        decisions = tuple(
            _decision(rng, config, family, world_id, index)
            for index in range(config["decisions_per_world"])
        )
        if _accepts(family, path_type, decisions):
            world = World(
                world_id=world_id,
                family=family,
                path_type=path_type,
                replicate=replicate,
                attempt=attempt,
                probe_available=True,
                decisions=decisions,
            )
            return with_probe(world, False) if path_type == "twin" else world
    raise RuntimeError(f"no {path_type} world for {family} within {config['max_attempts']} attempts")


def iter_worlds(
    config: Mapping[str, Any], salt: str, worlds_per_path_type: int | None = None
) -> Iterable[World]:
    count = config["worlds_per_path_type"] if worlds_per_path_type is None else worlds_per_path_type
    for family in config["families"]:
        for path_type in config["path_types"]:
            for replicate in range(count):
                yield generate_world(config, salt, family, path_type, replicate)


def world_hash_row(world: World) -> bytes:
    row = {
        "worldId": world.world_id,
        "attempt": world.attempt,
        "probeAvailable": world.probe_available,
        "decisions": [
            {
                "id": decision.decision_id,
                "truth": decision.truth,
                "threshold": decision.threshold,
                "junction": decision.junction,
                "reference": decision.reference,
                "evidence": [
                    {"id": item.observation_id, "value": item.value, "roots": dict(item.roots)}
                    for item in decision.evidence
                ],
                "units": [list(pair) for pair in decision.units],
            }
            for decision in world.decisions
        ],
    }
    return (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()
