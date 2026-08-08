# DRAFT RUN REPORT v1 — RUN-20260807-4 — KL-000 close-out

Final run of the program. This document is also the draft PR body. Nothing
pushed, nothing promoted without the owner. **The first-transaction gate is
NOT REACHED.**

## Two findings sit side by side, and the second is the headline

**First: the reproduction passed.** IND-20260807-3 — the independent Rust
implementation, zero dependencies, hand-written JSON/SHA-256/PRNG, whose
author reports never having located or read the reference across all three
of its runs — reproduced fixtures C11 and C12 **byte-for-byte**: canonical
unsigned forms identical (703 and 691 bytes), digests equal
(`sha256:84e63c21…33eafe`, `sha256:61000a9b…aa3b6e`), receipt member set
exactly the registered nine. I4 (deterministic replay) and I6 (digest
integrity) — the last two invariants never tested across implementations —
are tested now, and the answer is agreement. The conclusion distribution
agreed exactly for the second consecutive version (160 / 49,480 / 41,820 /
19,380), with zero violations of every registered invariant, in both
implementations, in every run either has ever executed.

**Second, the headline: the program's enforcement of its own decisions rests
on two pinned inputs, not on any property that holds across the
enumeration.** IND-3 ran two ablations, each corrupting one owner decision
and nothing else, through the same checker over the full 176,120-world
enumeration; this repository reproduced both measurements on the reference
side:

| Ablation | Receipts changed | Invariant violations | Caught by |
|---|---|---|---|
| R1 inverted (ties conclude `supported`) | 22,440 | **0** — all thirteen checks silent | C11, C12 |
| R5.2 inverted (margin signed) | 38,760 | **0** — all thirteen checks silent | **C12 only** |

Both owner decisions are enforced by **zero invariants**. They survive only
because two fixtures happen to pin receipts that exercise them. An evaluator
that gets either decision backwards passes every registered invariant over
176,120 enumerated and 1,000,000 randomized worlds. What the passing
reproduction demonstrates is that both implementations follow the same
registered prose — not that any test would notice if one stopped.

## The final claim, at its actual strength

**Established:** the evaluator, the conclusion function, and the canonical
form agree across two independent implementations in different languages
with no shared code — the conclusion function across the full
110,840-receipt enumeration; **the canonical form confirmed for two pinned
receipts, not for all 110,840**; every specification repair across three
protocol versions behaviour-preserving (no count, conclusion, or pinned
digest ever moved, each time as a registered prediction).

**Qualified by LEAK-101, which travels with the claim:** the independent
implementer saw the expected counts in the v1.1.0 commission package — the
registered protocol's own prediction table shipped verbatim, defeating a
redaction correctly applied to the file beside it. The conclusion-agreement
line was therefore not blind (mitigations verified: derivable from the
implementer's previously published output plus the registered rule, and
recomputed from the worlds in both IND runs). **The digest result is
unaffected** — a count gives no path to a hash, and the receipt object the
digests cover was registered after the leaked package — but the
qualification belongs in the claim and is in it.

**Not established:** "verified" in any form. KL-000's final state is
`adversarial-passed`, deliberately: a passing cross-implementation
reproduction is not `verified-independent` while the program's own decisions
are unenforced. Also not established: canonical-form agreement beyond the
two pins; randomized agreement across implementations (permanent replication,
F11); anything outside the declared bounds; and any part of a knowledge
transaction, cross-system result, Candidate First Transmission, or First
Transmission — none of these exist, none is claimed, exactly as
RUN-20260807-1 first put it.

## What this run recorded, beyond the verdicts

- **I12 is the committed gate, with both ablations as evidence.**
  `conclusion == conclusionFunction(world)` and `margin == abs(|S|−|O|)`,
  exact pass condition attached (catches the two ablations on exactly 22,440
  and 38,760 worlds with no fixture involved; B5 records zero violations; no
  other number moves). It is the sole remaining committed gate, owner's to
  schedule.
- **A1 and A2 are permanent limits, recorded undecided.** A1 (does absence
  need supporting evidence, or coverage alone) governs 4 worlds — the
  loudest receipts the schema can emit. A2 (does presence need complete
  coverage) governs **19,152 worlds, 17.3% of receipts**, and is an owner
  decision the program did not reach: the registered text implies one
  reading, both implementations follow it, and no one ever decided it the
  way R1 and R5.2 were decided. Both readings and their consequences are in
  STATUS `permanentLimits`. This run did not decide it.
- **Verification found a defect in the decisive artifact:** the IND-3 result
  JSON carries ten metadata sections byte-equal to the IND-2 result —
  including `runId` and `protocolVersion` — stale carry-overs of the
  updated-in-place workflow. The content is internally consistent and was
  re-verified from scratch here (both digest verdicts against the registered
  pins; the R5.2 ablation reproduced exactly). Recorded; the artifact is
  untouched.
- **The packaging discipline held, with one forward-looking caveat (H3):**
  manifest 16/16, all eight screened values absent in both formats — but the
  conclusion distribution itself ships in the v1.2.0 package, legitimately
  for this implementer (who published it first) and fatally for any fresh
  one. Any future commission must withhold it.
- **Amendment 2** corrects the protocol's "all nine non-`contentDigest`
  members" to eight (implementer finding H1; the program's fourth
  self-miscount, each caught by counting from scratch). Provably inert: the
  machine-readable member list was always correct, and the digests
  reproduced.
- **The margin-collision observation is on record for the owner:** C01
  (unopposed support) and C12 (outnumbered two to one) carry identical
  `margin` and `conversionsToReverse`; the implementer recommends a
  digest-moving v1.3.0 rename, not a reversal.
- **Eleven kernels audited: all still seeded with exact next gates, none
  silently advanced.** KL-011's two-implementation prerequisite is
  substantively met and everything else about it remains unexecuted.

## The program, in one table

| Run | What it did | What moved |
|---|---|---|
| RUN-1 | registered v1.0.0, executed KL-000, passed | kernel to adversarial-passed |
| IND-1 | independent reimplementation from the registered documents | exhaustive reproduced exactly; conclusions diverged on 22,440 worlds, predicted in advance |
| RUN-2 | registered v1.1.0 (R1 tie rule — owner decision — R2, R3/I11, R4) | nothing, as registered |
| IND-2 | re-run against v1.1.0 | divergence closed exactly; digest still uncomputable — receipt object unregistered (G2) |
| RUN-3 | registered v1.2.0 (R5.1 receipt object, R5.2 absolute margin — ratified) | nothing, including the pinned digest, as registered |
| IND-3 | re-run against v1.2.0 | **both digests reproduce byte-for-byte**; both owner-decision ablations pass all invariants |
| RUN-4 | this close-out | the record, not the numbers |

Every repair documented existing behaviour or resolved an ambiguity in
favour of it, and every "nothing moved" was a registered prediction tested
by full re-execution, not an assertion.

## Delivery

The PR branch `agent/kl-000-conformance` has been rebuilt from `github/main`
(`335b34e`), cherry-picking all 31 program commits plus the sidecar rebind
(head recorded in HANDOFF; all three registration chains verify on the
branch; 63 root + 80 KL-000 tests pass — the root count is 63, not the run
branch's 74, because eleven first-transmission-render tests belong to the
run branch's base and are not part of this program). **Nothing has been
pushed**; exact commands are in HANDOFF-v1.md. Promotion of any claim into
the canonical records remains a separate owner-reviewed commit that this
program never performed.

*A final report that records an unenforced decision and an undecided
ambiguity is worth more than one that reads as completion.*

🤖 Generated with [Claude Code](https://claude.com/claude-code)
