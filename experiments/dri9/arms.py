"""DRI-9 arms: one free rule, three instruments, and a ladder built from them.

Every arm decides with `rule.settle` over what it believes, so a merge an arm
comes to believe actually changes the identities the rule counts. DRI-8's arms
appended the merge as one extra cut and left the record's own identities in
place, which is why merging the true hidden group changed 0 settlements in 720
decisions there. That fix is the point of this experiment.

- **tiered rule** — the baseline: the record, believed as written.
- **fragile refusal** — free. Abstains when believing any two winning-side
  sources were one would change the answer. Spends nothing, learns nothing, and
  attacks the pile where the rule was wrong because it answered at all.
- **bait** — believes a pair seen carrying the same planted marker often enough.
  Planting happens before the decisions, so nothing is spent during them.
- **reflection** — believes a pair whose reports arrive in a consistent order
  often enough. Free, and the weakest signal.
- **ablation** — cuts a source's upstream and watches who changes with it.
  Strongest and most violent: the decision it is spent on loses that testimony,
  and the budget is small.
- **ladder (method under test)** — believes a pair when at least
  `ladder_score_to_merge` of its signals agree: bait, timing, co-error. Named
  before the run so the best of six arms cannot be picked afterwards.

Believing wrongly is a real cost: a believed pair that is in fact independent
loses a root on its own side, which in the decoy family moves decisions away from
the truth.
"""

from __future__ import annotations

import itertools
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from experiments.dri3.world import SETTLED
from experiments.dri9.rule import ABSTAIN, Belief, believe, outcome_if_believed, settle
from experiments.dri9.world import Campaign, Decision, cut_response, reveals

ARMS = ("tiered_rule", "fragile_refusal", "bait", "reflection", "ablation", "ladder", "oracle_reference")
SIGNAL_ARMS = ("bait", "reflection", "ablation", "ladder")
METHOD = "ladder"


@dataclass(frozen=True)
class Outcome:
    terminal: str
    stamped: bool
    looks: int
    interventions: int


def _winning_side_pairs(decision: Decision, terminal: str, belief: Belief) -> list[tuple[str, str]]:
    """Unbelieved pairs on the winning side. Shrinking the losing side cannot
    change which side wins."""
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


def run_campaign(
    arm: str, campaign: Campaign, config: Mapping[str, Any], salt: str
) -> tuple[list[Outcome], Belief]:
    belief = Belief()
    marker_hits: dict[tuple[str, str], int] = {}
    order_before: dict[tuple[str, str], int] = {}
    order_seen: dict[tuple[str, str], int] = {}
    coerror: dict[tuple[str, str], int] = {}
    joint: dict[tuple[str, str], int] = {}
    cuts_left = config["ablation_budget"]
    outcomes: list[Outcome] = []

    def timing_consistent(pair: tuple[str, str]) -> bool:
        seen = order_seen.get(pair, 0)
        if seen < config["timing_minimum_decisions"]:
            return False
        before = order_before.get(pair, 0)
        return max(before, seen - before) / seen >= config["timing_consistency_threshold"]

    def score(pair: tuple[str, str]) -> int:
        """Votes from the ladder's declared signals only.

        Timing is excluded by configuration, decided before the run: on the
        development world it made hundreds of false merges and destroyed correct
        settlements, so letting it supply a vote would contaminate the method
        under test. It still runs as its own arm, so that failure is recorded.
        """
        available = {
            "bait": marker_hits.get(pair, 0) >= config["marker_cooccurrences_to_merge"],
            "timing": timing_consistent(pair),
            "coerror": (
                joint.get(pair, 0) >= config["coerror_minimum_joint_decisions"]
                and coerror.get(pair, 0) / joint[pair] >= config["coerror_threshold"]
            ),
        }
        return sum(int(available[name]) for name in config["ladder_signals"])

    for index, decision in enumerate(campaign.decisions):
        if arm == "oracle_reference":
            outcomes.append(Outcome(decision.reference if decision.reference in SETTLED else ABSTAIN, False, 0, 0))
            continue

        terminal, stamped, looks = settle(decision, believe(decision, belief))
        spent = 0

        if arm == "fragile_refusal":
            if any(
                outcome_if_believed(decision, belief, [pair]) != (terminal, stamped)
                for pair in _winning_side_pairs(decision, terminal, belief)
            ):
                terminal, stamped = ABSTAIN, False
        elif arm == "ablation" and cuts_left > 0:
            for pair in _winning_side_pairs(decision, terminal, belief):
                if cuts_left <= 0:
                    break
                if outcome_if_believed(decision, belief, [pair]) == (terminal, stamped):
                    continue
                cuts_left -= 1
                spent += 1
                if cut_response(config, salt, campaign, pair[0], pair[1], index):
                    belief.merge(*pair)
                # The cut decision loses its testimony either way.
                terminal, stamped = ABSTAIN, False
                break
        elif arm in ("bait", "reflection", "ladder"):
            for pair in _winning_side_pairs(decision, terminal, belief):
                if arm == "bait":
                    convinced = marker_hits.get(pair, 0) >= config["marker_cooccurrences_to_merge"]
                elif arm == "reflection":
                    convinced = timing_consistent(pair)
                else:
                    convinced = score(pair) >= config["ladder_score_to_merge"]
                if convinced:
                    belief.merge(*pair)
                    terminal, stamped, looks = settle(decision, believe(decision, belief))

        outcomes.append(Outcome(terminal, stamped, looks, spent))

        source_of = dict(decision.source_of)
        carried: dict[str, set[str]] = {}
        for observation, marker in decision.markers:
            carried.setdefault(marker, set()).add(source_of[observation])
        position = {source: place for place, source in enumerate(decision.order)}
        sources = sorted({s for _, s in decision.source_of})
        revealed = decision.reference in SETTLED and reveals(config, salt, campaign, index, config["feedback_rate"])
        wrong = {source_of[i.observation_id] for i in decision.evidence if i.value != decision.truth}
        for pair in itertools.combinations(sources, 2):
            if any(pair[0] in holders and pair[1] in holders for holders in carried.values()):
                marker_hits[pair] = marker_hits.get(pair, 0) + 1
            order_seen[pair] = order_seen.get(pair, 0) + 1
            if position[pair[0]] < position[pair[1]]:
                order_before[pair] = order_before.get(pair, 0) + 1
            if revealed:
                joint[pair] = joint.get(pair, 0) + 1
                if pair[0] in wrong and pair[1] in wrong:
                    coerror[pair] = coerror.get(pair, 0) + 1

    return outcomes, belief
