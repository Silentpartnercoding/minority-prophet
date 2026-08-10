#!/usr/bin/env python3
"""GATE-01: same-origin roots do not collapse. Run from the gate checkout."""
import sys; sys.path.insert(0, ".")
from minority_prophet import DeterministicDecision, TrustAllVerifier, selective_decide

def root(cid, origin, value, subject="action-1"):
    return {"claim_id": cid, "agent": origin, "assertion": value,
            "attest": {"origin": origin, "subject": subject}}
def derived(cid, parent, origin, value, subject="action-1"):
    return {"claim_id": cid, "agent": origin, "assertion": value,
            "attest": {"origin": origin, "subject": subject, "derived_from": parent}}
def decide(ev):
    return selective_decide(DeterministicDecision("allow", "x", evidence_sensitive=True),
                            ev, TrustAllVerifier(), decision_subject="action-1").action

tie = [root("s0", "safe-0", "SAFE"), root("u0", "unsafe-0", "UNSAFE")]
print("tie 1v1                                :", decide(tie))
print("tie + 50 derived_from copies           :",
      decide(tie + [derived(f"c{i}", "s0", "safe-0", "SAFE") for i in range(50)]),
      " <- T2 holds")
print("tie + 50 roots sharing origin 'safe-0' :",
      decide(tie + [root(f"x{i}", "safe-0", "SAFE") for i in range(50)]),
      " <- origin does not collapse")
