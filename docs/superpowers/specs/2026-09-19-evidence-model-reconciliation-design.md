# Evidence-model canonical reconciliation

<!-- mp-status: {"id":"evidence-model-reconciliation-design","class":"current","asOf":"2026-09-19","replacement":null,"immutable":false} -->

**Status:** approved design, implementation not started

**Date:** 2026-09-19

**Scope:** the `minority-prophet` repository only

**Branch:** `codex/evidence-model-reconciliation`

## 1. Purpose

This design reconciles the repository's current mathematical, empirical,
implementation, and explanatory surfaces without rewriting historical evidence.
It answers two questions:

1. What is the strongest model the repository actually supports now?
2. How do we prevent a later document, implementation, or generated artifact
   from silently widening that model again?

This is a design for repository repair, not a new theorem and not a publication
plan. It does not post, file, email, or otherwise contact anyone. The two
scratchpad drafts and the AUDIT charter comment are outside this work. The
Master Hand delivery defect and automation-scope question are also outside this
repository reconciliation and remain open as recorded in the local handoff
`CODEX-HANDOFF-2026-09-19.md:131-159`.

## 2. Evidence basis and reading rule

The reconciliation follows the repository's own authority order:

1. content-bound research records;
2. the canonical-record registry;
3. the claim-to-record alignment ledger;
4. the theorem ledger and formal claim scope; and
5. the derived public summary.

That order is stated at `docs/README.md:18-36`. It also states that a newly
written explanation cannot promote an experiment or overrule an adverse result
(`docs/README.md:35-36`). Therefore recency alone is not authority, and a
present-tense sentence in a historical audit does not overrule a later compiled
proof, canonical result, or executable invariant.

For this design:

- **Read** means directly present in the cited artifact.
- **Derived** means mechanically entailed by artifacts that were read.
- **Inferred** means an architectural conclusion proposed by this design.
- A claim that something is absent names the surface searched.

The baseline repository was clean at commit
`1613e312056bb82b4de157906f88753d87c92575`. The Python baseline completed with
`1375 passed, 8 skipped, 21 subtests passed` under CPython 3.13.15. The first
documented `make verify` attempt failed before collecting tests because the
checkout initially selected Python 3.14 without `pytest`; this was an environment
failure, not a test failure.

## 3. Reconciliation findings

### 3.1 What is sound and should remain

The following are compatible and should be preserved:

- The formal kernel proves narrow properties of a side-consistent recorded DAG,
  not truth recovery (`formal/CLAIM-SCOPE.md:29-84`, `:88-96`).
- A recorded copy whose ancestry edge is present adds no new root vote
  (`formal/CLAIM-SCOPE.md:43-45`).
- An unrecorded copy remains indistinguishable from a recorded root to the graph
  (`provenance/graph.py:20-26`, `EvidenceNode.is_root` at `:203-215`).
- No rule reading only a record that lacks the relevant dependence can be immune
  to the ambiguity. DR3 is an existential indistinguishability witness, not a
  frequency claim (`formal/CLAIM-SCOPE.md:121-125`, `PROVENANCE.md:69-76`,
  `:86-91`).
- A settlement can be proved robust over all dependence readings the record
  actually admits, but not over dependence absent from the record
  (`formal/CLAIM-SCOPE.md:114-125`).
- Maximum-independent-set counting is exact or refused, and is only relative to
  the dependence graph supplied (`canon/U1-PROXIMATE-ROOTS.md:60-83`,
  `:142-155`).
- Independence is relative to a named error class rather than a scalar
  (`formal/CLAIM-SCOPE.md:108-112`, `canon/proximity.py:94-132`).
- Symmetric root margins do not answer universal or existential claims; those
  use separate compiled rules (`aggregation/root_vote.py:368-413`,
  `formal/THEOREM-LEDGER.json`, entries AC1-AC5).
- Evidence assessment, authority to act, and world-state verification are
  separate responsibilities (`SYSTEM-ARCHITECTURE.md:27-58`,
  `docs/architecture/README.md:18-21`).
- Rejected, incomplete, null, and adverse results remain part of the evidence
  base and are not rewritten (`docs/evidence/README.md:35-45`,
  `research/integrity/README.md:10-20`).

### 3.2 Contradictions and stale current-facing surfaces

These are repository defects to reconcile, not reasons to discard the evidence:

| Surface | Direct evidence | Reconciliation |
|---|---|---|
| `GLOSSARY.md` | “Evidence root” is defined as grounded in an observation at `:11`, then “Evidence root (recorded)” is defined as merely lacking recorded ancestry at `:31`. | One unqualified term currently denotes two different objects. Retire unqualified `evidence root` from normative use. |
| `FOUNDATIONS.md` | It speaks of mutually independent roots and minority-truth recovery at `:19-31`, while its own identifiability limit says votes alone cannot infer truth at `:53-57`. It also presents copy invariance as future-facing framing although the formal work has since changed. | Keep as conceptual framing or revise it into a current bounded overview; do not let it define runtime or proof semantics. |
| `formal/DEFINITION-AUDIT.md` | It says side/proposition enforcement is absent at `:132-153`. | This is historically accurate but stale as current state: `EvidenceGraph.add` now checks both at `provenance/graph.py:386-448`. Mark the audit as a dated snapshot and link the repairs. |
| `formal/CLAIM-SCOPE.md` | It says side-consistency has no enforcement point at `:174-181`. | Same stale present-tense defect; current code rejects or records those violations at `provenance/graph.py:427-466`. |
| `provenance/graph.py` versus U1 | The graph says root identity is caller-supplied and cannot identify a real observation at `:20-26`; U1 defines an effective witness count as a maximum independent set over a declared dependence graph (`canon/U1-PROXIMATE-ROOTS.md:60-83`). | These are different layers, not competing definitions: recorded graph roots versus effective witnesses. Name them separately. |
| `canon/proximity.py` | No shared recorded ancestry returns `True` for independence at `:94-105`. | This is a permissive research model and violates the no-positive-absence reporting rule if treated as a world claim. It cannot be the default assessment rule. |
| `canon/ATTESTED-INDEPENDENCE.md` | Its header calls the policy adopted and its cost unmeasured at `:1-8`. | The completed AID series rejected every proposed policy (`experiments/ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md:1-7`, `:18-57`). The document must be marked superseded/rejected as policy. |
| `aggregation/attested_independence.py` | Its module text still calls the cost unmeasured at `:39-41`; the file is the pinned artifact under test in AID manifests. | Do not edit the pinned file. Classify it through a sibling status document and current package documentation as a rejected research artifact. |
| `aggregation/README.md` | It presents attested-independence counting as a live policy at `:14-18`. | Label it as preserved experiment code whose proposed policies were rejected. |
| `docs/evidence/STATUS.md` | It says results added after 2026-08-09 are not canonical at `:8-13`. | This is false today: `CANONICAL-RECORDS.md:40-53` lists later DRI and AID canonical records. Generate or validate this section from lifecycle records. |
| DRI closure | It says the attested policy is the successor and its cost is unmeasured at `experiments/DECISION-RELATIVE-INDEPENDENCE-SERIES-CLOSURE.md:126-136`. | Preserve as the state at DRI closure; add an explicit later-outcome pointer rather than editing its historical conclusion. |
| AID closure | It says no real producer emits the origin link at `experiments/ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md:84-98`. | Preserve as the state at AID closure. Root issuance now emits and enforces the link (`docs/EMISSION-CENSUS.md:167-183`), while transport/relay and cache/fan-out remain unwired (`:185-204`). |
| `PROVENANCE-REQUIREMENTS.md` | It calls for enough “attested independent roots” at `:104-108` and describes independence as disjoint root sets at `:174-188`. | Split the theorem's recorded-root assumptions from the later error-relative dependence model. Do not claim attestation creates independence. |

### 3.3 The failed-policy conclusion must be binding

The AID series is not an unresolved experiment queue. Its closure says that all
three proposed downstream policies were tested and failed, and that the series
stops because a rule applied after the required fact was omitted cannot recover
that fact (`experiments/ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md:119-129`). It
also identifies the constructive seam: record the copy relationship when the
copy is made (`:59-93`).

Therefore:

- attested-depth deflation is not the canonical default;
- witness-count bounds are not a validated decision policy merely because they
  repair one suppression example;
- priced exposure is not a useful warning when it has no discrimination; and
- the surviving default is to preserve uncertainty, report the named record,
  use recorded-dependence robustness where its preconditions hold, and treat
  missing dependence as outside the result.

### 3.4 The emission repair is real but bounded

Root issuance now carries `origin_type` and `parent_roots`; copied or derived
issuance resolves to a parent identity rather than minting a fresh root
(`docs/EMISSION-CENSUS.md:167-178`). This repairs one production seam. It does
not defeat DR3, force external copiers to report truthfully, prove deployment
adoption, or cover transport/relay and cache/fan-out (`:185-204`).

## 4. Canonical answer

The repository should converge on the following model.

1. A **claim record** is a typed assertion plus its recorded evidence and
   provenance.
2. A **recorded root** is a claim record with no usable recorded ancestry. It is
   a fact about the record, not proof of independent observation.
3. An **issued root identity** is an authenticated, bounded registry identity.
   It limits issuance and can preserve declared copy ancestry. It does not prove
   truth, completeness, or distinct real-world observation.
4. A **dependence indication** is positive recorded evidence that two witnesses
   may share a relevant cause: declared ancestry, shared identity at a named cut,
   a content marker, a lookup, or another explicitly typed observable. Each
   indication states its error class and provenance.
5. A **possible-dependence graph** contains only dependence indications the
   assessment is entitled to use. Missing edges mean “not recorded by this
   basis,” never “independent.”
6. An **effective witness count** is an exact maximum independent set relative
   to one possible-dependence graph and one error class. It is not a count of
   objectively independent observations. If exact counting exceeds budget, the
   result is refused.
7. A **witness-count interval** or set of reachable settlements expresses the
   range supported by incomplete recorded dependence. A downstream consumer may
   settle only when every admissible reading yields the same settlement.
8. A **settlement** is an output of a named rule for a named claim shape.
   Symmetric, universal, and existential rules are different instruments and
   cannot exchange margins or verdict vocabulary.
9. An **assessment** always names its evidence basis, coverage domain, omitted
   surfaces, rule, assumptions, and limitations. It never implies that all
   evidence in the world was seen.
10. **Authority** is not an evidence score. A policy system may consume an
    assessment, but the assessment does not grant permission to act.

The shortest honest summary is:

> Recorded copies do not add recorded-root support. Missing copy links cannot be
> recovered by a better counting rule over the same record. Count only relative
> to a named dependence model, preserve the range of readings the record admits,
> and state what the record could not establish.

## 5. Layered object model

The word “root” has been doing work that belongs to several layers. The repaired
model makes the layers explicit.

| Layer | Object | Canonical question | Permitted conclusion | Forbidden leap |
|---|---|---|---|---|
| L0 World | event or state | What actually happened? | Outside this repository unless separately observed | A record proves the world |
| L1 Claim | claim record | What assertion was made? | Typed assertion and claim shape | Assertion is true |
| L2 Recorded derivation | ancestry edge | What derivation was recorded? | Parent/child relation in this record | No edge means no ancestry |
| L3 Issuance | issued root identity | Was origin issuance authenticated and bounded? | Registry membership, quota, declared parent links | Distinct IDs mean distinct observations |
| L4 Possible dependence | dependence indication/graph | What shared cause can this basis positively support? | Typed possible-dependence edge, relative to error class | Missing edge proves independence |
| L5 Counting | recorded-root count, MIS, or interval | How many units does this declared model admit? | Exact count or bounded range, exact-or-refused | Count is a real-world sample size |
| L6 Settlement | rule-specific result | Does every admissible reading settle the same way? | Symmetric or asymmetric typed result | One rule's margin applies to another claim shape |
| L7 Assessment | structured report | What was tested, over which basis and coverage? | Result plus limitations and non-establishment reasons | Assessment grants authority |
| L8 Policy/authority | external consumer | May an action proceed? | Decision under separate authority | Evidence engine authorizes action |

## 6. Vocabulary is typed, not global

The repository currently has several legitimate status vocabularies. The defect
is not that there are several; it is that prose sometimes swaps them.

| Vocabulary | Applies to | Must not be used as |
|---|---|---|
| `proved_compiled`, `verified_finite`, `tested_implementation`, `not_pursued` | theorem-ledger claim status | experiment verdict or runtime result |
| `exploratory`, `candidate`, `canonical`, `imported` | research lifecycle | truth or support verdict |
| `supported`, `rejected`, `incomplete`, `adverse` | preregistered experiment outcome | proof status |
| `settled_true`, `settled_false`, `unsettled` | symmetric dependence-robust settlement | universal/existential result |
| `refuted`, `not_refuted`, `established`, `not_established`, `indeterminate` | asymmetric claim rule | symmetric margin result |
| `verified`, `absent`, `unverifiable`, `no_reference` | dereference/recheck state | overall claim truth |
| `established`, `unestablished`, `failed`, `downgraded` | verifier-evidence reporting model | repository-wide universal outcome vocabulary |

The canonical registry will record the owner and domain of each vocabulary. A
checker will reject current-facing documents that use a value outside its
declared domain without an explicit mapping.

## 7. Authority and artifact classes after reconciliation

### 7.1 Immutable evidence

Canonical/imported lifecycle records, result packages, manifests, frozen
runners, and pinned source files remain byte-stable. A stale comment inside a
pinned source is corrected by a sibling status artifact, never by changing the
bytes and re-deriving historical pins.

This is mandatory because the repository itself records that an additive edit to
a pinned file invalidated eleven experiment checks, and that updating old pins
would falsely claim old experiments ran against new code
(`docs/EMISSION-CENSUS.md:107-130`).

### 7.2 Machine authorities

- `formal/THEOREM-LEDGER.json` controls theorem status.
- `research/records/*.json` controls enrolled lifecycle state.
- canonical manifests bind experiment artifacts.
- schemas control document shape; validators may add only explicitly documented
  semantic rules.
- a new `canon/model-registry.json` controls terminology, mechanism disposition,
  vocabulary domains, and pointers between the authorities above. It does not
  duplicate numeric results or promote records.

### 7.3 Derived current-facing surfaces

The following become generated or mechanically checked views:

- `docs/evidence/STATUS.md`;
- the current-status portions of `GLOSSARY.md`;
- canonical-record coverage in `EVIDENCE-ALIGNMENT.md`;
- the status table in `aggregation/README.md`; and
- a new reader-facing `docs/evidence/MODEL.md`.

`PUBLIC-CLAIMS.md` remains human-authored because claim wording requires
judgment, but every paragraph must carry stable claim identifiers that resolve
through the model registry to theorem or research-record authority.

### 7.4 Historical explanatory artifacts

Historical audits, series closures, old papers, and superseded proposals remain
in place. Each current navigation path must show a machine-checkable status
banner with:

- artifact class (`historical_snapshot`, `rejected_policy`, `superseded`, or
  `current`);
- the date/commit whose state it describes;
- its current replacement or later outcome; and
- whether the file is content-bound and therefore immutable.

## 8. Canonical registry design

Add `canon/model-registry.schema.json` and `canon/model-registry.json`.

The registry contains four collections.

### 8.1 Terms

Each term records:

```json
{
  "id": "recorded_root",
  "label": "recorded root",
  "layer": "L2",
  "definition": "A claim record with no usable recorded ancestry.",
  "notEquivalentTo": ["issued_root_identity", "effective_witness"],
  "authority": [{"artifact": "provenance/graph.py", "symbol": "EvidenceNode.is_root"}]
}
```

The definition is concise; detailed reasoning stays in cited artifacts. The
registry forbids duplicate normative labels unless the entries explicitly name
different domains.

### 8.2 Mechanisms

Each implementation or policy records:

- stable ID and symbols;
- layer and input/output types;
- disposition: `current`, `research_only`, `rejected`, `historical`, or
  `superseded`;
- theorem IDs and research-record IDs it may cite;
- prohibited claims;
- replacement, if any;
- pinned/immutable status.

Examples:

- `evidence_graph_recorded_roots`: current L2 primitive;
- `root_registry_bounded_issuance`: current L3 reference implementation;
- `proximate_mis_count`: research-only L4/L5 model;
- `attested_independence_point_policy`: rejected and pinned;
- `attested_independence_bounds_policy`: rejected as tested, with the broader
  bounds idea explicitly not proved impossible;
- `dependence_robust_settlement`: current for recorded possible dependence,
  backed by DR1/DR2;
- `root_vote_symmetric`: current kernel-reference implementation, not a complete
  assessment engine.

### 8.3 Claim bindings

Each present-tense public claim gets a stable identifier and references existing
authority rather than copying status:

```json
{
  "id": "PC-RECORDED-COPY-INVARIANCE",
  "theorems": ["T2"],
  "researchRecords": [],
  "requiredQualifiers": ["recorded ancestry edge", "side-consistent", "recorded graph"],
  "prohibitedOverstatement": ["all copies are free", "independent observations"]
}
```

The checker resolves the referenced IDs and fails if their authoritative status
does not permit the public claim.

### 8.4 Artifact status

Every current navigation target that can be mistaken for current authority gets
one entry. Content-bound paths carry their expected digest or manifest pointer.
This allows navigation to explain status without touching pinned bytes.

## 9. Structured assessment contract

Add a new versioned assessment schema rather than making any existing frozen
result shape silently mean more.

Required top-level fields:

- `schemaVersion`;
- `claimId`, `claimShape`, and proposition identity;
- `evidenceBasis`: exact records and graph/cut/error-class versions read;
- `coverageDomain`: enumerated or explicitly `not_established`;
- `recordedAncestryStatus` and unusable/unattributed records;
- `possibleDependenceBasis`: which positive indicators were admitted;
- `countResult`: tagged union of exact recorded-root count, exact error-relative
  MIS, interval, or refused-with-reason;
- `settlementResult`: tagged union for symmetric, universal, or existential
  rules;
- `assumptionsSatisfied` and `assumptionsNotEstablished`;
- `limitations` and prohibited interpretations;
- `authorityEffect: "none"`.

There is deliberately no top-level `independent: true` and no unqualified
`truth`, `confidence`, or `safeToAct` field.

## 10. Implementation migration

### Phase 0 — freeze semantic expansion

Until the reconciliation gate lands:

- no new public independence/root terminology;
- no new counting policy;
- no paper promotion based on unreconciled current-facing prose; and
- ordinary bug fixes may continue if they do not widen claims or touch pinned
  inputs.

### Phase 1 — land the registry and checker

1. Add the model-registry schema and initial registry.
2. Add `scripts/check_canonical_model.py`.
3. Add unit tests for registry validation and authority resolution.
4. Wire the checker into `make verify-integrity` and CI.
5. Emit a deterministic reconciliation report listing current, historical,
   rejected, superseded, pinned, and unresolved surfaces.

This phase changes no scientific result and no pinned artifact.

### Phase 2 — repair navigation and terminology

1. Replace the duplicate root definitions in `GLOSSARY.md` with the layered
   terms from section 4.
2. Bring `FOUNDATIONS.md` into the current boundary or mark it explicitly as
   conceptual framing.
3. Add dated historical-status banners to `formal/DEFINITION-AUDIT.md` and the
   DRI/AID closure documents without altering their findings.
4. Correct stale current-tense enforcement statements in current claim-scope
   documentation, citing both the historical defect and present implementation.
5. Mark `canon/ATTESTED-INDEPENDENCE.md` as a rejected/superseded policy and
   point to AID-1 through AID-4.
6. Mark `aggregation/attested_independence.py` as pinned rejected research code
   through sibling documentation; do not edit its bytes.
7. Generate `docs/evidence/STATUS.md` from lifecycle and theorem authority so
   later canonical records cannot leave the page stale.

### Phase 3 — add the assessment API beside pinned primitives

1. Introduce a new module; do not retrofit frozen experiment inputs.
2. Compose recorded graph validation, claim-shape dispatch, possible-dependence
   robustness, and coverage reporting.
3. Return the structured contract in section 9.
4. Treat the existing `root_vote.verdict` as a kernel/reference result and
   `dependence_robustness` as a recorded-basis component, not complete
   assessments.
5. Default missing basis or missing coverage to explicit non-establishment, not
   zero, false, independence, or permission.

### Phase 4 — adversarial regression fixtures

Promote the repository's existing failures into named cross-layer fixtures:

1. recorded copy adds no root;
2. unrecorded copy is not detected;
3. laundered provenance inflates a permissive count;
4. shared shock must not be called a shared source;
5. exact content fingerprint fails under paraphrase and cannot detect shared
   component/origin generally;
6. attestation deflation suppresses a true minority;
7. bounds repair one case but do not create shared-origin knowledge;
8. universal/existential claims reject the symmetric margin;
9. valid disclosed artifacts do not establish coverage completeness;
10. a cited source through `read_from` is ancestry, not a fresh root;
11. R2 conflict fails closed;
12. a pinned historical input cannot be modified to make current tests pass.

Each fixture must state which layer it attacks and the strongest conclusion it
permits. A fixture that demonstrates one mechanism must not silently promote an
entire system claim.

### Phase 5 — align public claims and papers last

Only after phases 1-4 pass:

1. bind every present-tense paragraph in `PUBLIC-CLAIMS.md` to stable claim IDs;
2. regenerate/check evidence status and alignment views;
3. audit current site copy against the same registry;
4. review papers as consumers of the now-reconciled model; and
5. leave historical manuscripts unchanged except for external navigation that
   identifies their status.

No filing or external publication is part of this phase without a separate user
instruction.

## 11. Verification gates

The reconciliation is complete only when all of the following pass:

1. `make verify` from a declared supported environment.
2. The model registry validates against its schema.
3. Every theorem and research-record reference resolves to an authoritative ID.
4. Every canonical/imported record in lifecycle JSON is represented in the
   registry or explicitly exempted as legacy with a reason.
5. Generated current-status documents have no diff after regeneration.
6. No current-facing normative surface defines unqualified `evidence root`.
7. No current-facing normative surface reports sources as independent without a
   named graph, error class, test, and coverage.
8. Every statement that an artifact lacks something names the searched paths or
   corpus.
9. Rejected mechanisms cannot be imported through the recommended public API.
10. Pinned artifacts match their existing manifests before and after the change.
11. The adversarial fixtures in phase 4 pass.
12. A clean-clone run reproduces the same generated model/status artifacts.

## 12. Non-goals

This work does not:

- prove real-world independence, truth, completeness, or deployment safety;
- invent a detector for hidden dependence;
- rescue any rejected AID policy;
- infer real-world error or adversary rates from synthetic results;
- decide the correct decision-relative cut for a deployment;
- make a weighted aggregator canonical;
- change authority policy in Gate or Border;
- rewrite historical records, manifests, papers, or frozen runners;
- resolve the Master Hand CRM projection defect;
- edit recurring automations; or
- post the AUDIT charter comment or file either IETF draft.

## 13. End state

After implementation, a reader and a program should reach the same answer:

- The repository proves properties of recorded evidence structures under named
  assumptions.
- It can preserve declared copy ancestry and assess robustness over recorded
  possible dependence.
- It cannot turn missing ancestry into independent observation.
- It reports exact counts only relative to a named model, otherwise a range,
  reachable-settlement set, or refusal.
- It keeps claim shape, evidence coverage, research status, and authority in
  separate typed fields.
- Historical mistakes and rejected policies stay visible, but they cannot pose
  as current defaults.
- Public prose and papers are downstream of machine-resolved claim authority,
  rather than a parallel source of truth.

That is the repository's strongest defensible position. It is narrower than
several current sentences and stronger than a blanket refusal: recorded
dependence can be handled exactly, its limitations can be stated precisely, and
the system can demonstrate what it checked without pretending to know what the
record omitted.
