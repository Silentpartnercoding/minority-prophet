# Crosswalk: W3C AI Agent Memory Interoperability scope → Memory Evidence Profile v0.1

A crosswalk, not a proposal. It maps the published scope of the W3C **AI Agent
Memory Interoperability Community Group** onto the fields this profile already
carries, and names the failure that becomes unobservable when a field is
absent. Every row ends in a fixture that can be run.

Source for the left column: <https://www.w3.org/groups/cg/ai-agent-memory-interop/>,
read 18 August 2026. Shortname `ai-agent-memory-interop`.

## What the left column is, and is not

The group has published a **scope**, not a specification. There is no field
vocabulary to map onto yet. So the left column quotes scope areas from the
group's own page; it does not invent field names and then map to them.

That distinction is the whole point of this directory. A crosswalk whose left
column was imagined would be a table asserting a correspondence it never
checked — the failure the fixtures below exist to catch. When the group
publishes field names, this document should be rewritten against them and the
scope-area version discarded.

## The crosswalk

| W3C scope area | Profile field | Failure if the distinction is absent | Fixture |
|---|---|---|---|
| Memory cell shape (encrypted unit with canonical metadata) | `binding.memory_object_digest`, `binding.proposition_digest` | A cell is canonical, intact and portable while carrying no statement of *which proposition* it is evidence for. The consumer supplies the link, and no transport records that it did. | `opaque-memory-cell.json` |
| Identity binding (post-quantum signatures, ML-DSA-65 / FIPS-204) | `claims[].root_authentication`, `claims[].derived_from` | A signature authenticates a *declaration*, not an observation. Three validly signed cells derived from one observation present as three signed sources. Stronger signatures do not change this. | `copied-consensus.json` |
| Encryption envelope semantics (per-cell DEK, wallet-derived KEK, rotation) | *(no mapping)* | Orthogonal. This profile takes no position on envelope semantics and should not be read as proposing one. | — |
| Audit anchor properties (public-chain receipts; verifiability without trusting the operator) | `verifiers[]` (asserted controller) | An anchor proves a cell existed at a time. It does not establish that the parties attesting to it are independently controlled. Verifiers under common recorded control still read as plural. | `shared-control-verifier.json` |
| Sharing contracts (temporary, permanent, syndicate; revocation semantics) | `lifecycle` (freshness, nonce, revocation) | Revoked or stale evidence is reused after the sharing contract that justified it has lapsed, and the reuse is invisible downstream. | `adversarial-cases.json` |
| Cryptographic erasure (DEK destruction, tombstone, blacklist; GDPR Art. 17) | `search.coverage`, `lifecycle` | Erasure changes what a later search can reach. Absence observed after erasure is indistinguishable from absence in the world, unless coverage is carried. | `incomplete-search.json` |
| Crosswalks to regulatory and protocol ecosystems (NIST AI RMF, ISO/IEC 42001, ISO/IEC 27001, EU AI Act, MCP, AAIF) | — | This document is an instance of that scope item. | — |

## Two distinctions the published scope does not yet name

Both are inside "portable memory" and neither is covered by shape, identity
binding, encryption, anchors, sharing, or erasure. Each is stated as a
falsifiable property with a fixture attached.

**1. Derivation — copies must not become roots.**
A claim with no `derived_from` is a *declared root*. `derived_from` makes copies
and transformations collapse back to the root they came from. Without it, a
transport that faithfully moves three authentic cells delivers three apparent
sources for one observation. Nothing was forged; the count is simply wrong.
→ `copied-consensus.json`

**2. Search coverage — partial search cannot support absence.**
`search` records the scope searched and the coverage achieved. Without it, a
query that reached 1 of 26 partitions and found nothing is transported as "not
found", and a consumer reads absence of evidence as evidence of absence.
→ `incomplete-search.json`

## Running the fixtures

```sh
python3 interop/memory-evidence-profile-v0.1/validate.py
```

Python standard library only, no install, no network, no dependency on any
Minority Prophet component. The fixtures are JSON. A consumer with their own
memory representation can map their fields onto the profile and run the same
cases against it — the point is the cases, not this schema.

Minority Prophet is named here only as where these cases were found. It is not
a required dependency and nothing here proposes adopting its schema.

## The question this asks

> Should a portable memory format preserve enough information for a consumer to
> distinguish these two cases — three copies of one observation from three
> observations, and a partial search from an exhaustive one?

A "no, that belongs in a companion profile" is a useful answer. So is "yes, open
an issue." The cases are given away either way.
