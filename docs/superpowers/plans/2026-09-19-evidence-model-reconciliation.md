# Evidence-model reconciliation implementation plan

> **Execution:** Apply this plan in the current `codex/evidence-model-reconciliation`
> branch. Preserve all content-bound results, manifests, frozen runners, and
> pinned source bytes. Use test-driven development for checker behavior.

**Goal:** Make the repository's current evidence model machine-resolvable, repair
the stale current-facing records that contradict it, and add adversarial gates
that prevent the rejected attestation policies or ambiguous root terminology
from silently becoming current again.

**Scope:** This plan implements phases 1, 2, and the status/authority portion of
phase 4 from the approved design. The new assessment API and public-paper binding
remain separate work because they change runtime interfaces and publication
surfaces rather than repairing the repository's records.

**Architecture:** Add a small JSON registry whose entries point to existing
theorem/research authority instead of duplicating results. A standard-library
checker validates registry structure, resolves authority IDs and artifact paths,
verifies declared manifest pins, and reconciles structured status banners on
current navigation targets. Human-readable pages then use the registry's typed
terms and dispositions while historical evidence remains byte-stable.

**Tech stack:** Python 3 standard library, JSON/JSON Schema documents, unittest
via pytest, Markdown, Make.

---

## Task 1: Define a machine-readable canonical model

**Files:**

- Create: `canon/model-registry.schema.json`
- Create: `canon/model-registry.json`
- Create: `scripts/check_canonical_model.py`
- Test: `tests/test_canonical_model.py`

### Step 1: Write failing registry-shape tests

Add tests that load a temporary registry and assert failures for:

- duplicate IDs and duplicate unqualified normative labels;
- an undeclared layer or disposition;
- a missing artifact path;
- an unknown theorem-ledger ID;
- an unknown research-record ID;
- a replacement ID that does not resolve;
- a current mechanism that cites only rejected research as promotion authority;
- a content-bound artifact whose manifest does not contain its declared path;
- a declared pin whose digest differs from the manifest or working-tree bytes.

Also assert the real registry validates successfully.

Run: `.venv/bin/python -m pytest -q tests/test_canonical_model.py`

Expected: fail because the checker and registry do not exist.

### Step 2: Implement the minimal validator

Implement `validate_repository(root: Path) -> list[str]` and a CLI in
`scripts/check_canonical_model.py`. Keep it read-only and dependency-free.

The checker must:

- validate required top-level collections and closed vocabularies;
- require unique IDs and normative labels;
- resolve artifact paths relative to repository root;
- load theorem IDs from `formal/THEOREM-LEDGER.json`;
- load research record IDs from `research/records/*.json`;
- resolve mechanism replacements and claim bindings;
- verify content-bound pins against the named canonical manifests and current
  working-tree bytes;
- parse structured `mp-status` JSON comments from registered current navigation
  targets and compare their class/replacement/immutability fields with registry
  entries; and
- print deterministic counts and errors.

Do not infer scientific status from filenames or prose.

### Step 3: Add the initial registry and schema

The initial registry must distinguish:

- `recorded_root` (L2), `issued_root_identity` (L3), and
  `effective_witness` (L5);
- current recorded-graph/root-issuance/dependence-robust mechanisms;
- `canon/proximity.py` as research-only;
- the attested point, bounds, margin, and priced-exposure policies as rejected;
- the broader idea of reporting admissible uncertainty as distinct from any
  rejected AID policy;
- theorem/research authority domains and prohibited overstatements; and
- current, historical, rejected, superseded, and content-bound artifact classes.

The registry must cite existing authority IDs and paths. It must not copy
experimental measurements.

### Step 4: Make the tests pass

Run: `.venv/bin/python -m pytest -q tests/test_canonical_model.py`

Expected: all tests pass.

### Step 5: Commit

Commit message: `feat: add canonical evidence-model registry`

---

## Task 2: Repair stale status records without rewriting evidence

**Files:**

- Modify: `canon/ATTESTED-INDEPENDENCE.md`
- Modify: `aggregation/README.md`
- Modify: `research/attested-independence/README.md`
- Modify: `docs/evidence/STATUS.md`
- Modify: `formal/CLAIM-SCOPE.md`
- Modify: `formal/DEFINITION-AUDIT.md`
- Modify: `experiments/DECISION-RELATIVE-INDEPENDENCE-SERIES-CLOSURE.md`
- Modify: `experiments/ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md`
- Test: `tests/test_canonical_model.py`

### Step 1: Add failing status-reconciliation tests

Add tests that mutate temporary copies of registered banners and require the
checker to reject:

- the attested policy classified as current/adopted;
- the DRI closure missing its later AID outcome pointer;
- the AID closure presented as current emission state rather than a dated
  snapshot;
- the formal audit presented as current enforcement state;
- `docs/evidence/STATUS.md` omitting the canonical AID records; and
- a rejected implementation advertised as a recommended package method.

Run the focused tests and confirm each injected regression fails for the
intended reason.

### Step 2: Add structured status banners and current corrections

- Mark `canon/ATTESTED-INDEPENDENCE.md` as rejected/superseded policy doctrine;
  retain its reasoning and point to AID-1 through AID-4 and the series closure.
- Describe `aggregation/attested_independence.py` as pinned rejected research
  code in sibling docs; do not edit the Python file.
- Update the attested-independence research index to say the completed series is
  negative and the surviving constructive seam is copy-time emission.
- Correct `docs/evidence/STATUS.md` so later DRI/AID canonical records are
  canonical and the old 2026-08-09 cutoff is not treated as a status rule.
- Correct current-tense enforcement in `formal/CLAIM-SCOPE.md` while preserving
  the historical counterexample and scope warning.
- Mark `formal/DEFINITION-AUDIT.md` as a dated historical snapshot and point to
  the later enforcement implementation.
- Add a later-outcome pointer to the DRI closure.
- Mark the AID closure's emission census as a closure-time snapshot and point to
  the bounded root-issuance repair plus the two remaining unwired seams.

### Step 3: Verify pinned bytes did not change

Run the checker and the existing research-integrity checks. Confirm the working
tree hashes for `aggregation/attested_independence.py`, `canon/proximity.py`, and
`provenance/dependence_robustness.py` still match every manifest that pins their
current version.

### Step 4: Run focused tests

Run:

```bash
.venv/bin/python -m pytest -q \
  tests/test_canonical_model.py \
  tests/test_attested_independence.py \
  tests/test_dependence_robustness.py \
  tests/test_root_registry.py \
  tests/test_evidence_alignment.py
```

Expected: all pass.

### Step 5: Commit

Commit message: `docs: reconcile rejected policies and historical status`

---

## Task 3: Replace overloaded root terminology in current guidance

**Files:**

- Modify: `GLOSSARY.md`
- Modify: `FOUNDATIONS.md`
- Create: `docs/evidence/MODEL.md`
- Modify: `docs/evidence/README.md`
- Modify: `EVIDENCE-ALIGNMENT.md`
- Test: `tests/test_canonical_model.py`
- Test: `tests/test_evidence_alignment.py`

### Step 1: Write failing terminology tests

Require current normative pages to:

- use `recorded root`, `issued root identity`, and `effective witness` with
  separate definitions;
- state that absence of a recorded edge is not proof of independent observation;
- state that an effective-witness count is relative to a named possible-
  dependence graph and error class;
- state that issuance identity authenticates/bounds issuance but does not prove
  truth or observation independence; and
- link the reader-facing model page from the evidence index.

The test should parse registry-owned status/term IDs rather than merely searching
for a favorable sentence.

### Step 2: Repair the current guidance

- Replace the two incompatible unqualified `Evidence root` glossary entries
  with the three layered terms.
- Mark `FOUNDATIONS.md` as conceptual framing, update its present-tense next-step
  statements, and qualify copy invariance as applying to recorded copy links.
- Add `docs/evidence/MODEL.md` as the concise reader view of the registry: object
  layers, the negative AID conclusion, the bounded issuance repair, and the
  remaining unknowns.
- Link the model from `docs/evidence/README.md`.
- Add a dated reconciliation entry to `EVIDENCE-ALIGNMENT.md` without changing
  any canonical experimental outcome.

### Step 3: Run focused tests

Run:

```bash
.venv/bin/python -m pytest -q \
  tests/test_canonical_model.py \
  tests/test_evidence_alignment.py \
  tests/test_root_identity.py \
  tests/test_root_registry.py \
  tests/test_read_from.py
```

Expected: all pass.

### Step 4: Commit

Commit message: `docs: separate recorded roots from effective witnesses`

---

## Task 4: Make reconciliation a required integrity gate

**Files:**

- Modify: `Makefile`
- Modify: `.github/workflows/ci.yml` if CI bypasses `make verify-integrity`
- Test: `tests/test_canonical_model.py`

### Step 1: Write a failing gate-wiring test

Assert `verify-integrity` depends on `check-canonical-model` and the target runs
`scripts/check_canonical_model.py`. If CI enumerates integrity scripts directly,
assert it invokes the target too.

### Step 2: Wire the checker

Add `check-canonical-model` to `.PHONY`, help output, and `verify-integrity`.
Prefer the existing `make verify-integrity` path over duplicating the command in
CI.

### Step 3: Stress-test the gate adversarially

Run the checker against temporary repositories containing each injected defect
from Tasks 1-3. Confirm failures are specific and deterministic. Then run it
twice on the real tree and confirm byte-identical output.

### Step 4: Run the full verification suite

Run: `make verify`

Expected:

- Python tests pass;
- documentation navigation passes;
- public-boundary diff and full sweep pass;
- registration-chain and research-integrity checks pass;
- canonical-model reconciliation reports no errors;
- site lint/build/tests pass; and
- evaluation tests pass.

### Step 5: Review the diff and immutable surfaces

Run:

```bash
git diff --check
git status --short
git diff --stat
git diff --name-only -- aggregation/attested_independence.py \
  canon/proximity.py provenance/dependence_robustness.py results research/records
```

The last command must show no changes to pinned source, results, manifests, or
lifecycle records.

### Step 6: Commit

Commit message: `test: gate canonical evidence-model reconciliation`

---

## Completion criteria

This repair is complete only when:

1. the registry and all status banners agree;
2. deliberately reintroducing each known stale conclusion causes a test or
   integrity check to fail;
3. every authority reference resolves;
4. all pinned inputs and content-bound records remain unchanged;
5. `make verify` passes from the supported local environment; and
6. the final report distinguishes what was repaired from the separate runtime
   assessment-API work that remains.
