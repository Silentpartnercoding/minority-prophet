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

CORRECTION, and it is the important part of this module. An earlier version
claimed "withholding action cannot cause a wrong action". That is false, and it
is false in the case that matters most.

Abstention is only neutral when the STATUS QUO is safe:

    "should I execute this irreversible transfer?"   defer -> nothing moves. Safe.
    "is there a vulnerability in this code?"         defer -> the hole stays open.

For the second kind, deferring IS the harmful act. Raising the bar on how many
scanners must agree before a finding is acted on does not make the system more
careful; it makes it sit on a real hole while it waits for a second opinion.

So this module will not apply a threshold above one unless the decision has
explicitly stated that deferring is safe. It falls back to one and records why.
A system that can be configured into ignoring a genuine finding will eventually
be configured that way by someone in a hurry.

`canon/precedent.py` states the deeper form of this and is worth reading before
anyone raises the bar here: witnesses are a profile per error class, never a
single number, because "trading off is exactly the step that requires a
preference". A single threshold cannot express "two witnesses before I believe a
consensus, one before I believe a warning". That asymmetry is the whole subject.
"""

from __future__ import annotations

ACTIONABLE = "actionable"
ESCALATE_THIN = "escalate_thin_counterexample"
NOT_APPLICABLE = "not_applicable"

#: A decision may raise the counterexample bar only by saying this outright.
#: Absent it, deferring is assumed to be harmful, because for absence claims
#: about safety it usually is.
DEFERRAL_SAFE_KEY = "deferring_is_safe"


def _declared(context, key):
    if context is None:
        return None
    value = getattr(context, key, None)
    if value is None and isinstance(context, dict):
        value = context.get(key)
    return value


def required_roots(context) -> tuple[int, str | None]:
    """The threshold this decision may use, and why it was lowered if it was.

    Returns (threshold, refusal_reason). The threshold is capped at one unless
    the decision states `deferring_is_safe`, because a bar above one means a
    single genuine counterexample does not get acted on -- and for a safety
    absence claim that is the hole staying open, not caution.
    """
    declared = _declared(context, "minimum_winning_roots")
    if declared is None:
        return 1, None
    declared = int(declared)
    if declared < 1:
        raise ValueError("minimum_winning_roots must be at least 1")
    if declared == 1:
        return 1, None
    if _declared(context, DEFERRAL_SAFE_KEY) is True:
        return declared, None
    return 1, (
        f"the decision asked for {declared} counterexample roots but did not declare "
        f"`{DEFERRAL_SAFE_KEY}`. Deferring action on a counterexample is only safe when the "
        "status quo is safe; for a safety absence claim it leaves the finding unremedied. "
        "Falling back to one.")


def assess(receipt: dict, context=None) -> dict:
    """Is this `present` verdict firm enough for the claim's declared bar?

    Reads the receipt; never rewrites it. `conclusion` is returned untouched so a
    caller cannot mistake this for a second opinion on the verdict.
    """
    minimum, refusal = required_roots(context)
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
    if refusal:
        out["thresholdRefused"] = refusal
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
