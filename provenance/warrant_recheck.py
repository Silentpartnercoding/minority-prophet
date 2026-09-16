"""Write a re-check result into the warrant field that was built to hold it.

`claim-warrant.schema.json` has carried `verify_outcome` -- "Result of an actual
re-check, if one was performed", three-valued by design -- since before this
module existed. Nothing has ever written to it. A field designed to record a
re-check, and no re-check had a way to reach it.

`root_dereference.dereference_root` produces exactly that vocabulary. The two
were designed for each other and had never been introduced. This is the
introduction, and it is deliberately thin: no new policy, no new state, one
translation and the rules that translation must obey.

THE TRANSLATION, and why each edge is where it is:

    dereference          verify_outcome     because
    ------------------------------------------------------------------
    verified          -> verified           the reference resolved
    absent            -> rejected           it did not, and we could look
    unverifiable      -> unverifiable       we could not look. NOT rejected.
    no_reference      -> (no outcome)       nothing was re-checked at all

`absent -> rejected` is the only edge that condemns, and it fires only when a
resolver actually answered False. The schema states the reason this matters
better than a comment can: "a claim whose source has become unreachable is not a
claim that failed, and the difference is exactly the signal false-prophet
screening depends on. A prophet can make claims unverifiable at no cost."

`no_reference` writes NOTHING. A root that names no reference is already refused
by `UnattributedRootError`; recording it here as a re-check would report a
different gate's work as this one's, and would make `verify_outcome` look
exercised when nothing was checked.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .graph import WARRANT_KEY
from .root_dereference import ABSENT, NO_REFERENCE, UNVERIFIABLE, VERIFIED, dereference_root

CHECKER = "provenance.warrant_recheck"

_RESULT = {VERIFIED: "verified", ABSENT: "rejected", UNVERIFIABLE: "unverifiable"}

# The schema asks that `unverifiable` carry a distinguishing detail, and names
# the vocabulary: fetch_failed, not_decodable, digest_malformed, oracle_absent,
# sla_timeout. Mapped explicitly rather than passing prose through, so the field
# stays machine-readable.
_UNVERIFIABLE_REASON = {
    "no resolver configured; shape was checked, existence was not": "oracle_absent",
    "the resolver could not answer; this is not evidence of absence": "fetch_failed",
}


def recheck_outcome(evidence: dict[str, Any], resolver=None, *, now=None) -> dict | None:
    """The `verify_outcome` object for this evidence, or None if nothing was checked."""
    result = dereference_root(evidence, resolver)
    if result.state == NO_REFERENCE:
        return None
    stamp = (now or datetime.now(timezone.utc)).isoformat()
    outcome = {"result": _RESULT[result.state], "checked_at": stamp, "checked_by": CHECKER}
    if result.state == UNVERIFIABLE:
        outcome["reason"] = _UNVERIFIABLE_REASON.get(
            result.reason or "", "not_decodable" if result.reference is None else "fetch_failed")
    elif result.reason:
        outcome["reason"] = result.reason
    return outcome


def attach_recheck(evidence: dict[str, Any], resolver=None, *, now=None) -> dict[str, Any]:
    """Return a copy of `evidence` whose warrant carries the re-check result.

    Never mutates the input, and never invents a warrant: evidence with no
    `claim_warrant` is returned unchanged. Writing a warrant here would mean
    asserting a `claim_type` and `verify_determinism` this module has no
    standing to decide -- the schema says determinism is DERIVED from claim_type,
    and only the producer knows the claim_type.
    """
    warrant = evidence.get(WARRANT_KEY)
    if not isinstance(warrant, dict):
        return dict(evidence)
    outcome = recheck_outcome(evidence, resolver, now=now)
    if outcome is None:
        return dict(evidence)
    return {**evidence, WARRANT_KEY: {**warrant, "verify_outcome": outcome}}


def recheck_report(nodes, resolver=None) -> dict:
    """Distribution of re-check outcomes over a graph's roots.

    A distribution rather than a pass rate, for the reason this repository keeps
    rediscovering: a gate whose outcome has only ever held one value has not been
    tested, however many nodes it has seen.
    """
    counts = {"verified": 0, "rejected": 0, "unverifiable": 0, "not_rechecked": 0}
    for node in nodes:
        if not node.is_root:
            continue
        outcome = recheck_outcome(node.evidence, resolver)
        counts["not_rechecked" if outcome is None else outcome["result"]] += 1
    checked = counts["verified"] + counts["rejected"]
    return {
        "roots": sum(counts.values()),
        "outcomes": counts,
        "rejectedRate": round(counts["rejected"] / checked, 3) if checked else None,
        "distinctOutcomes": sum(1 for v in counts.values() if v),
        "boundary": (
            "`unverifiable` is never counted as `rejected`; a prophet can make claims "
            "unverifiable at no cost, so the rate is over what a resolver actually answered. "
            "`not_rechecked` is a root naming no reference, which UnattributedRootError already "
            "governs -- it is not this check's finding."
        ),
    }
