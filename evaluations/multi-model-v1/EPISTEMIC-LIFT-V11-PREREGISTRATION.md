# Epistemic Lift v1.1 — raw-capture replication

Status: prospective transport revision frozen before v1.1 model execution.

This study reruns all 192 cells. It does not repair or combine cells from v1.0. The worlds, prompts, tool receipt, scoring, model configurations, condition ordering, and decision rule are unchanged. The only experimental change is response transport.

## Reason for revision

The v1.0 Claude CLI arm lost three cells because provider-managed structured-output enforcement exhausted its internal retries. V1.1 disables provider schema enforcement for both providers. Each invocation captures one raw final model response, after which the same versioned local parser validates it.

- No model-based schema repair.
- No formatting retry after a response is captured.
- One retry is allowed only when the provider process fails to return a response.
- Raw and invalid responses remain immutable.
- Any unparseable completed response invalidates verification rather than silently becoming an ordinary wrong answer.

## Frozen design

- Same 32 generated development worlds and world hashes as v1.0
- Same two model configurations: `gpt-5.6-sol` medium and `sonnet` medium
- Same three conditions: A raw, B provenance, C exact B plus the deterministic MP receipt
- Same six-permutation condition counterbalancing
- Same primary endpoint: paired C minus B truth recovery within each model
- Same success requirement: every model must show C−B at least 0.15 and exact paired two-sided p below 0.05

Because v1.0 outcomes on these development worlds are already known, v1.1 is a full transport-controlled replication, not an independent confirmatory test. Even a passing result requires a later held-out study before public scientific claims.

Frozen manifest hash: `sha256:7bf6d393e59ce6fbc78ca41bda4f71b5a0c29dc95d2b535bb19901c345bf3943`
