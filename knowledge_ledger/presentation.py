"""Derived presentation values for knowledge-transaction receipts.

This module is PRESENTATION, not evaluation: it computes values derivable
from the nine registered receipt members and never modifies, extends, or
re-signs a receipt. The evaluator (transaction.py, hash-frozen since
protocol v1.0.0) and the receipt object (registered at v1.2.0, pinned by
fixtures C11/C12) are untouched by importing or using this module.

Registered derivation (KL-000/FLIP-BUDGET-PRESENTATION.md, RUN-20260807-10):
Constraint CE-14 (this module, added 2026-08-17): the margin decides a
`presence` claim and decides NOTHING on an `absence` claim. Every branch of
the absence rule reads (opposing evidence present, coverage complete) and
never consults the margin -- so a flip budget presented beside an absence
verdict describes a quantity that did not determine it, and in the `present`
case describes the SIDE THAT LOST. The number is still returned, because
suppressing a derivable value hides rather than corrects; it is returned with
`budgetApplies: False` and the count of roots that would actually reverse the
conclusion. See formal/COUNTEREXAMPLES.md CE-14.

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


def _budget_applicability(receipt: dict[str, Any]) -> dict[str, Any]:
    """Whether the margin decided this verdict, and what would reverse it.

    CE-14. Derived from registered receipt members only (`claim.type`,
    `conclusion`, `evidence.opposingRoots`); adds no member and re-signs
    nothing.
    """
    if receipt["claim"].get("type") != "absence":
        # The presence branch compares supporting against opposing root counts,
        # so the margin is exactly what decided it and the budget is its budget.
        return {"budgetApplies": True, "decidedByRootCount": None}

    conclusion = receipt["conclusion"]
    opposing = len(receipt["evidence"]["opposingRoots"])
    if conclusion == "present":
        # One opposing root was sufficient and 999 confirming roots were not
        # relevant. Reversal means removing every opposing root, not out-voting
        # them, and the margin describes the side that did not decide.
        decisive = opposing
    else:
        # `absent_within_declared_scope` and `not_established` both hold with
        # zero opposing roots; one admitted opposing root moves either of them
        # to `present`, whatever the margin.
        decisive = 1
    return {"budgetApplies": False, "decidedByRootCount": decisive}


def reversal_metrics(receipt: dict[str, Any]) -> dict[str, Any]:
    """Both R3 metrics, labelled -- the only exported presentation of
    flip_budget, per constraint CE-03 -- gated by CE-14."""
    evidence = receipt["evidence"]
    applicability = _budget_applicability(receipt)
    note = (
        "CE-03: flip_budget alone overstates attacker cost ~2x when read "
        "as an action count; conversionsToReverse is the action cost. "
        "Both derive from the registered receipt; neither is a receipt "
        "member and no receipt byte depends on this module."
    )
    if not applicability["budgetApplies"]:
        note += (
            " CE-14: this claim is an absence claim, whose verdict is a "
            "function of (opposing evidence present, coverage complete) and "
            "never of the margin. flip_budget did not determine this "
            "conclusion and must not be cited as its security margin; "
            "decidedByRootCount is the number of opposing roots that "
            "actually carries it."
        )
    return {
        "flipBudget": derive_flip_budget(receipt),
        "flipBudgetUnits": "net per-side root gain (p0 - p1)",
        "conversionsToReverse": evidence["conversionsToReverse"],
        "conversionsToReverseUnits": "side-conversion actions (each worth two units of net gain)",
        **applicability,
        "note": note,
    }
