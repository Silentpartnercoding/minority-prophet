"""DRI-8 arms: per-decision rules, and two that learn across a campaign.

Every arm ends each decision the way DRI-3's tiered rule does: settle when the
record is robust (or when the cuts agree, stamping a settlement that is not
robust), otherwise look. The lookup is the one this world provides, which knows
recorded dependence and never the hidden component.

What differs is what each arm knows by the time it gets there.

- **tiered rule** — nothing. The DRI-3 baseline.
- **content tiered rule** — DRI-5's fingerprint as an extra cut. Content is
  independent per source here, so this is a control, not a contender.
- **track record** — merges a pair once it has been wrong together often enough,
  over enough decisions whose outcome was revealed. Free, and slow.
- **probe** — shakes the tree. When merging a suspect pair *would change this
  decision's settlement*, it spends a probe on that pair; otherwise it spends
  nothing, because a dependence that cannot move the outcome does not matter
  here. Enough positive tracers and the pair is merged from then on.

The margin test is exact rather than a heuristic: the settlement is recomputed
with the pair merged and compared. That is the don't-care zone the flip budget
describes, decided per decision instead of by a threshold.

A learned merge is applied as an identity at a `learned` cut, so it reaches the
engine the same way any recorded shared identity would. Learning can be wrong:
merging two genuinely independent sources removes a root from their side and can
hand the decision to the other one.
"""

from __future__ import annotations

import itertools
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from experiments.dri3.world import IRREVERSIBLE, SETTLED, settlement_over_units
from experiments.dri8.world import (
    ALL_CUTS,
    CONTENT_CUT,
    Campaign,
    Decision,
    lookup_grouping,
    probe_result,
    reveals,
)
from experiments.dri3.world import CUTS
from provenance.decision_relative import DecisionContext, DecisionEvidence, assess_decision
from provenance.dependence_robustness import assess_dependence_robustness

ABSTAIN = "abstain"
LEARNED_CUT = "learned"
TIERED_CUTS = CUTS
CONTENT_CUTS = ALL_CUTS
LEARNING_CUTS = CUTS + (LEARNED_CUT,)
ARMS = ("tiered_rule", "content_tiered_rule", "track_record", "probe", "oracle_reference")


@dataclass(frozen=True)
class Outcome:
    terminal: str
    stamped: bool
    looks: int
    probes: int


@dataclass
class Learned:
    """Merges an arm has decided on, as groups of source ids."""

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
        return "learned:" + "+".join(sorted(group)) if group else None


def _settlements_at(
    evidence: tuple[DecisionEvidence, ...], threshold: int, cuts: tuple[str, ...]
) -> dict[str, str]:
    """Each cut's settlement, over the cuts THIS arm reads.

    DRI-3's helper is fixed to the five lineage cuts. An arm that has learned a
    merge is making a claim about dependence, and a claim the arm cannot act on
    is not a claim, so the learned cut takes part in the agreement check like any
    other.
    """
    proposition = evidence[0].proposition_id
    context = DecisionContext(
        decision_id=proposition,
        proposition_id=proposition,
        failure_domain="undisclosed",
        independence_cut=cuts[0],
        minimum_winning_roots=threshold,
        cut_selection_basis="unknown",
        candidate_cuts=cuts,
    )
    result = assess_decision(evidence, context)
    by_cut = {result.selected.independence_cut: result.selected, **dict(result.alternatives)}
    return {cut: by_cut[cut].settlement for cut in cuts}


def _terminal(settlement: str | None) -> str:
    return settlement if settlement in SETTLED else ABSTAIN


def _with_learned(decision: Decision, learned: Learned) -> tuple[DecisionEvidence, ...]:
    source_of = dict(decision.source_of)
    return tuple(
        DecisionEvidence(
            observation_id=item.observation_id,
            proposition_id=item.proposition_id,
            value=item.value,
            roots={
                **dict(item.roots),
                # Total, not partial: a source in no merged group still gets its
                # own identity here. A cut that only some observations carry
                # leaves the rest unattributed at it, which would make every
                # decision disagree across cuts for the wrong reason.
                LEARNED_CUT: (
                    learned.label(source_of[item.observation_id])
                    or f"{LEARNED_CUT}:{source_of[item.observation_id]}"
                ),
            },
            basis=dict(item.basis),
        )
        for item in decision.evidence
    )


def _settle(
    decision: Decision, evidence: tuple[DecisionEvidence, ...], cuts: tuple[str, ...]
) -> tuple[str, bool, int]:
    """The DRI-3 tiered rule over `cuts`: (terminal, stamped, looks)."""
    robustness = assess_dependence_robustness(evidence, decision.threshold, cuts)
    if decision.decision_class == IRREVERSIBLE:
        if robustness.robust:
            return _terminal(robustness.settlement), False, 0
        return _look(decision, evidence), False, 1
    values = set(_settlements_at(evidence, decision.threshold, cuts).values())
    if len(values) == 1:
        terminal = _terminal(values.pop())
        if terminal == ABSTAIN:
            return ABSTAIN, False, 0
        return terminal, not (robustness.robust and robustness.settlement == terminal), 0
    return _look(decision, evidence), False, 1


def _look(decision: Decision, evidence: tuple[DecisionEvidence, ...]) -> str:
    return _terminal(settlement_over_units(evidence, lookup_grouping(decision), decision.threshold))


def _settlement_if_merged(
    decision: Decision, evidence: tuple[DecisionEvidence, ...], learned: Learned, pair: tuple[str, str]
) -> str:
    """The settlement this decision would reach if `pair` were one source."""
    trial = Learned(groups=[set(group) for group in learned.groups])
    trial.merge(*pair)
    merged = _with_learned(decision, trial)
    robustness = assess_dependence_robustness(merged, decision.threshold, LEARNING_CUTS)
    if robustness.robust:
        return _terminal(robustness.settlement)
    values = set(_settlements_at(merged, decision.threshold, LEARNING_CUTS).values())
    return _terminal(values.pop()) if len(values) == 1 else ABSTAIN


def _candidate_pairs(decision: Decision, learned: Learned, terminal: str) -> list[tuple[str, str]]:
    """Pairs on the winning side that are not already merged. A pair on the losing
    side cannot change the outcome by shrinking its own count."""
    if terminal not in SETTLED:
        side = None
    else:
        side = terminal == "settled_true"
    source_of = dict(decision.source_of)
    sources = sorted(
        {source_of[item.observation_id] for item in decision.evidence if side is None or item.value == side}
    )
    return [
        (left, right)
        for left, right in itertools.combinations(sources, 2)
        if learned.group_of(left) is None or learned.group_of(left) is not learned.group_of(right)
    ]


def run_campaign(
    arm: str,
    campaign: Campaign,
    config: Mapping[str, Any],
    salt: str,
    feedback: float,
    budget: int,
) -> tuple[list[Outcome], Learned]:
    """Run one arm across a campaign in order, carrying whatever it learns.

    Returns the per-decision outcomes and the merges the arm ended up believing,
    so reporting reads the same state the decisions were made with rather than a
    second implementation of the same loop.
    """
    learned = Learned()
    joint: dict[tuple[str, str], int] = {}
    coerror: dict[tuple[str, str], int] = {}
    attempts: dict[tuple[str, str], int] = {}
    positives: dict[tuple[str, str], int] = {}
    remaining = budget
    outcomes: list[Outcome] = []

    for index, decision in enumerate(campaign.decisions):
        if arm == "oracle_reference":
            outcomes.append(Outcome(_terminal(decision.reference), False, 0, 0))
            continue
        if arm == "tiered_rule":
            terminal, stamped, looks = _settle(decision, decision.evidence, TIERED_CUTS)
            outcomes.append(Outcome(terminal, stamped, looks, 0))
            continue
        if arm == "content_tiered_rule":
            terminal, stamped, looks = _settle(decision, decision.evidence, CONTENT_CUTS)
            outcomes.append(Outcome(terminal, stamped, looks, 0))
            continue

        evidence = _with_learned(decision, learned)
        terminal, stamped, looks = _settle(decision, evidence, LEARNING_CUTS)
        spent = 0

        if arm == "probe" and remaining > 0:
            for pair in _candidate_pairs(decision, learned, terminal):
                if remaining <= 0:
                    break
                if positives.get(pair, 0) >= config["probe_positives_to_merge"]:
                    continue
                if _settlement_if_merged(decision, evidence, learned, pair) == terminal:
                    continue  # merging this pair cannot move this decision
                while (
                    remaining > 0
                    and positives.get(pair, 0) < config["probe_positives_to_merge"]
                    and attempts.get(pair, 0) < config["probe_positives_to_merge"] + 1
                ):
                    hit = probe_result(config, salt, campaign, pair[0], pair[1], attempts.get(pair, 0))
                    attempts[pair] = attempts.get(pair, 0) + 1
                    positives[pair] = positives.get(pair, 0) + int(hit)
                    remaining -= 1
                    spent += 1
                if positives.get(pair, 0) >= config["probe_positives_to_merge"]:
                    learned.merge(*pair)
                    evidence = _with_learned(decision, learned)
                    terminal, stamped, looks = _settle(decision, evidence, LEARNING_CUTS)

        outcomes.append(Outcome(terminal, stamped, looks, spent))

        if arm == "track_record" and decision.reference in SETTLED and reveals(config, salt, campaign, index, feedback):
            source_of = dict(decision.source_of)
            wrong = {
                source_of[item.observation_id]
                for item in decision.evidence
                if item.value != decision.truth
            }
            sources = sorted({source for _, source in decision.source_of})
            for pair in itertools.combinations(sources, 2):
                joint[pair] = joint.get(pair, 0) + 1
                if pair[0] in wrong and pair[1] in wrong:
                    coerror[pair] = coerror.get(pair, 0) + 1
                if (
                    joint[pair] >= config["track_record_minimum_joint_decisions"]
                    and coerror.get(pair, 0) / joint[pair] >= config["track_record_coerror_threshold"]
                ):
                    learned.merge(*pair)

    return outcomes, learned
