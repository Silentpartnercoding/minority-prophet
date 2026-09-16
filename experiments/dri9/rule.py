"""The rule DRI-9 tests, and what it means to believe two sources are one.

DRI-8 recorded a learned merge as an identity at one extra cut and left the
record's own identities untouched. The rule settles across all cuts together, so
the five that still described the disguise — separate machine, separate
controller, separate origin — outvoted the one that said "these are the same
source". Measured on DRI-8's own world, merging the true hidden group changed
**0 settlements in 720 decisions** in each family. An arm could discover the
dependence and then be unable to act on it.

`believe` fixes that. Believing two sources are one means their separate recorded
identities stop being evidence of independence, so every cut is rewritten for the
merged group. On DRI-9's development world the same comparison changed 0 of 960
decisions when the merge was added as a cut, and 316 and 368 when it was believed
this way, every one of those toward the true grouping.

Both the generator and the arms import this module, so the situations the world
places and the rule the arms run are the same function by construction. That is
the other lesson from DRI-8, where the world was built against plain root
counting while the rule settled over six cuts, and the two disagreed everywhere.
"""

from __future__ import annotations

import itertools

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from experiments.dri3.world import CUTS, IRREVERSIBLE, SETTLED
from provenance.decision_relative import DecisionContext, DecisionEvidence, assess_decision
from provenance.dependence_robustness import assess_dependence_robustness

ABSTAIN = "abstain"
BELIEF_CUT = "belief"
RULE_CUTS = CUTS + (BELIEF_CUT,)


@dataclass
class Belief:
    """Which sources an arm has come to believe are one."""

    groups: list[set[str]] = field(default_factory=list)

    def group_of(self, source: str) -> set[str] | None:
        for group in self.groups:
            if source in group:
                return group
        return None

    def merge(self, left: str, right: str) -> None:
        a, b = self.group_of(left), self.group_of(right)
        if a is not None and a is b:
            return
        joined = (a or {left}) | (b or {right})
        self.groups = [g for g in self.groups if g is not a and g is not b] + [joined]

    def label(self, source: str) -> str | None:
        group = self.group_of(source)
        return "+".join(sorted(group)) if group and len(group) > 1 else None

    def copy(self) -> "Belief":
        return Belief(groups=[set(g) for g in self.groups])

    def pairs(self) -> list[tuple[str, str]]:
        out = []
        for group in self.groups:
            members = sorted(group)
            for index, left in enumerate(members):
                out.extend((left, right) for right in members[index + 1:])
        return out


def believe(decision: Any, belief: Belief) -> tuple[DecisionEvidence, ...]:
    """The evidence as it stands once `belief` is taken seriously.

    A believed group shares one identity at EVERY cut: the separate identities
    the record gives them were the disguise, not evidence. Sources in no group
    keep the record exactly as it is.
    """
    source_of = dict(decision.source_of)
    out = []
    for item in decision.evidence:
        source = source_of[item.observation_id]
        label = belief.label(source)
        roots = dict(item.roots)
        if label is not None:
            for cut in CUTS:
                roots[cut] = f"{cut}:believed:{label}"
        roots[BELIEF_CUT] = f"{BELIEF_CUT}:{label or source}"
        out.append(
            DecisionEvidence(
                observation_id=item.observation_id,
                proposition_id=item.proposition_id,
                value=item.value,
                roots=roots,
                basis=dict(item.basis),
            )
        )
    return tuple(out)


def _settlements_at(
    evidence: tuple[DecisionEvidence, ...], threshold: int, cuts: tuple[str, ...]
) -> dict[str, str]:
    proposition = evidence[0].proposition_id
    result = assess_decision(
        evidence,
        DecisionContext(
            decision_id=proposition,
            proposition_id=proposition,
            failure_domain="undisclosed",
            independence_cut=cuts[0],
            minimum_winning_roots=threshold,
            cut_selection_basis="unknown",
            candidate_cuts=cuts,
        ),
    )
    by_cut = {result.selected.independence_cut: result.selected, **dict(result.alternatives)}
    return {cut: by_cut[cut].settlement for cut in cuts}


def _terminal(settlement: str | None) -> str:
    return settlement if settlement in SETTLED else ABSTAIN


def lookup_grouping(decision: Any) -> tuple[tuple[str, str], ...]:
    """What the lineage system can report: recorded dependence, never a hidden
    component and never an arm's belief. Wrong the same way on every call."""
    return tuple(
        (item.observation_id, item.roots["upstream_component"]) for item in decision.evidence
    )


def settle(decision: Any, evidence: tuple[DecisionEvidence, ...]) -> tuple[str, bool, int]:
    """The tiered rule: (terminal, stamped, looks), over RULE_CUTS."""
    from experiments.dri3.world import settlement_over_units

    robustness = assess_dependence_robustness(evidence, decision.threshold, RULE_CUTS)
    if decision.decision_class == IRREVERSIBLE:
        if robustness.robust:
            return _terminal(robustness.settlement), False, 0
        return _terminal(settlement_over_units(evidence, lookup_grouping(decision), decision.threshold)), False, 1
    values = set(_settlements_at(evidence, decision.threshold, RULE_CUTS).values())
    if len(values) == 1:
        terminal = _terminal(values.pop())
        if terminal == ABSTAIN:
            return ABSTAIN, False, 0
        return terminal, not (robustness.robust and robustness.settlement == terminal), 0
    return _terminal(settlement_over_units(evidence, lookup_grouping(decision), decision.threshold)), False, 1


def outcome_if_believed(decision: Any, belief: Belief, extra: Iterable[tuple[str, str]] = ()) -> tuple[str, bool]:
    """What the rule would decide with `belief` plus any extra merges."""
    trial = belief.copy()
    for left, right in extra:
        trial.merge(left, right)
    terminal, stamped, _ = settle(decision, believe(decision, trial))
    return terminal, stamped


def is_pivotal(decision: Any, group: tuple[str, ...]) -> bool:
    """Whether believing any subset of `group` changes what the rule decides.

    This is the definition the generator places against and the scoring measures,
    so the world and the rule cannot drift apart the way they did in DRI-8.
    """
    if len(group) < 2:
        return False
    base = outcome_if_believed(decision, Belief())
    for size in range(2, len(group) + 1):
        for subset in itertools.combinations(group, size):
            pairs = [(subset[0], other) for other in subset[1:]]
            if outcome_if_believed(decision, Belief(), pairs) != base:
                return True
    return False
