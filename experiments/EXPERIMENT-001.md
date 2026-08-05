# Experiment 001 — Finite Semantic Aggregation Pilot

**Artifact status: CANONICAL (exploratory).** Frozen in-repository pilot; not a blinded confirmatory experiment.

## Status

Exploratory pilot completed on seed `20260803`. This was not a literal application of Łoś's theorem and was not a blinded confirmatory experiment.

## Question

Can a finite method inspired by model-theoretic aggregation recover truth under copying and preserve a logical relationship that proposition-wise voting can break?

## Null hypothesis

Evidence-root and consistency-constrained semantic aggregation provide no improvement over proposition-wise majority voting in copied-majority or logically coupled worlds.

## Methods

Each agent submits a complete three-proposition model `(p, q, r)`. Valid models satisfy the public constraint `r ↔ (p ∧ q)`.

1. **Proposition majority:** votes on `p`, `q`, and `r` separately and ignores lineage.
2. **Evidence-root vote:** collapses duplicate root identifiers, then votes separately.
3. **Semantic coalition:** collapses duplicate roots, scores submitted valid models by confidence- and competence-weighted agreement, selects a complete model, and abstains when the normalized support margin is below `0.05`.

The semantic coalition is a finite proxy. A genuine ultraproduct requires a specified ultrafilter and does not itself identify epistemically trustworthy sources.

## Regimes

- **Copied false majority:** 3 independent correct roots and 95 copies of one false root.
- **Independent true majority:** 95 independent correct roots and 3 false roots.
- **Unsupported false minority:** 7 independent correct roots and 3 false claims without evidence roots.
- **Doctrinal split:** three individually consistent models whose proposition-wise majority violates `r ↔ (p ∧ q)`; the correct complete model has higher declared competence.
- **Corrupted lineage:** the 95 copied false claims falsely appear to have independent roots.
- **Corruption sweep:** 0–12 of the copied claims receive forged root identities while the rest share one rumor root.

## Frozen run

- 2,000 worlds per main regime
- 10,000 total main-regime worlds
- 500 worlds at each corruption level
- Seed `20260803`; sweep seed `20260804`

## Metrics

- exact complete-model truth accuracy
- proposition-level accuracy
- logical consistency among answered worlds
- abstention rate
- mean computation time

## Success and failure conditions

The pilot succeeds if the ancestry-aware methods improve copied-majority exact accuracy by at least 15 percentage points, lose no more than 2 points in the two controls, and semantic aggregation preserves the logical constraint.

It fails as a general result if gains depend on perfect lineage, declared competence that encodes the answer, or constructed candidate models.

## Reproduction

```bash
python -m experiments.los_inspired_v01 \
  --worlds-per-regime 2000 \
  --seed 20260803
```
