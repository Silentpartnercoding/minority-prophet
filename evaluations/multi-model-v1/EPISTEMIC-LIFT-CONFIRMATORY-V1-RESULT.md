# Epistemic lift, confirmatory run v1

Run id `openrouter-confirmatory-v1`. World set sealed before the first model call.
Executed 13-14 September 2026 against OpenRouter.

**The receipt beats a neutral control on all three models.**

## Why this run exists

Versions 1.0 and 1.1 compared the Minority Prophet receipt against plain provenance.
They had no control for the possibility that *any* structured hint would have produced
the same gain. That is the first objection a reviewer raises, and it was unanswered.

This run adds `C_NEUTRAL_ROOT_INDEX`: the same shape of structured hint, in the same
position, with the analysis stripped out. The primary contrast is therefore **D minus
C**, not C minus B.

## Result

Preregistered rule: every model must show a paired gain of at least 0.03 with an exact
two-sided sign test below 0.05.

| Model | Paired worlds | C neutral | D receipt | D − C | Improved | Regressed | p | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| anthropic/claude-sonnet-4.6 | 288 | 0.483 | 0.778 | +0.295 | 85 | 0 | <0.000001 | **PASS** |
| openai/gpt-4.1 | 289 | 0.474 | 0.619 | +0.145 | 43 | 1 | <0.000001 | **PASS** |
| google/gemini-2.5-flash | 282 | 0.486 | 0.567 | +0.082 | 24 | 1 | 0.000002 | **PASS** |

Across 859 paired worlds: 152 improvements, 2 regressions.

Secondary contrast, D over B, which is what v1.0 and v1.1 measured:

| Model | n | B | D | Gain |
|---|---:|---:|---:|---:|
| anthropic/claude-sonnet-4.6 | 276 | 0.446 | 0.772 | +0.326 |
| openai/gpt-4.1 | 284 | 0.482 | 0.634 | +0.151 |
| google/gemini-2.5-flash | 277 | 0.480 | 0.585 | +0.105 |

## The effect grew with scale

The 28-world diagnostic on 25 August showed +0.250, +0.107 and +0.093 on the same
primary contrast. At roughly 290 worlds the figures are +0.295, +0.145 and +0.082.
A promising small result usually shrinks under proper testing. This one did not.

## Design

- 294 worlds, sealed before any model call, cohort balance 126 false-majority,
  126 correct-majority, 42 abstention
- Three conditions, six-permutation counterbalanced order by model and world
- Closed world: no tools, no retrieval, reasoning disabled, temperature 0
- Prospective power 0.98 per model, 0.94 joint, for a 10-point effect at a 0.03
  threshold, computed before the run by `lift-power.py`

The threshold is 0.03 rather than 0.10 because the power calculation found the original
design self-defeating: an expected effect of 0.08 against a 0.10 bar, with power peaking
near 0.08 joint at 96 worlds and then declining. Corrected before the run, not after.

## Reproduce

```sh
OPENROUTER_API_KEY=... npm run run:openrouter:real
node openrouter-confirmatory-v1.js
```

`real-test-worlds.js` takes a repetition count; the sealed set is 21 repetitions.
Verify the world set against `world_set_sha256` in `CONFIRMATORY-SEAL-v1.json` before
trusting any comparison to these numbers.

## Where the raw run state is

The per-cell record is about 15 MB and lives at
`evaluations/multi-model-v1/data/runtime/openrouter-confirmatory-v1-state.json`.
That path is gitignored by this directory's own `.gitignore`, so it is **not** in this
repository and this commit does not change that.

At time of writing it exists on one machine only, M4. It is the raw evidence behind
every number above and it has no second copy. Giving it a durable home is an owner
decision, not a code change.

## Boundaries, which must travel with any use of these numbers

- The worlds are constructed by the same programme that built the analysis. This is
  hidden and contamination-resistant, it is **not** independently generated or audited.
- 2,576 of 2,646 cells completed. The 70 missing are parse failures that exhausted their
  two attempts, not unattempted cells.
- Structured-output failures were not evenly distributed. That is an observation about
  output-contract compliance, not a claim about reasoning quality.
- Cost $27.19. This is a development-set confirmatory run, not an official leaderboard
  result and not a third-party replication.

## What it changes elsewhere

The investor deck describes the v1.0 or v1.1 figures, which came from a design with no
neutral control. Those numbers are both weaker and easier to attack. Slide 9 and anything
citing the lift study should be revisited against this result.
