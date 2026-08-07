# Superseded KL-000 result documents

These are the **first** confirmatory execution's outputs, committed at
`3ac618f` and superseded by the instrumented re-execution. They are retained
because governing principle 9 requires preserving corrected results, and because
a correction that leaves no trace of what was corrected is indistinguishable
from having been right the first time.

| File | Digest | What it is |
|---|---|---|
| `kl000-confirmatory-uninstrumented.json` | `sha256:9dc447ce…08864b` | first execution, uninstrumented |
| `kl000-effective-sample-uninstrumented.json` | `sha256:1ec6e5a7…64e37` | its secondary analysis |

## What these documents cannot tell you, and why they were replaced

**Baselines ran on 2% of the worlds.** `phases.baselines.*.worldsChecked` reads
`20000` for each ablation, against an exhaustive set of 176,120, while
`PROTOCOL.md` claimed the baselines were "run against the same worlds and the
same checker". The vacuity conclusion survived comfortably at that sample — B1
alone produced 71,352 violations — but the protocol and the execution disagreed,
and only the protocol's version was written down.

**Refusals were an undifferentiated count.** There is no `failClosedByCause`
key in these documents. `phases.randomized.failClosedRejections` reads `756619`
— 75.7% of the phase — with no exception type, no message, and no preserved
sample behind it. A genuine implementation defect and a designed refusal both
incremented that single integer.

That is the substantive reason for replacement. As written, "0 violations across
1,000,000 randomized worlds" was **not readable as stated**: roughly
three-quarters of those worlds errored for reasons the record did not contain.
The instrumented re-execution established that 100% of refusals in both phases
are the single expected `ValueError: One root cannot support opposing sides.`,
with zero unexpected causes — but that is a finding produced by the second run,
not something these documents ever supported.

**The stop condition was ambiguous.** `haltedOnFirstViolation: false` is
consistent both with "armed and never fired" and with "never armed".

## What did not change

Every scientific number is identical across both executions. The re-execution
used the same frozen seed and the same world stream:

```
worldsChecked, totalViolations, failClosedRejections, outOfDeclaredBounds,
and both conclusionDistributions:  IDENTICAL in both runs
```

The verdict — KL-000 passed, zero violations — is unchanged. What changed is
what the verdict is *allowed to say*, which is why the correction was worth
making rather than waving through.

## History note

`3ac618f` was initially **amended** into `1b0ce02` rather than corrected by a
follow-up commit. That was inconsistent with the treatment this same run gave
`ORIENTATION.md`, where the original text was preserved and a correction
appended, on the reasoning that rewriting it "would destroy the evidence that a
correction was needed". The stricter standard belongs on results at least as
much as on orientation notes.

The amend was reverted: `3ac618f` is an ancestor of the branch again, the
corrections live in the follow-up commit that added this directory, and both
result documents survive. Recorded as constraint `PROV-007`.
