# Epistemic Lift v1 — frozen candidate result

Status: **INCOMPLETE / NOT VERIFIED**

This is a local candidate-development result. It is not eligible for the public leaderboard and does not establish the cross-model hypothesis.

## Frozen identity

- Protocol commit: `8059049d2730c87139d781b56018550e21b658f2`
- Manifest: `sha256:27f03b6fa35938eb5c81fc3f255aac17aa523b7802e68f52d8fba6b8d2518b7f`
- Runtime-state SHA-256: `ab92e6819efc707ab27b854c95a16827227bec5a915c9e5cd28de30753423f11`
- Expected cells: 192
- Valid completed cells: 189
- Missing cells after the preregistered retry cap: 3
- Namespace: DEMO

## Results

| Model | A baseline | B provenance | C + MP | Observed C − B | Exact paired p | Protocol result |
|---|---:|---:|---:|---:|---:|---|
| `gpt-5.6-sol` | 4/32 (12.5%) | 24/32 (75.0%) | 29/32 (90.6%) | +15.6 points | 0.0625 | Effect-size threshold met; significance threshold missed |
| `claude-sonnet-5` | 4/31 (12.9% complete case) | 21/32 (65.6%) | 26/30 (86.7% complete case) | +20.0 points across 30 complete B/C pairs | 0.03125 complete case | Invalid primary arm because three cells are missing |

For Claude, treating the two missing C responses as incorrect yields C = 26/32 (81.25%), an observed C − B difference of +15.6 points and exact paired p = 0.125. This conservative sensitivity analysis does not pass the preregistered significance rule.

## What this means

The direction and size of the observed changes are encouraging in both model configurations. The complete Codex arm shows a measurable +15.6-point C-over-B difference, but the exact paired test narrowly misses the frozen threshold. Claude's complete cases show a larger and nominally significant difference, but that arm cannot support the preregistered claim because the missing outcomes were condition-dependent.

Therefore the frozen decision is:

> **H2 is not established by this candidate run.**

This is not evidence that Minority Prophet has no effect. It is evidence that a larger study and a more reliable provider-neutral response transport are required before making the claim.

## Failure record

All three terminal failures came from the Claude CLI's structured-output layer after both allowed outer attempts:

- `mp_lift_00005`, Condition C
- `mp_lift_00017`, Condition A
- `mp_lift_00019`, Condition C

The raw attempts remain in the ignored local runtime store. They were not replaced, deleted, or retried beyond the frozen cap.

## Required next study

1. Freeze a provider-neutral transport that records a model's raw text once and parses it outside the provider, avoiding provider-internal structured-output retry behavior.
2. Use more than 32 worlds per model and prospectively power the study for a smaller effect than 15 points.
3. Rerun every A/B/C cell under the revised transport; do not combine repaired cells with this run.
4. Add at least one held-out or externally reviewed world set before any public empirical claim.
