# Minority Prophet Test v0.1 Specification

## Task

Given a set of binary claims with agent-level confidence and competence metadata, predict hidden world truth. World truth is available only to the evaluator.

## Default generation regime

- 500 independently seeded worlds
- binary truth sampled uniformly
- 3 independent observers with 0.98 measurement accuracy
- 95 agents copying one false social origin
- deterministic generation from a disclosed integer seed

The default regime is deliberately extreme and diagnostic. It does not approximate a natural population, establish real-world source independence, or show that minorities are generally more accurate.

## Required output

Each method returns a belief in `{true, false, abstain}` and a probability assigned to `true`. Evaluations report truth accuracy, minority-truth recovery, Brier score, abstention rate, and mean compute time.

## Controls and anti-gaming

Future frozen evaluations must include independent-majority controls, ungrounded minority controls, incorrect instruments, hidden shared causes, sybil observers, temporal drift, and lineage corruption. Scores without generation configuration and seed are invalid.

## Baseline interpretation

The v0.1 weighted baseline is intentionally agent-based and does not solve copying. It establishes that confidence or competence weighting alone is insufficient under an overwhelming copied majority. Provenance-aware methods are reserved for the next public benchmark release after preregistration.

## Decision-relative independence extension (constructed only)

`decision-relative-independence-v0.1.json` is a set of falsification fixtures,
not a benchmark result. It reuses one evidence set under multiple decision
contexts and requires the evaluator to name the failure domain, independence
cut and minimum winning-root count. A method must expose when an alternative
cut materially changes settlement; it receives no credit for merely producing
more abstention. Cut selection from natural-language or runtime context remains
an untested research task and must be scored separately from root aggregation.
