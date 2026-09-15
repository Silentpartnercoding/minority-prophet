"""DRI-3 arms, frozen at protocol v1.

Contestant arms see only a ``VisibleDecision``: the observations, the sufficiency
threshold and the decision class. Reversibility is a property of the decision
that a real system knows. They are never given the truth, the true grouping, or
the family. The only way to learn the grouping is a counted lookup, which returns
nothing in lookup-unavailable worlds.

Every arm returns ``(terminal, stamped)``. ``terminal`` is a settlement or
``abstain``. ``stamped`` is True when the arm settled while marking the
settlement "not robust".
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from experiments.dri3.world import (
    CUTS,
    IRREVERSIBLE,
    SETTLED,
    Decision,
    settlement_over_units,
    settlements_at_cuts,
)
from provenance.decision_relative import DecisionEvidence
from provenance.dependence_robustness import assess_dependence_robustness

ABSTAIN = "abstain"
Choice = tuple[str, bool]


@dataclass(frozen=True)
class VisibleDecision:
    decision_id: str
    threshold: int
    decision_class: str
    evidence: tuple[DecisionEvidence, ...]


class Look:
    """The lineage lookup for one decision. Every call is counted."""

    def __init__(self, decision: Decision) -> None:
        self._decision = decision
        self.calls = 0

    def __call__(self) -> tuple[tuple[str, str], ...] | None:
        self.calls += 1
        return self._decision.units if self._decision.lookup_available else None


def _terminal(settlement: str | None) -> str:
    return settlement if settlement in SETTLED else ABSTAIN


def _after_look(view: VisibleDecision, look: Look) -> Choice:
    units = look()
    if units is None:
        return ABSTAIN, False
    return _terminal(settlement_over_units(view.evidence, units, view.threshold)), False


def agreement_rule(view: VisibleDecision, look: Look) -> Choice:
    """The DRI-2 method: settle when every cut agrees, look when they disagree."""
    values = set(settlements_at_cuts(view.evidence, view.threshold).values())
    if len(values) == 1:
        return _terminal(values.pop()), False
    return _after_look(view, look)


def robustness_everywhere(view: VisibleDecision, look: Look) -> Choice:
    """Settle only on a settlement robust over recorded possible dependence."""
    robustness = assess_dependence_robustness(view.evidence, view.threshold, CUTS)
    if robustness.robust:
        return _terminal(robustness.settlement), False
    return _after_look(view, look)


def tiered_rule(view: VisibleDecision, look: Look) -> Choice:
    """The owner's cost rule.

    Irreversible decisions are handled as by robustness everywhere. Reversible
    decisions are handled as by the agreement rule, except that a settlement made
    without looking that is not robust is stamped "not robust".
    """
    if view.decision_class == IRREVERSIBLE:
        return robustness_everywhere(view, look)
    values = set(settlements_at_cuts(view.evidence, view.threshold).values())
    if len(values) == 1:
        terminal = _terminal(values.pop())
        if terminal == ABSTAIN:
            return ABSTAIN, False
        robustness = assess_dependence_robustness(view.evidence, view.threshold, CUTS)
        return terminal, not (robustness.robust and robustness.settlement == terminal)
    return _after_look(view, look)


def always_look(view: VisibleDecision, look: Look) -> Choice:
    """Look at every decision; without a lookup, settle only if robust."""
    units = look()
    if units is not None:
        return _terminal(settlement_over_units(view.evidence, units, view.threshold)), False
    robustness = assess_dependence_robustness(view.evidence, view.threshold, CUTS)
    return (_terminal(robustness.settlement) if robustness.robust else ABSTAIN), False


def oracle_reference(decision: Decision) -> Choice:
    return _terminal(decision.reference), False


CONTESTANT_ARMS: dict[str, Callable[[VisibleDecision, Look], Choice]] = {
    "agreement_rule": agreement_rule,
    "robustness_everywhere": robustness_everywhere,
    "tiered_rule": tiered_rule,
    "always_look": always_look,
}
REFERENCE_ARMS: dict[str, Callable[[Decision], Choice]] = {"oracle_reference": oracle_reference}
ALL_ARMS = tuple(CONTESTANT_ARMS) + tuple(REFERENCE_ARMS)


def act(arm: str, decision: Decision) -> tuple[str, bool, int]:
    """Run one arm on one decision: (terminal, stamped, lookups)."""
    if arm in REFERENCE_ARMS:
        terminal, stamped = REFERENCE_ARMS[arm](decision)
        return terminal, stamped, 0
    look = Look(decision)
    view = VisibleDecision(decision.decision_id, decision.threshold, decision.decision_class, decision.evidence)
    terminal, stamped = CONTESTANT_ARMS[arm](view, look)
    return terminal, stamped, look.calls
