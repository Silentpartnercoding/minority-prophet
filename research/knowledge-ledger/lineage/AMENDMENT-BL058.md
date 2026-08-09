# BL-058 — the side-consistency reading, and what a mutant audit must report

An amendment to be folded into any LIN-000 v0.5 registration. Not itself a
registration, and it modifies no frozen document.

## The defect

v0.4 registers that the side-consistency reading — parent-local or root-based —
is free: *"either may be implemented"*. Verified against the primary data in
`results/independent-v4/IND-v4-RESULTS.json`, not against the summary of it:

| mutant | parent checked/fired | root checked/fired | |
|---|---|---|---|
| correct | 5912 / 0 | 5912 / 0 | agree |
| depth0 | 5912 / 5786 | **50362 / 50236** | populations diverge |
| depth1 | 5912 / 2904 | 5912 / 2904 | agree |
| depth2 | 5912 / 572 | 5912 / 572 | agree |
| alwaysZero | 5912 / 5604 | **1746 / 1438** | populations diverge |
| offByOneStop | 5912 / 2904 | 5912 / 2904 | agree |
| minIndexInChain | 5912 / 0 | 5912 / 0 | fires nowhere |
| grandparentSkip | 5912 / 0 | 5912 / 0 | fires nowhere |

For a correct implementation the readings agree exactly. Under two of the
mutations the *eligible population* differs — 5,912 against 50,362, and 5,912
against 1,746 — so the choice is free precisely where it does not matter and not
free where it does. The ablations are how this experiment measures checker power.

**Amendment 1.** Replace *"either may be implemented"* with: the parent-local
reading is normative for reported results, and every ablation must additionally be
run under the root-based reading with its own population and firing count reported
separately. A single figure that silently depends on the reading is withdrawn.

## The second defect, which the finding did not carry

`FINDING-BL057.md` describes "five deliberately broken `root()` implementations".
The data has **seven**. The two it omits, `minIndexInChain` and `grandparentSkip`,
are the two that fire zero under both readings, and they appear in no finding at
all — only in the raw results.

A zero has two opposite meanings:

- **equivalent** — the mutation cannot change behaviour, so nothing could fire.
  Harmless, and it says nothing about the checker.
- **undetected** — the mutation changes behaviour and the checker misses it. A
  blind spot, and the most serious result this experiment can produce.

`IND-v4-RESULTS.json` records mutants by name and firing count with no
implementation, no behavioural fingerprint and no equivalence classification. The
file contains none of the strings `equivalent`, `fingerprint`, `description` or
`semantics`. So no reader can tell which meaning applies. **An audit whose zeros
cannot be interpreted is not falsifiable**, and BL-056 had already established
behavioural fingerprinting as the method for separating the two.

`classify_survivors.py` reconstructs both mutants from their names and classifies
them against this repository's v4 reference: both **EQUIVALENT**, 0 differing
calls out of 297,378 across all 50,362 exhaustive worlds.

That is deliberately a weak claim. It establishes what *these reconstructions* do
to *this* implementation — the same names admit other implementations, and the
independent code is not in this repository. It does not show the originals were
harmless. What it does show is that the question cannot be settled from the
published artefact, which is the finding.

The classifier carries a positive control, `control:offByOneStop`, which differs
on 174,812 of 297,378 calls. Without it, a classifier that returned EQUIVALENT
unconditionally would have produced the same two lines and "proved" both mutants
harmless.

**Amendment 2.** A mutant audit must publish, for every mutant: its
implementation or a behavioural fingerprint sufficient to reproduce it, and an
explicit equivalent/non-equivalent classification. A mutant reported as firing
zero without that classification is not a result and may not be counted toward
checker power in either direction.

## Scope note

Amendment 2 is the more general of the two and is not specific to LIN-000. Any
experiment in this programme that reports mutation counts is exposed to the same
ambiguity.
