"""Derived presentation values for knowledge-transaction receipts.

This module is PRESENTATION, not evaluation: it computes values derivable
from the nine registered receipt members and never modifies, extends, or
re-signs a receipt. The evaluator (transaction.py, hash-frozen since
protocol v1.0.0) and the receipt object (registered at v1.2.0, pinned by
fixtures C11/C12) are untouched by importing or using this module.

Registered derivation (KL-000/FLIP-BUDGET-PRESENTATION.md, RUN-20260807-10):

    flip_budget = margin        # units: net per-side root gain (p0 - p1)

per the paper's Theorem 4: "The attacker's budget equals the margin in
units of net per-side root gain"; section 6 R3 promises flip_budget and
conversions_to_reverse are "surfaced with every verdict".

Constraint CE-03 (registered): flip_budget is reported BESIDE
conversionsToReverse, never instead of it. A side-conversion action moves
one root off one side and onto the other -- two units of net per-side gain
-- so reading flip_budget as an action count overstates attacker cost by
~2x. conversionsToReverse (floor(margin/2) + 1, Theorem 4 [E2]) is the
action-denominated cost; flip_budget is the flow-denominated budget. The
presentation function returns both, labelled with their units, and has no
variant that returns flip_budget alone.
"""

from __future__ import annotations

from typing import Any


def derive_flip_budget(receipt: dict[str, Any]) -> int:
    """The attacker's budget in net per-side root-gain units: the margin."""
    return receipt["evidence"]["margin"]


def reversal_metrics(receipt: dict[str, Any]) -> dict[str, Any]:
    """Both R3 metrics, labelled -- the only exported presentation of
    flip_budget, per constraint CE-03."""
    evidence = receipt["evidence"]
    return {
        "flipBudget": derive_flip_budget(receipt),
        "flipBudgetUnits": "net per-side root gain (p0 - p1)",
        "conversionsToReverse": evidence["conversionsToReverse"],
        "conversionsToReverseUnits": "side-conversion actions (each worth two units of net gain)",
        "note": (
            "CE-03: flip_budget alone overstates attacker cost ~2x when read "
            "as an action count; conversionsToReverse is the action cost. "
            "Both derive from the registered receipt; neither is a receipt "
            "member and no receipt byte depends on this module."
        ),
    }
