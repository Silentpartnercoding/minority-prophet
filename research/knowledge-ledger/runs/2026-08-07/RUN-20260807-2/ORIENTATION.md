# ORIENTATION — RUN-20260807-2

Opened 2026-08-07T19:49:58Z on branch `agent/knowledge-ledger-run-20260807-1`,
HEAD `cc1d494` (RUN-20260807-1's closing commit). Worktree clean at start
except for this run directory itself (`git-status-before.txt` records exactly
one entry: the untracked `RUN-20260807-2/` being created).

## 1. What this run is

Specification repair and re-run of KL-000. The independent Rust
reimplementation commissioned after RUN-20260807-1 has completed; its findings
motivate four specification repairs (R1–R4), to be published as protocol
v1.1.0 with v1.0.0 preserved unmodified, followed by a full re-run whose
numbers must be identical to RUN-20260807-1. Identical numbers are the
evidence that the repairs document existing behaviour rather than change it.

## 2. Prompt capture

Agent transcription, unverified — no operator-side artifact was found. See
`inputs/PROMPT-CAPTURE-NOTE.md` and constraint PROV-004. The v3 prompt named
by RUN-20260807-1 (`sha256:4bf92221…73f`) was not located and remains unread;
this run received a new instruction instead.

## 3. External evidence read, none modified

Read-only, as instructed. Nothing under `kl000-independent-spec/` was touched.

| Artifact | Role |
|---|---|
| `kl000-independent-spec/impl-rs/FINDINGS.md` | independent implementer's report, findings F1–F15 |
| `kl000-independent-spec/impl-rs/results/kl000-independent-result.json` | independent full-scale result |
| `kl000-operator-notes/OPERATOR-DISCLOSURE.md` | package leaked reference language + module structure |
| `kl000-operator-notes/NAMING-CONVERGENCE.md` | one unexplained shared identifier; schema otherwise disjoint |

## 4. Verification of the operator notes' checkable claims

The disclosure note says "grep rather than take this file's word for it". Done:

- **Structure leak confirmed, and understated.** `kl000-independent-spec/preregistration.json`
  names not three but **five** reference paths: the three `src/` modules the
  disclosure lists, **plus** `tests/test_kl000_invariants.py` and
  `tests/test_kl000_adversarial.py` (lines 187–188 of the packaged file), plus
  a sixth mention of `kl000_worlds.py` inside `enumerationMethod`. The
  disclosure's substance stands — numbers were checked, structure was not —
  but the leaked surface includes the test-file names. This bears directly on
  finding F12: the implementer knew the adversarial suite's *filename* while
  its *contents* were absent from the package, which is consistent with its
  statement that its ten attacks are its own construction.
- **Naming convergence confirmed exactly as stated.** Of the reference's
  result-schema identifiers (`receiptProducingWorlds`, `worldsChecked`,
  `failClosedRejections`, `outOfDeclaredBounds`, `totalViolations`,
  `preservedViolations`, `violationsByInvariant`, `conclusionDistribution`),
  only `violationsByInvariant` and `conclusionDistribution` appear in
  `impl-rs/src/main.rs`, plus `DECLARED_WORLD_COUNT`. `conclusionDistribution`
  is spec-supplied (a secondary endpoint phrase). The phrase "by invariant"
  appears zero times in the packaged PROTOCOL.md, preregistration.json, and
  fixtures. `violationsByInvariant` remains matched without a visible path
  from the specification, exactly as the operator note records.

## 5. Verification of the reproduction/replication claims

Computed from the two committed result documents, not transcribed:

| Quantity | Reference (RUN-20260807-1) | Independent (Rust) | Agreement |
|---|---|---|---|
| exhaustive worlds | 176,120 | 176,120 | exact |
| receipt-producing | 110,840 | 110,840 | exact |
| fail-closed | 65,280, one cause | 65,280, one cause (`root_on_both_sides` ≡ I3) | exact |
| hard violations | 0 | 0 | exact |
| `present` | 41,820 | 41,820 | exact |
| `absent_within_declared_scope` | 160 | 160 | exact |
| `supported` | 19,380 | 41,820 | **diverges** |
| `not_established` | 49,480 | 27,040 | **diverges** |
| divergent worlds | — | — | **22,440** (= independent ambiguity A3's pre-comparison prediction) |
| randomized worlds | 1,000,000 | 1,000,000 | same count, **different stream** |
| randomized fail-closed | 756,619 (75.66%) | 755,909 (75.59%) | equivalent rate, not comparable counts |
| randomized violations | 0 | 0 | agrees as replication |

Decomposition of the 22,440 (verified by direct enumeration of the 259
evidence ledgers): 66 clean ledgers with ≥1 supporting root and opposing ≥
supporting, × 340 location ledgers = 22,440; of these, ties (support ==
oppose) account for 16,320 worlds and strict minorities (oppose > support ≥ 1)
for 6,120.

**Terminology discipline for the record:** the exhaustive phase is a
*reproduction* (identical world set, independently derived, exact agreement on
all counts and on two of four conclusion classes). The randomized phase is a
*replication only* — the preregistration froze the seed but not the draw
schedule, so the two implementations sampled different worlds (reference:
CPython Mersenne Twister; independent: splitmix64-seeded xoshiro256**). Its
agreement is "0 violations at an equivalent fail-closed rate", never
count-for-count. This is the independent implementer's finding F11 and it is
adopted here.

## 6. Verification that R1–R4 describe existing reference behaviour

Probed empirically against `knowledge_ledger/transaction.py`
(sha256 `15dfd500…3a3e21f`, byte-identical to the preregistered hash):

| Repair | Probe | Result |
|---|---|---|
| R1 tie rule | presence claim, 1 support + 1 oppose root | `not_established` ✓ (strict minority also `not_established`; 1 support + 0 oppose → `supported`) |
| R2 empty scope | zero-location search ledger | refuses: `ValueError: The declared search space must not be empty.` ✓ |
| R3 duplicate ids | two locations sharing an id | refuses: `ValueError: Search-location identifiers must be unique.` ✓ |
| R4 canonicalisation | recompute digest from receipt minus `contentDigest` | verifies; form is sorted keys, `,`/`:` separators, no whitespace, raw UTF-8 (`ensure_ascii=False`) ✓ |

The code sites: strict-majority conclusion at `transaction.py:69`; empty-scope
refusal at `:31–32`; uniqueness refusal at `:34–36`; canonical bytes at
`:17–18`; digest scope (all top-level receipt fields except `contentDigest`)
at `:21–24` and `:98`.

## 7. Plan of record

1. Import the external evidence into the repository by copy, with digests
   (originals untouched).
2. Register protocol v1.1.0: new `PROTOCOL-v1.1.0.md`,
   `preregistration-v1.1.0.json`, and digest-pinned fixture C11 under
   `fixtures/v1.1.0/` (outside the v1.0.0 glob). v1.0.0 files unmodified.
3. Extend runner/checker/tests minimally to execute against a named
   preregistration and to compare a fixture's pinned `contentDigest`.
4. Re-run KL-000 in full against v1.1.0. Every RUN-20260807-1 number must
   reappear exactly; any moved number stops the run and becomes the finding.
5. Close with the versioned packet. Nothing pushed, nothing promoted.

## 8. Scope refusals, stated up front

- The four repairs are the owner's list. Findings F1/F2 (I2/I5 stated
  receipt-internally), F5 (margin sign), F4 (`conversionsToReverse`
  undefined for the empty ledger), F13 (C06's note), F3 (B2≡B3) are real and
  are **not** repaired here; they go to the backlog as candidate v1.2.0
  material. Repairing them uninstructed would mix owner decisions with agent
  decisions inside a document whose whole value is knowing who decided what.
- The independent implementation is not re-run and not touched. Its re-run
  against v1.1.0 is KL-000's next gate and a separate commission.
