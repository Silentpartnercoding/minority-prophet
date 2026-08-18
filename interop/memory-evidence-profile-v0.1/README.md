# Memory Evidence Interoperability Profile v0.1

Status: optional, vendor-neutral interoperability profile. This directory does
not change the Minority Prophet research claims.

The profile carries bounded evidence through otherwise opaque memory systems.
It is an exchange contract and executable set of invariants, not a proof that
memory is true, complete, untampered, independently controlled, or authorized.
It keeps seven distinctions explicit:

1. A claim with no `derived_from` entries is a **declared root**. Its
   `root_authentication.status` says whether an external verifier authenticated
   that declaration; a parentless claim is not automatically trusted.
2. `derived_from` makes copies and transformations collapse to declared roots.
3. Digests and `binding` connect the evidence to the exact proposition, memory
   object, and optional request or action without granting authority.
4. Freshness, nonce, and revocation fields make replay and stale evidence
   visible to the consumer.
5. `search` records the searched scope and its coverage; partial coverage
   cannot support absence.
6. `verifiers` records asserted controller identity; verifiers under common
   recorded control do not count as independent. Controller labels alone do
   not prove real-world organizational independence.
7. `conclusion` records its input claims and method. Strength is a declared
   result, not a universal score produced by this profile.

`schema.json` defines the exchange shape. The examples demonstrate copied
consensus, incomplete search, shared verifier control, and embedding the
profile in a generic opaque memory cell. Run:

```sh
python3 interop/memory-evidence-profile-v0.1/validate.py
```

The validator uses only Python's standard library. It validates examples from
`schema.json`, checks the semantic invariants above, and runs adversarial
negative fixtures. A conforming producer may add vendor fields outside the
`evidence_profile` object, but must not reinterpret fields inside it.

`W3C-MEMORY-CROSSWALK.md` maps the published scope of the W3C AI Agent Memory
Interoperability Community Group onto these fields, and names the failure that
becomes unobservable when one is absent. It is a crosswalk, not a proposal.

Consumers decide whether an authentication method, controller assertion,
clock, revocation source, or conclusion method is acceptable. Invalid,
expired, revoked, replayed, incompletely searched, or insufficiently
authenticated evidence must remain inconclusive or be escalated; this profile
never converts it into permission.
