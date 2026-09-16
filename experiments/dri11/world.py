"""DRI-11 world: every named method has a family that can fail it.

Claude named fragile refusal first and a two-signal composite second, then
asked for a world that can reject both. DRI-10 made refusal look broad because
every hidden family was a pair. DRI-9 already measured refusal at 0.00 on
trios. This world puts that case back, and adds the three traps DRI-10
omitted: expensive refusal, a baseline that is already right, and two signals
that agree because they share a cause.

Families:

- **unmarked_hidden_pair** — real dependence, no mark. Refusal must carry it.
- **unmarked_hidden_trio** — real dependence of three, no mark. Refusal tests
  pairs and cannot see it. DRI-9 footnote, now a failure condition.
- **marked_hidden_pair** — dependence with a mark. The composite's signals
  have something true to agree on.
- **fragile_correct** — baseline already right, and believing any winning
  pair would change the answer. Refusal's cost, as a family.
- **common_carrier** — shared library, no shared error. Collapse check.
- **shared_shock** — two independents are jointly wrong and jointly marked
  by one shock that is not an identity. Bait and co-error agree for the
  same reason. Kills corroboration.
- **robust_correct** — many independent high-accuracy sources, not fragile.
  Reflexive refusal or merging is pure loss.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import random
from collections.abc import Iterable, Mapping
from typing import Any

from experiments.dri3.world import IRREVERSIBLE, REVERSIBLE, SETTLED, settlement_over_units
from experiments.dri8.world import ALL_CUTS, CONTENT_CUT, HIDDEN, _identities
from experiments.dri9.rule import RULE_CUTS, Belief, believe, outcome_if_believed, settle
from provenance.decision_relative import DecisionEvidence
from provenance.dependence_robustness import assess_dependence_robustness

FAMILIES = (
    "unmarked_hidden_pair",
    "unmarked_hidden_trio",
    "marked_hidden_pair",
    "fragile_correct",
    "common_carrier",
    "shared_shock",
    "robust_correct",
)
DEPENDENCE_FAMILIES = (
    "unmarked_hidden_pair",
    "unmarked_hidden_trio",
    "marked_hidden_pair",
)
HARM_FAMILIES = ("common_carrier", "shared_shock", "robust_correct", "fragile_correct")
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
    shocked: bool


@dataclasses.dataclass(frozen=True)
class Campaign:
    campaign_id: str
    family: str
    sources: tuple[Source, ...]
    focus_group: tuple[str, ...]
    marked_channel: str
    shocked_pair: tuple[str, str] | None
    decisions: tuple[Decision, ...]


def _layout(
    config: Mapping[str, Any], family: str, rng: random.Random
) -> tuple[tuple[Source, ...], tuple[str, ...], str, tuple[str, str] | None]:
    accuracies = tuple(config["source_accuracies"])
    n_ind = config["independents_per_campaign"]
    high = max(accuracies)
    if family == "unmarked_hidden_pair":
        group = [Source(f"g{i}", rng.choice(accuracies), "hidden:u", HIDDEN, None) for i in range(2)]
        rest = [Source(f"i{i}", rng.choice(accuracies), None, None, None) for i in range(n_ind)]
        return tuple(group + rest), tuple(s.source_id for s in group), "env:public", None
    if family == "unmarked_hidden_trio":
        group = [Source(f"g{i}", rng.choice(accuracies), "hidden:u", HIDDEN, None) for i in range(3)]
        rest = [Source(f"i{i}", rng.choice(accuracies), None, None, None) for i in range(n_ind)]
        return tuple(group + rest), tuple(s.source_id for s in group), "env:public", None
    if family == "marked_hidden_pair":
        group = [Source(f"g{i}", rng.choice(accuracies), "hidden:u", HIDDEN, "hidden:u") for i in range(2)]
        rest = [Source(f"i{i}", rng.choice(accuracies), None, None, None) for i in range(n_ind)]
        return tuple(group + rest), tuple(s.source_id for s in group), "hidden:u", None
    if family == "fragile_correct":
        # Exactly two truth-tellers and one opponent: 2 vs 1 at threshold 2.
        # Merging the winning pair drops the true side to one root.
        group = [Source(f"g{i}", high, None, None, None) for i in range(2)]
        rest = [Source("i0", high, None, None, None)]
        return tuple(group + rest), tuple(s.source_id for s in group), "env:public", None
    if family == "common_carrier":
        group = [Source(f"c{i}", rng.choice(accuracies), None, None, "lib:shared") for i in range(3)]
        rest = [Source(f"i{i}", rng.choice(accuracies), None, None, None) for i in range(n_ind)]
        return tuple(group + rest), tuple(s.source_id for s in group), "lib:shared", None
    if family == "shared_shock":
        pair = [Source(f"s{i}", rng.choice(accuracies), None, None, None) for i in range(2)]
        rest = [Source(f"i{i}", rng.choice(accuracies), None, None, None) for i in range(n_ind)]
        return tuple(pair + rest), tuple(s.source_id for s in pair), "env:public", (pair[0].source_id, pair[1].source_id)
    if family == "robust_correct":
        sources = tuple(Source(f"i{i}", high, None, None, None) for i in range(6))
        return sources, (), "env:public", None
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


def is_fragile_correct(decision: Decision) -> bool:
    """Baseline settles the reference, and merging some winning pair would move it."""
    if decision.reference not in SETTLED:
        return False
    terminal, stamped, _ = settle(decision, believe(decision, Belief()))
    if terminal != decision.reference:
        return False
    side = terminal == "settled_true"
    source_of = dict(decision.source_of)
    winners = sorted({
        source_of[i.observation_id] for i in decision.evidence if i.value == side
    })
    from itertools import combinations
    return any(
        outcome_if_believed(decision, Belief(), [pair]) != (terminal, stamped)
        for pair in combinations(winners, 2)
    )


def _pack(
    config: Mapping[str, Any],
    campaign_id: str,
    index: int,
    sources: tuple[Source, ...],
    marked: str,
    values: dict[str, bool],
    truth: bool,
    decision_class: str,
    holders: set[str],
    rng: random.Random,
    shocked: bool,
) -> Decision:
    threshold = config["decision_classes"][decision_class]
    proposition = f"{campaign_id}|d{index:02d}"
    evidence: list[DecisionEvidence] = []
    units: list[tuple[str, str]] = []
    source_of: list[tuple[str, str]] = []
    markers: list[tuple[str, str]] = []
    for source in sources:
        observation = f"{proposition}|{source.source_id}"
        evidence.append(
            DecisionEvidence(
                observation_id=observation,
                proposition_id=proposition,
                value=values[source.source_id],
                roots=_identities(source, proposition),
                basis={cut: "attested" for cut in ALL_CUTS},
            )
        )
        units.append((observation, source.component or source.source_id))
        source_of.append((observation, source.source_id))
        if source.source_id in holders:
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
        order=_order(sources, config["timing_jitter"], rng),
        reference=reference,
        record_settles_reference=robustness.robust and robustness.settlement == reference,
        shocked=shocked,
    )


def _ordinary_values(
    sources: tuple[Source, ...], truth: bool, rng: random.Random, config: Mapping[str, Any]
) -> dict[str, bool]:
    faulty = {
        component: rng.random() < config["component_fault_rate"]
        for component in sorted({s.component for s in sources if s.component})
    }
    values = {}
    for source in sources:
        if source.component and faulty[source.component]:
            values[source.source_id] = not truth
        else:
            values[source.source_id] = truth if rng.random() < source.accuracy else not truth
    return values


def _decision(
    config: Mapping[str, Any],
    campaign: str,
    index: int,
    sources: tuple[Source, ...],
    marked: str,
    pickup: float,
    leak: float,
    rng: random.Random,
    family: str,
    shocked_pair: tuple[str, str] | None,
) -> Decision:
    decision_class = IRREVERSIBLE if index % 2 == 0 else REVERSIBLE
    truth = bool(rng.getrandbits(1))
    shocked = False
    holders: set[str] = set()

    if family == "fragile_correct" and decision_class == REVERSIBLE:
        focus = [s.source_id for s in sources if s.source_id.startswith("g")]
        others = [s.source_id for s in sources if s.source_id not in focus]
        values = {sid: truth for sid in [s.source_id for s in sources]}
        if others:
            values[others[0]] = not truth
        for source in sources:
            if rng.random() < leak:
                holders.add(source.source_id)
        packed = _pack(config, campaign, index, sources, marked, values, truth, decision_class, holders, rng, False)
        if is_fragile_correct(packed):
            return packed
        # Fall through to ordinary sampling if the shape missed.

    if family == "shared_shock" and shocked_pair is not None:
        shocked = rng.random() < config["shock_rate"]
        if shocked:
            values = _ordinary_values(sources, truth, rng, config)
            values[shocked_pair[0]] = not truth
            values[shocked_pair[1]] = not truth
            holders = {shocked_pair[0], shocked_pair[1]}
            for source in sources:
                if source.source_id not in holders and rng.random() < leak:
                    holders.add(source.source_id)
            return _pack(config, campaign, index, sources, marked, values, truth, decision_class, holders, rng, True)

    values = _ordinary_values(sources, truth, rng, config)
    for source in sources:
        rate = pickup if source.carrier == marked else leak
        if rng.random() < rate:
            holders.add(source.source_id)
    return _pack(config, campaign, index, sources, marked, values, truth, decision_class, holders, rng, shocked)


def generate_campaign(
    config: Mapping[str, Any], salt: str, family: str, replicate: int, pickup: float, leak: float
) -> Campaign:
    rng = random.Random(_seed(salt, family, replicate, pickup, leak))
    campaign_id = f"{family}|{replicate:05d}"
    sources, focus, marked, shocked_pair = _layout(config, family, rng)
    decisions = tuple(
        _decision(config, campaign_id, index, sources, marked, pickup, leak, rng, family, shocked_pair)
        for index in range(config["decisions_per_campaign"])
    )
    return Campaign(
        campaign_id=campaign_id,
        family=family,
        sources=sources,
        focus_group=focus,
        marked_channel=marked,
        shocked_pair=shocked_pair,
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
        "shocked": list(campaign.shocked_pair) if campaign.shocked_pair else None,
        "sources": [
            [s.source_id, s.accuracy, s.component, s.component_kind, s.carrier] for s in campaign.sources
        ],
        "decisions": [
            {
                "id": d.decision_id,
                "truth": d.truth,
                "class": d.decision_class,
                "reference": d.reference,
                "shocked": d.shocked,
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
