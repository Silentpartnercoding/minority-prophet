# KL-000: dual-ledger conformance — protocol v1.3.0

Status: **preregistered.** This document and `preregistration-v1.3.0.json` are
committed before the v1.3.0 confirmatory run executes and before any outcome
is inspected.

## Why this version exists, and why after the program closed

The program closed at RUN-20260807-4 with one committed gate outstanding:
`v1.3.0-I12-decision-enforcement`, promoted from candidate to gate by owner
direction precisely so that closure could not silently retire it. This
registration pays that gate, on owner direction, and nothing else: the
program reopened deliberately for it (RUN-20260807-5) and closes again after
it. v1.0.0, v1.1.0 and v1.2.0 are preserved byte-for-byte.

The gate's evidence, measured in both implementations before this
registration existed: an evaluator with either owner decision inverted —
R1's tie rule or R5.2's absolute margin — passed **all eleven** registered
invariants over the complete 176,120-world enumeration, changing 22,440 and
38,760 receipts respectively, caught only by pinned fixtures (R5.2's entire
detection surface was one world). The program's decisions were prose with
fixtures behind them. I12 makes them checkable.

## The one repair

### R6 — I12, decision enforcement (hard invariant)

For every receipt-producing world:

```
conclusion == conclusionFunction(world)          computed from the WORLD
margin     == abs(|supportingRoots| − |opposingRoots|)   likewise
```

Both quantities derive from the world's ledgers, never from receipt fields —
the world-referential form that F1/F2 showed the receipt-internal invariants
lack. I12 subsumes I2's and I5's conclusion clauses (their registered
statements are carried verbatim; their receipt-internal defect remains open
as F1/F2). It is skipped where no receipt exists, emits **at most one
violation per world** (detail naming conclusion, margin, or both), and its
content is a derivation from the registered `conclusionFunction` and R5.2 —
unlike R1 and R5.2 themselves, nothing here could defensibly have gone
another way.

**Positive controls: the two registered decision ablations**, replacing
fixture-coincidence with measurement. Each is B5 with one decision inverted
and nothing else, run over the full enumeration through the same checker
that clears B5, **with no fixture consulted anywhere in the phase**:

| Ablation | Must fail I12 on exactly | Other invariants |
|---|---|---|
| ABL-R1 — ties/minorities conclude `supported` | **22,440** worlds | 0 |
| ABL-R52 — margin signed | **38,760** worlds | 0 |

The counts are prior measurements (IND-20260807-3 both; reference-side
reproductions in RUN-3 and RUN-4), registered as exact-match pass
conditions. **A different caught-count in either direction means I12 is
wrong, not the measurement: the run halts and reports rather than adjusts.**

**Baseline continuity.** B1–B4's registered totals are sums over I1–I11 and
remain the preserved, cross-version-comparable power metric — they must not
move. Their I12 counts are reported **separately** (`i12Violations`), as new
information: folding them in would move every total, since all four
baselines' conclusion distributions differ from the reference's. I12's power
is established by the two ablations at exact counts, not by B1–B4.

## Everything else is carried unmodified

Evaluator (same hash since v1.0.0 — I12 changes the *checker*, not the
evaluator), bounds, seed, canonical form, receipt object, fixture set
C01–C12 (byte-identical, both pinned digests unchanged), conclusionFunction
text (now enforced rather than merely registered). **A1 and A2 remain
undecided owner decisions** (4 and 19,152 worlds, STATUS `permanentLimits`);
I12 enforces the registered text as written without deciding them.

## Preregistered prediction

This is an enforcement change, not a semantics change. Everything must be
unchanged:

| Quantity | Required value |
|---|---|
| exhaustive worlds / receipts / fail-closed / violations | 176,120 / 110,840 / 65,280 / 0 |
| exhaustive conclusions (absent / not_established / present / supported) | 160 / 49,480 / 41,820 / 19,380 |
| randomized worlds / violations; receipts / fail-closed | 1,000,000 / 0; 243,381 / 756,619 |
| baseline preserved totals B1 / B2 / B3 / B4 (I1–I11) | 634,440 / 26,880 / 26,208 / 189,720 |
| C11 / C12 digests | unchanged: `sha256:84e63c21…33eafe`, `sha256:61000a9b…aa3b6e` |
| ablation catches (I12 only) | ABL-R1 exactly 22,440; ABL-R52 exactly 38,760 |
| B5 I12 violations | 0, in every phase |
| fail-closed causes | exactly one per phase |

A moved value means I12 changed evaluation rather than enforcing it — halt
and report as the primary finding.

**Packaging note (LEAK-101/LEAK-102, binding):** this table and
`expectedIdenticalToRun1` never ship in a commission package; any future
package also withholds the conclusion distribution and is screened per file
in both number formats, with a digest manifest.

## Stop, failure, and invalidation

All prior conditions carry over. New: either ablation caught at a count
other than its registered value invalidates the run (in either direction);
any non-I12 violation by an ablation is a finding; any I12 violation by B5
is failure.

## Claim discipline

**If passed:** the two owner decisions are enforced by an invariant rather
than by two fixtures, with power demonstrated at the exact previously
measured surfaces, and the enforcement change altered nothing the evaluator
does. **Still not licensed:** "verified" in any form; conformance of the
independent implementation to v1.3.0 (it has not run against it); A1/A2
(open); cross-implementation randomized agreement (F11); anything outside
the declared bounds; any part of a knowledge transaction or First
Transmission — the first-transaction gate is **NOT REACHED** and eleven
kernels remain seeded.

## Amendment log

None at registration.

## `protocolCommit` remains null

Sidecar `PROTOCOL-COMMIT-v1.3.0.txt`, same mechanics and check as every
prior version.
