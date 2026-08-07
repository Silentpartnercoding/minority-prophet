# KL-000 — final record

Written at the close of RUN-20260807-4, the last run of the program. This
document consolidates what four repository runs (RUN-20260807-1..4), three
independent runs (IND-20260807-1..3), and three protocol versions
established, at the strength it actually holds. It supersedes nothing;
every underlying artifact remains in place and governs itself.

## What is established

**The evaluator, the conclusion function, and the canonical form agree
across two independent implementations in different languages with no shared
code.** The reference is 100 lines of Python; the independent implementation
is zero-dependency Rust with hand-written JSON, SHA-256 and PRNG, whose
author states — and whose three findings documents are consistent with —
never having located or read the reference.

At full strength, by object (methodology note M17):

| Object | Strength | Evidence |
|---|---|---|
| Exhaustive enumeration and partitioning | agreement on the identical 176,120-world set, independently derived: 110,840 receipts / 65,280 fail-closed, one cause, both sides | IND-1 onward |
| Conclusion function | agreement on the complete distribution, 160 / 49,480 / 41,820 / 19,380, across the full enumeration | IND-2, after v1.1.0 R1 decided the tie rule; the implementations demonstrably disagreed on 22,440 worlds under v1.0.0 |
| Canonical form and digests (I4/I6) | **agreement for two pinned receipts** — C11 (703 bytes) and C12 (691 bytes), canonical forms byte-identical, digests equal — **not for all 110,840** | IND-3, after v1.2.0 R5.1 registered the receipt object |
| Hard invariants | zero violations, every registered invariant, every run, both implementations; checker power shown against four ablated baselines throughout | all runs |
| Specification repairs | behaviour-preserving, proven by exact-equality prediction tables: across three protocol versions no count, no conclusion, and no pinned digest ever moved | RUN-2, RUN-3, and both IND re-runs |
| Randomized phase | **replication only, never reproduction** — the frozen seed fixes no cross-implementation stream (F11, permanent unless a stream is registered) | all runs |

**Qualification that travels with the claim (LEAK-101):** the v1.1.0
commission package leaked the expected counts — including the conclusion
distribution — through the registered protocol's own prediction table, so
IND-2's distribution-agreement line was not blind. Mitigations, verified:
the line is derivable from IND-1's published output plus R1's stated rule,
and both IND runs recompute it from the worlds. **The digest result is
unaffected**: a count gives no path to a hash, and the receipt object whose
bytes the digests cover was registered after the leaked package. The v1.2.0
package was screened per file, manifested (16/16), and verified clean of all
eight screened values by the implementer and by this repository — with the
recorded caveat (H3) that the conclusion distribution itself still ships and
must be withheld from any *future* implementer's package.

## The mechanistic finding — stated at full strength

**The program's enforcement of its own decisions rests on two pinned inputs,
not on any property that holds across the enumeration.**

IND-3 corrupted each owner decision in isolation and ran the full checker
over the complete enumeration; the reference side reproduced both
measurements exactly:

| Ablation | Receipts changed | Invariant violations (13 checks, both implementations) | Caught by |
|---|---|---|---|
| R1 inverted — ties conclude `supported` | 22,440 | **0** | C11, C12 |
| R5.2 inverted — margin signed | 38,760 | **0** | **C12 only** |

An evaluator that gets either owner decision backwards passes every
registered invariant over 176,120 enumerated and 1,000,000 randomized
worlds. The registered `conclusionFunction` and `receiptObject` are prose
with fixtures behind them; had C11 and C12 not happened to pin receipts that
exercise these rules, nothing in the program would notice the rules
breaking. This sits **beside** the passing result, not behind it: what the
reproduction demonstrated is that both implementations follow the same
registered prose, not that any test would notice if one stopped.

The committed repair is **I12** (`conclusion == conclusionFunction(world)`
and `margin == abs(|S|−|O|)`) — a committed v1.3.0 gate with both ablations
as its evidence and an exact pass condition (STATUS `committedGates`),
owner's to schedule. Contrast R3, which made its rule invariant I11
precisely so it would be checked; R1 and R5.2 got fixtures.

## What the program did not decide

Recorded per owner instruction, decided by no one (STATUS
`permanentLimits`):

- **A1 — does absence need supporting evidence?** Registered text says
  coverage alone suffices; 4 worlds hang on it — the loudest receipts the
  schema can emit (bounded absence with an empty evidence ledger).
- **A2 — does presence need complete coverage?** Registered text has no
  coverage term; **19,152 worlds (17.3% of receipts)** hang on it. A third
  implementation reading it the other way would diverge on all of them while
  passing every invariant. This is an owner decision the program did not
  reach; both readings are preserved with their consequences.

Also on record, undecided: the margin-collision observation (registered
fixtures C01 — unopposed support — and C12 — outnumbered two to one — carry
identical `margin` and `conversionsToReverse`; the implementer recommends a
digest-moving v1.3.0 rename, not a reversal of R5.2).

## What is not established, plainly

- **"Verified" in any form.** A passing cross-implementation reproduction is
  not `verified-independent` while the program's own decisions are
  unenforced. KL-000's final state is `adversarial-passed`.
- Canonical-form agreement beyond the two pinned receipts.
- Cross-implementation randomized agreement (F11, permanent as registered).
- That the dual ledger recovers truth; that declared rootIds are genuinely
  independent (ADV-001..007 all stand, including the under-declared search
  space, root minting, and the unrepresentable shared dependency); that any
  invariant holds outside the declared bounds; that any real-world evidence
  process is improved.
- **Any part of a knowledge transaction, cross-system result, Candidate
  First Transmission, or First Transmission. The first-transaction gate is
  NOT REACHED**, exactly as RUN-20260807-1 first recorded — KL-000 was the
  precondition for attempting KL-011, and KL-011 remains seeded with its
  prerequisites now substantively met but unexecuted and unregistered.

## Open ledger

Every open finding, with its home: F1/F2/F3 (receipt-internal invariants,
baseline dedup, missing B6 control), F11 (stream registration or permanent
replication-only status), F12 (adversarial phase unreproducible from the
protocol), F13 (C06's wrong note, carried as registered), F14 (`unavailable`
inert), F15 and I9-coverage (63% conclusion coverage of the enumeration; I9
exercised by zero non-adversarial worlds in every run), H1 (four
self-miscounts, protocol site corrected by Amendment 2, preregistration
sites preserved as committed), H3 (distribution must be withheld from any
future package), the IND-3 result-artifact header defect, and the
implementer's eight-item list of what it would do next
(`results/independent/FINDINGS-v120.md` §7) — including the one condition
never met in three runs: an implementer on a machine that does not hold the
reference, so that abstention is enforced rather than reported.

Eleven kernels (KL-001..KL-011) remain seeded with exact next gates, none
advanced, audited at close (RUN-20260807-4 `logs/kernel-audit.txt`).

*A final report that records an unenforced decision and an undecided
ambiguity is worth more than one that reads as completion. This is that
report.*

---

# Addendum — RUN-20260807-5: the committed gate is paid

Everything above is the record as written at RUN-20260807-4's close and is
preserved unmodified. This addendum records what changed afterwards and why
the record now says something different.

## What happened

The program was reopened deliberately, on owner direction, for exactly the
one committed gate — `v1.3.0-I12-decision-enforcement` — and closed again.
Protocol v1.3.0 registered and implemented **I12** as a hard invariant:
`conclusion == conclusionFunction(world)` and
`margin == abs(|supportingRoots| − |opposingRoots|)`, both computed from the
world and never from receipt fields, at most one violation per world.

The registered pass condition was met **exactly**:

| Ablation | Caught by I12 on | Other invariants | Fixture involved |
|---|---|---|---|
| ABL-R1 (ties conclude `supported`) | **exactly 22,440** worlds | 0 | none |
| ABL-R52 (margin signed) | **exactly 38,760** worlds | 0 | none |

B5 recorded zero I12 violations in every phase, and nothing else moved — no
count, no conclusion, no baseline preserved total, and neither pinned digest
(the full run re-verified all of them). New reported-only information:
baseline I12 counts (B1 57,120 / B2 13,440 / B3 13,108 / B4 57,120), beside
the preserved I1–I11 totals, not folded in.

## How this changes the mechanistic finding

The headline of the close-out above — *"the program's enforcement of its own
decisions rests on two pinned inputs, not on any property that holds across
the enumeration"* — **was true through v1.2.0 and is now repaired.** Both
owner decisions are enforced by an invariant with demonstrated power at the
exact surfaces where the fixtures used to be the only defence. The finding
is retained above as history because it explains why v1.3.0 exists and why
the state never advanced on the strength of a passing reproduction alone.

## What this does not change

- **The state.** KL-000 remains `adversarial-passed`. `verified-independent`
  is an owner promotion decision; the independent implementation's checker
  is its own and has not run against v1.3.0. Its v1.2.0 conformance evidence
  is undisturbed — I12 changed the checker, and nothing the evaluator does
  moved — but enforcement on its side is its own choice to make.
- **A1 and A2.** Still undecided owner decisions (4 and 19,152 worlds), by
  explicit instruction. I12 enforces the registered text as written without
  deciding them.
- **The qualifications.** LEAK-101 travels with the conformance claim as
  before; the canonical form is confirmed for two pinned receipts, not all
  110,840; the randomized phase is a permanent replication (F11); the open
  ledger above stands, minus G4/H2.
- **The boundary.** The first-transaction gate is **NOT REACHED**. Eleven
  kernels remain seeded with exact next gates. No promotion has occurred.

The program is closed again, with no committed gate outstanding.

