# DRAFT RUN REPORT v1 — RUN-20260807-3

R5: the receipt object registered, the margin sign decided, protocol v1.2.0
passed with nothing moved — counts, conclusions, or bytes. Draft only;
nothing pushed, nothing promoted.

## The headline first

**Two independent implementations now agree exactly on the evaluator and its
complete conclusion function.** IND-20260807-2 (the Rust implementation's
re-run against v1.1.0) reproduced the reference's exhaustive conclusion
distribution value-for-value — present 41,820, supported 19,380,
not_established 49,480, absent 160 — closing the 22,440-world divergence that
motivated v1.1.0. R1 was the fix, and the closure was measured from the
worlds on both sides, not asserted. This is genuine cross-implementation
conformance, recorded as such, with one qualification (the package leak,
below).

**What is still not established:** I4 and I6 across implementations. No
digest has ever reproduced between the two implementations — C11's pin
failed again under v1.1.0, and the implementer's diagnosis (finding G2) is
verified here: not a codec defect, a specification gap. v1.2.0 repairs it.
"Verified" remains unlicensed until a digest reproduces.

## Verification before action — all seven checkable claims held

The implementer's codec was cleared by round-tripping its published 463-byte
canonical form through the protocol's own stated realisation
(byte-identical; its digest recomputes). The reference's receipt members are
exactly the registered nine. Zero negative margins across all 110,840
receipts, 38,760 under the rejected signed reading — both exact. The
703/424/279 byte budget of C11 — 39.7% of hashed bytes unregistered —
recomputed exactly. G4's ablation claim verified against the full
enumeration: an evaluator with the inverted presence reading changes 22,440
conclusions, violates **zero** of the eleven invariants, and is caught by
fixture C11 alone. (This run's first ablation attempt was wrong — a blanket
inversion, catching C01/C02 too — and is preserved in the log with its
correction; both attempts agree on the zero-violations core.)

## LEAK-101 — the v1.1.0 commission package leaked the answers, and the trace runs to the registration

The implementer's §0 disclosure, verified and extended: the v1.1.0 package's
`PROTOCOL.md` — byte-identical to the registered `PROTOCOL-v1.1.0.md` —
carries the preregistered-prediction table, and with it **all eight values
the operator's v1.0.0 screening list was built to withhold**, comma-formatted
(which is one reason a comma-less grep missed them). The redaction was
correctly applied to `preregistration.json` and defeated by the file beside
it. The origin is structural: the prediction table is scientifically
necessary in a registration (it makes the documentation-only claim
falsifiable) and fatal in a commission package, and one file served both
roles.

Impact: the conclusion-distribution agreement line was not blind for
IND-20260807-2. Two mitigations, both verified: the line is derivable from
IND-20260807-1's *published* output plus R1's stated rule
(41,820−22,440 = 19,380; 27,040+22,440 = 49,480), and the implementer's run
recomputes it from the worlds. The conformance claim survives qualified — not
void, not clean. The delivered package (`kl000-v110-spec/`, digests recorded)
also shipped C11 at a flattened path the registration does not name (G6),
and the operator preserved the original v1.0.0 package unmodified beside it,
which is what made the trace possible.

## The two repairs of v1.2.0

**R5.1 — the receipt object is registered** (repairs G2). The closed
nine-member list with types; exact values for `schema`, `reason` (all four
branch strings) and `limits`; sorted root lists; the `conversionsToReverse`
formula — and the deliberate decision that the digest covers **all nine**
unsigned members rather than excluding the newly registered three.
Sub-decisions are called out per the G5 lesson: registering the formula
decides open finding F4 as-is, with the implementer's empty-ledger objection
preserved. C11 is re-pinned under `fixtures/v1.2.0/` with its complete
703-byte canonical string in `expected`, so any future digest mismatch
localises to a byte offset rather than a bare hash inequality.

**R5.2 — margin is the absolute difference** (repairs G1). A decision, not a
derivation, and recorded as one: the signed reading was the independent
implementation's defensible choice and carries more information; it was
rejected because the reference has emitted absolute margins in every receipt
of every run, the sign is recoverable from the root lists, and signed margins
would strip 38,760 exhaustive receipts of a defined canonical form under the
numbers clause. This resolves v1.1.0's self-contradiction (its numbers clause
asserted what its openFindings listed as open) and closes F5. New fixture
**C12** pins the decision on a strict-minority world — the exact case C11 was
built to avoid.

**Registration hygiene event, self-caught:** the registered protocol prose
said "ten top-level members" over a nine-entry list. Corrected as
**Amendment 1** before any execution; the preregistration was *not* edited —
its authoritative `memberList` was always correct and its prose error stays
on record, per the immutability discipline. Both sidecar chains verify.

## The re-run: everything identical, including the bytes

Registered prediction: nothing moves, *including C11's digest* — because the
object v1.2.0 registers is exactly what the reference has emitted since
v1.0.0. Observed (`kl000-confirmatory-v1.2.0.json`, result `passed`, zero
invalidation reasons):

```
fixtures     12/12 — C11 digest UNCHANGED (sha256:84e63c21…33eafe), C12 passes (sha256:61000a9b…aa3b6e)
exhaustive   176,120 / 110,840 / 65,280 / 0    conclusions 160 / 49,480 / 41,820 / 19,380
randomized   1,000,000 / 243,381 / 756,619 / 0
baselines    B1 634,440   B2 26,880   B3 26,208   B4 189,720   all caught
```

74 repo + 80 KL-000 tests pass (12 new). All three registration chains
verify. Comparison log: `logs/v120-comparison.txt`.

**What C11 passing here does and does not show** (owner correction, adopted):
C11's pin was computed *from the reference*, so the reference reproducing it
is true **by construction** — the same self-referential structure the
implementer identified in v1.0.0's I4/I6, one level up. It is not
cross-implementation evidence. What v1.2.0 established is that the digest is
now **computable** by an independent implementation — every hashed byte is
registered — not that it **agrees**. Only IND-20260807-3 can establish
agreement. The registered prediction this run's re-run did test is narrower
and real: that registering the receipt object changed nothing the reference
emits (no count, conclusion, or byte moved).

## Findings this run opens or carries

- **LEAK-101** (high, above) — packaging and registration have structurally
  conflicting requirements; remediation registered in v1.2.0 itself and in
  the next-gate packaging instructions.
- **G4 / SPEC-110** (open, verified) — the conclusion function has no
  enforcing invariant; its entire detection surface is one fixture (one
  input out of 176,120, where I12 would cover all 22,440 divergent worlds).
  By owner direction at close, I12 (`conclusion == conclusionFunction(world)`)
  is recorded as a **committed v1.3.0 gate with its evidence attached**
  (STATUS `committedGates`), not a candidate — a deferred gate and an
  optional idea must not look the same in the record. Deferring the *work*
  behind IND-20260807-3 stands: mixing a new invariant into a
  serialisation-only repair would have destroyed the did-evaluation-move
  test that made v1.2.0 verifiable.
- **G5 / SPEC-111** (recorded) — v1.1.0's "repairs are exactly R1–R4" was
  false: `conclusionFunction` silently closed F6/F7 (19,152 + 4 worlds).
  v1.2.0's sub-decision list is exhaustive to its authors' best ability, and
  the re-run tests it.
- **G6 / REC-102** — F15 and the I9-coverage fact fell out of v1.1.0's
  openFindings and are reinstated; the "eight invariants" uncertainty wording
  corrected.

## Commits of this run

| SHA | What |
|---|---|
| `2f81b9e` | run open: verification of all seven IND-20260807-2 claims; leak traced |
| `d51ead6` | IND-20260807-2 evidence imported with provenance and conformance record |
| `7e9e55f` | **registration commit** — protocol v1.2.0, preregistration, C11 re-pin + C12 |
| `461bfbf` | Amendment 1 (member count, pre-execution) + sidecar |
| `bc67075` | execution support + 12 permanent tests |
| `a7f4d37` | **result commit** — v1.2.0 confirmatory, passed, nothing moved |
| `d29904b` | STATUS: next gate IND-20260807-3 |
| *(packet)* | this closing packet |

## What this licenses, and does not

KL-000 remains `adversarial-passed` under all three protocol versions.
Newly claimable (qualified): cross-implementation conformance of the
evaluator and the conclusion function. Not claimable: `verified-independent`
— that word waits on IND-20260807-3, the first run in this program's history
with a genuine chance of reproducing a digest across implementations,
because v1.2.0 is the first registration under which every hashed byte is
specified. That commission is the owner's; its packaging instructions
(screen every file, both number formats, no prediction tables, resolvable
paths) are registered in v1.2.0 and in STATUS. Nothing is promoted; no
First Transmission language applies.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
