# Evidence alignment ledger

This ledger states which public claims are supported by which immutable record.
`CANONICAL-RECORDS.md` controls status; a paper cannot promote an experiment.

## EXP007 correction

Earlier paper drafts reported an E7 optimum of `(0.93, 0.91, 0.35, 0.36)`,
accuracy `0.357`, margins `3.88` and `5.71`, and Welch t `9.89`. The archived
runner did not contain a completed optimizer: its attack functions returned
`None` after printing the optimizer heading. EXP007R canonically reproduced
that incompleteness. Those numeric claims therefore have no canonical support
and are withdrawn from the active manuscript.

EXP007A is a distinct new experiment, not a retroactive repair. Its protocol
and implementation were committed before execution at
`9906f50485455172cbcd3a0d456c6c6aa9cee0d6`. Its two clean outputs were
byte-identical with SHA-256
`a9400e24f483fcb3911c2daf143c840744f23db5d634f3c72c45a838600c55c4`.

The supported synthetic-model claims are:

- selected `(paraphrase, forged citation, sybil, timing)` parameters:
  `(0.701175, 1.0, 0.0, 0.0)`;
- selected holdout accuracy `0.371544`, versus `0.446144` for uniform-0.5 and
  `0.413321` for uniform-1.0;
- incorrect-verdict mean honest margin `3.7684`, versus `5.6886` for correct
  verdicts, with Welch t `25.1144`;
- both preregistered hypotheses supported on ten untouched holdout seeds.

Permitted interpretation: within the frozen synthetic model, a budget-limited
attack against inferred lineage outperformed uniform comparators and failures
concentrated in thinner-margin worlds.

Not permitted: claiming an external exploit, general security performance,
the historical optimum, or proof that any identity/attestation provider solves
causal independence.

## Other canonical boundaries

| Record | Supported statement | Unsupported extension |
| --- | --- | --- |
| EXP001 | Frozen constructed pilot reproduced its declared output. | General truth recovery. |
| EXP002 | Frozen derived market record and declared source boundary are hash-bound. | Replay of mutable upstream bytes or superiority to market prices. |
| EXP003R–EXP005R | Archived implementations replayed deterministically. | External validity or promotion of legacy E3–E5. |
| EXP006R | Archived implementation replayed; H5 was rejected at spread 0.651. | A universal scalar failure curve. |
| EXP007R | Archived multi-seed section ran; optimizer was incomplete. | Any optimizer optimum. |
| EXP007A | New synthetic optimizer and holdout result are canonical. | Real-world exploitability or provider validation. |
| EXP008R | Archived runner and output table replayed deterministically. | Canonical comparison against released third-party implementations. |
| EXP009 | Frozen selective hybrid recovered 1.98% of majority-wrong cases at a 0.64% false-reversal rate and 0.11-point accuracy cost in the attack regime. | External validity, reliable deployed lineage inference, or authority to act. |
| HVI-1 | Control-domain aggregation admitted zero additional roots from aliases, key rotation, service splitting, or self-verification and escalated all unknown-control cases. | Discovery of hidden common control, causal evidence independence, truth, or authorization. |
| HEO-1 | Evidence-origin aggregation admitted zero additional roots from supported copies and transformations; unknown and forged origins always escalated. | Discovery of undisclosed common sources, truth of root observations, or authorization. |

## Manuscript policy

- `papers/minority-prophet-v1.0.3.md` is the active evidence-aligned draft.
- v0.9, v1.0, v1.0.1, and v1.0.2 are preserved historical drafts and defer to this ledger.
- EXP008's archived attack mixture is not EXP007A's selected attack.
- All point estimates must name their record and scope.
- Rejected, incomplete, and null results remain visible.

## Remaining release blockers

1. E2 matched-coverage analysis and final H2c status.
2. Canonical head-to-head against released truth-discovery implementations for
   E8/E8b comparative claims.
3. Verbatim verification of every literature citation against primary sources.
4. A vendor-neutral evidence contract and conformance suite tested against at
   least one real provider, without treating identity as proof of independence.
