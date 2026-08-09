# KL-001 v0.3 — the dual ledger's effect is one repository, and v0.2's corpus could not have shown it

Run against the registered protocol in `preregistration-v0.3.json`, pinned by
`PROTOCOL-COMMIT-v0.3.txt`. Both arms use the identical scanner; only the
aggregation differs.

## Result

|                        | corpus v1 (1 defect/file) | corpus v2 (40 files carry 2) |
|------------------------|---------------------------|------------------------------|
| baseline recall        | 81.7%                     | 79.3%                        |
| dual-ledger recall     | 81.7%                     | 79.3%                        |
| baseline false-clean   | 12.2%  (6/49)             | 4.3%  (2/47)                 |
| dual-ledger false-clean| **12.2%  (6/49)**         | **2.1%  (1/47)**             |

Recall is preserved exactly, on both corpora. The registered "preserve 95% of
true positives" target is met at 100%, and it was never at risk: the dual ledger
changes aggregation, not detection, so the two arms cannot differ on recall. A
target that cannot fail is decoration, and this one is. Recorded as such.

**On v1 the primary endpoint does not move at all.** Not by a little — by zero.

**On v2 it moves from two repositories to one.** The "50% relative reduction" is
n=1. It should not be reported as a percentage, and this document is the
correction to reporting it that way earlier.

## Why v1 could not exhibit the effect

The dual ledger reduces false-clean by exactly one mechanism: it notices that the
scanner *silently skipped a file* and returns `not_established` instead of a
clean verdict. Measured, not inferred:

    repos with a file the scanner cannot read      22
      ... that had findings anyway  -> present     18
      ... with no findings -> not_established       4
    repos with NO unreadable file that got
      not_established                               0

The state fires **if and only if** coverage was incomplete and nothing was found:
4 of 4, no exceptions in either direction.

Corpus v1 contains **zero** unreadable files. The generator never produced one.
So the mechanism had nothing to act on, and the primary endpoint was pinned to
the baseline by construction. v0.2's headline endpoint was registered against a
corpus incapable of moving it — the failure already recorded in
`DECISION-RW-001.md`, now measured rather than argued.

This is the case **BL-060** was opened for: a pre-flight trap asking "can this
corpus exhibit the effect the primary endpoint measures?" It would have caught
v0.2 before the run. It is no longer hypothetical.

## The cost the endpoint does not measure

Of the 4 repositories moved to `not_established`, **1 was truly defective** (the
rescue) and **3 were truly clean**. Three of the corpus's 13 clean repositories —
23% — can no longer be certified clean.

Whether that is a cost is a judgement, and the honest reading is that
`not_established` is the *correct* verdict for "I could not read part of this
repository": it is a refusal to certify, not a false positive. But the registered
primary endpoint counts only defective repositories, so it books the one rescue
and is structurally blind to the three downgrades. A one-sided endpoint will
always favour the intervention.

**The trade is 1 rescue for 3 refusals.** No registered endpoint reports that
ratio. Adding one is a protocol change, not a result, and is left for v0.4.

## The false clean that remains

`repo-001` is defective, has no unreadable file, and the scanner simply did not
match its defect — a `missing-timeout`, the class the baseline detects at 0/28.
Full coverage, honest report, missed bug. The dual ledger correctly cannot help:
it claims only to detect incomplete coverage, and coverage here was complete.
This is the boundary of what the mechanism can do, and it is where most real
false cleans will live.

## Taxonomy

Corpus v2 was built to answer whether two defects in one file are one finding or
two. Measured on both corpora: **0 of 135 planted defects share a (file, kind)
key with another**, so the key is injective and recall is not inflated by
collapsing.

That is a property of *these corpora*, not of the metric. A corpus with two
same-kind defects in one file would score 1/1 where the truth is 1/2, silently.
Registered as a known limitation; the defect-class taxonomy remains deliberately
unregistered.

## Disposition

The v0.3 run replicates on a harder corpus and sharpens the claim downward. The
defensible statement is:

> On a corpus containing files a scanner cannot read, the dual ledger converts a
> clean verdict into `not_established` whenever coverage was incomplete and
> nothing was found. On this corpus that rescued one false clean of two, and
> withheld certification from three clean repositories. Recall is unaffected by
> construction.

Not "reduces false cleans by half".

Follow-ups: **BL-060** (corpus-capability pre-flight, now demonstrated),
**BL-061** (register a two-sided endpoint that books the specificity cost),
**BL-062** (the 95%-preservation target cannot fail and should be retired or
replaced with one that can).
