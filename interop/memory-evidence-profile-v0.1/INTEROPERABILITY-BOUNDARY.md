# Interoperability boundary

This is an experimental, optional interchange profile. It does not select a
storage, identity, attestation, or verification vendor.

The profile transports evidence boundaries; it does not establish truth,
identity, controller independence, memory integrity, or authority. A consumer
must preserve recorded root ancestry, authentication status, exact bindings,
freshness, revocation state, search coverage, recorded common control, and
stated uncertainty. Local policies may demand stronger evidence, but must not
turn a parentless declaration into an authenticated root, copies into
independent roots, partial search into proof of absence, or commonly controlled
checks into independent verification.
