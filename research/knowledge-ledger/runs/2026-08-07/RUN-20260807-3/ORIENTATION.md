# ORIENTATION — RUN-20260807-3

Opened 2026-08-07T20:48:15Z on branch `agent/knowledge-ledger-run-20260807-1`,
HEAD `0b6614f` (RUN-20260807-2's closing commit). Worktree clean at start
except this run directory's own creation. Environment unchanged from
RUN-20260807-2 (lock copied, pip freeze identical).

## 1. What this run is

R5: register the receipt object (R5.1, from IND-20260807-2 finding G2) and
define the sign of `margin` (R5.2, from finding G1), publish as protocol
v1.2.0 preserving v1.0.0 and v1.1.0 unmodified, re-pin C11, and re-run
KL-000 in full. Counts and the conclusion distribution must not move; the
C11 digest is permitted to move if the registered object differs from what
the reference emitted (registered prediction below: it does not differ, so
the digest should not move either).

## 2. IND-20260807-2, read and none of it modified

`impl-rs/FINDINGS-v110.md` and `results/kl000-independent-result-v110.json`.
Status `passed-except-c11-digest`: 0 violations of all eleven invariants,
every registered *value* of all eleven controls matched, all four baselines
caught, C11's digest not reproduced. Two new IND findings G1–G6, plus a §0
disclosure that the v1.1.0 commission package leaked the expected values.

## 3. Verification of the checkable claims — all pass

| # | Claim | Verified how | Result |
|---|---|---|---|
| 1 | Conclusion function agrees exactly | their result JSON vs `kl000-confirmatory.json` | 160 / 49,480 / 41,820 / 19,380 on both sides, exact |
| 2 | Their codec conforms: canonical output round-trips byte-identically through `json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False)` | re-serialised their published 463-byte unsigned form | **byte-identical**; sha256 over it reproduces their computed digest `0d178b…` |
| 3 | Reference receipt members are exactly claim, conclusion, contentDigest, evidence, limits, reason, schema, search, transactionId | evaluated C11's input | exact; no `receiptVersion` |
| 4 | Zero negative margins in the reference; 38,760 receipts negative under the signed reading | full 110,840-receipt enumeration | 0 and 38,760, exact |
| 5 | C11's hashed bytes: 703 total, 424 from package-stated values, 279 (39.7%) from `schema`+`reason`+`limits`, stated nowhere | recomputed from the reference receipt | 703 / 424 / 279, exact |
| 6 | G4: an evaluator with the existential presence reading changes 22,440 conclusions, violates zero invariants, is caught only by C11 | ran the ablation through `check_world` over the full enumeration | 22,440 / 0 / C11-only, exact. **This run's first attempt used the wrong ablation** (blanket inversion: 55,420 changed, caught by C01/C02/C11) — preserved with the correction in `logs/g4-inverted-r1-ablation.txt`; zero violations held for both |
| 7 | Leaked-line derivability: the exhaustive distribution follows from IND-1's published output + R1 | 41,820−22,440 = 19,380; 27,040+22,440 = 49,480 | exact |

## 4. The commission package, located and traced

The implementer's §0 leak disclosure initially appeared to contradict the
disk: `kl000-independent-spec/`'s top-level PROTOCOL.md and
preregistration.json are still byte-identical to **v1.0.0** (`dea9649f…`,
`5204e640…`, fixtures c01–c10 only). The delivered v1.1.0 package is a
**separate directory, `kl000-v110-spec/`**, and resolves everything:

- `kl000-v110-spec/PROTOCOL.md` is **byte-identical to the registered
  `PROTOCOL-v1.1.0.md`** (`2ce181f3…`). Its preregistered-prediction table
  (lines 26–33, verified) carries all eight values the operator's v1.0.0
  screening list names, comma-formatted. **The leak's origin is the
  registration itself** — the prediction table is scientifically necessary in
  the registered protocol and fatal in a commission package, and the same
  file was used for both roles.
- `kl000-v110-spec/preregistration.json` (`6a95d024…`) is a redacted variant
  of the registered `preregistration-v1.1.0.json` (`e9458f71…`):
  `expectedIdenticalToRun1`'s values are redacted in place, but the key is
  still referenced by `target`, `successCondition`, and
  `invalidationCondition` — the redaction was applied to one of the two
  files that carried the values.
- C11 ships **byte-identical** to the registered fixture but at the flattened
  path `fixtures/c11-canonical-digest.json`; the registered path
  `fixtures/v1.1.0/…` does not resolve in the package (their G6, confirmed).
- A first grep for the leak used comma-less values against the v1.0.0-era
  files and found nothing; both errors (wrong format, wrong directory) are
  this run's own and are recorded rather than deleted.

Impact assessment: the one contaminated line is the exhaustive conclusion
distribution (no longer blind for IND-20260807-2). Mitigations, both
verified: the line is derivable from IND-1's *published* output plus R1's
stated rule without the leak (§3.7), and their run recomputes it from the
worlds. The evaluator-conformance claim survives with that qualification
stated; it is not treated as void and not treated as clean.

## 5. Plan of record

1. Import IND-20260807-2 evidence by copy with digests; provenance record
   including the leak trace and package digests.
2. Register v1.2.0: R5.1 receipt object (member list, types, exact
   `schema`/`reason`/`limits` values, sorted root lists,
   margin/conversionsToReverse formulas, no-extra-members rule, and the
   deliberate decision that the digest covers every unsigned member);
   R5.2 margin = absolute (decision; signed rejected and recorded; the
   independent implementation's signed choice was defensible). C11 re-pinned
   under `fixtures/v1.2.0/` with the full canonical unsigned string in
   `expected`; new C12 pins the margin sign on a strict-minority world.
   Registered prediction: counts, conclusion distribution, and C11's digest
   all unchanged.
3. Acknowledge in the v1.2.0 record: G1 (v1.1.0's rule-6/openFindings
   self-contradiction), G5 (`conclusionFunction` closed F6/F7 beyond the
   listed R1–R4), G6 (reinstate F15 and I9-zero-exercise in openFindings).
   G4's recommended I12 is recorded as the leading v1.3.0 candidate, not
   implemented — the owner's repair list for this version is exactly R5.1
   and R5.2.
4. Re-run in full; compare; close with the packet.

## 6. Scope refusals

- No I12 invariant this version (G4) — owner's list is two repairs.
- No execution of IND-20260807-3 and no edits under `kl000-independent-spec/`
  or `kl000-v110-spec/` — the next gate is a separate commission.
- No promotion; registry and canonical records untouched.
