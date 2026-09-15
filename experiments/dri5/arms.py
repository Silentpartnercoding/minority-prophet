"""DRI-5 arms.

The frozen DRI-3 arms are reused unchanged and read only the five lineage cuts. Two
arms are added that also count the content fingerprint as possible dependence:

- **content robustness everywhere:** settle only on a settlement robust over lineage
  and content.
- **content tiered rule (method under test):** the tiered rule, with robustness
  judged over lineage and content. Whether to settle without looking is still decided
  by agreement over the five lineage cuts, exactly as in the tiered rule, so content
  can only add a "not robust" stamp or a look.

Adding shared identities can only widen the reachable settlements, so a decision the
content tiered rule settles silently and wrongly is one the tiered rule also settles
silently and wrongly. The criterion checks that in the implementation.
"""

from __future__ import annotations

from collections.abc import Callable

from experiments.dri3.arms import (
    ABSTAIN,
    Choice,
    Look,
    VisibleDecision,
    _after_look,
    _terminal,
    agreement_rule,
    always_look,
    oracle_reference,
    robustness_everywhere,
    tiered_rule,
)
from experiments.dri3.world import IRREVERSIBLE, Decision, settlements_at_cuts
from experiments.dri5.world import ALL_CUTS
from provenance.dependence_robustness import assess_dependence_robustness


def content_robustness_everywhere(view: VisibleDecision, look: Look) -> Choice:
    robustness = assess_dependence_robustness(view.evidence, view.threshold, ALL_CUTS)
    if robustness.robust:
        return _terminal(robustness.settlement), False
    return _after_look(view, look)


def content_tiered_rule(view: VisibleDecision, look: Look) -> Choice:
    if view.decision_class == IRREVERSIBLE:
        return content_robustness_everywhere(view, look)
    values = set(settlements_at_cuts(view.evidence, view.threshold).values())
    if len(values) == 1:
        terminal = _terminal(values.pop())
        if terminal == ABSTAIN:
            return ABSTAIN, False
        robustness = assess_dependence_robustness(view.evidence, view.threshold, ALL_CUTS)
        return terminal, not (robustness.robust and robustness.settlement == terminal)
    return _after_look(view, look)


CONTESTANT_ARMS: dict[str, Callable[[VisibleDecision, Look], Choice]] = {
    "agreement_rule": agreement_rule,
    "robustness_everywhere": robustness_everywhere,
    "tiered_rule": tiered_rule,
    "content_robustness_everywhere": content_robustness_everywhere,
    "content_tiered_rule": content_tiered_rule,
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
