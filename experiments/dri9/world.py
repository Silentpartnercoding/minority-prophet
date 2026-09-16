"""DRI-9 world generator: persistent sources, hidden dependence, three ways to see it.

Campaigns are DRI-8's in structure — persistent sources, a component with a
per-decision fault state whose members err together, recorded at no cut — with a
decoy family whose group shares only low accuracy.

Nothing is placed. An earlier draft tried to position decisions on an enumerated
table of "pivotal" vote shapes; that table predicted a single-cut root count
while the rule settles across every cut together, and the two disagreed
everywhere. Once belief is applied properly (`rule.believe`), roughly two thirds
of reversible decisions are already ones where believing the group changes the
answer, so the world is sampled honestly and the critical share is measured by
`rule.is_pivotal` rather than engineered.

Three observables live outside the record:

- **markers (bait):** a component is marked once per campaign; its members carry
  the marker at the cell's pickup rate, anyone else only at `marker_leak`.
- **arrival order:** consistent within a component group, shuffled between
  groups. Ordering by "has a component at all" made unrelated component members
  look perfectly linked — an artifact that handed the ladder a free vote.
- **cut response:** what happens when a source's upstream is cut. Members of one
  component change together at `cut_together`, others at `cut_alone`.

Every stream is keyed by campaign, so two arms asking the same question get the
same answer.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import random
from collections.abc import Iterable, Mapping
from typing import Any

from experiments.dri3.world import IRREVERSIBLE, REVERSIBLE, settlement_over_units
from experiments.dri8.world import ALL_CUTS, CONTENT_CUT, HIDDEN, Source, _identities
from experiments.dri9.rule import RULE_CUTS
from provenance.decision_relative import DecisionEvidence
from provenance.dependence_robustness import assess_dependence_robustness

FAMILIES = ("shared_upstream_pair", "shared_upstream_trio", "coincident_independents")
MARKER = "marker"
GROUP_SIZE = {"shared_upstream_pair": 2, "shared_upstream_trio": 3, "coincident_independents": 2}


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


@dataclasses.dataclass(frozen=True)
class Decision:
    decision_id: str
    truth: bool
    threshold: int
    decision_class: str
    evidence: tuple[DecisionEvidence, ...]
    units: tuple[tuple[str, str], ...]
    source_of: tuple[tuple[str, str], ...]
    markers: tuple[tuple[str, str], ...]
    order: tuple[str, ...]
    reference: str
    record_settles_reference: bool


@dataclasses.dataclass(frozen=True)
class Campaign:
    campaign_id: str
    family: str
    sources: tuple[Source, ...]
    focus_group: tuple[str, ...]
    """What the family is about: a hidden component's members, or the decoy's
    equally sized group that shares nothing."""
    marked_component: str | None
    decisions: tuple[Decision, ...]


def _sources(config: Mapping[str, Any], family: str, rng: random.Random) -> tuple[Source, ...]:
    accuracies = tuple(config["source_accuracies"])
    hidden = family != "coincident_independents"
    sources = [
        Source(
            f"g{index}",
            rng.choice(accuracies) if hidden else min(accuracies),
            "hidden:u" if hidden else None,
            HIDDEN if hidden else None,
        )
        for index in range(GROUP_SIZE[family])
    ]
    sources += [
        Source(f"i{index}", rng.choice(accuracies), None, None)
        for index in range(config["independents_per_campaign"])
    ]
    return tuple(sources)


def _order(sources: tuple[Source, ...], jitter: float, rng: random.Random) -> tuple[str, ...]:
    component = {s.source_id: s.component for s in sources}
    blocks: list[list[str]] = []
    grouped: dict[str, list[str]] = {}
    for source in sources:
        if component[source.source_id] is None:
            blocks.append([source.source_id])
        else:
            grouped.setdefault(component[source.source_id], []).append(source.source_id)
    for members in grouped.values():
        members = sorted(members)
        if rng.random() < jitter:
            rng.shuffle(members)
        blocks.append(members)
    rng.shuffle(blocks)
    return tuple(source for block in blocks for source in block)


def _decision(
    config: Mapping[str, Any],
    campaign_id: str,
    index: int,
    sources: tuple[Source, ...],
    marked: str | None,
    pickup: float,
    jitter: float,
    rng: random.Random,
) -> Decision:
    truth = bool(rng.getrandbits(1))
    decision_class = IRREVERSIBLE if index % 2 == 0 else REVERSIBLE
    threshold = config["decision_classes"][decision_class]
    proposition = f"{campaign_id}|d{index:02d}"
    faulty = {
        component: rng.random() < config["component_fault_rate"]
        for component in sorted({s.component for s in sources if s.component})
    }
    evidence: list[DecisionEvidence] = []
    units: list[tuple[str, str]] = []
    source_of: list[tuple[str, str]] = []
    markers: list[tuple[str, str]] = []
    for source in sources:
        if source.component and faulty[source.component]:
            value = not truth
        else:
            value = truth if rng.random() < source.accuracy else not truth
        observation = f"{proposition}|{source.source_id}"
        evidence.append(
            DecisionEvidence(
                observation_id=observation,
                proposition_id=proposition,
                value=value,
                roots=_identities(source, proposition),
                basis={cut: "attested" for cut in ALL_CUTS},
            )
        )
        units.append((observation, source.component or source.source_id))
        source_of.append((observation, source.source_id))
        carries = (
            rng.random() < pickup
            if marked is not None and source.component == marked
            else rng.random() < config["marker_leak"]
        )
        if carries and marked is not None:
            markers.append((observation, f"{MARKER}:{marked}"))

    frozen = tuple(evidence)
    reference = settlement_over_units(frozen, tuple(units), threshold)
    robustness = assess_dependence_robustness(frozen, threshold, RULE_CUTS[:-1])
    return Decision(
        decision_id=proposition,
        truth=truth,
        threshold=threshold,
        decision_class=decision_class,
        evidence=frozen,
        units=tuple(units),
        source_of=tuple(source_of),
        markers=tuple(markers),
        order=_order(sources, jitter, rng),
        reference=reference,
        record_settles_reference=robustness.robust and robustness.settlement == reference,
    )


def generate_campaign(
    config: Mapping[str, Any], salt: str, family: str, replicate: int, pickup: float, jitter: float
) -> Campaign:
    rng = random.Random(_seed(salt, family, replicate, pickup, jitter))
    campaign_id = f"{family}|{replicate:05d}"
    sources = _sources(config, family, rng)
    focus = tuple(s.source_id for s in sources if s.source_id.startswith("g"))
    components = sorted({s.component for s in sources if s.component_kind == HIDDEN})
    marked = components[0] if components else None
    decisions = tuple(
        _decision(config, campaign_id, index, sources, marked, pickup, jitter, rng)
        for index in range(config["decisions_per_campaign"])
    )
    return Campaign(
        campaign_id=campaign_id,
        family=family,
        sources=sources,
        focus_group=focus,
        marked_component=marked,
        decisions=decisions,
    )


def cut_response(
    config: Mapping[str, Any], salt: str, campaign: Campaign, cut_source: str, observed: str, index: int
) -> bool:
    component = {s.source_id: s.component for s in campaign.sources}
    together = component.get(cut_source) is not None and component.get(cut_source) == component.get(observed)
    rate = config["cut_together"] if together else config["cut_alone"]
    rng = random.Random(_seed(salt, "cut", campaign.campaign_id, cut_source, observed, index))
    return rng.random() < rate


def reveals(config: Mapping[str, Any], salt: str, campaign: Campaign, index: int, feedback: float) -> bool:
    rng = random.Random(_seed(salt, "feedback", campaign.campaign_id, index))
    return rng.random() < feedback


def cells(config: Mapping[str, Any]) -> tuple[tuple[float, float], ...]:
    return tuple((p, j) for p in config["marker_pickups"] for j in config["timing_jitters"])


def cell_key(pickup: float, jitter: float) -> str:
    return f"pickup={pickup}|jitter={jitter}"


def parse_cell(cell: str) -> tuple[float, float]:
    p, j = (float(part.split("=")[1]) for part in cell.split("|"))
    return p, j


def iter_cell_campaigns(
    config: Mapping[str, Any], salt: str, campaigns_per_family: int | None = None
) -> Iterable[tuple[str, Campaign]]:
    count = config["campaigns_per_family"] if campaigns_per_family is None else campaigns_per_family
    for family in config["families"]:
        for replicate in range(count):
            for pickup, jitter in cells(config):
                yield cell_key(pickup, jitter), generate_campaign(config, salt, family, replicate, pickup, jitter)


def campaign_hash_row(cell: str, campaign: Campaign) -> bytes:
    row = {
        "cell": cell,
        "campaignId": campaign.campaign_id,
        "marked": campaign.marked_component,
        "focus": list(campaign.focus_group),
        "sources": [[s.source_id, s.accuracy, s.component, s.component_kind] for s in campaign.sources],
        "decisions": [
            {
                "id": d.decision_id,
                "truth": d.truth,
                "class": d.decision_class,
                "reference": d.reference,
                "order": list(d.order),
                "markers": [list(pair) for pair in d.markers],
                "evidence": [
                    {"id": i.observation_id, "value": i.value, "roots": dict(i.roots)} for i in d.evidence
                ],
                "units": [list(pair) for pair in d.units],
            }
            for d in campaign.decisions
        ],
    }
    return (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()


__all__ = [
    "ALL_CUTS", "CONTENT_CUT", "Campaign", "Decision", "FAMILIES", "GROUP_SIZE", "HIDDEN", "MARKER",
    "campaign_hash_row", "cell_key", "cells", "cut_response", "generate_campaign",
    "iter_cell_campaigns", "parse_cell", "reveals",
]
