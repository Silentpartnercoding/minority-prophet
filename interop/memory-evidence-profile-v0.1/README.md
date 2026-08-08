# Memory Evidence Profile v0.1

Status: optional, vendor-neutral interoperability profile. This directory is
not a W3C specification and does not change the Minority Prophet research
claims.

The profile carries bounded evidence through otherwise opaque memory systems.
It keeps five distinctions explicit:

1. `independent_roots` identifies observations with no recorded derivation.
2. `derived_from` makes copies and transformations collapse to those roots.
3. `search` records the searched scope and its coverage; partial coverage
   cannot support absence.
4. `verifiers` records controller identity; verifiers under common control do
   not count as independent.
5. `conclusion` is bounded by a proposition, strength, and uncertainty.

`schema.json` defines the exchange shape. The examples demonstrate copied
consensus, incomplete search, shared verifier control, and embedding the
profile in a generic opaque memory cell. Run:

```sh
python3 interop/memory-evidence-profile-v0.1/validate.py
```

The validator uses only Python's standard library. It checks the schema-shaped
structure and the semantic invariants above. A conforming producer may add
vendor fields outside the `evidence_profile` object, but must not reinterpret
fields inside it.
