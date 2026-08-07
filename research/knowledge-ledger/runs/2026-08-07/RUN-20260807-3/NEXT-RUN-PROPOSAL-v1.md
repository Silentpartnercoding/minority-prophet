# NEXT-RUN-PROPOSAL v1 — after RUN-20260807-3

## The smallest step that resolves the highest-value uncertainty

**Commission IND-20260807-3: the independent implementation against protocol
v1.2.0, attempting C11 and C12.** This is the first commission in the
program's history with a genuine chance of reproducing a digest across
implementations, because v1.2.0 is the first registration under which every
hashed byte is specified. If C11's digest reproduces, I4 and I6 become
cross-implementation properties, the F10 → R4 → G2 → R5.1 repair arc closes,
and KL-000's `verified-independent` claim becomes available for owner
promotion. It is the owner's commission; this repository's agents prepare
the package and adjudicate the return, nothing more.

## Packaging requirements — now registered, not advisory

LEAK-101 made BL-019 a requirement. The package for IND-20260807-3:

1. Derives from the registration by **deletion**: `PROTOCOL-v1.2.0.md`
   without its "Preregistered prediction" section;
   `preregistration-v1.2.0.json` without `expectedIdenticalToRun1`. (Note
   the fixtures necessarily carry the two pinned digests and canonical
   strings — that is the test, not a leak.)
2. Screening greps run against **every shipped file**, in comma and
   comma-less formats, for the count values (the conclusion-distribution
   values are inherently shipped in the C-fixture expected blocks from
   v1.0.0 onward and are already published in both implementations' results;
   the counts table is what must not ship).
3. Registered paths resolve as registered (`fixtures/v1.2.0/…`), per G6.
4. The package carries a manifest of its own digests, so what was delivered
   is provable afterward — this run could trace LEAK-101 only because the
   operator happened to preserve both package states.
5. The operator's original remediation stands: strongest form is a machine
   that does not hold the reference.

## Exact pass condition

- C11 digest `sha256:84e63c21…33eafe` and C12 digest `sha256:61000a9b…aa3b6e`
  reproduced byte-for-byte (the canonical strings in the fixtures localise
  any miss).
- Conclusion distribution again exactly 160 / 49,480 / 41,820 / 19,380.
- Zero violations of all eleven invariants; R2/R3 refusals present.
- Randomized: 0 violations at a consistent rate; counts not compared (F11).

A digest miss with matching values localises a canonicalisation or
receipt-object misreading to a byte offset — publish the offset, not just
the failure. Residual conclusion disagreement would be a new ambiguity and
reopens the loop.

## If it passes

`verified-independent` becomes claimable — **by owner promotion, not by the
run** — and KL-011's two-implementation prerequisite is substantively met.
The run after is v1.3.0, whose I12 component (`conclusion ==
conclusionFunction(world)`, subsuming I2/I5's conclusion clauses — G4's
repair) is a **committed gate, not a proposal**: promoted by owner direction
at this run's close, with its evidence and exact pass condition recorded in
KL-000's STATUS `committedGates`. The rest of the bundle (F1/F2
world-referential restatement, B2/B3 dedup and B6 ablation, F11 stream
registration via `worldStreamHash`) travels with it. Then KL-011
preregistration at schema v0.2.

## If it fails

The byte offset is the deliverable. Classify: canonicalisation misreading
(codec), receipt-object misreading (R5.1 text), or a residual specification
gap (v1.3.0 repair). No smoothing; the divergence is the result.

## What NOT to do

- Do not fold v1.3.0 repairs into the commission window — the target stays
  frozen while the implementer works (the rule that has now held three
  times).
- Do not touch the evaluator; do not execute the commission from this
  repository; do not promote anything before the owner reviews.
