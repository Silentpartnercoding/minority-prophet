# LIR-1 PHEME-R2 — disjoint holdout replication

**Status:** registered before selecting, normalizing, or scoring the disjoint
holdout.

PHEME-R2 exists because deviation D1 exhausted the original confirmatory set.
It does not relabel that invalid attempt.

## Frozen method

Use the transparent inference implementation committed at
`ce40c37489ef41f81853cd64800cb31811ad544b` and corrected development threshold
`0.40`. Score only edges removed from the feature view. Do not tune on R2.

## Disjoint selection

The 317 case IDs used by v0.1, sorted with one trailing newline, have SHA-256
`8871f2db99c7e31645b3b567a9dee23541557e2a19bfd9299d0932f57f950978`.
Exclude exactly those cases. From the remaining rumor directories sorted by
path, admit complete cases without exceeding 5,000 claim instances. Raw and
normalized tweet text remains local.

## Endpoints and verdict

At every registered hidden fraction report hidden-parent precision, recall,
and F1; root-pair precision, recall, and F1; root-count absolute error; and
case-bootstrap 95% intervals for hidden-parent F1.

The inherited secondary criterion is supported only if hidden-parent F1 is
strictly above `0.50` at 40% hidden edges. The root-family metrics are reported
as separate operational endpoints and cannot be rescued by a parent score.
All outcomes remain visible.

