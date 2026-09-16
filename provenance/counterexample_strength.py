"""How firmly is an absence claim refuted, and may anyone act on that yet?

KL-000 pins I5 as a hard invariant: "For absence claims, a non-empty
opposingRoots implies conclusion == 'present', at any coverage level." It held
across 110,840 receipts in two independent implementations. The evaluator is not
the place to reconsider it, and this module does not touch it -- every verdict
it sees stays exactly what the evaluator said.

I5 is also correct as logic. One genuine counterexample refutes a universal
absence claim; five do not refute it harder. What I5 does not say -- because a
conclusion is not an instruction -- is whether anyone should ACT on a `present`
that rests on a single root.

That question has no fixed answer, and the reason is worth stating rather than
defaulting past. "Fail safe" points in opposite directions depending on what
acting would do:

    "no vulnerability here"   a missed one is catastrophic, a false alarm is an
                              afternoon. One report SHOULD be enough to act on.
    "this party did nothing"  a false accusation is catastrophic and hard to
                              undo. One report should NOT be enough to act on.

Same verdict, same logic, opposite safe settings -- and the thing that separates
them is not the subject of the claim but the COST AND REVERSIBILITY OF THE
ACTION. That is already modelled. `DecisionContext` requires `consequence`,
`reversibility` and `minimum_winning_roots`, and this module reads that rather
than inventing a parallel threshold: one decision-scoped number, declared with
the decision, not a second global dial that could disagree with the first.

It is also the right component boundary. Minority Prophet reports how firmly
something was refuted; it does not know or need to know what acting would cost.
Whoever holds consequence supplies the threshold.

What this module can do safely in every direction is escalate. Withholding
action cannot cause a wrong action, which is the same asymmetry that lets the
unverifiable policy exist at all.
"""

from __future__ import annotations

ACTIONABLE = "actionable"
ESCALATE_THIN = "escalate_thin_counterexample"
NOT_APPLICABLE = "not_applicable"


def required_roots(context) -> int:
    """The threshold this decision declared, or 1 when no context was supplied.

    Accepts a `DecisionContext`, a plain mapping shaped like one, or None. The
    default of 1 reproduces today's behaviour exactly, so adopting this module
    changes nothing until a decision declares otherwise.
    """
    if context is None:
        return 1
    value = getattr(context, "minimum_winning_roots", None)
    if value is None and isinstance(context, dict):
        value = context.get("minimum_winning_roots")
    if value is None:
        return 1
    value = int(value)
    if value < 1:
        raise ValueError("minimum_winning_roots must be at least 1")
    return value


def assess(receipt: dict, context=None) -> dict:
    """Is this `present` verdict firm enough for the claim's declared bar?

    Reads the receipt; never rewrites it. `conclusion` is returned untouched so a
    caller cannot mistake this for a second opinion on the verdict.
    """
    minimum = required_roots(context)
    conclusion = receipt.get("conclusion")
    opposing = list((receipt.get("evidence") or {}).get("opposingRoots") or [])

    if conclusion != "present":
        return {
            "decision": NOT_APPLICABLE, "conclusion": conclusion,
            "counterexampleRoots": len(opposing),
            "note": "This governs how firmly an absence claim was refuted. Nothing was refuted here.",
        }

    firm = len(opposing) >= minimum
    out = {
        "decision": ACTIONABLE if firm else ESCALATE_THIN,
        "conclusion": conclusion,
        "counterexampleRoots": len(opposing),
        "declaredMinimum": minimum,
        "consequence": getattr(context, "consequence", None)
                       or (context or {}).get("consequence") if context else None,
        "reversibility": getattr(context, "reversibility", None)
                         or (context or {}).get("reversibility") if context else None,
        "verdictUnchanged": True,
        "invariantRespected": "I5 — a non-empty opposingRoots still concludes `present`",
    }
    if not firm:
        out["reason"] = (
            f"refuted by {len(opposing)} independent root(s); this decision declared that acting "
            f"takes {minimum}"
        )
        out["wouldLiftIf"] = (
            f"{minimum - len(opposing)} more independent counterexample "
            "root(s) are recorded, or a human accepts the thin refutation explicitly"
        )
    return out


def strength_note(receipt: dict) -> str:
    """One line a reader can act on, for claims that declare no threshold at all.

    Adds information without moving any line: the difference between a refutation
    resting on one root and on nine is invisible in the conclusion, and a reader
    who cannot see it cannot weigh it.
    """
    if receipt.get("conclusion") != "present":
        return ""
    n = len((receipt.get("evidence") or {}).get("opposingRoots") or [])
    if n == 1:
        return "Refuted by a single independent root. One counterexample is sufficient in logic; " \
               "whether it is sufficient to act on is a question this receipt does not answer."
    return f"Refuted by {n} independent roots."
