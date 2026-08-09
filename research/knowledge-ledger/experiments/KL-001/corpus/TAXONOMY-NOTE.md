# The defect-class taxonomy question, and why most of it dissolves

Recorded 2026-08-09, prompted by the owner asking: *"isn't there the risk they
identified different bugs still... why can't they normalize their finding? What
is the more integrity path"*.

Both halves of that were right, and the recommendation they were responding to
was worse than it needed to be.

## The recommendation that was wrong

The proposal was to count one bug per `(file, line, defect class)`. It has the
defect the question names: **two scanners reporting the same line may be finding
two different bugs**, and that rule silently merges them. It also splits one bug
reported at two lines. It is a positional heuristic standing in for identity.

## Why the question mostly dissolves

The taxonomy problem arises when you must decide whether two *scanner outputs*
are the same finding. **That comparison is never needed here.** The corpus is
seeded, so every defect has an identity by construction, and a finding is a true
positive if and only if it locates a planted defect. Findings are scored against
**ground truth**, never against each other.

    planted = {(file, kind) for each planted defect}
    true positive  <=>  a finding matches a planted defect

Two scanners locating the same planted defect is not a counting problem. It is
the phenomenon this product exists to measure: repetition is not extra evidence,
which is exactly what the one-family-one-root rule (MAPPING-RULES.md M2) encodes.

Measured under three different matching rules — strict `(file, class)`,
file-only, and class-only — recall is **81.7% under all three**. The taxonomy
cannot move the number.

## Where it does not dissolve, stated rather than glossed

**1. This corpus cannot test the hard case.** `generate_corpus.py` plants at most
one defect per file: **0 of 71 files carry two.** The "same file, two different
bugs" case — the one the owner's question is about — therefore never arises, and
the three-rule agreement above is a fact about frozen-v1, not a general result.
That is a gap in the generator, and the endpoints registered against frozen-v1
inherit it.

**2. False positives still need a rule.** A finding matching no planted defect is
a false positive, but whether two scanners reporting the same spurious thing is
one or two is genuinely undecided. It does not affect the **false-clean rate**,
which is repo-level and is the registered primary endpoint. It does affect any
raw false-positive count, which is why none is registered as an endpoint.

**3. A right-file, wrong-class finding** is currently a miss and a false positive
simultaneously. Defensible, and a choice.

## The higher-integrity path

1. **Score against ground truth, never against other scanners' outputs.** Already
   done; it removes the taxonomy from recall entirely.
2. **Report under multiple matching rules and show whether the conclusion moves.**
   Done above. If a future corpus makes them diverge, the divergence is the
   finding and the aggregate must not be quoted without it.
3. **Fix the corpus, not the rule.** A generator that plants multiple defects per
   file makes the hard case testable. That is **BL-059**, and it requires a new
   corpus and therefore a new baseline — the registered endpoints are pinned to
   frozen-v1 and do not move retroactively.

## Status

No taxonomy is registered, and on this corpus none is needed for the registered
endpoints. The claim that must **not** be made is that the taxonomy question has
been settled in general. It has been shown not to bite here, on a corpus that
cannot make it bite.
