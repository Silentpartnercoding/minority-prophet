# Vendor-neutral authority and evidence contract v0.1

This draft is the seam between an agent runtime, an authorization provider,
and an evidence-aware consumer. It deliberately names no vendor. Any provider
may implement it without becoming a required dependency.

The contract separates five facts that must not be collapsed:

1. **identity** — which agent key or account acted;
2. **human-backed authority** — which principal authorized it;
3. **delegation** — the exact bounded grant used for this action;
4. **effect** — whether the action executed, and exactly how many times;
5. **evidence origin** — whether a claim is an observation, a derivation, a
   copy, or unknown, and what may legitimately count as its root.

A signature can authenticate a statement. It does not prove that the signer
discovered the information independently. The `independence_basis` field is
therefore explicit and conservative; `unknown` is valid and must not be
silently upgraded.

## Files

- `schema.json` — structural JSON Schema for one request/receipt envelope.
- `conformance/authority_evidence.py` — stdlib canonicalization, digest, and
  semantic invariant checker.
- `tests/test_authority_evidence_contract.py` — valid and adversarial
  conformance vectors expressed as executable tests.

## Required invariants

- allow + succeeded executes exactly once;
- deny executes zero times;
- expired or revoked authority cannot allow or execute;
- the receipt binds the exact canonical action digest;
- subject identity, principal, and delegation cannot be substituted;
- copied or derived claims cannot mint a fresh evidence root;
- unknown independence stays unknown;
- malformed or ambiguous records fail closed.

This is a draft interoperability contract, not a production authorization
service, cryptographic verifier, patent opinion, or proof of independence.
