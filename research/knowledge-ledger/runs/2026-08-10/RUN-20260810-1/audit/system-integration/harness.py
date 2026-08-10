#!/usr/bin/env python3
"""End-to-end composition harness: invariant 1, allow executes at most once.

    authority/identity -> evidence assessment -> Gate policy -> runtime effect

Run from the gate checkout. Everything here is out-of-tree; no target repository
is modified.

Invariant 1 (from the audit brief): "Allow executes the exact action at most
once." Tested under duplicate delivery, key substitution, and the two failure
modes that occur between deciding and recording.
"""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

from minority_prophet import (  # noqa: E402
    DeterministicDecision, TrustAllVerifier, selective_decide,
)
from minority_prophet.gate import GateDecision  # noqa: E402
from minority_prophet.runtime_adapter import (  # noqa: E402
    RuntimeAction, RuntimeBoundaryError, RuntimeController, RuntimeReceipt,
)

EFFECTS: list[str] = []          # the only ground truth that matters


class CountingAdapter:
    """A faithful adapter. Every execute_once is a real side effect."""

    def __init__(self, receipt_mutator=None, crash_after_execute=False):
        self._mutate = receipt_mutator
        self._crash = crash_after_execute

    def prepare(self, action: RuntimeAction) -> RuntimeAction:
        return action

    def execute_once(self, prepared: RuntimeAction) -> RuntimeReceipt:
        EFFECTS.append(prepared.action_id)          # THE EFFECT HAPPENS HERE
        if self._crash:
            raise ConnectionError("network dropped after the effect landed")
        receipt = RuntimeReceipt(prepared.action_id, prepared.idempotency_key,
                                 "succeeded", 1)
        return self._mutate(receipt) if self._mutate else receipt

    def prevent(self, action: RuntimeAction, reason: str) -> RuntimeReceipt:
        return RuntimeReceipt(action.action_id, action.idempotency_key,
                              "prevented", 0, diagnostics={"reason": reason})


def action(key="idem-1", action_id="act-1"):
    return RuntimeAction(action_id, "transfer", "acct-9", "sha256:abc", key,
                         payload={"amount": 100})


def roots(f, a, subject="act-1"):
    out = []
    for value, count in (("SAFE", f), ("UNSAFE", a)):
        for i in range(count):
            r = f"{value.lower()}-{i}"
            out.append({"claim_id": r, "agent": r, "assertion": value,
                        "attest": {"origin": r, "subject": subject}})
    return out


def gate_decision(sel):
    """Adapt a SelectiveDecision into the GateDecision the controller expects."""
    return GateDecision(sel.action, None, 0.0, 0.0, 0, 0, sel.diagnostics or {}, None)


def decide(f, a, primary="allow", sensitive=True):
    return gate_decision(selective_decide(
        DeterministicDecision(primary, "policy", evidence_sensitive=sensitive),
        roots(f, a), TrustAllVerifier(), decision_subject="act-1"))


def scenario(name, fn):
    EFFECTS.clear()
    try:
        note = fn()
    except Exception as exc:                       # noqa: BLE001 - harness
        note = f"raised {type(exc).__name__}: {exc}"
    print(f"  {name:52s} effects={len(EFFECTS)}  {note}")
    return len(EFFECTS)


def main() -> int:
    print("  INVARIANT 1 -- allow executes the exact bound action AT MOST ONCE\n")

    def happy():
        c, a = RuntimeController(), action()
        c.apply(decide(3, 0), a, CountingAdapter())
        return "single apply"
    n_happy = scenario("allow, applied once", happy)

    def duplicate():
        c, a = RuntimeController(), action()
        ad = CountingAdapter()
        for _ in range(5):
            c.apply(decide(3, 0), a, ad)
        return "5 duplicate deliveries, same idempotency key"
    n_dup = scenario("allow, delivered 5 times", duplicate)

    def substituted():
        c = RuntimeController()
        ad = CountingAdapter()
        c.apply(decide(3, 0), action("idem-1", "act-1"), ad)
        c.apply(decide(3, 0), action("idem-1", "act-DIFFERENT"), ad)
        return "should have raised"
    n_sub = scenario("same key, different action (substitution)", substituted)

    def denied():
        c, a = RuntimeController(), action()
        c.apply(decide(0, 3), a, CountingAdapter())
        return "deny path"
    n_den = scenario("deny", denied)

    # --- the two windows between deciding and recording -------------------
    def crash_after_effect():
        c, a = RuntimeController(), action()
        ad = CountingAdapter(crash_after_execute=True)
        for attempt in range(3):
            try:
                c.apply(decide(3, 0), a, ad)
            except ConnectionError:
                continue                            # caller retries, as callers do
        return "effect landed, then the transport failed; caller retried 3x"
    n_crash = scenario("allow, transport fails AFTER the effect", crash_after_effect)

    def bad_receipt():
        c, a = RuntimeController(), action()
        ad = CountingAdapter(
            receipt_mutator=lambda r: RuntimeReceipt(r.action_id, r.idempotency_key,
                                                     "succeeded", 2))
        for attempt in range(3):
            try:
                c.apply(decide(3, 0), a, ad)
            except RuntimeBoundaryError:
                continue
        return "adapter returned attempt_count=2; validation rejected it"
    n_bad = scenario("allow, adapter returns an invalid receipt", bad_receipt)

    print()
    ok = True
    for label, n, want in (("applied once", n_happy, 1),
                           ("5 duplicates", n_dup, 1),
                           ("substitution", n_sub, 1),
                           ("deny", n_den, 0),
                           ("crash after effect", n_crash, 1),
                           ("invalid receipt", n_bad, 1)):
        verdict = "OK " if n == want else "VIOLATION"
        if n != want:
            ok = False
        print(f"  {verdict:9s} {label:24s} effects={n} expected<={want}")
    print(f"\n  INVARIANT 1 HOLDS: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
