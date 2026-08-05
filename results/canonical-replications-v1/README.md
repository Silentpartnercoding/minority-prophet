# Canonical replications v1 — results

Protocol commit: `b31dc9ed2c610faefc41d24bf67542a13d879b4c`

The protocol and runner were committed and pushed before either execution.
Two runs were then performed from a clean detached worktree at that commit,
using separate temporary directories and child processes. Every file and its
SHA-256 digest matched. `run-a/` retains one complete copy; `verification.json`
binds both independently generated receipts and records the comparison.

## Honest outcome

| Record | Reproducibility verdict | Scientific or completeness note |
| --- | --- | --- |
| EXP003R | reproduced | Archived lineage/aggregation implementation was deterministic. |
| EXP004R | reproduced | Original and corrected-axis sweeps were deterministic. |
| EXP005R | reproduced | Side-confusion sweep was deterministic. |
| EXP006R | reproduced | H5 was **rejected**: maximum cross-mode spread was 0.651, above 0.10. |
| EXP007R | incomplete | Multi-seed results ran, but the archived optimizer ends in placeholders and emitted no optimizer verdict. |
| EXP008R | reproduced | Full comparison table was deterministic. |

“Reproduced” here means the frozen archived implementation produced the same
bytes twice. It does not imply that the hypothesis was supported, that the
model is externally valid, or that the legacy experiment ID became canonical.
EXP007R is deliberately retained as an adverse result rather than repaired
after seeing its output.
