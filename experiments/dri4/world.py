"""DRI-4 world generator, frozen at protocol v1.

Base worlds come from the frozen DRI-3 generator, plus one new family,
`side_asymmetric_trap`, built so that the agreement trap is always present. Each
base world is then shown through a degraded record at every (missing, spurious)
cell:

- **missing rate m:** every identity group that encodes a true dependence (two or
  more observations of one true unit sharing an identity at a cut) is, with
  probability m, split into distinct identities at that cut.
- **spurious rate s:** every pair of true units, with probability s, receives a
  shared identity at one randomly chosen cut, covering all observations of both.

Degradation changes only what the record shows. The truth, the true grouping and
the lookup are unchanged, and the same base world is used in every cell, so cells
are paired.

At m = 0 the true grouping stays a reading the record allows, so the proven
guarantee applies. For m > 0 it can fail.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import random
from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

from experiments.dri3.world import (
    CONDITIONS,
    CUTS,
    SETTLED,
    Decision,
    World,
    decision_classes,
    generate_world as generate_dri3_world,
    settlement_over_units,
    settlements_at_cuts,
)
from provenance.decision_relative import DecisionEvidence
from provenance.dependence_robustness import assess_dependence_robustness

FAMILIES = (
    "joint_domain",
    "separate_control_shared_origin",
    "three_stacked",
    "decoy_shared_identity",
    "side_asymmetric_trap",
)
TRAP_FAMILY = "side_asymmetric_trap"
TRAP_PAIR_CUTS = ("machine", "controller", "evidence_origin")


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


def _finish(
    decision_id: str,
    truth: bool,
    decision_class: str,
    threshold: int,
    accuracy: float,
    amplification: int,
    copy_cut: str,
    evidence: tuple[DecisionEvidence, ...],
    units: tuple[tuple[str, str], ...],
    lookup_available: bool,
    reference: str | None = None,
) -> Decision:
    cut_settlements = settlements_at_cuts(evidence, threshold)
    reference = settlement_over_units(evidence, units, threshold) if reference is None else reference
    robustness = assess_dependence_robustness(evidence, threshold, CUTS)
    return Decision(
        decision_id=decision_id,
        truth=truth,
        threshold=threshold,
        decision_class=decision_class,
        accuracy=accuracy,
        amplification=amplification,
        copy_cut=copy_cut,
        evidence=evidence,
        units=units,
        lookup_available=lookup_available,
        reference=reference,
        cut_settlements=tuple((cut, cut_settlements[cut]) for cut in CUTS),
        record_settles_reference=robustness.robust and robustness.settlement == reference,
    )


def trap_decision(
    rng: random.Random,
    config: Mapping[str, Any],
    world_id: str,
    index: int,
    decision_class: str,
    lookup_available: bool,
) -> Decision:
    """A decision on which all five cuts settle one way while the truth is a tie.

    Six roots. The winning side's three roots are wrong and copied, and copies are
    distinct at every cut except `upstream_component`, so they inflate the winning
    side's count at the other four cuts. The winning side's roots 0 and 1 are one
    source, recorded at one of machine, controller or evidence origin. The losing
    side's three roots are right; roots 3 and 4 are one source, recorded at the
    upstream component. The true units are therefore two against two.
    """
    truth = bool(rng.getrandbits(1))
    amplification = rng.choice(tuple(a for a in config["erroneous_root_amplifications"] if a >= 3))
    pair_cut = rng.choice(TRAP_PAIR_CUTS)
    threshold = config["decision_classes"][decision_class]
    proposition = f"{world_id}|d{index}"
    winner_value = not truth
    evidence: list[DecisionEvidence] = []
    units: list[tuple[str, str]] = []
    for root in range(6):
        winning = root <= 2
        value = winner_value if winning else truth
        copies = amplification if winning else 1
        unit = {0: "u_w", 1: "u_w", 3: "u_l", 4: "u_l"}.get(root, f"u{root}")
        for copy in range(copies):
            roots = {}
            for cut in CUTS:
                if cut == pair_cut and root in (0, 1):
                    roots[cut] = f"{cut}:pw"
                elif cut == "upstream_component" and root in (3, 4):
                    roots[cut] = f"{cut}:pl"
                elif cut == "upstream_component":
                    roots[cut] = f"{cut}:r{root}"
                else:
                    roots[cut] = f"{cut}:r{root}c{copy}"
            observation = f"{proposition}|r{root}|c{copy}"
            evidence.append(
                DecisionEvidence(
                    observation_id=observation,
                    proposition_id=proposition,
                    value=value,
                    roots=roots,
                    basis={cut: "attested" for cut in CUTS},
                )
            )
            units.append((observation, unit))
    decision = _finish(
        proposition, truth, decision_class, threshold, 0.0, amplification, "upstream_component",
        tuple(evidence), tuple(units), lookup_available,
    )
    winner = "settled_true" if winner_value else "settled_false"
    if set(dict(decision.cut_settlements).values()) != {winner} or decision.reference in SETTLED:
        raise AssertionError(f"trap structure failed for {proposition}")
    return decision


def base_world(config: Mapping[str, Any], salt: str, family: str, replicate: int) -> World:
    if family != TRAP_FAMILY:
        return generate_dri3_world(config, salt, family, replicate)
    condition = CONDITIONS[replicate % 2]
    world_id = f"{family}|{replicate:05d}"
    rng = random.Random(_seed(salt, family, replicate))
    decisions = tuple(
        trap_decision(rng, config, world_id, index, decision_class, condition == CONDITIONS[0])
        for index, decision_class in enumerate(decision_classes(replicate))
    )
    return World(world_id=world_id, family=family, condition=condition, replicate=replicate, decisions=decisions)


def degrade(decision: Decision, missing: float, spurious: float, rng: random.Random) -> Decision:
    """Show the decision through a record with missing and spurious shared identities."""
    if missing == 0 and spurious == 0:
        return decision
    unit_of = dict(decision.units)
    roots = {item.observation_id: dict(item.roots) for item in decision.evidence}
    for cut in CUTS:
        groups: dict[str, list[str]] = defaultdict(list)
        for item in decision.evidence:
            groups[item.roots[cut]].append(item.observation_id)
        for identity in sorted(groups):
            members = groups[identity]
            if len(members) < 2 or len({unit_of[o] for o in members}) != 1:
                continue
            if rng.random() < missing:
                for observation in members:
                    roots[observation][cut] = f"{cut}:missing:{observation}"
    units = sorted(set(unit_of.values()))
    for a in range(len(units)):
        for b in range(a + 1, len(units)):
            if rng.random() < spurious:
                cut = rng.choice(CUTS)
                identity = f"{cut}:spurious:{units[a]}:{units[b]}"
                for item in decision.evidence:
                    if unit_of[item.observation_id] in (units[a], units[b]):
                        roots[item.observation_id][cut] = identity
    evidence = tuple(
        DecisionEvidence(
            observation_id=item.observation_id,
            proposition_id=item.proposition_id,
            value=item.value,
            roots=roots[item.observation_id],
            basis=dict(item.basis),
        )
        for item in decision.evidence
    )
    return _finish(
        decision.decision_id, decision.truth, decision.decision_class, decision.threshold,
        decision.accuracy, decision.amplification, decision.copy_cut, evidence, decision.units,
        decision.lookup_available, reference=decision.reference,
    )


def cells(config: Mapping[str, Any]) -> tuple[tuple[float, float], ...]:
    return tuple((m, s) for m in config["missing_rates"] for s in config["spurious_rates"])


def cell_key(missing: float, spurious: float) -> str:
    return f"m={missing}|s={spurious}"


def degraded_world(
    config: Mapping[str, Any], salt: str, base: World, missing: float, spurious: float
) -> World:
    rng = random.Random(_seed(salt, "degrade", base.family, base.replicate, missing, spurious))
    return dataclasses.replace(
        base, decisions=tuple(degrade(d, missing, spurious, rng) for d in base.decisions)
    )


def iter_cell_worlds(
    config: Mapping[str, Any], salt: str, worlds_per_family: int | None = None
) -> Iterable[tuple[str, World]]:
    count = config["worlds_per_family"] if worlds_per_family is None else worlds_per_family
    for family in config["families"]:
        for replicate in range(count):
            base = base_world(config, salt, family, replicate)
            for missing, spurious in cells(config):
                yield cell_key(missing, spurious), degraded_world(config, salt, base, missing, spurious)


def world_hash_row(cell: str, world: World) -> bytes:
    row = {
        "cell": cell,
        "worldId": world.world_id,
        "condition": world.condition,
        "decisions": [
            {
                "id": d.decision_id,
                "truth": d.truth,
                "class": d.decision_class,
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
