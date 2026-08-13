# Epistemic Lift v1.1 — complete raw-capture replication

Status: **COMPLETED / VALIDATED DEMO**

Verdict under the frozen candidate decision rule: **SUPPORTED_IN_FROZEN_CANDIDATE**

This is a complete local development-set result. It is not an official leaderboard result or an independent confirmation on hidden worlds.

## Frozen identity

- Protocol commit: `0b7291015d78897474eb3d8ad6a3c093df9f5c4f`
- Manifest: `sha256:7bf6d393e59ce6fbc78ca41bda4f71b5a0c29dc95d2b535bb19901c345bf3943`
- MP tool contract: `sha256:fac9d675d2c77998174a6d934a4c24ff4e3258b69b812d1a02d54365db59394a`
- Runtime-state SHA-256: `dc13e6559be51f61c4854868c06ef2efba3fa0dcc9c5413610e3affaf619ce2f`
- Result JSON SHA-256: `5f45bbd5e414efcead1266b2257466b74f0ac475678b6ae892c8636f25cac391`
- Result Markdown SHA-256: `bf985e836b9fe5319c23bb7270026fc6a951678375008ee25eab3e4ebc17a96c`
- Namespace: DEMO

## Full results

| Model | A baseline | B provenance | C + Minority Prophet | B − A | C − B | Exact paired p for C − B |
|---|---:|---:|---:|---:|---:|---:|
| `gpt-5.6-sol` | 4/32 (12.5%) | 22/32 (68.75%) | 31/32 (96.875%) | +56.25 points | **+28.125 points** | **0.003906** |
| `claude-sonnet-5` | 1/32 (3.125%) | 22/32 (68.75%) | 29/32 (90.625%) | +65.625 points | **+21.875 points** | **0.015625** |

Paired B-to-C transitions:

- GPT: nine improvements, zero regressions, 22 unchanged-correct, one unchanged-incorrect.
- Claude: seven improvements, zero regressions, 22 unchanged-correct, three unchanged-incorrect.

Both preregistered model configurations exceed the frozen 15-point effect threshold and the exact paired p < 0.05 threshold.

## Integrity result

All automated verification checks passed:

- 192/192 expected cells completed;
- 192/192 raw responses parsed locally;
- zero failed trials;
- all world hashes matched;
- the same world, system prompt, and concrete model version were used across A/B/C;
- every B/C epistemic base matched exactly;
- the MP receipt appeared only in C and used the pinned contract;
- condition ordering was recorded and counterbalanced;
- all scores were recorded.

## Interpretation boundary

This run demonstrates a large, statistically detectable Minority Prophet lift beyond provenance alone on these constructed development worlds and these two locally authenticated model configurations.

It does not yet establish external validity because:

- the worlds are synthetic and were designed alongside the deterministic analysis;
- v1.0 results on the same worlds were known before this transport replication;
- there are only 32 worlds per model;
- there is no private held-out set or independent evaluator audit;
- hosted CLI model aliases and serving behavior can change.

The scientifically defensible statement is:

> On the frozen 32-world development candidate, both tested models showed more than 20 percentage points of paired truth-recovery lift when the exact provenance payload was augmented with the deterministic Minority Prophet receipt, with zero B-to-C regressions and exact paired p-values below 0.05.

The next requirement before public empirical claims is a prospectively powered, hidden, contamination-resistant benchmark generated or audited independently of the MP engine.

## Telemetry

- Completed model trials: 192
- Recorded input tokens: 1,632,471
- Recorded output tokens: 103,152
- Recorded cached tokens: 987,904
- Provider-reported cost estimate: $4.72028
- Provider-reported cost per world: $0.14751
