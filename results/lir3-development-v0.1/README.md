# LIR-3 development selection

The frozen grid was evaluated on 417 development cases (5,000 claims). All 36
candidates met the `0.99` precision eligibility floor. The registered selection
rule chose the simplest effective configuration:
`author-0.00-margin-0.00-fallback-none`.

At 40% hidden recorded edges, development root-pair precision was `0.9997`,
recall was `0.9954`, and F1 was `0.9975`; root-count MAE was `0.0`. Frozen LIR-2
on the same cases had recall `0.2766` and F1 `0.4333`.

This is selection evidence, not confirmatory evidence. The configuration and
untouched holdout hash are sealed in
`experiments/lir3/HOLDOUT-COMMITMENT.json` before holdout scoring.
