"""The assembled pipeline: every Minority Prophet organ that works, in one path.

Until now each piece was tested alone. Composition is where things break, which
is the premise of the whole DRI series, so this exists to find that out rather
than to assert it does not happen.

    derive scope        KL-001 M1  -- the search space is computed, never supplied
    resolve roots       KL-002/005 -- ancestry, refusing silence as originality
    evaluate            KL-000 v2  -- the frozen evaluator, unmodified
    score               KL-005     -- two-sided, so silence cannot win

Deliberately NOT included, because they belong to other systems and forcing them
in would be assembly theatre: the control plane's commit durability, and the
opportunity scanner's coverage-scope derivation. Both address the same family of
defect in their own codebases; neither is Minority Prophet.

What this composition can and cannot show is stated in `assemble()`.
"""

from __future__ import annotations

from provenance.unverifiable_policy import UnverifiablePolicy, apply_policy
from provenance.warrant_recheck import recheck_outcome

from .root_resolution import resolution_report, resolve_transaction_roots
from .transaction_v2 import evaluate_transaction_v2


class ScopeSuppliedError(TypeError):
    """KL-001 M1, at the pipeline boundary: the scope is derived, never supplied."""


def derive_scope(locations: list[dict], **kwargs) -> list[dict]:
    """Refuse a supplied scope, then pass the derived one through.

    The pipeline does not invent a scope -- it enforces that whoever built the
    search ledger did not hand one in through this interface. Supplying it is
    ADV-001 through the interface; see KL-001 FC1 W3.
    """
    for forbidden in ("scope", "locations", "declared", "files"):
        if forbidden in kwargs:
            raise ScopeSuppliedError(
                f"{forbidden!r} may not be supplied: the search space is derived "
                "(KL-001 M1). Supplying it is ADV-001 through the interface."
            )
    if not locations:
        raise ValueError("The declared search space must not be empty.")
    return locations


def _recheck_stage(payload: dict, resolver, policy) -> dict:
    """Dereference every record's evidence, then decide whether a settlement may rest on it.

    The counts and the decision are kept apart on purpose. `unverifiable` stays
    `unverifiable` in the counts -- the schema is emphatic that it must never
    become `rejected` -- and the cost lands on the SETTLEMENT instead. Nothing
    here condemns a claim; it withholds the right to settle on one.
    """
    counts = {"verified": 0, "rejected": 0, "unverifiable": 0, "not_rechecked": 0}
    for record in (payload.get("evidenceLedger") or {}).get("records") or []:
        evidence = record.get("evidence")
        if not isinstance(evidence, dict):
            counts["not_rechecked"] += 1
            continue
        outcome = recheck_outcome(evidence, resolver)
        counts["not_rechecked" if outcome is None else outcome["result"]] += 1
    return {"outcomes": counts, "settlement": apply_policy(counts, policy)}


def assemble(payload: dict, documents: dict, *, require_origin_claim: bool = True,
             resolver=None, policy: UnverifiablePolicy | None = None) -> dict:
    """Run one transaction through every organ and report each stage.

    Returns both the unresolved and resolved verdicts, because the value of the
    root organ is only visible as a difference. A single verdict would hide
    whether the composition did anything at all.

    What this shows: that the four organs run together on one input, and where
    the answer moves.

    Where it moves, stated as a boundary rather than a rate: an absence
    conclusion turns on whether ANY opposing root SURVIVES resolution, never on
    how many. Resolution flips it exactly when it takes the opposing side from
    some to none -- unattributable opposition stops refuting the absence -- and
    moves only the margin otherwise. That asymmetry is correct rather than a
    defect: one genuine counterexample refutes a universal absence claim and
    five do not refute it harder. A presence conclusion does depend on the
    count, so resolution moves it directly.

    What it does NOT show: that the composition is correct in general. The
    population here is whatever the caller supplies. And it says nothing about
    root emptiness -- a fabricated root with honest copies collapses to one root
    and is still worth zero. See research/adversarial-weighting/two_failure_classes.py.
    """
    stages = {}

    derive_scope(payload.get("searchLedger", {}).get("locations") or [])
    stages["scope"] = {"derived": True, "suppliedScopeRefused": True}

    stages["roots"] = resolution_report(payload, documents, require_origin_claim)
    stages["recheck"] = _recheck_stage(payload, resolver, policy)

    before = evaluate_transaction_v2(payload)
    after = evaluate_transaction_v2(resolve_transaction_roots(payload, documents, require_origin_claim))
    stages["evaluation"] = {
        "unresolved": {"conclusion": before["conclusion"],
                       "supportingRoots": len(before["evidence"]["supportingRoots"]),
                       "opposingRoots": len(before["evidence"]["opposingRoots"])},
        "resolved": {"conclusion": after["conclusion"],
                     "supportingRoots": len(after["evidence"]["supportingRoots"]),
                     "opposingRoots": len(after["evidence"]["opposingRoots"]),
                     "unattributedRecords": after["evidence"]["unattributedRecords"]},
        "conclusionChanged": before["conclusion"] != after["conclusion"],
        # Whether the verdict was sensitive to the root count at all. An absence
        # conclusion turns on whether ANY opposing root survives, so collapsing
        # five laundered roots into one moves the margin and leaves the answer
        # alone. Surfacing that stops a reader crediting the root rule for a
        # verdict it did not affect.
        "rootCountWasDecisive": (
            before["conclusion"] != after["conclusion"]
            or len(before["evidence"]["supportingRoots"]) == len(after["evidence"]["supportingRoots"])
        ),
        "marginMovedWithoutVerdict": (
            before["conclusion"] == after["conclusion"]
            and len(before["evidence"]["supportingRoots"]) != len(after["evidence"]["supportingRoots"])
        ),
    }
    settlement = stages["recheck"]["settlement"]["decision"]
    stages["settlement"] = {
        "decision": settlement,
        "actionable": settlement == "settle",
        "note": ("The evaluator still returns its conclusion. This says whether anyone is "
                 "entitled to act on it, which is a separate question and the only one an "
                 "unverifiable rate is allowed to affect."),
    }
    return {
        "stages": stages,
        "organsRun": ["derive_scope", "resolve_roots", "evaluate", "evaluate_resolved"],
        "boundaries": [
            "The frozen evaluator is unmodified; resolution happens before it.",
            "Root emptiness is untouched: a fabricated root with honest copies is structurally perfect and worth zero.",
            "This composes the Minority Prophet organs only. Commit durability and scanner coverage live in other systems and are not forced in.",
        ],
    }
