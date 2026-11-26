# EXP010 preserved synthetic run

This packet is available for review before any decision to register it as a
canonical record. It preserves the [protocol](../EXP010-ROOT-IDENTIFIABILITY-PREREGISTRATION.md),
runner, scientific output, and diagnostics from the original local run. The
commit IDs below identify the original local history. Public pre-run
timestamping has not been verified.

Protocol commit: `3e47d1f827d337c52a144b52db7dee2018bfe707`

Implementation commit: `0bc044716b7795b7e3f4e969f219e92f3e0a35e7`

EXP010 evaluated 4,000 paired causal templates (8,000 hidden worlds) across
untouched seeds 401–420. Each pair had a different generator-known root
relation. The confirmatory schedule contained 400 pairs from each of ten case
families.

## Results

- H10-1 was supported: all 4,000 pairs had byte-identical L0–L3 projections
  and different hidden root relations.
- H10-2 was supported: source receipts made zero false independent-root
  acceptances across 2,800 copied-relation opportunities in the frozen
  honest-provider regime. The exact one-sided 95% upper bound was
  `0.00106933224`.
- H10-3 was supported: source receipts preserved all 3,600 target independent
  acquisitions. The exact one-sided 95% lower bound was `0.999168198285`.
- H10-4 was supported as a limitation: all 400 compromised-provider pairs
  remained byte-identical at L4 despite different hidden root relations.
- The runner marked H10-5 supported: no applicable `k < m` margin check
  changed its oracle root verdict. The check used the experiment's own
  `_root_votes` helper. Conformance of the shipped aggregator remains
  unverified by this run. The all-claims method had no applicable `k < m` cases.

The source-receipt method's overall pairwise-root F1 was `0.999606299213`; its
world-pair-clustered bootstrap 95% interval was
`[0.999568897638, 0.999641732283]`. The residual error comes from the expressly
compromised-provider family.

## Reproducibility

Two clean detached-worktree executions produced byte-identical scientific JSON
with SHA-256
`d3c360bb2dfe9ea869a7aa5c89d122ca62119595b30c55df1f53a1cb2ecc93c6`.
Runtime diagnostics are separate and intentionally noncanonical.

## Known reporting limitations

The runner reports a world-pair-clustered bootstrap interval for the primary
source-receipt pairwise-F1 diagnostic, but not for every descriptive metric of
every comparator. It also implements the preregistered exact formulas on the
observed boundary paths (zero copy errors and all independent acquisitions
preserved); an adverse nonboundary path would conservatively report an upper
bound of `1` or lower bound of `0` and reject the corresponding hypothesis
rather than calculate the promised general exact-binomial interval. These
limitations do not change H10-1 through H10-5 for the preserved result, but
they restrict secondary interval reporting and must be repaired in a future
runner version before reuse with nonboundary outcomes.

## Interpretation boundary

This experiment establishes a construction-level non-identifiability result
for the frozen L0–L3 interfaces and a conditional operational sufficiency
result for the frozen L4 policy under an honest provider. It does not show that
Minority Prophet can discover genuine causal independence from claims,
identities, signatures, language, or behavior. A provider receipt attests to a
provider-recorded acquisition event; it does not prove truth, competence,
absence of collusion, or independence from unobserved causes. The compromised
provider result is a deliberate counterexample to any universal root-integrity
claim.
