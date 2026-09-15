"""DRI-6 arms.

The frozen DRI-3 agreement rule, tiered rule and always-look arms are reused
unchanged. They settle on whatever a lookup reports. Two arms are added that differ
from the tiered rule only in what they do with a lookup:

- **checked tiered rule:** accepts a reported grouping only if the record allows it,
  meaning every reported unit is joined by recorded shared identities inside it.
  Otherwise it abstains. With a complete record, a truthful lookup always passes, so
  the check only rejects invented dependence.
- **confirmed tiered rule (method under test):** looks twice. It settles only when
  both reported groupings pass the check and give the same settlement; otherwise it
  abstains.

Both make their first lookup exactly where the tiered rule makes its only one, and
see the same report there. Each can therefore only abstain where the tiered rule
settles after a look, never settle where it does not.
"""

from __future__ import annotations

from collections.abc import Callable

from experiments.dri3.arms import (
    ABSTAIN,
    Choice,
    VisibleDecision,
    _terminal,
    agreement_rule,
    always_look,
    oracle_reference,
    tiered_rule,
)
from experiments.dri3.world import CUTS, IRREVERSIBLE, Decision, settlement_over_units, settlements_at_cuts
from experiments.dri5.world import true_grouping_admissible
from experiments.dri6.world import ImperfectLook
from provenance.dependence_robustness import assess_dependence_robustness

LookAction = Callable[[VisibleDecision, ImperfectLook], Choice]


def _allowed(view: VisibleDecision, units: tuple[tuple[str, str], ...] | None) -> bool:
    return units is not None and true_grouping_admissible(view.evidence, units, CUTS)


def checked_look(view: VisibleDecision, look: ImperfectLook) -> Choice:
    units = look()
    if not _allowed(view, units):
        return ABSTAIN, False
    return _terminal(settlement_over_units(view.evidence, units, view.threshold)), False


def confirmed_look(view: VisibleDecision, look: ImperfectLook) -> Choice:
    first = look()
    if not _allowed(view, first):
        return ABSTAIN, False
    second = look()
    if not _allowed(view, second):
        return ABSTAIN, False
    settlement = settlement_over_units(view.evidence, first, view.threshold)
    if settlement != settlement_over_units(view.evidence, second, view.threshold):
        return ABSTAIN, False
    return _terminal(settlement), False


def _tiered_with(view: VisibleDecision, look: ImperfectLook, after: LookAction) -> Choice:
    """The DRI-3 tiered rule with a different action after a look."""
    if view.decision_class == IRREVERSIBLE:
        robustness = assess_dependence_robustness(view.evidence, view.threshold, CUTS)
        if robustness.robust:
            return _terminal(robustness.settlement), False
        return after(view, look)
    values = set(settlements_at_cuts(view.evidence, view.threshold).values())
    if len(values) == 1:
        terminal = _terminal(values.pop())
        if terminal == ABSTAIN:
            return ABSTAIN, False
        robustness = assess_dependence_robustness(view.evidence, view.threshold, CUTS)
        return terminal, not (robustness.robust and robustness.settlement == terminal)
    return after(view, look)


def checked_tiered_rule(view: VisibleDecision, look: ImperfectLook) -> Choice:
    return _tiered_with(view, look, checked_look)


def confirmed_tiered_rule(view: VisibleDecision, look: ImperfectLook) -> Choice:
    return _tiered_with(view, look, confirmed_look)


CONTESTANT_ARMS: dict[str, Callable[[VisibleDecision, ImperfectLook], Choice]] = {
    "agreement_rule": agreement_rule,
    "tiered_rule": tiered_rule,
    "checked_tiered_rule": checked_tiered_rule,
    "confirmed_tiered_rule": confirmed_tiered_rule,
    "always_look": always_look,
}
REFERENCE_ARMS: dict[str, Callable[[Decision], Choice]] = {"oracle_reference": oracle_reference}
ALL_ARMS = tuple(CONTESTANT_ARMS) + tuple(REFERENCE_ARMS)


def act(arm: str, decision: Decision, look: ImperfectLook) -> tuple[str, bool, int]:
    """Run one arm on one decision with its own lookup: (terminal, stamped, lookups)."""
    if arm in REFERENCE_ARMS:
        terminal, stamped = REFERENCE_ARMS[arm](decision)
        return terminal, stamped, 0
    view = VisibleDecision(decision.decision_id, decision.threshold, decision.decision_class, decision.evidence)
    terminal, stamped = CONTESTANT_ARMS[arm](view, look)
    return terminal, stamped, look.calls
