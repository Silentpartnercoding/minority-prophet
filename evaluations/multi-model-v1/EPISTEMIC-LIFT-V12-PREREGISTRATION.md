# Epistemic Lift v1.2 — prospectively powered, sealed confirmatory study

Status: **DRAFT. NOT FROZEN. NOT RUN.**

This document is not yet a preregistration. It becomes one when the owner
settles the open decision in section 3, a salt is drawn, and the seal is
committed. Nothing here has consumed a paid model call.

## 1. Why v1.2 exists

v1.1 passed its frozen rule on both model configurations, with zero B-to-C
regressions and exact paired p-values below 0.05. Its own interpretation
boundary is the reason that is not the end:

- the worlds are synthetic and were designed alongside the deterministic analysis;
- v1.0 outcomes on those same worlds were known before the v1.1 replication;
- there are only 32 worlds per model;
- there is no private held-out set or independent evaluator audit.

Two of the four items from the v1.0 required-next-study list are closed. The
provider-neutral raw capture landed and every cell completed. The two that
remain are sample size and a hidden set, and they are what this study is for.

## 2. What the power calculation found, before any money was spent

`lift-power.py` computes exact power over the trinomial outcome space for the
frozen decision rule: every model must show C minus B at or above an effect
threshold AND an exact two-sided paired sign test below 0.05.

**Finding 1. The sign test has a floor no sample size removes.** With d
discordant pairs all in one direction the two-sided p-value is 2 × 0.5^d. Six
discordant pairs are required before any result can clear 0.05. A run producing
five improvements and no regressions cannot pass, at any N.

**Finding 2. The design as specified is infeasible, and this is the important
one.** Holding the effect threshold at 0.10 while assuming a 10% improvement
rate and a 2% regression rate sets the expected observed effect at 8 points,
below the threshold itself. Power does not rise with N. It peaks near 0.08
joint at 96 worlds and then declines, because the observed effect concentrates
on 0.08 and the threshold is never met.

Joint power, conservative scenario, 10% improve and 2% regress:

| threshold | 48 | 64 | 96 | 128 | 160 | 192 |
|---|---:|---:|---:|---:|---:|---:|
| 0.100 | 0.03 | 0.07 | 0.08 | 0.07 | 0.07 | 0.03 |
| 0.075 | 0.03 | 0.10 | 0.23 | 0.32 | 0.38 | 0.32 |
| 0.050 | 0.03 | 0.10 | 0.29 | 0.50 | 0.67 | 0.77 |
| 0.040 | 0.03 | 0.10 | 0.29 | 0.50 | 0.67 | 0.80 |

An effect threshold must sit below the effect it is meant to detect. That is
the whole content of finding 2, and it was invisible at 32 worlds because the
observed v1.1 effects were so large.

## 3. The open decision, which is the owner's

The v1.0 requirement was to power for an effect smaller than 15 points. How
much smaller decides the cost, and the choice is a scientific one, not a
budgetary one.

| target | threshold | confirmatory worlds | joint power | run cost |
|---|---:|---:|---:|---:|
| detect 10-point improvement | 0.05 | 192 | 0.77 | $28.32 |
| detect 10-point improvement | 0.04 | 192 | 0.80 | $28.32 |
| detect 12.5-point improvement | 0.075 | 128 | ~0.32 | $18.88 |
| accept v1.1-sized effects only | 0.10 | 64 | ~1.00 | $9.44 |

Cost uses the v1.1 provider-reported figure of $0.14751 per world across both
models and all three conditions. The last row is honest but weak: it powers the
study only for an effect as large as the one already observed, which is close
to assuming the answer.

**Recommendation:** threshold 0.05, 192 confirmatory worlds, $28.32. State the
threshold in the frozen rule as a floor on the net difference, and report the
improvement and regression counts separately so a reader can apply their own.

## 4. Sealing the confirmatory set

`lift-split.mjs` assigns every generated world to development or confirmatory by
hashing its id with a salt fixed at seal time. Nobody chooses which worlds are
hidden. Anyone holding the seed, the repetition count and the salt can recompute
the assignment and check it was not adjusted afterwards.

The development set is written in full and may be inspected freely. The
confirmatory seal records ids, set digests, the salt and the generator
parameters, and deliberately omits world contents, so reading this repository
does not contaminate the held-out set.

Protocol:

1. Draw a salt. Run the splitter. Commit `confirmatory-seal.json` **before any
   model call.** A seal committed afterwards is not a commitment.
2. Do all prompt, parser and tooling work against the development set only.
3. Regenerate the confirmatory worlds from seed, repetitions and salt at run
   time, once.
4. Run every A/B/C cell. Do not repair or combine cells across runs, and do not
   re-run after inspecting outcomes.
5. Publish the verdict the rule returns, including a failure.

A roughly even split means generating about 447 worlds to seal 192.

## 5. What is still missing, and is not solved by this document

The v1.1 boundary asks for a benchmark "generated or audited independently of
the MP engine". The seal above delivers hidden and contamination-resistant. It
does **not** deliver independent: these worlds still come from the same
generator, written by the same author, as the analysis they test. An external
party generating or auditing a world set is a separate piece of work and should
not be quietly folded into this one.

## 6. Authority and cost

Execution requires paid model API calls. The signed worker identity used to
prepare this study does not carry paid-API authority, so the run stops here
until the owner authorises it explicitly.

At the time of writing the OpenRouter balance is $4.84 against a $28.32
recommended run. The study cannot start, and a partial run is worse than none:
three missing cells were sufficient to invalidate the entire Claude arm of v1.0.
