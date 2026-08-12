# Minority Prophet Epistemic Lift v1.1 — complete development result

Status: **COMPLETED / VALIDATED DEMO**

Frozen candidate verdict: **SUPPORTED_IN_FROZEN_CANDIDATE**

This is a complete local development-set result. It is not an official leaderboard result, a hidden evaluation, or an independent external confirmation.

## Controlled comparison

Each model received the same frozen world in three conditions:

- **A — Raw baseline:** claims and ordinary source labels only.
- **B — Provenance:** the exact A world plus declared ancestry, timestamps, control domains, observation origins, and context.
- **C — Minority Prophet:** the exact B payload plus one deterministic, read-only evidence-structure receipt computed exclusively from B-visible bytes.

The receipt contained no ground truth, correct answer, recommended answer, external retrieval, or execution authority.

## Full results

| Model | A baseline | B provenance | C + Minority Prophet | B − A | C − B | Exact paired p for C − B |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.6 Sol | 4/32 (12.5%) | 22/32 (68.75%) | 31/32 (96.875%) | +56.25 points | **+28.125 points** | **0.003906** |
| Claude Sonnet 5 | 1/32 (3.125%) | 22/32 (68.75%) | 29/32 (90.625%) | +65.625 points | **+21.875 points** | **0.015625** |

GPT produced nine B-to-C improvements and zero regressions. Claude produced seven improvements and zero regressions.

Both preregistered configurations exceeded the frozen requirement of at least 15 percentage points of C-over-B lift and an exact paired two-sided p-value below 0.05.

## Integrity

- 32 frozen worlds
- two model configurations
- three matched conditions
- 192/192 completed cells
- zero provider failures
- zero parse failures
- the same world, system prompt, and concrete model version across A/B/C
- exact B/C base-payload equality
- MP receipt present only in C
- all six condition orders counterbalanced

Frozen protocol commit: `0b7291015d78897474eb3d8ad6a3c093df9f5c4f`

Manifest: `sha256:7bf6d393e59ce6fbc78ca41bda4f71b5a0c29dc95d2b535bb19901c345bf3943`

MP tool contract: `sha256:fac9d675d2c77998174a6d934a4c24ff4e3258b69b812d1a02d54365db59394a`

Result report: `sha256:396a3330d2368804e7bdb79ba7d3e028dea80573c13693bb8b94c06c83719c98`

## Defensible interpretation

On this frozen 32-world development candidate, both tested model configurations showed more than 20 percentage points of paired truth-recovery lift when the exact provenance payload was augmented with the deterministic Minority Prophet receipt. Neither model regressed on a B-to-C pair.

This does not establish external validity. The worlds are synthetic, were designed alongside the analysis, and had been exposed in an earlier transport run. A public scientific claim requires a larger hidden set generated or audited independently of the MP engine, contamination controls, and prospective power.
