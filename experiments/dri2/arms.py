"""DRI-2 arms, frozen at protocol v1.

Contestant arms see only a ``VisibleDecision``: the observations and the
sufficiency threshold. They are never given the failure domain, the junction
type, the truth, or the causal grouping. The only way to learn the grouping is
to call the lineage probe, which is recorded and costs time.

Reference arms are told the hidden facts. They bound what is achievable and are
not contestants.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from canon.decision_sensitivity import Action, Model, compare
from experiments.dri2.world import (
    CUT_INDEX,
    CUTS,
    DOMAIN_CUT,
    HAND_OVER,
    SETTLED,
    Decision,
    assess_cuts,
    settlement_over_units,
    settlements_at_cuts,
)
from provenance.decision_relative import DecisionEvidence

ESCALATE = "escalate"


@dataclass(frozen=True)
class VisibleDecision:
    decision_id: str
    threshold: int
    evidence: tuple[DecisionEvidence, ...]


class Probe:
    """The lineage probe for one decision. Every call is counted."""

    def __init__(self, decision: Decision) -> None:
        self._decision = decision
        self.calls = 0

    def __call__(self) -> tuple[tuple[str, str], ...] | None:
        self.calls += 1
        return self._decision.units if self._decision.probe_available else None


ContestantArm = Callable[[VisibleDecision, Probe], str]


def _terminal(settlement: str) -> str:
    return settlement if settlement in SETTLED else ESCALATE


def fixed_cut(cut: str) -> ContestantArm:
    def arm(view: VisibleDecision, probe: Probe) -> str:
        return _terminal(settlements_at_cuts(view.evidence, view.threshold)[cut])

    arm.__name__ = f"fixed_{cut}"
    return arm


def weakest_link(view: VisibleDecision, probe: Probe) -> str:
    """Act on the cut with the fewest winning roots; ties go to the coarser cut.

    The cut-space counterpart of always acting on the least-defended error class.
    """
    assessed = assess_cuts(view.evidence, view.threshold)
    weakest = min(CUTS, key=lambda cut: (assessed[cut].winning_root_count, -CUT_INDEX[cut]))
    return _terminal(assessed[weakest].settlement)


def determined_or_escalate(view: VisibleDecision, probe: Probe) -> str:
    """Settle only when every cut settles the same way; otherwise escalate."""
    values = set(settlements_at_cuts(view.evidence, view.threshold).values())
    return _terminal(values.pop()) if len(values) == 1 else ESCALATE


_IMPLIED = {
    "settled_true": Action.PROCEED,
    "settled_false": Action.BLOCK,
    "unsettled": Action.ESCALATE,
}


def method_under_test(view: VisibleDecision, probe: Probe) -> str:
    """Decision-sensitivity guided: settle when the cut does not matter, look when it does.

    Each cut is a surviving model of which lineage is relevant, implying the action
    its settlement would take (``canon.decision_sensitivity``). If every cut implies
    the same action, the choice of cut is not decision-material and the arm acts on
    it. If they differ, every model names the lineage probe as the observation that
    would separate them, so the arm probes and counts by the causal grouping it
    reveals. If the probe is unavailable, nothing can settle the difference and the
    arm escalates.
    """
    settlements = settlements_at_cuts(view.evidence, view.threshold)
    sensitivity = compare(
        [
            Model(name=cut, implies=_IMPLIED[settlements[cut]], discriminating_observation="lineage probe")
            for cut in CUTS
        ]
    )
    if not sensitivity.is_material:
        return _terminal(settlements[CUTS[0]])
    units = probe()
    if units is None:
        return ESCALATE
    return _terminal(settlement_over_units(view.evidence, units, view.threshold))


def oracle_reference(decision: Decision) -> str:
    """The best achievable move: the junction's own correct move.

    Knowing the causal grouping is exactly what a twin withholds, so where the
    junction is a hand-over the oracle hands over rather than settling on
    knowledge the world does not provide.
    """
    if decision.junction == HAND_OVER:
        return ESCALATE
    return _terminal(decision.reference)


def rules_engine_reference(decision: Decision) -> str:
    """The declared family-to-cut table applied to the first disclosed domain."""
    cut = DOMAIN_CUT[decision.domains[0]] if decision.domains else CUTS[0]
    return _terminal(dict(decision.cut_settlements)[cut])


CONTESTANT_ARMS: dict[str, ContestantArm] = {
    "agent_headcount": fixed_cut("agent"),
    "fixed_machine": fixed_cut("machine"),
    "fixed_controller": fixed_cut("controller"),
    "fixed_evidence_origin": fixed_cut("evidence_origin"),
    "fixed_upstream_component": fixed_cut("upstream_component"),
    "weakest_link": weakest_link,
    "determined_or_escalate": determined_or_escalate,
    "method_under_test": method_under_test,
}
REFERENCE_ARMS: dict[str, Callable[[Decision], str]] = {
    "oracle_reference": oracle_reference,
    "rules_engine_reference": rules_engine_reference,
}
COMPARISON_ARMS = tuple(name for name in CONTESTANT_ARMS if name != "method_under_test")


def act(arm: str, decision: Decision) -> tuple[str, int]:
    """Run one arm on one decision. Returns the terminal action and probe calls."""
    if arm in REFERENCE_ARMS:
        return REFERENCE_ARMS[arm](decision), 0
    probe = Probe(decision)
    view = VisibleDecision(decision.decision_id, decision.threshold, decision.evidence)
    return CONTESTANT_ARMS[arm](view, probe), probe.calls
