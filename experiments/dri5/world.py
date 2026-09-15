"""DRI-5 world generator.

Base worlds and lineage degradation are DRI-4's, unchanged (`experiments/dri4/world.py`),
with nothing spurious added. DRI-5 adds one observable that losing lineage does not
touch: a content fingerprint on every observation.

- **copies:** every copy of a root repeats that root's fingerprint. With paraphrase
  rate p, each copy after the first is reworded and gets a fingerprint of its own.
- **collisions:** with collision rate q, a root whose side already has an earlier
  root reuses the fingerprint of one of those roots, chosen uniformly. This is common
  wording, not a shared source.
- **roots of one true unit that are not copies** (a shared component or origin) get
  independent fingerprints. Content says nothing about that kind of dependence.

The fingerprint enters the evidence as an identity at the `content` cut. The truth,
the true grouping and the lookup are unchanged.

Random numbers are common across cells. One stream per base world, seeded without
m, p or q, draws a collision number and a choice for every root and a paraphrase
number for every copy. A paraphrase or collision therefore happens at rate 0.5 or 0.2
exactly where it also happens at any higher rate, and the fingerprints are identical
across missing rates.
"""

from __future__ import annotations

import dataclasses
import hashlib
import random
from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

from experiments.dri3.world import CUTS, Decision, World
from experiments.dri4.world import base_world, degraded_world
from provenance.decision_relative import DecisionEvidence
from provenance.dependence_robustness import assess_dependence_robustness

CONTENT_CUT = "content"
ALL_CUTS = CUTS + (CONTENT_CUT,)
FAMILIES = (
    "joint_domain",
    "separate_control_shared_origin",
    "three_stacked",
    "decoy_shared_identity",
    "side_asymmetric_trap",
)


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


def root_and_copy(observation_id: str) -> tuple[int, int]:
    *_, root, copy = observation_id.split("|")
    return int(root[1:]), int(copy[1:])


def true_grouping_admissible(
    evidence: Iterable[DecisionEvidence], units: Iterable[tuple[str, str]], cuts: Iterable[str]
) -> bool:
    """Whether every true unit is connected by recorded shared identities inside it,
    which is the assumption of the proven guarantee (ledger DR2)."""
    records = tuple(evidence)
    unit_of = dict(units)
    parent = {item.observation_id: item.observation_id for item in records}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for cut in cuts:
        first: dict[tuple[str, str], str] = {}
        for item in records:
            root = item.roots.get(cut)
            if root is None:
                continue
            key = (unit_of[item.observation_id], root)
            if key in first:
                parent[find(item.observation_id)] = find(first[key])
            else:
                first[key] = item.observation_id
    components: dict[str, set[str]] = defaultdict(set)
    for item in records:
        components[unit_of[item.observation_id]].add(find(item.observation_id))
    return all(len(roots) == 1 for roots in components.values())


@dataclasses.dataclass(frozen=True)
class ContentDraws:
    """The common random numbers for one decision."""

    collision: dict[int, float]
    choice: dict[int, float]
    paraphrase: dict[str, float]


def content_draws(decision: Decision, rng: random.Random) -> ContentDraws:
    roots = sorted({root_and_copy(item.observation_id)[0] for item in decision.evidence})
    collision = {root: rng.random() for root in roots}
    choice = {root: rng.random() for root in roots}
    paraphrase = {item.observation_id: rng.random() for item in decision.evidence}
    return ContentDraws(collision, choice, paraphrase)


def add_content(decision: Decision, draws: ContentDraws, paraphrase: float, collision: float) -> Decision:
    value_of: dict[int, bool] = {}
    for item in decision.evidence:
        value_of[root_and_copy(item.observation_id)[0]] = item.value
    token: dict[int, str] = {}
    for root in sorted(value_of):
        earlier = [r for r in sorted(token) if value_of[r] == value_of[root]]
        if earlier and draws.collision[root] < collision:
            token[root] = token[earlier[int(draws.choice[root] * len(earlier))]]
        else:
            token[root] = f"{CONTENT_CUT}:{decision.decision_id}|r{root}"
    evidence = []
    for item in decision.evidence:
        root, copy = root_and_copy(item.observation_id)
        fingerprint = token[root]
        if copy > 0 and draws.paraphrase[item.observation_id] < paraphrase:
            fingerprint = f"{CONTENT_CUT}:{item.observation_id}"
        evidence.append(
            DecisionEvidence(
                observation_id=item.observation_id,
                proposition_id=item.proposition_id,
                value=item.value,
                roots={**dict(item.roots), CONTENT_CUT: fingerprint},
                basis={**dict(item.basis), CONTENT_CUT: "attested"},
            )
        )
    frozen = tuple(evidence)
    robustness = assess_dependence_robustness(frozen, decision.threshold, ALL_CUTS)
    return dataclasses.replace(
        decision,
        evidence=frozen,
        record_settles_reference=robustness.robust and robustness.settlement == decision.reference,
    )


def cells(config: Mapping[str, Any]) -> tuple[tuple[float, float, float], ...]:
    return tuple(
        (m, p, q)
        for m in config["missing_rates"]
        for p in config["paraphrase_rates"]
        for q in config["collision_rates"]
    )


def cell_key(missing: float, paraphrase: float, collision: float) -> str:
    return f"m={missing}|p={paraphrase}|q={collision}"


def parse_cell(cell: str) -> tuple[float, float, float]:
    m, p, q = (float(part.split("=")[1]) for part in cell.split("|"))
    return m, p, q


def iter_cell_worlds(
    config: Mapping[str, Any], salt: str, worlds_per_family: int | None = None
) -> Iterable[tuple[str, World]]:
    count = config["worlds_per_family"] if worlds_per_family is None else worlds_per_family
    for family in config["families"]:
        for replicate in range(count):
            base = base_world(config, salt, family, replicate)
            rng = random.Random(_seed(salt, "content", family, replicate))
            draws = tuple(content_draws(decision, rng) for decision in base.decisions)
            for missing in config["missing_rates"]:
                degraded = degraded_world(config, salt, base, missing, 0.0)
                for paraphrase in config["paraphrase_rates"]:
                    for collision in config["collision_rates"]:
                        decisions = tuple(
                            add_content(decision, draw, paraphrase, collision)
                            for decision, draw in zip(degraded.decisions, draws, strict=True)
                        )
                        yield (
                            cell_key(missing, paraphrase, collision),
                            dataclasses.replace(degraded, decisions=decisions),
                        )
