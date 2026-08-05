# Finite Łoś-inspired pilot — results

**Artifact status: CANONICAL (exploratory).** Frozen in-repository pilot output; not a confirmatory result.

Frozen run: seed `20260803`, 2,000 worlds per main regime, 10,000 main-regime worlds, plus 6,500 corruption-sweep worlds.

## Main results

| Regime | Proposition majority | Evidence-root vote | Semantic coalition |
| --- | ---: | ---: | ---: |
| Copied false majority | 0% | 100% | 100% |
| Independent true majority | 100% | 100% | 100% |
| Unsupported false minority | 100% | 100% | 100% |
| Doctrinal split | 0% exact; 0% consistent | 0% exact; 0% consistent | 100% exact; 100% consistent |
| Fully corrupted lineage | 0% | 0% | 0% |

In the doctrinal split, the two proposition-wise methods got two of three propositions right but combined them into a model violating `r ↔ (p ∧ q)`. The semantic method selected a submitted complete model and preserved the constraint.

## Lineage corruption boundary

The root-vote method remained correct with 0–1 forged roots, abstained with 2, and selected the false model from 3 onward.

The semantic method remained 100% correct through 3 forged roots. At 4 forged roots it was 69.2% correct and abstained on 30.8%. At 5 it was 8.6% correct and abstained on 91.4%. At 6 it abstained on 95.4% but was wrong on the remaining 4.6%. From 9 forged roots onward it consistently selected the false model.

## Interpretation

The implementation behaves as designed when lineage and competence metadata are correct: copied claims stop acting like independent votes, and selecting a complete valid model avoids proposition-wise logical inconsistency.

The stronger finding is the failure boundary. Logical coherence cannot rescue fabricated provenance. A coherent false model wins once enough copied claims masquerade as independent evidence. Identity and lineage verification are therefore assumptions of this method, not solved outputs.

## What this does not establish

- It does not validate Łoś's theorem as a truth-selection procedure.
- It does not show that real-world source independence can be identified.
- It does not estimate performance on natural claims or language-model debates.
- Perfect scores reflect deliberately separated synthetic regimes, not generalization.
- The exact pilot protocol was implemented before this report was frozen; v0.2 must be preregistered before execution.

Machine-readable output: [`los-inspired-v0.1-seed-20260803.json`](los-inspired-v0.1-seed-20260803.json).
