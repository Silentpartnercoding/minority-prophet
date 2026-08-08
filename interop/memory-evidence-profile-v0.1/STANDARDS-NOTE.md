# Standards note

This is an experimental, optional interchange profile, not a W3C standard,
Recommendation, Working Draft, or Community Group report. It is intended to
invite interoperable implementation feedback without selecting a storage,
identity, attestation, or verification vendor.

The profile transports evidence boundaries; it does not establish truth,
identity, controller independence, memory integrity, or authority. A consumer
must preserve recorded root ancestry, authentication status, exact bindings,
freshness, revocation state, search coverage, recorded common control, and
stated uncertainty. Local policies may demand stronger evidence, but must not
turn a parentless declaration into an authenticated root, copies into
independent roots, partial search into proof of absence, or commonly controlled
checks into independent verification.

## Draft public mailing-list note (do not send)

Subject: Experimental memory evidence profile v0.1 for implementation feedback

Hello,

We have prepared a small, vendor-neutral, optional JSON evidence profile for
systems that exchange opaque memory records. It carries derivation roots,
external authentication status, exact bindings, freshness and revocation
state, search coverage, recorded verifier control, and bounded conclusions
with uncertainty. Executable examples and adversarial fixtures demonstrate
that a parentless declaration is not automatically authenticated, copied
claims do not increase roots, incomplete search cannot establish absence,
replayed or revoked evidence cannot support a conclusion, and multiple
verifiers under common recorded control do not establish independence.

This is an independent experimental proposal and is not represented as W3C
work or status. We would welcome implementation feedback on the field model and
the three invariants. Artifact: [insert final verified public artifact URL].

Regards,
[verified sender name and affiliation]

Publication remains blocked until both the W3C public list recipient route and
the final public artifact URL are independently verified. No message has been
sent.
