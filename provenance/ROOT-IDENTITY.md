# Root identity and bounded issuance

Status: implementation contract for R1.4.

A root is not an arbitrary caller-provided label. `mp-root-v1` is the SHA-256
digest of the authenticated issuer, issuer-scoped observation identifier,
proposition, asserted value and evidence digest. The signed issuance request
also binds key identity, observation time and a one-use nonce.

`RootRegistry` enforces the operational boundary omitted by the mathematical
core:

- issuer authentication is injected through a provider-neutral verifier;
- roots are bounded per authenticated issuer and fixed time window;
- quota allocation is serialized and durable across processes and restarts;
- root identity, request nonce and issuance slots are unique;
- records are append-only and removal is represented by a tombstone;
- tombstoning does not restore issuance capacity or remove the original root;
- every event is HMAC-chained, and mutation fails closed before later issuance;
- unknown identity, unverifiable signatures, uncertain clocks, replay and
  unavailable or corrupted state do not mint roots.

Deployment graphs must construct `EvidenceGraph(root_authority=registry)`.
That makes every parentless node prove membership in the active registry before
it enters the aggregation graph; callers cannot bypass issuance by supplying an
arbitrary node identifier.

The included HMAC issuer verifier is a deterministic test fixture. A production
deployment must inject an authenticated organizational, workload, hardware or
identity-provider verifier and keep the registry integrity key outside SQLite.
This mechanism limits the blast radius of a compromised key; it does not prove
that an observation is true.
