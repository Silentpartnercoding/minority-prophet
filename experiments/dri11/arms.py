"""DRI-11 arms. Methods named in DRI-11-DESIGN-DRAFT.md before this world existed."""

from __future__ import annotations

import itertools
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from experiments.dri3.world import SETTLED
from experiments.dri9.rule import ABSTAIN, Belief, believe, outcome_if_believed, settle
from experiments.dri11.world import Campaign, Decision, reveals

ARMS = (
    "tiered_rule",
    "fragile_refusal",
    "composite",
    "bait",
    "ladder",
    "oracle_reference",
)
SIGNAL_ARMS = ("composite", "bait", "ladder")
PRIMARY = "fragile_refusal"
SECONDARY = "composite"


@dataclass(frozen=True)
class Outcome:
    terminal: str
    stamped: bool
    looks: int
    interventions: int


def _winning_side_pairs(decision: Decision, terminal: str, belief: Belief) -> list[tuple[str, str]]:
    side = terminal == "settled_true" if terminal in SETTLED else None
    source_of = dict(decision.source_of)
    sources = sorted(
        {source_of[i.observation_id] for i in decision.evidence if side is None or i.value == side}
    )
    return [
        (a, b)
        for a, b in itertools.combinations(sources, 2)
        if belief.group_of(a) is None or belief.group_of(a) is not belief.group_of(b)
    ]


def _fragile(decision: Decision, terminal: str, stamped: bool, belief: Belief) -> bool:
    return any(
        outcome_if_believed(decision, belief, [pair]) != (terminal, stamped)
        for pair in _winning_side_pairs(decision, terminal, belief)
    )


def run_campaign(
    arm: str, campaign: Campaign, config: Mapping[str, Any], salt: str
) -> tuple[list[Outcome], Belief]:
    belief = Belief()
    marker_hits: dict[tuple[str, str], int] = {}
    coerror: dict[tuple[str, str], int] = {}
    joint: dict[tuple[str, str], int] = {}
    outcomes: list[Outcome] = []

    def signals(pair: tuple[str, str]) -> dict[str, bool]:
        return {
            "bait": marker_hits.get(pair, 0) >= config["marker_cooccurrences_to_merge"],
            "coerror": (
                joint.get(pair, 0) >= config["coerror_minimum_joint_decisions"]
                and coerror.get(pair, 0) / joint[pair] >= config["coerror_threshold"]
            ),
        }

    def score(pair: tuple[str, str]) -> int:
        available = signals(pair)
        return sum(int(available[name]) for name in config["ladder_signals"])

    for index, decision in enumerate(campaign.decisions):
        if arm == "oracle_reference":
            outcomes.append(Outcome(decision.reference if decision.reference in SETTLED else ABSTAIN, False, 0, 0))
            continue

        terminal, stamped, looks = settle(decision, believe(decision, belief))
        pairs = _winning_side_pairs(decision, terminal, belief)

        if arm == "fragile_refusal":
            if _fragile(decision, terminal, stamped, belief):
                terminal, stamped = ABSTAIN, False
        elif arm == "composite":
            merged = False
            for pair in pairs:
                if score(pair) >= config["ladder_score_to_merge"]:
                    belief.merge(*pair)
                    terminal, stamped, looks = settle(decision, believe(decision, belief))
                    merged = True
            if not merged:
                any_signal = any(any(signals(pair).values()) for pair in pairs)
                if _fragile(decision, terminal, stamped, belief) and not any_signal:
                    terminal, stamped = ABSTAIN, False
        elif arm == "bait":
            for pair in pairs:
                if marker_hits.get(pair, 0) >= config["marker_cooccurrences_to_merge"]:
                    belief.merge(*pair)
                    terminal, stamped, looks = settle(decision, believe(decision, belief))
        elif arm == "ladder":
            for pair in pairs:
                if score(pair) >= config["ladder_score_to_merge"]:
                    belief.merge(*pair)
                    terminal, stamped, looks = settle(decision, believe(decision, belief))

        outcomes.append(Outcome(terminal, stamped, looks, 0))

        source_of = dict(decision.source_of)
        carried: dict[str, set[str]] = {}
        for observation, marker in decision.markers:
            carried.setdefault(marker, set()).add(source_of[observation])
        sources = sorted({s for _, s in decision.source_of})
        revealed = decision.reference in SETTLED and reveals(
            config, salt, campaign, index, config["feedback_rate"]
        )
        wrong = {source_of[i.observation_id] for i in decision.evidence if i.value != decision.truth}
        for pair in itertools.combinations(sources, 2):
            if any(pair[0] in holders and pair[1] in holders for holders in carried.values()):
                marker_hits[pair] = marker_hits.get(pair, 0) + 1
            if revealed:
                joint[pair] = joint.get(pair, 0) + 1
                if pair[0] in wrong and pair[1] in wrong:
                    coerror[pair] = coerror.get(pair, 0) + 1

    return outcomes, belief
