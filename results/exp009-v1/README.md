# EXP009 canonical result

EXP009 tested a frozen selective hybrid: majority remained the default, while
inferred evidence-root voting could reverse it only on disagreement with root
margin at least three. The protocol, thresholds, seeds `301–320`, sample size,
and bootstrap procedure were public before execution.

In the primary attack regime, the inferred selective challenger recovered
`1.97697%` of copied-minority cases, lost `0.1125` percentage points of overall
accuracy relative to majority, and produced a `0.64375%` false-reversal rate.
The paired world-bootstrap intervals satisfied all three frozen primary
hypotheses. The primary claim is therefore **supported inside this synthetic
model**.

The declared-lineage diagnostic recovered `87.3590%` of copied-minority cases
with zero false reversals in the attack regime. That is an upper-bound
diagnostic using hidden generator truth, not a deployable inference result.

Two clean detached-worktree executions at implementation commit
`d8501e6f4d538350ed8d12d933c96ced2fe513ef` produced byte-identical scientific
JSON. Runtime measurements are preserved separately because timing is
observational and cannot be byte-identical.

This result does not establish external validity, reliable real-world lineage
inference, general minority correctness, or authorization to act.
