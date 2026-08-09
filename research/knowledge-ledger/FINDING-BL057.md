# BL-057 — LIN-000 v0.4: the round where the package was not the finding

Closed 2026-08-09 by RUN-20260809-2. Artifacts imported verbatim to
`lineage/results/independent-v4/`.

## Result: passed, on every condition

| condition | outcome |
|---|---|
| both stream digests | reproduced |
| 150 prefix digests | 150/150 |
| seven conformance vectors, digest **and** word count | 7/7 |
| every withheld theorem counter | exact match to the reference |

    T1-POS   116,032 pairs   0 violations
    T1-NEC   194,112 pairs   47,224 verdict changes
    T1-ID  1,225,776 pairs   0 violations
    L1-DISC  exhaustive {1:36038, 2:8292, 3:120} — identical to the reference
    L1-POS   0 violations in both phases

Three previous rounds each found the *registration* defective — v0.1 and v0.2 in
the schedule, v0.3 in its own packaging. **v0.4 is the first where the package
held.** That is what the pre-flight was built to buy, and it is the only thing
about this round that can be credited to it: the traps encode defects already
made, and they say nothing about the ones below.

## The implementer corrected their own frozen pre-declaration

`PRE-DECLARATION.md` is byte-identical and still hashes to `24aab653…`. Beside
it sits `PRE-DECLARATION-ERRATUM.md`, written after the first run, correcting a
factual claim inside it: the pre-declaration said no digest value had been read
before freezing, and that was false. They had seen both stream digests and the
50 exhaustive prefix digests.

They fixed the claim in a separate file rather than the original, on the grounds
that *"a pre-declaration that can be edited after the fact is worth nothing"*.
That is the correct handling and the record keeps both.

**What it costs, assessed rather than waved away.** The stream digests are no
longer blind evidence for this round. What remains uncontaminated is everything
they demonstrably had not seen: the 100 randomized prefix digests and all seven
conformance vectors — **and those match 100/100 and 7/7**. A digest is not
invertible, so seeing `a71c64eb…` conveys nothing about the enumeration order or
the canonical form; the exposure would matter only if the pins had been used as
an oracle across repeated runs, and the clean half of the evidence corroborates
that they were not.

The programme should note which side of this it was on: the disclosure came from
the implementer, unprompted, about their own document. Nothing in our packaging
would have detected it.

## What they found that we had not

**Two definitions of side-consistency stop being equivalent under mutation.**
Their `mutantAudit` ran both the parent-based and root-based readings against
five deliberately broken `root()` implementations:

    correct        parentLocal 0/5,912 fired      rootBased 0/5,912 fired
    depth0         parentLocal 5,786/5,912        rootBased 50,236/50,362
    alwaysZero     parentLocal 5,604/5,912        rootBased 1,438/1,746

For a *correct* implementation the two are identical — v0.4 says so, and their
run confirms it at 0 disagreements across 50,362 worlds. Under a *mutated*
`root()` they diverge, and not slightly: the eligible population itself changes,
5,912 against 50,362.

The consequence is that v0.4's line — *"either may be implemented"* — is true of
a correct implementation and false of an ablated one. Since the ablations are
how this experiment measures checker power, the choice is **not** free where it
matters most. v0.4 registered it as free.

This is the same shape as every finding this experiment has produced: a statement
true under the conditions we tested and false under the conditions the test
exists to explore.

## Disposition

BL-057 closed; its counters are publishable and the reference results are
committed. The side-consistency equivalence defect opens as **BL-058**: v0.5 must
either register one reading normatively or state that the ablations must be run
under both, with the populations reported separately.

No further LIN-000 commission is proposed. The stream question is answered, the
semantics are specified well enough that an independent implementation reproduced
everything blind, and the remaining defect is a one-sentence registration change
rather than a round.
