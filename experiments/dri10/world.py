"""DRI-10 world: hidden dependence and markers are independent knobs.

DRI-9 glued them together. The hidden families *were* "one unmarked shared
component," that component was the marked channel, and the decoy planted no
markers at all. Bait looked for the thing the generator planted on the group
it was supposed to find.

Here a source has an optional **error component** (hidden, recorded nowhere)
and an optional **carrier** (what can pick up a planted marker). The marked
channel is chosen per family and is not required to be the error component.
`marker_leak` therefore fires in every family: anyone whose carrier is not
the marked channel still carries the token at the leak rate.

Families:

- **marked_hidden_pair** — positive control. The hidden pair's carrier *is*
  the hidden component, and that component is marked. DRI-9's bait story.
- **unmarked_hidden_pair** — the hidden pair still shares an error component
  recorded at no cut, but their carrier is empty. The marked channel is an
  environmental token nobody preferentially holds. They carry it only by leak.
- **common_carrier** — no shared error. Three sources share a library carrier
  that is marked. They pick up the same token and err independently. Merging
  them is wrong.
- **leaky_independents** — no shared error, no shared carrier. The marked
  channel is environmental, so leak produces markers. The harm test DRI-9's
  decoy could not run.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import random
from collections.abc import Iterable, Mapping
from typing import Any

from experiments.dri3.world import IRREVERSIBLE, REVERSIBLE, settlement_over_units
from experiments.dri8.world import ALL_CUTS, CONTENT_CUT, HIDDEN, _identities
from experiments.dri9.rule import RULE_CUTS
from provenance.decision_relative import DecisionEvidence
from provenance.dependence_robustness import assess_dependence_robustness

FAMILIES = (
    "marked_hidden_pair",
    "unmarked_hidden_pair",
    "common_carrier",
    "leaky_independents",
)
HIDDEN_FAMILIES = ("marked_hidden_pair", "unmarked_hidden_pair")
HARM_FAMILIES = ("common_carrier", "leaky_independents")
MARKER = "marker"


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


@dataclasses.dataclass(frozen=True)
class Source:
    source_id: str
    accuracy: float
    component: str | None
    component_kind: str | None
    carrier: str | None


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
    marked_channel: str
    decisions: tuple[Decision, ...]


def _layout(
    config: Mapping[str, Any], family: str, rng: random.Random
) -> tuple[tuple[Source, ...], tuple[str, ...], str]:
    accuracies = tuple(config["source_accuracies"])
    n_ind = config["independents_per_campaign"]
    if family == "marked_hidden_pair":
        group = [
            Source(f"g{index}", rng.choice(accuracies), "hidden:u", HIDDEN, "hidden:u")
            for index in range(2)
        ]
        rest = [Source(f"i{index}", rng.choice(accuracies), None, None, None) for index in range(n_ind)]
        return tuple(group + rest), tuple(s.source_id for s in group), "hidden:u"
    if family == "unmarked_hidden_pair":
        group = [
            Source(f"g{index}", rng.choice(accuracies), "hidden:u", HIDDEN, None)
            for index in range(2)
        ]
        rest = [Source(f"i{index}", rng.choice(accuracies), None, None, None) for index in range(n_ind)]
        return tuple(group + rest), tuple(s.source_id for s in group), "env:public"
    if family == "common_carrier":
        group = [
            Source(f"c{index}", rng.choice(accuracies), None, None, "lib:shared")
            for index in range(3)
        ]
        rest = [Source(f"i{index}", rng.choice(accuracies), None, None, None) for index in range(n_ind)]
        return tuple(group + rest), tuple(s.source_id for s in group), "lib:shared"
    if family == "leaky_independents":
        low = min(accuracies)
        group = [Source(f"g{index}", low, None, None, None) for index in range(2)]
        rest = [Source(f"i{index}", rng.choice(accuracies), None, None, None) for index in range(n_ind)]
        return tuple(group + rest), tuple(s.source_id for s in group), "env:public"
    raise ValueError(f"unknown family {family}")


def _order(sources: tuple[Source, ...], jitter: float, rng: random.Random) -> tuple[str, ...]:
    blocks: list[list[str]] = []
    grouped: dict[str, list[str]] = {}
    for source in sources:
        key = source.component or source.carrier
        if key is None:
            blocks.append([source.source_id])
        else:
            grouped.setdefault(key, []).append(source.source_id)
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
    marked: str,
    pickup: float,
    leak: float,
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
    jitter = config["timing_jitter"]
    for source in sources:
        if source.component and faulty[source.component]:
            value = not truth
        else:
            value = truth if rng.random() < source.accuracy else not truth
        observation = f"{proposition}|{source.source_id}"
        # dri8._identities only reads component / component_kind / source_id.
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
        rate = pickup if source.carrier == marked else leak
        if rng.random() < rate:
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
    config: Mapping[str, Any], salt: str, family: str, replicate: int, pickup: float, leak: float
) -> Campaign:
    rng = random.Random(_seed(salt, family, replicate, pickup, leak))
    campaign_id = f"{family}|{replicate:05d}"
    sources, focus, marked = _layout(config, family, rng)
    decisions = tuple(
        _decision(config, campaign_id, index, sources, marked, pickup, leak, rng)
        for index in range(config["decisions_per_campaign"])
    )
    return Campaign(
        campaign_id=campaign_id,
        family=family,
        sources=sources,
        focus_group=focus,
        marked_channel=marked,
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
    return tuple((p, leak) for p in config["marker_pickups"] for leak in config["marker_leaks"])


def cell_key(pickup: float, leak: float) -> str:
    return f"pickup={pickup}|leak={leak}"


def parse_cell(cell: str) -> tuple[float, float]:
    p, leak = (float(part.split("=")[1]) for part in cell.split("|"))
    return p, leak


def iter_cell_campaigns(
    config: Mapping[str, Any], salt: str, campaigns_per_family: int | None = None
) -> Iterable[tuple[str, Campaign]]:
    count = config["campaigns_per_family"] if campaigns_per_family is None else campaigns_per_family
    for family in config["families"]:
        for replicate in range(count):
            for pickup, leak in cells(config):
                yield cell_key(pickup, leak), generate_campaign(
                    config, salt, family, replicate, pickup, leak
                )


def campaign_hash_row(cell: str, campaign: Campaign) -> bytes:
    row = {
        "cell": cell,
        "campaignId": campaign.campaign_id,
        "marked": campaign.marked_channel,
        "focus": list(campaign.focus_group),
        "sources": [
            [s.source_id, s.accuracy, s.component, s.component_kind, s.carrier] for s in campaign.sources
        ],
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
    "ALL_CUTS", "CONTENT_CUT", "Campaign", "Decision", "FAMILIES", "HARM_FAMILIES",
    "HIDDEN", "HIDDEN_FAMILIES", "MARKER", "Source", "campaign_hash_row", "cell_key",
    "cells", "cut_response", "generate_campaign", "iter_cell_campaigns", "parse_cell",
    "reveals",
]
