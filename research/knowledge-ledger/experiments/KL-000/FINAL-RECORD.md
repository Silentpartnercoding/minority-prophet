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
