# Cross-programme reconciliation

Written 2026-09-15. **This document advances no experiment.** It records that
gates declared open in `experiments/KL-*/STATUS.json` describe work that other
parts of this repository have already done, and that nothing reconciles the two.

## Why it exists

The KL-001..011 ladder was reviewed at `RUN-20260807-*`. Since then the
repository gained the DRI series, the H-series (HEO/HES/HGD/HVI), the LIR
series, and KL-012..019. None of those are referenced from a KL-001..011 status
file, and none of them reference one.

The result is that an experiment can declare a prerequisite *unsolved* while the
artifact that solves it sits two directories away. `CLAIMS.md` C2 is the
load-bearing instance: it states a problem is unsolved and that **nothing in
this programme solves it**. A NIST SARD replication in the same repository
solves it.

This is the `stale-self-description` family — PROV-005, ART-101, TEST-101,
DOC-102 — at a third scope. The within-repository instances were caught by
reviews that re-derive rather than re-read. The cross-repository instance
(KL-011 and Border) was caught by the owner's memory. This one, cross-*series*
within a single repository, was caught the same way. No review spans series.

## The map

Strength is stated per row and is not uniform. `covers` means the cited artifact
answers the gate as written. `partial` means it answers a necessary part.
`adjacent` means it answers the same question about a different artifact and is
**not** admissible for the gate — the distinction that kept KL-011 at
`fixture-passed`.

| Gate declared open | Answered by | Strength |
|---|---|---|
| **KL-001** — *"a real-repository run needs defect ground truth for real repositories"*, and `CLAIMS.md` C2's *"nothing in this programme solves it"* | **HGD-2 Domain B**: NIST SARD test suite 101, the C test suite for source-code analyzers, with real detector families (`clang_analyze`, `clang_warning`, `clang_security`, `flawfinder`, lexical). A labelled real-software defect corpus with frozen source digests. | **covers** the ground-truth prerequisite. Does **not** run KL-001's registered endpoint. |
| **KL-001**, same gate, second instance | **DRI-7**: ground truth on real repository records obtained by dereference rather than planting — 123 checkable, 102 absent. Unauthored population. | **partial** — establishes the method on a different defect class (dangling reference, not injection). |
| **KL-008** — *"Does root-aware aggregation resist shared sensor or model failure?"*; first gate *"derived products sharing one instrument are collapsed into one dependency family"* | **HGD-1 and HGD-2 Domain A**: EPA collocated PM2.5, real instruments, with common-mode failure injected into the collocated family only while the separate-site family is held unchanged. HGD-1's question is collocated sensors verbatim. | **covers** the question on real data. Primary claims recorded **false** in both. |
| **KL-002 / ADV-004** — root identity, and whether multiplying names manufactures independence | **HVI-1**: *"Can explicit creator, verifier, and controller provenance stop one controlling party from manufacturing apparent independent evidence by multiplying names, keys, services, or organizational labels?"* — `primary_claim: true`. | **covers** the mechanism. KL-002's own gate scopes its remainder to an agent **pipeline**, which HVI-1 does not test. |
| **KL-006 and KL-008 / ADV-005** — *"shared upstream dependency is not representable in schema v0.1"* | **`experiments/hgd1/dependency-receipt.schema.json`**: `components[]` carrying `componentId`, `kind` ∈ {instrument, station, calibration, operator, model, dataset, other}, and `sharedWeightLower`/`sharedWeightUpper`. Shared dependency is representable, as interval-valued shared weight. | **partial** — a representation exists; ADV-005 is stated against KL schema v0.1 and migration is not done. |
| **KL-005** — *"assemble timestamped closed news events"* | **LIR-1 `DATASET-CATALOG.md`** (churnalism, memetracker, rumor_cascades, retraction_cascades, llm_echo, prediction_markets — each with acquisition path, edge type and recorded caveats) and **LIR-3 `pheme_provenance.py`**, which materialises disjoint PHEME splits with observable provenance. | **partial** — the corpus problem is scoped and one source is materialised; no KL-005 registration exists. |
| **KL-003** — independent data-collection roots vs publication counts | **KL-016 v0.2**: root structure measured on real mathematical literature. Root ratios 0.132–0.429; **57%–87% of a conjecture's citing literature descends from other citing literature**, against a negative control of 0%. | **adjacent** — literature descent, not replication outcome. KL-016 also records that its own control arm collapsed. |
| **KL-011** — a foreign transport, and a second implementation reading the receipt | Border `A2A-MCP-CROSSING-001` transport run, and `Heaviside479/handoffprobe#20`. | **adjacent** — different corpus. Already recorded in `KL-011/EXTERNAL-EVIDENCE.md`; state deliberately unchanged. |

## What this does not do

- **No experiment state changes.** Every KL experiment keeps the state it had.
  A gate being answerable is not the same as a registration being satisfied, and
  the difference is the whole subject of this repository.
- **No claim is transferred.** An `adjacent` row is evidence about its own
  artifact and is inadmissible for the gate it sits beside.
- **It is a snapshot.** This document goes stale the moment either side moves,
  which is the defect it documents. `scripts/check_gate_coverage.py` exists so
  that staleness fails a test instead of waiting for someone to remember.

## The correction owed

`CLAIMS.md` **C2** asserts a prerequisite is unsolved and that nothing in this
programme solves it. The second clause is false and is corrected in this change.
The first clause is narrowed rather than withdrawn: KL-001's registered endpoint
still has not been run against SARD, and HGD-2 was not designed to run it.
