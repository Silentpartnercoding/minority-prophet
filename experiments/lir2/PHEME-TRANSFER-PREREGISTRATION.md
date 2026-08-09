# LIR-2/PHEME transfer preregistration

**Status:** frozen before the LIR-2 grouper is executed on PHEME text or labels.

## Boundary

This is a prospective **method-transfer test on a previously studied corpus**,
not a new independent dataset holdout. PHEME-R2's recorded reply-tree results
are already known. LIR-2 threshold `0.75` was selected exclusively on the
constructed LIR-1E corpus and is frozen before this transfer.

The target is recorded platform-root grouping. A PHEME reply tree is not proof
of causal evidence independence, content truth, or common observation.

## Frozen input and method

- Input: the 290-case, 5,000-claim normalized PHEME-R2 file with SHA-256
  `1c3e9e08149021cdb81da02b96750d75e0f0dce1dd7432bf5f7613fb206a2266`.
- Label basis: `explicit_edge`; label scope: `record_root`.
- Perturbation: the existing deterministic nested edge hiding at
  `0.05, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95`.
- Primary fraction: `0.40`.
- Method: committed LIR-2 direct root grouper, threshold `0.75`, without tuning,
  exclusions, source-specific tokens, or parameter changes.
- Inference receives only `ClaimInstance.feature_view()`.
- Bootstrap: 10,000 whole-case resamples, seed `20260808`.

PHEME lacks the controlled asserted-value field used by LIR-1E, so no truth
aggregation claim is made here.

## Known comparator

The prior LIR-1/PHEME-R2 parent baseline at 40% hiding had root-pair precision
`0.9990`, recall `0.2256`, F1 `0.3680`, and root-count MAE `4.9310`. Those known
values motivate an explicit transfer target but are not hidden evidence.

## Joint success criterion

At 40% hiding, all conditions must hold:

1. root-pair precision at least `0.99`;
2. root-pair recall at least `0.45`;
3. root-pair F1 at least `0.60`; and
4. root-count mean absolute error below `4.0`.

The recall target is approximately twice the known baseline while retaining its
near-perfect precision. Failure of any condition rejects the joint transfer
claim. All fractions and bootstrap intervals are reported; they cannot rescue
a failed primary criterion.

## Integrity and interpretation

Two clean outputs must be byte-identical. Publish success or failure unchanged.
Success would show useful transfer from constructed root grouping to this one
recorded-reply corpus. It would not establish unseen-dataset generalization,
causal source independence, authentication, or general truth recovery.
