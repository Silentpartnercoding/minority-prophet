# Minority Prophet documentation

This is the map of the project. It adds navigation without relocating or
rewriting historical research artifacts.

## Choose a path

| Goal | Recommended path |
|---|---|
| Learn the concept | [Public claims](../PUBLIC-CLAIMS.md) → [Foundations](../FOUNDATIONS.md) → [Glossary](../GLOSSARY.md) |
| Check what is actually supported | [Evidence status](evidence/STATUS.md) → [Evidence map](evidence/README.md) |
| Run something | [Use guide](use/README.md) → [Benchmark](../benchmark/) or [runtime engine](../evaluations/multi-model-v1/RUNTIME-README.md) |
| Understand the system | [Architecture map](architecture/README.md) → [System architecture](../SYSTEM-ARCHITECTURE.md) |
| Review the research | [Research map](research/README.md) → [current paper](../papers/00-CURRENT-PAPER.md) |
| Contribute or reproduce | [Contributor map](contributing/README.md) → [Contributor quickstart](../CONTRIBUTOR-QUICKSTART.md) |
| Browse by directory | [Repository map](repository-map.md) |

## How authority works here

The repository contains explanations, proposals, experiments, generated
outputs, and immutable research records. They do not all carry the same weight.
For a present-tense public claim, use this order:

1. [`research/records/`](../research/records/) supplies content-bound,
   machine-readable lifecycle records.
2. [`CANONICAL-RECORDS.md`](../CANONICAL-RECORDS.md) identifies canonical and
   imported evidence packages.
3. [`EVIDENCE-ALIGNMENT.md`](../EVIDENCE-ALIGNMENT.md) maps claims to records and
   records corrections or blockers.
4. [`formal/THEOREM-LEDGER.json`](../formal/THEOREM-LEDGER.json) and
   [`formal/CLAIM-SCOPE.md`](../formal/CLAIM-SCOPE.md) bound formal claims.
5. [`PUBLIC-CLAIMS.md`](../PUBLIC-CLAIMS.md) is the shortest public summary of
   those sources.

README files and website copy are guides. A newly written explanation cannot
promote an experiment or overrule an adverse result.

## Stable entry points

These files intentionally remain at their existing paths because papers,
reviews, and external links may depend on them:

- [`PUBLIC-CLAIMS.md`](../PUBLIC-CLAIMS.md)
- [`CANONICAL-RECORDS.md`](../CANONICAL-RECORDS.md)
- [`EVIDENCE-ALIGNMENT.md`](../EVIDENCE-ALIGNMENT.md)
- [`SYSTEM-ARCHITECTURE.md`](../SYSTEM-ARCHITECTURE.md)
- [`ROADMAP.md`](../ROADMAP.md)
- [`papers/00-CURRENT-PAPER.md`](../papers/00-CURRENT-PAPER.md)
- [`CONTRIBUTING.md`](../CONTRIBUTING.md)

Earlier papers, null results, rejected candidates, incomplete runs, and
superseded materials remain preserved. Navigation should make their status
clear, never hide them.
