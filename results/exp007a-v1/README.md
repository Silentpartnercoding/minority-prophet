# EXP007A canonical result

Protocol commit: `9906f50485455172cbcd3a0d456c6c6aa9cee0d6`

EXP007A completes the adversary experiment that EXP007R proved was unfinished.
The protocol, implementation, 45-evaluation budget, training set, holdout set,
and verdict rules were committed and pushed before execution.

## Result

- selected parameters `(paraphrase, forged citation, sybil, timing)`:
  `(0.701175, 1.0, 0.0, 0.0)`;
- selected attack holdout accuracy: `0.371544`;
- uniform-0.5 holdout accuracy: `0.446144`;
- uniform-1.0 holdout accuracy: `0.413321`;
- no-attack holdout accuracy: `0.991333`;
- incorrect-verdict honest margin: `3.7684` (`n=924`);
- correct-verdict honest margin: `5.6886` (`n=546`);
- Welch t statistic: `25.1144`;
- H7A-1: supported;
- H7A-2: supported;
- overall: supported.

Two clean detached-worktree invocations produced the identical scientific
record with SHA-256
`a9400e24f483fcb3911c2daf143c840744f23db5d634f3c72c45a838600c55c4`.

## Interpretation boundary

The attack used paraphrasing and forged citations rather than sybil or timing
pressure. It beat both frozen uniform comparators on ten unseen seeds and its
errors concentrated in thinner-margin worlds.

This is a new synthetic result. It does not retroactively complete EXP007R,
demonstrate an external exploit, or validate the papers' previously reported
four-parameter optimum. Those papers require a separate evidence-alignment
change before treating EXP007A as their canonical support.
