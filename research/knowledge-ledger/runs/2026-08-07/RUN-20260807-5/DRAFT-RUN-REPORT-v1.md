# KL-000: cross-implementation conformance, with its limits measured

This is the draft PR body for the KL-000 program: five repository runs
(RUN-20260807-1..5), three independent runs (IND-20260807-1..3), four
protocol versions. Nothing in this PR promotes any claim into the canonical
records; promotion is a separate owner-reviewed commit.

## What is established, by object and at its actual strength

Two independently written implementations — the Python reference, and a
zero-dependency Rust implementation with hand-written JSON/SHA-256/PRNG
whose author reports never having located or read the reference — agree on:

- **The evaluator and the complete conclusion function, across the full
  enumeration.** Identical partitioning of all 176,120 exhaustive worlds
  (110,840 receipts / 65,280 fail-closed, one cause) and an identical
  conclusion distribution over all 110,840 receipt-producing worlds:
  absent 160, not_established 49,480, present 41,820, supported 19,380.
  Zero violations of every registered hard invariant, in every run of both
  implementations.
- **The canonical form and digests — for the two pinned receipts only, not
  for all 110,840.** Fixtures C11 and C12 reproduce byte-for-byte across
  implementations: canonical unsigned forms identical (703 and 691 bytes),
  digests equal (`sha256:84e63c21…33eafe`, `sha256:61000a9b…aa3b6e`). This
  became possible only when v1.2.0 registered the receipt object — before
  that, 279 of the 703 hashed bytes were specified nowhere, and the digest
  provably could not be computed from the documents.
- **That four versions of specification repair changed nothing the evaluator
  does.** Every repair was published with a registered exact-equality
  prediction and tested by full re-execution: no count, no conclusion, and
  no pinned digest ever moved.

The randomized phase (1,000,000 seeded worlds, zero violations on both
sides) is a **replication, not a reproduction**, permanently: the frozen
seed fixes no cross-implementation world stream.

## The qualification that travels with the claim (LEAK-101)

The v1.1.0 commission package leaked the expected counts — including the
conclusion distribution — to the independent implementer, through the
registered protocol's own prediction table, shipped verbatim; the redaction
was correctly applied to the preregistration and defeated by the file beside
it. The conclusion-agreement line was therefore not blind. Two mitigations
are verified in the record: the line is derivable from the implementer's
*previously published* output plus the registered rule, and both later
independent runs recompute it from the worlds. **The digest result is
unaffected** — a count gives no path to a hash, and the receipt object the
digests cover was registered after the leaked package. The qualification
stays in the claim regardless.

## The decisions are now enforced (I12)

Until v1.3.0, the program's two owner decisions — the R1 tie rule and
R5.2's absolute margin — were enforced by **zero invariants**: an evaluator
with either decision inverted passed all eleven invariants over the complete
enumeration, caught only by the two pinned fixtures (R5.2's entire detection
surface was one world). v1.3.0 registered **I12**
(`conclusion == conclusionFunction(world)`;
`margin == abs(|supporting| − |opposing|)`, both world-referential) and
demonstrated its power at the exact previously measured surfaces:

| Ablation | Caught by I12 on | Other invariants | Fixture involved |
|---|---|---|---|
| R1 inverted — ties conclude `supported` | exactly **22,440** worlds | 0 | none |
| R5.2 inverted — margin signed | exactly **38,760** worlds | 0 | none |

The reference records zero I12 violations, and the enforcement change moved
nothing — every count, conclusion, baseline total, and both pinned digests
are unchanged. (The independent implementation conformed through v1.2.0; its
checker is its own and it has not run against v1.3.0.)

## What remains open, deliberately

- **A1** — does absence require supporting evidence, or coverage alone?
  **4 worlds.** The registered text says coverage alone; never brought to an
  explicit decision.
- **A2** — does presence require complete coverage? **19,152 worlds, 17.3%
  of receipts** — the largest undecided surface in the kernel. Recorded as
  an owner decision the program did not reach, with both readings and their
  consequences preserved. Neither is decided in this PR.

Also on the open ledger: the receipt-internal forms of I2/I5 (a registered
must-fail baseline does not fail literal I2 — measured in both
implementations), the margin-collision observation (unopposed support and
outnumbered-two-to-one produce identical `margin` scalars), the permanently
replication-only randomized phase, and the packaging rule that any future
commission must withhold the conclusion distribution.

## What this is not

KL-000's state is `adversarial-passed` — not "verified", not
`verified-independent`; that is an owner promotion decision not taken here.
**The first-transaction gate is NOT REACHED.** KL-000 was the precondition
for attempting KL-011; **eleven kernels (KL-001..KL-011) remain seeded**
with exact next gates, none executed. No knowledge transaction, no
cross-system result, no Candidate First Transmission, and no First
Transmission exists or is claimed.

## In the diff

Four preserved protocol registrations with commit-bound sidecars; the
evaluator (unchanged since v1.0.0) and its generator/checker/runner; twelve
fixtures including the two byte-pinned receipts; 88 permanent tests; the
confirmatory results of all four versions plus the imported independent
results with provenance and digests; the complete run records
(RUN-20260807-1..5) with constraints, methodology notes, and the final
record (`research/knowledge-ledger/experiments/KL-000/FINAL-RECORD.md`) —
which states everything above with its evidence, including the parts that
did not go well: two commission-package leaks, four self-miscounts, a
result artifact with stale identity metadata, and the three-version path it
took to make a digest computable from the specification.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
