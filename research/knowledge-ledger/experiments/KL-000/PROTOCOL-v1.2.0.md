# KL-000: dual-ledger conformance — protocol v1.2.0

Status: **preregistered.** This document and `preregistration-v1.2.0.json` are
committed before the v1.2.0 confirmatory re-run is executed and before any of
its outcomes are inspected.

## Relationship to prior versions

v1.2.0 is a **new registration, not an edit**. v1.0.0 (`PROTOCOL.md`,
`preregistration.json`, `fixtures/c01…c10`) and v1.1.0 (`PROTOCOL-v1.1.0.md`,
`preregistration-v1.1.0.json`, `fixtures/v1.1.0/`) are preserved byte-for-byte
and continue to govern their own results: RUN-20260807-1, RUN-20260807-2,
IND-20260807-1 and IND-20260807-2 are not reinterpreted by this document.

**The evaluator under test is unchanged**: `knowledge_ledger/transaction.py`
at `sha256:15dfd50051ef5da3db13d8e591f58537325ee50aa4e3573914f86e4ff3a3e21f`,
the same bytes frozen by v1.0.0. v1.2.0 changes specification text only.

## Why v1.2.0 exists

IND-20260807-2 — the independent implementation's re-run against v1.1.0 —
established **genuine cross-implementation conformance on the evaluator and
the conclusion function**: identical exhaustive partitioning and an identical
conclusion distribution (present 41,820 / supported 19,380 / not_established
49,480 / absent 160), closing the 22,440-world divergence that motivated
v1.1.0. R1 was the fix. (Qualified by the commission-package leak recorded in
`results/independent/PROVENANCE-IND-20260807-2.md`; the agreement line is
independently derivable and was recomputed from the worlds.)

What did **not** reproduce is C11's pinned digest, and the implementer's
diagnosis is verified and adopted: **not a codec defect** — its canonical
bytes round-trip byte-identically through this protocol's own stated
realisation — but a specification gap. R4 defined the canonical *form* and
the digest *scope* while never defining the receipt *object*: 279 of the 703
bytes C11 hashes are the values of `schema`, `reason` and `limits`, which no
v1.1.0 document states (finding G2). I4 and I6 therefore remain untested
across implementations. v1.2.0 repairs exactly that, plus the margin-sign
contradiction (finding G1) that v1.1.0 carried unresolved.

## The two repairs

### R5.1 — the receipt object is registered (repairs finding G2)

A digest is a function of a codec and an object; v1.1.0 registered only the
codec. v1.2.0 registers the object. The complete, closed member list — **a
conforming receipt has exactly these nine top-level members and no others**
(a receipt carrying anything else, e.g. `receiptVersion`, does not conform):

| member | type | value |
|---|---|---|
| `schema` | string | constant: `minority-prophet.knowledge-transaction.v0.1` |
| `transactionId` | string | echoed verbatim from the input |
| `claim` | object | exactly `{type, proposition}`, both echoed verbatim from the input |
| `search` | object | exactly `{declared, searched, unavailable, complete}`: three non-negative integers per I8 and one boolean |
| `evidence` | object | exactly `{records, distinctRoots, repeatedRecordsCollapsed, supportingRoots, opposingRoots, margin, conversionsToReverse}` — see below |
| `conclusion` | string | one of `present`, `supported`, `not_established`, `absent_within_declared_scope`, per `conclusionFunction` |
| `reason` | string | exactly one of the four registered reason strings — see below |
| `limits` | array | constant, exactly two strings — see below |
| `contentDigest` | string | `sha256:` + 64 lowercase hex, per `canonicalForm.digestScope` |

**`evidence` in full.** `records`, `distinctRoots`, `repeatedRecordsCollapsed`
are non-negative integers per I10. `supportingRoots` and `opposingRoots` are
arrays of distinct rootId strings **sorted ascending by Unicode code point**
(this sortedness is what makes I7's digest stability possible and was never
registered before). `margin` is a non-negative integer, defined in R5.2.
`conversionsToReverse` is a positive integer:
`floor(margin / 2) + 1` when `margin > 0`, and `1` when `margin == 0`.

**The four `reason` strings**, exact and exhaustive:

| branch | string |
|---|---|
| absence claim, ≥1 opposing root | `At least one distinct counterexample root was recorded.` |
| absence claim, no opposing root, coverage complete | `Every declared location was searched and no counterexample root was recorded.` |
| absence claim, otherwise | `The declared search space was not exhaustively searched.` |
| presence claim (always) | `The conclusion follows only from the declared root counts.` |

**`limits`**, constant:

```
["Root identity and independence are declared operationally, not proved semantically.",
 "This result applies only to the declared search space."]
```

**Digest coverage — the deliberate decision.** Everything a digest covers must
be specified or excluded; v1.2.0 **specifies everything and excludes
nothing**: the digest covers all nine non-`contentDigest` members, including
`schema`, `reason` and `limits`. The alternative — shrinking the digest scope
to the five members v1.1.0 happened to pin — was rejected because it would
leave the receipt's human-facing fields (`reason`, `limits`) tamperable
without digest failure, which is precisely what I6 exists to prevent.

**Sub-decisions this registration necessarily makes** (stated per the G5
lesson — no silent repairs): registering `conversionsToReverse`'s formula
decides open finding **F4** in favour of the reference's existing behaviour,
including the empty-ledger value `1` that IND-20260807-1 argued is
questionable (a conversion cannot reverse an empty ledger; an addition can) —
that objection is preserved, and the value is registered as-is for
compatibility with every receipt both implementations have ever emitted.
Registering the sorted order of the root lists, and `claim` as a verbatim
echo, likewise turns previously implicit reference behaviour into
specification.

### R5.2 — `margin` is the absolute difference (repairs finding G1) — DECISION

**`margin = |count(supportingRoots) − count(opposingRoots)|`. It is never
negative.** `canonicalForm.numbers`' assertion that receipts contain only
non-negative integers is therefore true, with no other change.

This is a **decision, not a derivation**, of the same kind as R1's tie rule,
and it could defensibly have gone the other way. The rejected reading —
signed margin, `count(supporting) − count(opposing)` — carries strictly more
information (which side leads), and the independent implementation chose it
in IND-20260807-1; that choice was defensible and is preserved in its
FINDINGS.md (F5). It was rejected here because: the reference has emitted
absolute margins in every receipt of every run (verified: zero negative
margins across all 110,840 exhaustive receipts); the sign it would add is
recoverable from the two root lists the receipt already carries; and signed
margins would require `canonicalForm.numbers` to define negative-integer
serialisation and would leave 38,760 exhaustive receipts (35.0%) — 82,830
randomized on the independent implementation's stream — with a canonical form
dependent on that new rule.

This closes open finding **F5** and resolves the self-contradiction
IND-20260807-2's G1 identified in v1.1.0: `canonicalForm.numbers` asserted a
property only the absolute reading has, three sections after `openFindings`
listed the sign as open and one section after C11 was declared sign-agnostic
so as not to resolve it. Both statements could not hold; v1.2.0 decides.
C11's sign-agnosticism is now moot as a guard (the ambiguity it protected is
closed) and **C12** pins the decision on a strict-minority world — the
distinguishing case C11 was built to avoid.

## Corrections to the v1.1.0 record, acknowledged

- **G5 — v1.1.0's repair list was incomplete as claimed.** v1.1.0 said its
  repairs were "exactly R1–R4", but its `conclusionFunction` also closed the
  independent implementation's ambiguities A1/finding F7 (absence gates on
  coverage alone; 4 worlds) and A2/finding F6 (presence has no coverage term;
  19,152 worlds) without listing either. Both implementations already read
  those clauses the same way, so no number moved between these two — but the
  documentation-only claim is weaker against an arbitrary third
  implementation, which could move 19,152 worlds on adopting v1.1.0
  attributable to no listed repair. Recorded here rather than repeated: this
  document's sub-decision list above is exhaustive to the best ability of
  its authors, and the re-run tests it.
- **G6 — two findings fell out of v1.1.0's openFindings and are reinstated**
  in v1.2.0's: F15 (the exhaustive phase exercises conclusion logic on 63% of
  what it enumerates — a reporting-completeness point) and the I9 coverage
  fact (I9 is exercised by zero fixture, exhaustive, or randomized worlds —
  its entire evidence is the adversarial suite; unchanged across all four
  runs to date). The v1.1.0 uncertainty wording "eight of the invariants" is
  corrected: ten invariants are exercised on receipt-producing worlds, I3 on
  all worlds, I9 on none outside the adversarial phase.
- **G4 — recorded, deliberately not repaired this version.** The conclusion
  function still has no enforcing invariant: an evaluator with the inverted
  (existential) presence reading changes 22,440 conclusions, violates zero of
  the eleven invariants, and is caught only by C11 (verified by this
  repository against the full enumeration). The implementer's recommended
  I12 — `conclusion` equals `conclusionFunction` applied to the world — is
  the leading candidate for v1.3.0. It is not added here because this
  version's owner-directed repair list is exactly R5.1 and R5.2, and R1's
  precedent shows what silent scope growth costs.

## Phases

As v1.1.0, with the fixture phase extended:

1. **Fixture.** C01–C10 (v1.0.0, unchanged), C11 **re-registered from
   `fixtures/v1.2.0/`** — input byte-identical to v1.1.0's C11; `expected`
   now carries the values of `schema`, `reason` and `limits` and the complete
   canonical unsigned form (703 bytes), so a digest mismatch localises to
   bytes rather than a bare hash inequality — and **C12** (margin-sign pin,
   `fixtures/v1.2.0/c12-margin-sign.json`, expected digest
   `sha256:61000a9b978222ce227601621167d8d66109ba2a0fea13f6431f7830b0aa3b6e`,
   canonical unsigned form 691 bytes).
2. **Exhaustive-small**, 3. **Randomized**, 4. **Adversarial** — identical to
   v1.1.0 in every bound, seed, and attack, plus the twelve controls above.

Baselines B1–B5 exactly as before, full exhaustive set, same checker.

## Preregistered prediction

Because both repairs register serialisation-level facts the reference already
exhibits, **nothing may move**, including the digest:

| Quantity | Required value |
|---|---|
| exhaustive worlds / receipts / fail-closed / violations | 176,120 / 110,840 / 65,280 / 0 |
| exhaustive conclusions (absent / not_established / present / supported) | 160 / 49,480 / 41,820 / 19,380 |
| randomized worlds / violations | 1,000,000 / 0 |
| randomized receipts / fail-closed | 243,381 / 756,619 |
| baseline violations B1 / B2 / B3 / B4 | 634,440 / 26,880 / 26,208 / 189,720 |
| **C11 `contentDigest`** | **unchanged**: `sha256:84e63c21271a19c3bfbb1d42c5ce61e60288456a48c33829a66ae916bc33eafe` |
| fail-closed causes | exactly one per phase: `ValueError: One root cannot support opposing sides.` |

C11's digest not moving is itself a registered claim: the receipt object
v1.2.0 registers is exactly the object the reference has emitted since
v1.0.0. Had R5.2 chosen signed margins, or R5.1 altered the member set, the
pin would move — the prompt for this run anticipated that possibility; the
registered decision forecloses it, and the re-run tests the foreclosure. A
moved **count or conclusion** means a repair changed evaluation rather than
serialisation: the run halts and the deviation is the finding.

**Packaging note (constraint LEAK-101).** This table is scientifically
necessary here and must **never ship in a commission package**: the v1.1.0
package leaked every screened value through exactly this table in
`PROTOCOL.md`, defeating a redaction correctly applied to the
preregistration. Any future package derives from the registration by
removing this section and the `expectedIdenticalToRun1` block, and the
screening grep runs against **every file shipped**, in both comma and
comma-less formats.

## Stop, failure, and invalidation

All v1.1.0 conditions carry over. The prediction table above is an
invalidation condition as in v1.1.0: any deviation marks the run incomplete
and is reported as a finding. I11 remains a hard invariant; C11 and C12
digest mismatches are fixture failures.

## What v1.2.0 does not repair, deliberately

Open, with the independent implementer's recommended repairs on record:
**F1/F2** (receipt-internal I2/I5; B2 does not fail literal I2 — measured),
**F3** (B2≡B3), **F11** (no cross-implementation randomized stream; the
implementer's `worldStreamHash` is the candidate repair), **F12** (the
adversarial phase is defined by reference to a test file), **F13** (C06's
note contradicts C04/C07), **F14** (`unavailable` is inert), **F15**
(reinstated), **I9's zero non-adversarial exercise** (reinstated), and
**G4/I12** (conclusion-function enforcement — leading v1.3.0 candidate).

## What a pass licenses, and does not

**Established already, and not by this run:** cross-implementation
conformance of the evaluator and the conclusion function, by two independent
implementations (IND-20260807-2, qualified per the provenance record).

**A v1.2.0 pass adds:** the receipt object and margin sign as registered,
byte-compatible specification — no number and no digest moved.

**Still not established, and untestable until IND-20260807-3:** I4 and I6
across implementations. A digest has never reproduced between
implementations; C11 under v1.2.0 is the first pin whose every hashed byte
is registered, which makes cross-implementation digest agreement *possible*,
not actual. If IND-20260807-3 reproduces C11's digest, deterministic replay
and digest integrity become cross-implementation properties for the first
time; until then they are per-implementation only. The randomized phase
remains a replication (F11). "Verified" remains unlicensed.

## Safety boundary

Unchanged from v1.0.0/v1.1.0.

## Amendment log

| # | When | Change | Experimental content affected |
|---|---|---|---|
| 1 | after registration commit `7e9e55fb`, **before** any confirmatory phase was executed; self-caught by the registering run while validating the commit | The member-count prose above read "ten top-level members" while the list beneath it — and the authoritative `receiptObject.memberList` in the preregistration — has **nine** (`schema`, `transactionId`, `claim`, `search`, `evidence`, `conclusion`, `reason`, `limits`, `contentDigest`). Corrected to "nine" here. The same miscount appears in `preregistration-v1.2.0.json`'s `repairs[0].statement` prose and in the registration commit message; **both are left as committed** — the preregistration is never edited after registration, and its machine-readable `memberList` (nine entries) is the registered authority the prose contradicts. Recorded rather than smoothed over. | **None.** No member was added or removed; the list itself was always nine in both documents. |

## `protocolCommit` remains null

Same mechanics as prior versions; sidecar `PROTOCOL-COMMIT-v1.2.0.txt`:

```bash
P=research/knowledge-ledger/experiments/KL-000
test "$(git log -1 --format=%H -- $P/preregistration-v1.2.0.json)" \
   = "$(cat $P/PROTOCOL-COMMIT-v1.2.0.txt)" && echo "unedited since registration"
```
