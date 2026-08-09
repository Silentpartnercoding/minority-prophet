# BL-044 — does registering a draw schedule buy cross-implementation reproducibility?

**Answer: necessary, not sufficient.** Commissioned by RUN-20260808-1, executed
by an independent Rust implementation, recorded by RUN-20260808-2.

Primary artifacts, imported verbatim and unedited:
`lineage/results/independent/IND-LIN000-{RESULTS.md,DECISIONS.md,primary.txt,confirmed.txt}`.

## The question

KL-000's randomized phase is **replication only, never reproduction** (F11): a
frozen seed fixes no cross-implementation stream, because two languages turn one
seed into different numbers. The proposed repair was to register the *draw
schedule* in prose rather than only the seed. LIN-000 was the first experiment
carrying such a schedule, so it was the cheap place to test the repair before
KL-000 committed to it.

Pass condition: reproduce two pinned world-stream digests. Counter equality was
retired as a pass condition because twelve of fourteen counters had already been
published (M27).

## Result

| phase | pre-declared reading, frozen before comparing | after sweep |
|---|---|---|
| exhaustive | **MISS** `a71c64eb…` | MATCH `b56d1228…` |
| randomized | **MISS** `2870b954…` | MATCH `f200184f…` |

Both pre-declared readings missed. The matches were found by sweeping an
enumerated space of readings, and are recorded as sweep results, not
reproductions — the implementer's own pre-registered protocol required exactly
that: *"A match found by sweep is reported as a sweep result and never as a
reproduction."*

**The measurement that answers F11 is not the match. It is the size of the space
the match had to be found in:**

- exhaustive: **96** enumeration orders tried → 96 distinct digests, exactly 1 correct
- randomized: **72** draw-schedule readings tried → exactly 1 correct

Registering the schedule moved the program from "no cross-language stream exists
at all" to "one coin-flip away". It did not produce a stream.

## The two misses are different, and the second is worse

**1. Randomized — the F11 clause failing at one point.** Every hard part
succeeded: hand-written MT19937, CPython's `init_by_array` seeding, `_randbelow`
rejection sampling, the 53-bit float construction. The clause that broke it reads
unambiguously: *"k uniform in 1..20"*. Several standard realisations of that
phrase consume different numbers of draws, so they are distribution-identical and
stream-distinct. One extra bite of entropy shifts everything after it.

The implementer also found that **two conforming MT19937 implementations diverge
on the same seed** (Ruby vs CPython), so even naming the algorithm and the seed
under-determines the stream.

**2. Exhaustive — nothing to do with F11.** That phase contains no PRNG. It
missed because `REGISTRATION.md` never states the enumeration order of a phase
whose pass condition is an order-sensitive digest. A fingerprint was demanded of
a list without specifying how to sort it. This gap would bite any future
digest-pinned deterministic phase and is independent of the randomness question.

## What did hold

Theorem 1 and Lemma 1 are no longer shadow-tested. Zero violations across both
phases, including 975,782 randomized rewirings, with negative controls firing as
required (cross-side rewiring changed the verdict 164,456 times, so the tests can
detect failure). Both ablations were caught. No invalidation condition triggered.

**[Corrected 2026-08-09 by BL-051.] The T1-positive half of that claim was
overstated, here and in FINDING-BL051.** In this schema `S_a` is defined as
`{root(c) : side(c) = a}`, so it is a function of the multiset of
`(root(c), side(c))` pairs alone. A rewiring that preserves every `root(c)` and
touches no side leaves that multiset identical, hence the verdict identical —
**by construction**. T1-positive cannot fail under the intended reading, so its
zero is not evidence about the schema. What does carry information, and did pass:
L1-positive, L1-negative, T1-negative, and both ablations. See
`FINDING-BL051.md` §"T1-positive is an identity".

## The M27 leak did less damage than feared

The implementer did not read the reference, and did not consult the public
repository, `PROVENANCE-REQUIREMENTS.md`, `formal/THEOREM-LEDGER.json`, or the
RUN-20260807-10 draft run report — the files carrying twelve of the fourteen
counters. Their counters were computed and, in their words, *"recognised from
nothing"*. The counter evidence this program wrote off as spoiled is independent
after all, by the implementer's choice rather than by our protection. The
withheld-set discipline still stands; it was not what saved this run.

Independently verified before accepting the report: the stream byte-lengths
(1,189,512 and 4,250,451) appear nowhere in the commission package and match the
reference exactly. They cannot be produced without generating the stream.

## Recommendation, adopted from the implementer

Registering the schedule is a real improvement on a frozen seed and should be
kept. The gap is not closable by writing the same kind of sentence more
carefully:

1. **Define the generator in the document, not by reference.** Not
   `random.Random`, and not "MT19937 seeded with N" either. A counter-based
   construction the registration can state in full, e.g. draw *j* is
   `SHA-256(seed_bytes || j)` truncated.
2. **Register draws as primitives, not distributions.** "Uniform in 1..20" has
   multiple stream-distinct realisations. State the acceptance rule and the word
   count, including degenerate cases — `_randbelow(1)` is not a no-op.
3. **Specify boundary cases and orders.** Claim 0's draw; the enumeration order
   of every deterministic phase; the canonical stream form inside the
   registration rather than in the covering brief.

Plus one cheap structural addition worth taking program-wide: **publish prefix
digests** every 1,000 worlds alongside the total. It leaks no more than the total
already does and converts an unlocalisable miss into a binary search.

## Monitoring error, recorded because the record is not for flattering the monitor

The agent monitoring this run reported to the owner that both digests had matched
**on the primary reading, first attempt, with no sweep**. That was false and it
inverted the finding. `out/confirmed.txt` was read and its MATCH lines reported;
`out/primary.txt`, which holds both misses, had appeared in the same watch and
was never opened.

The error is the same shape as the defects this program keeps recording: a single
artifact read, a stronger claim asserted than it supported. It was corrected on
reading `RESULTS.md`, before anything was committed, but it was stated to the
owner as fact first.
