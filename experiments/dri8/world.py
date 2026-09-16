"""DRI-8 world generator: persistent sources, hidden shared upstream, probes.

A **campaign** is one population of sources answering a sequence of decisions.
Persistence is the whole point: a track record needs the same sources to appear
again, and a probe needs something to probe.

Each campaign carries two kinds of dependence and one independent source:

- **hidden:** sources that share an upstream component recorded at no cut, with
  independent content. Neither DRI-4's engine nor DRI-5's fingerprint can see it.
  This is the case DR3 proves no record-only rule can settle.
- **recorded:** a pair that shares an identity at the upstream-component cut and
  is truly one source. DRI-4's missing-lineage degradation can erase that link,
  which is how the combined failure is tested.

A component has a per-decision fault state. When it is faulty every source
drawing on it errs together; otherwise each source errs independently at its own
rate.

The lookup returns the grouping the lineage system knows: recorded dependence
included, the hidden component never. It is therefore wrong the same way on every
call, which is the correlated lookup error DRI-6 declared out of scope.

Probes are the intervention. `probe_result` puts a tracer through one source's
upstream and reports whether the other source's next report carries it: a shared
path carries it with probability `probe_detect`, an unrelated one with
`probe_leak`. Results are drawn from a stream keyed by campaign, pair and probe
index, so every arm that spends its nth probe on a pair sees the same answer.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import random
from collections.abc import Iterable, Mapping
from typing import Any

from experiments.dri3.world import (
    CUTS,
    IRREVERSIBLE,
    REVERSIBLE,
    settlement_over_units,
    settlements_at_cuts,
)
from provenance.decision_relative import DecisionEvidence
from provenance.dependence_robustness import assess_dependence_robustness

CONTENT_CUT = "content"
ALL_CUTS = CUTS + (CONTENT_CUT,)
HIDDEN = "hidden"
RECORDED = "recorded"
FAMILIES = ("shared_upstream_pair", "shared_upstream_trio", "coincident_independents")


def _seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big")


@dataclasses.dataclass(frozen=True)
class Source:
    source_id: str
    accuracy: float
    component: str | None
    """The upstream component this source draws on, or None. Hidden components
    are absent from every cut; recorded ones appear at `upstream_component`."""
    component_kind: str | None


@dataclasses.dataclass(frozen=True)
class Decision:
    decision_id: str
    truth: bool
    threshold: int
    decision_class: str
    evidence: tuple[DecisionEvidence, ...]
    units: tuple[tuple[str, str], ...]
    source_of: tuple[tuple[str, str], ...]
    reference: str
    record_settles_reference: bool


@dataclasses.dataclass(frozen=True)
class Campaign:
    campaign_id: str
    family: str
    sources: tuple[Source, ...]
    decisions: tuple[Decision, ...]


def _sources(config: Mapping[str, Any], family: str, rng: random.Random) -> tuple[Source, ...]:
    """Six persistent sources. 0..n share a hidden component (or, in the decoy
    family, merely share low accuracy); 3 and 4 share a recorded one; 5 is alone."""
    accuracies = tuple(config["source_accuracies"])
    low = min(accuracies)
    hidden_size = {"shared_upstream_pair": 2, "shared_upstream_trio": 3, "coincident_independents": 0}[family]
    sources = []
    for index in range(config["sources_per_campaign"]):
        if index < max(hidden_size, 2) and family == "coincident_independents":
            accuracy, component, kind = low, None, None
        elif index < hidden_size:
            accuracy, component, kind = rng.choice(accuracies), "hidden:u", HIDDEN
        elif index in (3, 4):
            accuracy, component, kind = rng.choice(accuracies), "recorded:u", RECORDED
        else:
            accuracy, component, kind = rng.choice(accuracies), None, None
        sources.append(Source(f"s{index}", accuracy, component, kind))
    return tuple(sources)


def _identities(source: Source, decision_id: str) -> dict[str, str]:
    """What the record shows. A recorded component is shared at its cut; a hidden
    one leaves no trace anywhere, and content differs per source and decision."""
    roots = {
        "agent": f"agent:{source.source_id}",
        "machine": f"machine:{source.source_id}",
        "controller": f"controller:{source.source_id}",
        "evidence_origin": f"evidence_origin:{source.source_id}",
        "upstream_component": (
            f"upstream_component:{source.component}"
            if source.component_kind == RECORDED
            else f"upstream_component:{source.source_id}"
        ),
    }
    roots[CONTENT_CUT] = f"{CONTENT_CUT}:{decision_id}|{source.source_id}"
    return roots


def _decision(
    config: Mapping[str, Any], campaign_id: str, index: int, sources: tuple[Source, ...], rng: random.Random
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
    return _finish(proposition, truth, threshold, decision_class, tuple(evidence), tuple(units), tuple(source_of))


def _finish(
    decision_id: str,
    truth: bool,
    threshold: int,
    decision_class: str,
    evidence: tuple[DecisionEvidence, ...],
    units: tuple[tuple[str, str], ...],
    source_of: tuple[tuple[str, str], ...],
) -> Decision:
    reference = settlement_over_units(evidence, units, threshold)
    robustness = assess_dependence_robustness(evidence, threshold, ALL_CUTS)
    return Decision(
        decision_id=decision_id,
        truth=truth,
        threshold=threshold,
        decision_class=decision_class,
        evidence=evidence,
        units=units,
        source_of=source_of,
        reference=reference,
        record_settles_reference=robustness.robust and robustness.settlement == reference,
    )


def generate_campaign(config: Mapping[str, Any], salt: str, family: str, replicate: int) -> Campaign:
    rng = random.Random(_seed(salt, family, replicate))
    campaign_id = f"{family}|{replicate:05d}"
    sources = _sources(config, family, rng)
    decisions = tuple(
        _decision(config, campaign_id, index, sources, rng)
        for index in range(config["decisions_per_campaign"])
    )
    return Campaign(campaign_id=campaign_id, family=family, sources=sources, decisions=decisions)


def degrade(decision: Decision, missing: float, rng: random.Random) -> Decision:
    """DRI-4's model, applied to the one dependence this record does carry: each
    recorded shared identity is split into distinct ones with probability m."""
    if missing == 0:
        return decision
    unit_of = dict(decision.units)
    groups: dict[str, list[str]] = {}
    for item in decision.evidence:
        groups.setdefault(item.roots["upstream_component"], []).append(item.observation_id)
    split = {
        identity
        for identity, members in sorted(groups.items())
        if len(members) > 1 and len({unit_of[o] for o in members}) == 1 and rng.random() < missing
    }
    if not split:
        return decision
    evidence = tuple(
        DecisionEvidence(
            observation_id=item.observation_id,
            proposition_id=item.proposition_id,
            value=item.value,
            roots={
                **dict(item.roots),
                "upstream_component": (
                    f"upstream_component:missing:{item.observation_id}"
                    if item.roots["upstream_component"] in split
                    else item.roots["upstream_component"]
                ),
            },
            basis=dict(item.basis),
        )
        for item in decision.evidence
    )
    return _finish(
        decision.decision_id, decision.truth, decision.threshold, decision.decision_class,
        evidence, decision.units, decision.source_of,
    )


def lookup_grouping(decision: Decision) -> tuple[tuple[str, str], ...]:
    """What the lineage system can report: recorded dependence, never the hidden
    component. Systematically wrong the same way on every call."""
    return tuple(
        (item.observation_id, item.roots["upstream_component"])
        for item in decision.evidence
    )


def probe_result(
    config: Mapping[str, Any], salt: str, campaign: Campaign, left: str, right: str, index: int
) -> bool:
    """One tracer, from a stream shared by every arm.

    True when the tracer arrives. A shared upstream carries it with
    `probe_detect`; unrelated sources carry it only by coincidence, at
    `probe_leak`.
    """
    components = {source.source_id: source.component for source in campaign.sources}
    shared = components.get(left) is not None and components.get(left) == components.get(right)
    rate = config["probe_detect"] if shared else config["probe_leak"]
    pair = "|".join(sorted((left, right)))
    rng = random.Random(_seed(salt, "probe", campaign.campaign_id, pair, index))
    return rng.random() < rate


def reveals(config: Mapping[str, Any], salt: str, campaign: Campaign, index: int, feedback: float) -> bool:
    """Whether decision `index`'s true settlement is revealed to a learner."""
    rng = random.Random(_seed(salt, "feedback", campaign.campaign_id, index))
    return rng.random() < feedback


def cells(config: Mapping[str, Any]) -> tuple[tuple[float, float, int], ...]:
    return tuple(
        (m, r, b)
        for m in config["missing_rates"]
        for r in config["feedback_rates"]
        for b in config["probe_budgets"]
    )


def cell_key(missing: float, feedback: float, budget: int) -> str:
    return f"m={missing}|r={feedback}|b={budget}"


def parse_cell(cell: str) -> tuple[float, float, int]:
    m, r, b = (part.split("=")[1] for part in cell.split("|"))
    return float(m), float(r), int(b)


def degraded_campaign(config: Mapping[str, Any], salt: str, base: Campaign, missing: float) -> Campaign:
    rng = random.Random(_seed(salt, "degrade", base.campaign_id, missing))
    return dataclasses.replace(base, decisions=tuple(degrade(d, missing, rng) for d in base.decisions))


def iter_cell_campaigns(
    config: Mapping[str, Any], salt: str, campaigns_per_family: int | None = None
) -> Iterable[tuple[str, Campaign]]:
    count = config["campaigns_per_family"] if campaigns_per_family is None else campaigns_per_family
    for family in config["families"]:
        for replicate in range(count):
            base = generate_campaign(config, salt, family, replicate)
            for missing in config["missing_rates"]:
                degraded = degraded_campaign(config, salt, base, missing)
                for feedback in config["feedback_rates"]:
                    for budget in config["probe_budgets"]:
                        yield cell_key(missing, feedback, budget), degraded


def campaign_hash_row(cell: str, campaign: Campaign) -> bytes:
    row = {
        "cell": cell,
        "campaignId": campaign.campaign_id,
        "sources": [[s.source_id, s.accuracy, s.component, s.component_kind] for s in campaign.sources],
        "decisions": [
            {
                "id": d.decision_id,
                "truth": d.truth,
                "class": d.decision_class,
                "reference": d.reference,
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
    "ALL_CUTS", "CONTENT_CUT", "Campaign", "Decision", "FAMILIES", "HIDDEN", "RECORDED", "Source",
    "campaign_hash_row", "cell_key", "cells", "degrade", "degraded_campaign", "generate_campaign",
    "iter_cell_campaigns", "lookup_grouping", "parse_cell", "probe_result", "reveals",
    "settlements_at_cuts",
]
