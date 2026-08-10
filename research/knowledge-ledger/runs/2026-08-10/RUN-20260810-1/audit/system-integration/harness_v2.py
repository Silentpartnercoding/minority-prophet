#!/usr/bin/env python3
"""System invariants 2-11. Run from the gate checkout.

Invariant 1 is in harness.py and was fixed by gate#15. This covers the rest of
the list, and states plainly which ones cannot be decided at this layer rather
than reporting them as passed.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")

from minority_prophet import (  # noqa: E402
    DeterministicDecision, TrustAllVerifier, selective_decide,
)
from minority_prophet.gate import GateDecision  # noqa: E402
from minority_prophet.runtime_adapter import (  # noqa: E402
    RuntimeAction, RuntimeBoundaryError, RuntimeController, RuntimeReceipt,
)

RESULTS: list[tuple[str, str, str]] = []


class Adapter:
    def __init__(self):
        self.effects: list[str] = []

    def prepare(self, action):
        return action

    def execute_once(self, prepared):
        self.effects.append(prepared.action_id)
        return RuntimeReceipt(prepared.action_id, prepared.idempotency_key,
                              "succeeded", 1)

    def prevent(self, action, reason):
        return RuntimeReceipt(action.action_id, action.idempotency_key,
                              "prevented", 0, diagnostics={"reason": reason})


def act(key="k1", aid="act-1"):
    return RuntimeAction(aid, "transfer", "acct-9", "sha256:abc", key,
                         payload={"amount": 100})


def stamp(seconds_ago):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).isoformat()


def root(cid, origin, assertion, subject="act-1", observed_at=None, **extra):
    attest = {"origin": origin, "subject": subject}
    if observed_at:
        attest["observed_at"] = observed_at
    attest.update(extra)
    return {"claim_id": cid, "agent": origin, "assertion": assertion, "attest": attest}


def roots(f, a, **kw):
    out = []
    for value, count in (("SAFE", f), ("UNSAFE", a)):
        for i in range(count):
            out.append(root(f"{value.lower()}-{i}", f"{value.lower()}-{i}", value, **kw))
    return out


def sel(primary, envelopes, sensitive=True, **kw):
    return selective_decide(
        DeterministicDecision(primary, "policy", evidence_sensitive=sensitive),
        envelopes, TrustAllVerifier(), decision_subject="act-1", **kw)


def gate(s):
    return GateDecision(s.action, None, 0.0, 0.0, 0, 0, s.diagnostics or {}, None)


def effects_for(primary, envelopes, **kw):
    a = Adapter()
    RuntimeController().apply(gate(sel(primary, envelopes, **kw)), act(), a)
    return a.effects


def record(inv, verdict, detail):
    RESULTS.append((inv, verdict, detail))
    print(f"  {inv:5s} {verdict:12s} {detail}"[:150])


def main() -> int:
    print("  SYSTEM INVARIANTS 2-11\n")

    # 2. Deny executes zero times.
    n = len(effects_for("deny", roots(20, 0)))
    record("INV-2", "HOLDS" if n == 0 else "VIOLATION",
           f"deny with 20 supporting roots -> {n} effect(s)")

    # 3. Escalate executes zero times.
    n = len(effects_for("review", roots(1, 1)))
    record("INV-3", "HOLDS" if n == 0 else "VIOLATION",
           f"escalate on a tie -> {n} effect(s)")

    # 4. Expired authority executes zero times.
    fresh = {"probe": {"ttl_s": 60}}
    stale = roots(3, 0, observed_at=stamp(10_000))
    for e in stale:
        e["attest"]["origin_class"] = "probe"
    d = sel("allow", stale, freshness=fresh)
    n = len(effects_for("allow", stale, freshness=fresh)) if d.action == "proceed" else 0
    record("INV-4", "HOLDS" if n == 0 else "VIOLATION",
           f"3 supporting roots, all past ttl -> decision={d.action}, {n} effect(s)")

    # 4b. missing observed_at under a freshness policy
    nots = roots(3, 0)
    for e in nots:
        e["attest"]["origin_class"] = "probe"
    d = sel("allow", nots, freshness=fresh)
    record("INV-4b", "HOLDS" if d.action != "proceed" else "VIOLATION",
           f"3 supporting roots, no observed_at under ttl policy -> {d.action}")

    # 5. Evidence binds to the exact subject.
    d = sel("allow", roots(3, 0, subject="a-DIFFERENT-action"))
    record("INV-5", "HOLDS" if d.action != "proceed" else "VIOLATION",
           f"3 supporting roots bound to another subject -> {d.action}")

    # 6. Payload cannot be silently substituted at the runtime seam.
    c, a = RuntimeController(), Adapter()
    c.apply(gate(sel("allow", roots(3, 0))), act("k1", "act-1"), a)
    try:
        c.apply(gate(sel("allow", roots(3, 0))),
                RuntimeAction("act-1", "transfer", "acct-EVIL", "sha256:abc", "k1"), a)
        record("INV-6", "VIOLATION", "target substituted under the same key and was accepted")
    except RuntimeBoundaryError:
        record("INV-6", "HOLDS", "target substitution under a reused key raised")

    # 7. A deterministic deny cannot be overturned downstream.
    worst = max(len(effects_for("deny", roots(f, 0))) for f in (0, 5, 20, 100))
    record("INV-7", "HOLDS" if worst == 0 else "VIOLATION",
           f"deny with up to 100 supporting roots -> max {worst} effect(s)")

    # 8. Missing provenance cannot become independence.
    unattested = [{"claim_id": f"u{i}", "agent": f"u{i}", "assertion": "SAFE"}
                  for i in range(20)]
    d = sel("allow", unattested + roots(0, 1))
    record("INV-8", "HOLDS" if d.action != "proceed" else "VIOLATION",
           f"20 claims with no attest block vs 1 opposing root -> {d.action}")

    # 9. Extra identifiers must not create extra votes without an independence basis.
    tie = roots(1, 1)
    same_origin = tie + [root(f"x{i}", "safe-0", "SAFE") for i in range(50)]
    d = sel("allow", same_origin)
    record("INV-9", "DOCUMENTED GAP" if d.action == "proceed" else "HOLDS",
           f"tie + 50 claims sharing one origin -> {d.action} (GATE-01: origin is "
           f"not a collapse key; the verifier must supply independence)")

    # 10. Failure at a required seam fails closed.
    class Exploding(Adapter):
        def prepare(self, action):
            raise RuntimeError("adapter blew up during prepare")
    a = Exploding()
    try:
        RuntimeController().apply(gate(sel("allow", roots(3, 0))), act(), a)
        record("INV-10", "VIOLATION", "prepare() raised and apply returned anyway")
    except RuntimeError:
        record("INV-10", "HOLDS", f"prepare() failure propagated, {len(a.effects)} effect(s)")

    # 11. The recorded result distinguishes the three layers.
    s = sel("allow", roots(1, 1))
    has_route = getattr(s, "route", None) is not None
    record("INV-11", "HOLDS" if has_route else "VIOLATION",
           f"escalate carries route={getattr(s,'route',None)!r} distinguishing "
           f"authorization from evidence from enforcement")

    print()
    bad = [r for r in RESULTS if r[1] == "VIOLATION"]
    gaps = [r for r in RESULTS if r[1] == "DOCUMENTED GAP"]
    print(f"  {len(RESULTS)} invariants exercised: "
          f"{len(RESULTS)-len(bad)-len(gaps)} hold, {len(gaps)} documented gap, "
          f"{len(bad)} VIOLATION")
    for inv, _, detail in bad:
        print(f"    VIOLATION {inv}: {detail}"[:150])
    print("\n  NOT DECIDABLE AT THIS LAYER, and not reported as passing:")
    print("    delegation scope, audience binding, revocation state, canonical")
    print("    serialization, DSSE verification -- these live in Border, which this")
    print("    harness does not reach. Tested separately.")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
