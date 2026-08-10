"""Knowledge-transaction evaluator v0.2 — the receipt can now carry doubt.

WHY THIS IS A NEW FILE AND NOT AN EDIT.

`transaction.py` is pinned by SHA-256 in four KL-000 preregistrations as
`evaluatorUnderTest`. Editing it would invalidate every one of them and break the
chain that proves those protocols predate their results. An attempt to add these
fields in place was caught by `test_frozen_hashes_unchanged`, which exists for
exactly that reason. v0.1 is frozen and stays byte-identical; v0.2 lives here.

WHAT WAS MISSING, AND THE PATTERN IN IT (SCH-005).

`RESEARCH-DIRECTION.md` has always specified that the evidence ledger records
evidence-root identifiers, repeated records collapsed, declared shared
dependencies and side-separation status, supporting and opposing counts,
`flip_budget` and `conversions_to_reverse`, and *unattributed evidence,
uncertainty, and the reason for abstention*.

v0.1 emits the first four. It emits none of the last three, and the omission is
not random: **everything it emits expresses confidence, and everything absent
expresses doubt.** The machinery for saying "here is my answer" was built. The
machinery for saying "here is what I am unsure about" was not.

That matters for KL-011 specifically, whose claim is that protected fields survive
crossing systems. A receipt that cannot carry doubt could pass that test while
establishing only that *confident* claims survive a boundary — leaving the
interesting question structurally untestable.

These fields are added because the specification requires them, not because an
experiment needs them. The test for that distinction: would they be added if
KL-011 did not exist? Yes. That makes this a conformance fix rather than designing
an instrument around its result.

OWNER DECISION A2, REGISTERED HERE.

*Does presence require complete coverage?* **No.** A found counterexample is a
found counterexample; incomplete coverage does not downgrade it. 19,152 worlds —
17.3% of receipts — hang on this, and a third implementation reading it the other
way would diverge on all of them while passing every invariant.

This is what v0.1 already does. The decision changes no behaviour; it removes the
ambiguity that let two conforming implementations disagree. The asymmetry with
absence is deliberate and is stated in `limits`: absence requires complete
coverage, presence does not, because absence is a claim about everything that was
not found and presence is a claim about something that was.
"""

from __future__ import annotations

import hashlib
from typing import Any

from .transaction import TERMINAL_SEARCH_STATUSES, canonical_bytes

SCHEMA = "minority-prophet.knowledge-transaction.v0.2"


def evaluate_transaction_v2(payload: dict[str, Any]) -> dict[str, Any]:
    claim = payload["claim"]
    locations = payload["searchLedger"]["locations"]
    evidence = payload["evidenceLedger"]["records"]
    if not locations:
        raise ValueError("The declared search space must not be empty.")

    ids = [location["id"] for location in locations]
    if len(ids) != len(set(ids)):
        raise ValueError("Search-location identifiers must be unique.")
    if any(location["status"] not in TERMINAL_SEARCH_STATUSES for location in locations):
        search_complete = False
    else:
        search_complete = all(location["status"] == "searched" for location in locations)

    root_sides: dict[str, str] = {}
    unattributed = 0
    for record in evidence:
        side = record["side"]
        if side not in {"support", "oppose"}:
            raise ValueError("Evidence sides must be support or oppose.")
        root_id = record.get("rootId")
        if not root_id:
            # Evidence that cannot be attributed to a root cannot join a side.
            # v0.1 required rootId and would raise; here it is counted and
            # reported. A dropped record is the difference between "we found
            # nothing" and "we could not attribute what we found", and those are
            # not the same receipt.
            unattributed += 1
            continue
        previous = root_sides.setdefault(root_id, side)
        if previous != side:
            raise ValueError("One root cannot support opposing sides.")

    declared_dependencies = sorted({
        str(dependency)
        for record in evidence
        for dependency in (record.get("sharedDependencies") or [])
    })

    supporting = sorted(root for root, side in root_sides.items() if side == "support")
    opposing = sorted(root for root, side in root_sides.items() if side == "oppose")
    margin = abs(len(supporting) - len(opposing))
    repeated_collapsed = len(evidence) - len(root_sides) - unattributed

    # Two prices, because there are two attacks. flip_budget forges new roots on
    # the losing side, each moving the margin one unit. conversions_to_reverse
    # compromises a root already asserting the winning side, which removes one
    # and adds one, so each action moves the margin two units and the price is
    # roughly half. Quoting either alone misstates the other (CE-03).
    flip_budget = margin if margin else 1
    conversions = margin // 2 + 1 if margin else 1

    abstention_reason: str | None = None
    if claim["type"] == "absence":
        if opposing:
            # A2, decided: presence does not require complete coverage.
            conclusion = "present"
            reason = "At least one distinct counterexample root was recorded."
        elif search_complete:
            conclusion = "absent_within_declared_scope"
            reason = "Every declared location was searched and no counterexample root was recorded."
        else:
            conclusion = "not_established"
            reason = "The declared search space was not exhaustively searched."
            abstention_reason = "incomplete_coverage"
    else:
        conclusion = "supported" if len(supporting) > len(opposing) else "not_established"
        reason = "The conclusion follows only from the declared root counts."
        if conclusion == "not_established":
            abstention_reason = ("tied_roots" if len(supporting) == len(opposing)
                                 else "outnumbered")

    unsearched = len(locations) - sum(
        location["status"] == "searched" for location in locations)

    result = {
        "schema": SCHEMA,
        "transactionId": payload["transactionId"],
        "claim": claim,
        "search": {
            "declared": len(locations),
            "searched": sum(location["status"] == "searched" for location in locations),
            "unavailable": sum(location["status"] == "unavailable" for location in locations),
            "complete": search_complete,
        },
        "evidence": {
            "records": len(evidence),
            "distinctRoots": len(root_sides),
            "repeatedRecordsCollapsed": repeated_collapsed,
            "supportingRoots": supporting,
            "opposingRoots": opposing,
            "margin": margin,
            "flipBudget": flip_budget,
            "conversionsToReverse": conversions,
            "unattributedRecords": unattributed,
            "declaredSharedDependencies": declared_dependencies,
        },
        # The fields v0.1 could not carry. `abstentionReason` is None on a
        # decisive conclusion on purpose: a field that is always populated
        # distinguishes nothing.
        "uncertainty": {
            "unsearchedLocations": unsearched,
            "unattributedRecords": unattributed,
            "declaredSharedDependencies": len(declared_dependencies),
            "sideSeparationDeclared": not declared_dependencies,
            "abstentionReason": abstention_reason,
        },
        "conclusion": conclusion,
        "reason": reason,
        "limits": [
            "Root identity and independence are declared operationally, not proved semantically.",
            "This result applies only to the declared search space.",
            "Presence does not require complete coverage; absence does. A found "
            "counterexample stands regardless of what was not searched, while an "
            "absence claim is a claim about everything that was not found. "
            "Owner decision A2.",
            "Unattributed records are counted and never silently dropped, but "
            "they join no side and move no margin.",
        ],
    }
    result["contentDigest"] = f"sha256:{hashlib.sha256(canonical_bytes(result)).hexdigest()}"
    return result
