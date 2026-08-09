# LIR-1E development analysis amendment

**Status:** frozen after response generation but before answer-content inspection,
construction-label opening, copy/mutation materialization, inference, or scoring.

## Reason

The parent LIR-1 preregistration freezes development-only threshold selection
and the higher-threshold tie rule, but the LIR-1E execution configuration did
not enumerate the candidate grid. This amendment supplies that missing
mechanical detail before any development outcome is inspected.

## Frozen selection

- Candidate parent thresholds:
  `0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85`.
- Apply the registered deterministic 40% edge-hiding perturbation.
- Score hidden direct-parent edges only across all 12 development cases.
- Select the threshold with maximum hidden-parent F1.
- Break exact ties in favor of the higher threshold.
- Do not use root-pair, root-count, aggregation, model identity, pair cell, or
  confirmatory information to select the threshold.
- Freeze the selected value and the development output hashes in Git before
  any confirmatory model request is made.

## State at registration

Sixty response wrappers and sixty private CLI receipts exist: 48 assigned to
Claude Fable 5 and 12 assigned to GPT-5.6. All wrappers passed structural
validation on their first provider attempt. Only counts, status, assigned model
IDs, usage-field names, and the response-file SHA-256 were inspected. No answer,
explanation, expected value, constructed truth, root, parent, or pairwise score
was inspected.
