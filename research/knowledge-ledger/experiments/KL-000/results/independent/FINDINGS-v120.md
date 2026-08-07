# KL-000 v1.2.0 — final independent run: results and findings

**Run identifier: IND-20260807-3.** The last independent run; there is no IND-4.
Predecessors: **IND-20260807-2** (v1.1.0, `FINDINGS-v110.md`) and
**IND-20260807-1** (v1.0.0, `FINDINGS.md`, named retroactively). Same Rust
implementation throughout, updated in place three times, never rewritten. The
reference implementation was not located, opened, or read in any of the three
runs.

**Status: `passed`.** Every registered success condition met.

---

## 1. The two verdicts that decide this run

### C11 — MATCHES

```
pinned    sha256:84e63c21271a19c3bfbb1d42c5ce61e60288456a48c33829a66ae916bc33eafe
computed  sha256:84e63c21271a19c3bfbb1d42c5ce61e60288456a48c33829a66ae916bc33eafe
```

Canonical unsigned form: **703 bytes, byte-identical to the pin.** First
differing byte offset: none.

### C12 — MATCHES

```
pinned    sha256:61000a9b978222ce227601621167d8d66109ba2a0fea13f6431f7830b0aa3b6e
computed  sha256:61000a9b978222ce227601621167d8d66109ba2a0fea13f6431f7830b0aa3b6e
```

Canonical unsigned form: **691 bytes, byte-identical to the pin.**

My receipt's top-level members are now exactly the registered nine — `schema`,
`transactionId`, `claim`, `search`, `evidence`, `conclusion`, `reason`, `limits`,
`contentDigest`. `receiptVersion`, which IND-1 and IND-2 emitted and which R5.1
names as an example of a nonconformant extra member, is gone.

**R5.1 worked, and it is the only reason these match.** In IND-20260807-2 my
codec was already byte-identical to the protocol's stated realisation and the
digest still could not be computed, because 279 of C11's 703 bytes were the
values of `schema`, `reason` and `limits` and no document stated them. v1.2.0
registered them. Nothing about my canonicalisation changed; I added three
members with registered values and deleted one non-registered member, and the
703 bytes fell out.

Two things this does and does not show. It **does** show that two
independently-written implementations, one of which has never seen the other,
produce the same 703 and 691 bytes from the same inputs under a specification
that now determines them — the first genuine cross-implementation test of I4 and
I6 in this program, and the answer is agreement. It does **not** show that
either receipt is right; the brief's own point stands, that C11 reproducing on
the reference proves nothing because the pin was computed from it. What is new
is that the pin now reproduces somewhere it was not computed from.

I verified before implementing that both fixtures are internally consistent —
SHA-256 of each pinned canonical string equals its pinned digest, and each string
is a fixed point of the stated realisation. Had they not been, no implementation
could have matched and the fixture would have been the defect.

---

## 2. Counts per phase

| | IND-3 (v1.2.0) | IND-2 (v1.1.0) | moved |
|---|---|---|---|
| **Fixture** | 12 / 12 controls match every registered value | 11 / 11 values, digest missed | C12 added; **digest now matches** |
| **Exhaustive** worlds | 176,120 | 176,120 | — |
| receipt-producing | **110,840** | 110,840 | — |
| fail-closed | **65,280**, one cause | 65,280, one cause | — |
| hard violations | **0** | 0 | — |
| `absent_within_declared_scope` | **160** | 160 | — |
| `not_established` | **49,480** | 49,480 | — |
| `present` | **41,820** | 41,820 | — |
| `supported` | **19,380** | 19,380 | — |
| **Randomized** worlds | 1,000,000 | 1,000,000 | — |
| receipt-producing | **244,091** | 244,091 | — |
| fail-closed | **755,909**, one cause | 755,909, one cause | — |
| hard violations | **0** | 0 | — |
| conclusions | 1,070 / 119,641 / 82,077 / 41,303 | identical | — |
| **Adversarial** | **14 / 14** | 12 / 12 | A13, A14 added |
| **Baselines** B1/B2/B3/B4 | 1,218,240 / 124,280 / 26,880 / 687,480 | identical | — |

Conclusion distribution **160 / 49,480 / 41,820 / 19,380**, as the pass condition
requires. Fail-closed cause is `root_on_both_sides` and nothing else, in both
phases. Seed reproduces a bit-identical stream (`fnv1a64:4dee7326f948b0fe`);
generator inside declared bounds; no unexpected cause. 161 s total.

**R5.1 and R5.2 moved no count of mine either.** Every number above except the
fixture row is identical to IND-20260807-2's. That is the prediction v1.2.0 makes
about itself, tested on the other side of the wall.

**Receipts with no defined canonical form: 0**, down from 38,760 exhaustive and
82,830 randomized in IND-2. This is G1 closing. Under v1.1.0 the specification
asserted receipts hold only non-negative integers while leaving the margin sign
open; a third of my receipts fell in the gap. R5.2 removes it by construction.

Randomized counts remain **not comparable** across implementations (F11, open).

### Coverage

I9 is exercised by **zero** worlds in the fixture, exhaustive and randomized
phases — for the third run running, across 1,176,132 evaluated worlds. Its
entire evidence remains the five schema attacks I wrote. I1 is vacuous on 680
exhaustive and 40,148 randomized worlds (empty evidence ledger, nothing to
duplicate). I11's refusal path is adversarial-only, as registered.

---

## 3. R5.2 — I accept it, and here is one argument the record does not contain

The brief invites a last argument against absolute margin. I have one. It is not
a correctness objection and it does not ask for a reversal; it identifies a cost
that I believe is not yet written down anywhere.

**Absolute margin makes `margin` non-monotonic in the evidence, and collides
opposite worlds onto identical receipts.**

Two *registered fixtures* demonstrate it:

| | supporting roots | opposing roots | `margin` | `conversionsToReverse` |
|---|---|---|---|---|
| **C01** | 1 | 0 | **1** | **1** |
| **C12** | 1 | 2 | **1** | **1** |

C01 is a claim with unopposed support. C12 is a claim outnumbered two-to-one.
**Their evidence summaries are identical in both scalar fields.** A consumer
ranking receipts by `margin` — which is what a field called *margin* invites —
ranks these equal. Adding a second opposing root to a tied world *raises* margin
from 0 to 1, so mounting opposition reads as a strengthening claim.

The direction is recoverable, from `len(supportingRoots)` vs
`len(opposingRoots)`. So this is not information loss in the receipt as a whole.
It is a scalar whose name asserts a direction it no longer carries, in a document
whose stated purpose is stopping evidence from being read as stronger than it is.
Scope: **38,760 exhaustive receipts (35.0% of all receipts)** report a positive
margin for a claim in the evidential minority.

The record already contains the tie-break that decided this: `canonicalForm.numbers`
requires non-negative integers, and R5.2 makes that true. I note only that the
argument is circular in the direction it was applied — rule 6 was written to
describe existing behaviour and then used to justify it — and that IND-2's G1
offered the other branch (drop "non-negative" from rule 6), which the record
shows was considered and not taken.

**My recommendation is not to reverse R5.2.** Reversing it now would invalidate
C12's pin, reopen G1, and cost more than it buys. The cheap mitigation is a
v1.3.0 naming change — `rootCountGap`, or an added `majoritySide` member — which
would change digests and so must be versioned deliberately. Recorded here so the
close-out can decide, rather than rediscovered by whoever first compares a C01
receipt with a C12 receipt.

---

## 4. What v1.2.0 introduced

### H1 — the digest-coverage count is still off by one, in the sentence the correction produced

PROTOCOL.md's amendment log self-caught "ten top-level members" and corrected it
to nine, and left the same miscount in `preregistration.json` deliberately and on
the record. Good handling.

The correction did not reach the neighbouring sentence. `PROTOCOL.md:87`,
`repairs[0].statement`, and `receiptObject.digestCoverage` all say the digest
covers **"all nine non-`contentDigest` members."** There are **eight**: nine
total, minus `contentDigest`. "Nine" is right for the member list and wrong for
the covered count, so the fix propagated the correct word into a place where it
is a different error.

Severity: **document only.** It cannot change a digest, because `memberList` and
`digestScope` are both explicit and machine-readable, and my implementation
hashes eight members to produce the correct 703 and 691 bytes. Confirmed
empirically by §1.

Worth recording anyway, because this program has now miscounted its own
enumerations four times: the operator's leak count (three, then five, then six),
and this. Each was caught by counting from scratch rather than by reading the
previous count. That is the pattern, not the individual errors.

### H2 — R5.2 is enforced by exactly one world, and R1 by two

The same measurement IND-2 ran for R1, extended to R5.2. Each ablation is the
registered rule inverted and *nothing else*, run through the same checker over
the full 176,120-world enumeration:

| decision | receipts the ablation changes | invariant violations detected | fixtures that catch it |
|---|---|---|---|
| **R1** (tie rule) | 22,440 | **0** | C11, C12 |
| **R5.2** (absolute margin) | 38,760 | **0** | **C12 only** |

An evaluator with the margin sign backwards passes all eleven hard invariants
over the complete enumeration and one million randomized worlds. Its entire
detection surface is one world in one fixture — and only because C12 was written.

This is IND-2's G4 unchanged and now doubled: **no invariant constrains
`conclusion`, and none constrains `margin` either.** The registered
`conclusionFunction` and `receiptObject` are prose with fixtures behind them, not
invariants. v1.2.0 says so — it names I12 as the leading v1.3.0 candidate and
deliberately omits it — so this is an acknowledged gap, not a hidden one. I
record the measured size because "deliberately not added" reads differently
against 0 invariant violations and a one-world surface.

Note the asymmetry with R3, which made its rule invariant I11 precisely so it
would be *checked*, and argued the point carefully. R1 and R5.2 got fixtures.

### H3 — the packaging held, and its exemption does not generalise

I verified the package myself. `shasum -a 256 -c MANIFEST.sha256`: **16 / 16 OK**,
and nothing ships outside the manifest. Requirement 4 met and independently
checkable, which is the point of it.

I re-ran the screen in both formats. **All eight of the tuning targets that were
present in the v1.1.0 package are gone** from v1.2.0 — bare and comma-separated.
Requirement 2 held under an adversarial re-check by the party it was written to
protect from.

What still ships: the exhaustive conclusion distribution (41,820 / 19,380 /
49,480 / 160) in PROTOCOL.md and BRIEF.md, and 22,440 / 38,760. The brief
pre-declares these legitimate because they appear in my own published results.
For me that is exactly right and I confirm it: I published all five figures in
IND-20260807-2 before this package existed.

**But the exemption is implementer-specific and the packaging requirement is
not.** A fresh implementer — the "next commission" this packaging exists to
protect — would receive the complete exhaustive conclusion distribution as a
pre-stated target, in a document they must read. The pass condition states it
outright. That is precisely the class of value the screen removes elsewhere.
If a fourth implementation is ever commissioned, the distribution must be
withheld from *its* package or its agreement on those four numbers will measure
nothing. Recorded because it is invisible from inside this run: the leak that
matters is not in what I received but in what the next person would.

### H4 — smaller

- `uncertainty` is now stated over eleven invariants; the v1.1.0 "eight of the
  invariants" wording is fixed. My count: ten exercised on receipt-producing
  worlds, I3 on all worlds, I9 on none.
- Registered fixture paths now resolve (`fixtures/v1.2.0/`), closing G6.
- `baselineIdNote` records the B1–B4 naming mapping in the registration instead
  of in a private comparison script. Correct, and it fixes a real coupling.
- C06's note (F13) is still wrong and still shipped, now explicitly
  carried-as-registered with the error on record. That is the right call for a
  frozen fixture, but note the error is only recorded in `controlsNote`, not in
  the fixture a reader actually opens.

---

## 5. Every open finding I hold, ranked by what it could change

Ranked by blast radius, as requested. "Conclusion" means it could change what a
receipt says; "digest" means it could change bytes; "document" means it cannot
change either.

### Could change a conclusion

| | finding | status | scope |
|---|---|---|---|
| **1** | **G4/H2 — no invariant constrains `conclusion` or `margin`.** Registered rules with fixture-only enforcement. | open, acknowledged; I12 named for v1.3.0 | R1: 22,440 receipts, 2 fixtures. R5.2: 38,760 receipts, **1 fixture** |
| **2** | **F1 — I2's two forms are not equivalent** ("Equivalently" is false). B2, a preregistered must-fail-I2 baseline, records **0** I2a violations and is caught only by I2b and I8. | open since v1.0.0 | 13,440 exhaustive worlds; one of four positive controls |
| **3** | **F2 — I5 has the same receipt-internal defect**, and no baseline has power against it. An evaluator omitting `opposingRoots` satisfies I5 vacuously while burying counterexamples. | open, undemonstrated by any control | unbounded; the invariant is unenforceable as written |
| **4** | **F3 — B2 and B3 are one ablation** unless B2 is read as fabricating its search block. Measured: my B2′ is byte-identical to B3 on all 176,120 worlds. | open | the four positive controls may be three |
| **5** | **F7/A1 — absence with an empty evidence ledger** concludes `absent_within_declared_scope`. Closed by `conclusionFunction` in favour of coverage-alone; I still think a bounded-absence receipt containing no evidence is the loudest thing this schema can emit. | closed by text, unremarked as a repair | 4 exhaustive worlds |

### Could change a digest

| | finding | status | scope |
|---|---|---|---|
| **6** | **§3 — `margin` collides opposite worlds** (C01 and C12 have identical `margin` and `conversionsToReverse`). Fixing it means renaming the field or adding `majoritySide`. | new here; not previously recorded | 38,760 receipts misreport direction; any fix moves every digest |
| **7** | **F4 — `conversionsToReverse` on an empty ledger is 1**, with no root available to convert. Registered as-is by R5.1 with my objection preserved. | decided against me, explicitly | 680 exhaustive receipts |

### Document only

| | finding | status |
|---|---|---|
| **8** | **H1 — "all nine non-contentDigest members"**; there are eight. Three places. | new here |
| **9** | **H3 — the conclusion distribution ships in v1.2.0** and would be a live tuning target for a fresh implementer. | new here; forward-looking |
| **10** | **F11 — the frozen seed freezes no cross-implementation stream.** The randomized phase can only ever be a replication. | open, accepted |
| **11** | **F12 — the adversarial phase is defined by reference to a test file**, so it is not reproducible from the protocol. My 14 attacks are my own construction. | open |
| **12** | **F13 — C06's "here and only here" note** is contradicted by C04 and C07. | open, carried deliberately |
| **13** | **F14 — `unavailable` is reported and reconciled by I8 but no conclusion depends on it.** `failed` and `not_searched` are equally inert. | open |
| **14** | **I9 is exercised zero times** by fixture, exhaustive and randomized phases in all three runs. Never listed as open in any version. | unrecorded |
| **15** | **F15 — "exhaustive enumeration of 176,120 worlds" tests conclusion logic on 110,840** (63%); 76% of randomized worlds fail closed before any conclusion runs. Two numbers are needed where one is reported. | unrecorded since v1.0.0 |
| **16** | **F6/A2 — presence needing coverage** was closed by `conclusionFunction`, not by a listed repair (G5). A third implementation reading it the other way would move 19,152 worlds attributable to no named repair. | closed by text, unremarked |

Items 14 and 15 have now fallen out of the record for two versions. If the
close-out records nothing else from this document, it should record those two,
because they are the only ones with no home.

---

## 6. What conformance has actually been established

Two independently written implementations — one Rust, zero-dependency,
hand-rolled JSON/SHA-256/PRNG, never having seen the other — agree on: the
complete 176,120-world exhaustive enumeration and its 110,840/65,280 split; the
full conclusion distribution 160/49,480/41,820/19,380; zero violations of all
eleven hard invariants; a single fail-closed cause; four ablations all caught;
and, newly and decisively, the exact 703 and 691 canonical bytes and both SHA-256
digests of fixtures C11 and C12. That is a real result and it is stronger than
either previous run's. It is bounded in five ways that must travel with it.
**(a)** It is agreement under a specification that took three versions to
determine the answers, and the two implementations demonstrably disagreed on
22,440 worlds under v1.0.0 — agreement here is agreement with a document, reached
after the document was fixed, not independent arrival at a truth. **(b)** I had
seen the exhaustive conclusion distribution before this run, having published it
myself; I recomputed rather than asserted it, and the recomputation is in the
artifact, but that line is not blind and I will not claim it is. **(c)** The
digests are the one result unreachable from any count, computed from a registered
object I could not have guessed — that part is clean. **(d)** The randomized
phase is a replication, never a reproduction, and its counts were never compared.
**(e)** Per H2, the conclusion function and the margin rule are enforced by three
fixture worlds between them and by no invariant at all, so what has been verified
is that both implementations follow the same prose, not that any test would
notice if one stopped. The word for this state is **reproduced, under a
specification now known to have been ambiguous at three of the places the
implementations were compared** — and "verified" is still not licensed.

---

## 7. What I would do next, if there were a next run

Recorded so the close-out can carry these as known limits rather than have
someone rediscover them.

1. **Add I12: `conclusion` equals `conclusionFunction(world)`, and `margin`
   equals `abs(|S| − |O|)`.** This is the single highest-value change available.
   It would have caught the 22,440-world divergence in v1.0.0 with no fixture,
   and it closes items 1, 2 and 3 together by making the conclusion function
   checkable instead of merely written. Everything else on this list is smaller.
2. **Restate I2 and I5 world-referentially** (or register both forms
   separately). As written they are satisfiable by an evaluator that fabricates
   or omits the fields they quantify over, and one registered baseline already
   demonstrates it.
3. **Add a fifth baseline that drops `opposingRoots` from the receipt.** F2 has
   no positive control; this gives it one, and it costs one function.
4. **Withhold the exhaustive conclusion distribution from any future package**
   (H3), and screen `PROTOCOL.md` and `BRIEF.md`, not only the preregistration —
   the v1.1.0 leak and this one were both in the file the screen did not cover.
5. **Specify the adversarial phase in the protocol** rather than by reference to
   a test file (F12), so the phase is reproducible from the public documents like
   the other three.
6. **Register a draw schedule** for the randomized phase, or adopt a
   `worldStreamHash` primitive, so it can become a reproduction instead of a
   replication (F11). If neither is wanted, say in the claim discipline that the
   randomized phase is permanently replication-only — which is true today and is
   easy for a reader to miss.
7. **Decide `margin`'s name** (§3) and **`conversionsToReverse` on an empty
   ledger** (F4). Both are digest-moving, so they belong in one version together
   or not at all.
8. **Run a fourth implementation on a machine that does not hold the reference.**
   Packaging requirement 5, the only one still unmet across all three runs. Every
   independence claim in this program currently rests on my word that I did not
   open a file I could see, and no artifact can distinguish that from the
   alternative. Three runs of self-reported abstention is not the same evidence
   as one run where abstention was not possible.

---

*Provenance: written from `PROTOCOL.md`, `preregistration.json`,
`RESEARCH-METHOD.md`, `BRIEF.md` and `fixtures/` of the v1.2.0 package, verified
against `MANIFEST.sha256` (16/16). The reference implementation was not located,
opened, or read in any of IND-20260807-1, -2 or -3. `python3` was used for
arithmetic and external cross-checks only, never for the implementation; every
such use is listed in `REPRODUCE.md`.*
