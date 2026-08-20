# Pramana ↔ minority-prophet seam — Phase A notes

**Status: Phase A partial.** Steps 1–3 complete. Step 4 complete for `provenance/`,
**blocked** for `ledger_adapter.py`, the scorer stub, and the H2.1–H2.4 spec — none of which
exist in the repository or on this machine. See *Blocked* below.

Pramana inventoried at `ravikiran438/pramana-attestation` HEAD, cloned 2026-08-20.
**Licence: Apache 2.0**, Copyright 2026 Ravi Kiran Kadaboina. (GitHub reports `NOASSERTION`
only because the `LICENSE` file is an abbreviated header pointing at the canonical text rather
than the full verbatim licence. The declaration is unambiguous and vendoring is permitted with
attribution.)

## (a) Field inventory

### Pramana — `ClaimAttestation` base

`claim_id: UUID` · `claim_type: ClaimType` · `claim: str` · `attester_id: str` ·
`attested_at: datetime`

### Pramana — the four variants

| Variant | Fields beyond base | `verify()` dependency |
|---|---|---|
| **MeasurementClaim** | `measured_value`, `measurement_unit?`, `measurement_method`, `measurement_source`, `measurement_uncertainty?` | `MeasurementFetcher` |
| **CitationClaim** | `source_uri`, `source_excerpt`, `source_retrieved_at`, `source_hash?` | `SourceFetcher` |
| **InferenceClaim** | `premises: list[str]`, `inference_method`, `confidence: float` | `InferenceOracle` |
| **AnalogyClaim** | `reference_case`, `similarity_basis: list[str]`, `similarity_score?`, `similarity_method` | `SimilarityComputer` |

### Pramana — wire extension fields

`verify_endpoint_hint` is **the only required field**. `verification_artifact_id`,
`artifact_signature`, `source_digest`, `sla_window_ms` are all optional.

### Pramana — invariants

- **CA-1 Reachability** — every attestation carries `verify_endpoint_hint`. *TLC-verified.*
- **CA-2 SLA-Bound** — terminal state within `sla_window_ms` or auto-`unverifiable`
  (`sla_timeout`). *Runtime-enforced* by `extensions/claim_attestation/validators.py`.
- **CA-3 Offline Re-verifiability** — every `VerificationOutcome` re-verifiable offline by any
  party holding `(claim, source_digest, artifact_signature)`; artifacts deterministic and
  signed, never dependent on the original verifier's session state. *TLC-verified.*

### minority-prophet — ledger node (`provenance/evidence-lineage.schema.json`)

All required: `node_id`, `proposition_id`, `value: boolean`, `observer_id`, `source_id`,
`timestamp`, `confidence: number`, `evidence: object`, `copied_from: array`,
`transformations: array`. Optional `signature`.

### minority-prophet — `RootReceipt`

`root_id`, `issuer_id`, `window_start`, `sequence`, `issued_at`, `record_hash`.

## (b) Findings that bear on using ClaimAttestation as a ledger input

**1. `verify()` is three-valued, and the third value is the interesting one.**
`CitationClaim.verify()` returns **VERIFIED** (fetch succeeded, hash matched if present, excerpt
found), **REJECTED** (fetch succeeded but excerpt absent *or* hash mismatch), or
**UNVERIFIABLE** (fetch failed, content not UTF-8-decodable, or `source_hash` malformed/unknown
algorithm).

*"I checked and it is wrong"* and *"I could not check"* are different states. A false prophet
can move claims into UNVERIFIABLE — a dead URI costs nothing — without ever being REJECTED. Any
ledger mapping that collapses the two loses precisely the signal the screening needs. **This
distinction must survive into the ledger entry.**

**2. Pramana carries no lineage.** There is no analogue of `copied_from` or `transformations`
anywhere in the type hierarchy. Pramana types a claim; it does not relate claims to each other.

This is not a defect — it is the seam. It also **forces** the architecture Phase B step 3 asks
for: type can only enter as a per-node attribute, because Pramana has no edges to contribute.
The requirement that independence semantics stay unchanged is satisfied structurally rather than
by discipline.

**3. `confidence` exists on exactly one variant.** `InferenceClaim.confidence: float` is the
only occurrence. The ledger node requires `confidence: number` on **every** node. So three of
four variants have no confidence to map and the local default must govern — and that default is
in `ledger_adapter.py`, which is unavailable.

**4. No `proposition_id`, and `claim` is a string, not a truth value.** The ledger node requires
`proposition_id` and a boolean `value`. A ClaimAttestation says *"here is an assertion and how
you would check it"*, not *"proposition P is true."* Nothing in Pramana indexes claims to a
shared proposition. **This is the largest single gap** and it is unmappable without local
invention — a `NO-MATCH` requiring both fields to remain local.

**5. The field CA-3 depends on is optional on the wire.** CA-3 — the invariant most useful to
this project, offline re-verifiability — requires `source_digest` and `artifact_signature`.
Both are **optional** in the wire schema; only `verify_endpoint_hint` is required. So an
attestation can be CA-1 conformant and CA-3 unusable. Any ingest path must treat CA-3 material
as *conditionally present* and degrade explicitly, not assume it.

**6. Name collision.** Both projects have a `RootRegistry`. They are unrelated: Pramana's
anchors attestation identity, minority-prophet's issues signed root receipts with replay and
issuance limits. Any shared document must disambiguate.

## (c) Go / no-go

**GO — adapt with a thin mapping layer.** Not verbatim adoption, not rejection.

*Not verbatim*, because the shapes do not align: no `proposition_id`, no boolean `value`, no
lineage edges, `confidence` on one variant of four. Four of the ledger's ten required fields
have no Pramana source.

*Not rejection*, because the two things being borrowed are real and not available elsewhere:
the four-way typology, and the determinism asymmetry — deterministic-verify claims (measurement,
citation) can be mechanically re-checked during false-prophet screening; oracle-conditional
claims (inference, analogy) cannot. That asymmetry is the feature worth having, and Pramana
states it precisely enough to implement against.

The project is also a better-than-expected source: TLA+ specification, five safety invariants
exhaustively model-checked across 38,563 states with zero violations, 84 passing tests including
property-based ones, and a preregistered empirical study. Single maintainer, one star, untouched
since 2026-05-19 — so **vendor the schemas at a pinned commit and depend on nothing at
runtime**, which is what the task already specifies.

## Blocked — required before Phase B

Phase B's mapping table maps `TODO(wire)` sites to Pramana fields. **The `TODO(wire)` sites do
not exist in the repository.** Neither does the scorer stub or the H2.1–H2.4 specification, and
`main` has no branch containing them.

Not writable until those land:
- the mapping table (one side of it is unavailable);
- the `claim_type` / `verify_determinism` placement decision (depends on the local entry shape);
- the scorer hook specification (depends on the existing hard gates).

Writable now, once unblocked, from the inventory above.

---

# Reframing for Phase B — added after review

Two corrections to how the seam was originally posed. Both narrow the task and strengthen the
case for it.

## 1. A ClaimAttestation is a warrant, not a ledger entry

The task was posed as *"make ClaimAttestation a usable typed input to the evidence ledger."* On
the field inventory that is not achievable, and should not be attempted.

A ledger node is **a position on a shared proposition, with an ancestry**: `proposition_id` +
`value: boolean` + `copied_from`. Ten nodes sharing a `proposition_id` are ten votes on one
question, and `copied_from` records which of them are the same observation counted twice. That
is the whole apparatus.

A ClaimAttestation is **an assertion with a checking recipe**. Ten attestations are ten
unrelated strings. There is no shared index, so they cannot be aggregated — nothing says which
are about the same question. It lacks exactly the two fields that make a node aggregatable, and
those absences are not oversights: Pramana was never aggregating anything.

**So an attestation cannot become a node. It can only attach to one.** The node's `evidence`
field is an unconstrained `{"type": "object"}` — the natural and already-provided home for a
typed warrant. `proposition_id`, `value` and all lineage remain local and must be supplied by
whoever constructs the node.

The mapping table will therefore be **mostly `NO-MATCH`, and that is the correct result** rather
than a shortfall. Four of the ten required node fields having no Pramana source is the two
systems correctly minding their own business.

## 2. Verifiability and independence are orthogonal — which is why this composes

|  | Independent | Dependent |
|---|---|---|
| **Verifiable** | strong evidence | one fact counted many times — *what this project exists to catch* |
| **Unverifiable** | weak but genuine | worthless — *the most attractive position for a false prophet* |

A verifiable claim can be entirely dependent (copying someone else's correct citation). An
unverifiable claim can be entirely independent. Typing by verifiability therefore does **not**
substitute for lineage; it adds an axis the ledger does not currently have.

## 3. The real justification: this is an Effect Reachability precondition

`epistemic-ci` check 8:

> Effect Reachability requires every stratum the endpoint depends on to contain instances. A
> population with 208 searched and 0 not-searched is positive, fingerprinted, and structurally
> unable to move the endpoint.

False-prophet screening depends on mechanical re-checkability. Deterministic-verify claims
(measurement, citation) can be re-checked; oracle-conditional claims (inference, analogy) cannot.
**Those are strata.**

If a corpus is entirely oracle-conditional, a screen that relies on re-checking is *positive,
fingerprinted, and structurally unable to move* — it returns green and could never have returned
anything else. That is check 8's failure exactly, not an analogy to it.

**Until claim type is recorded, that check cannot be run on the evidence ledger at all**, because
nothing distinguishes the strata. This converts the Pramana typing from a scoring refinement into
a **validity precondition** for false-prophet screening.

The `epistemic-ci` README already records a second instance of check 8 in this programme — *"a
method consuming recorded ancestry, evaluated on a corpus where 5.5% of items record any
ancestry."* That is the same shape one level over: an apparatus that depends on a property most
of the population does not have.

## Consequence for Phase B

The mapping table is no longer the centre of the work. The centre is:

1. `claim_type` and a derived `verify_determinism` flag recorded per node — the minimum needed to
   make the strata visible;
2. the three-valued verify outcome preserved, so *unverifiable* stays distinct from *rejected*;
3. an Effect Reachability check over claim type, so a false-prophet screen reports when it was
   structurally incapable of finding anything;
4. type-aware weighting behind the existing gates, config-gated and off by default, as specified.

Item 3 is new, follows from the reframing, and is arguably worth more than item 4.
