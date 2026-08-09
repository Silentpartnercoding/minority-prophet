# LIR-1E confirmatory analysis lock

**Status:** frozen before any confirmatory model request, response, label opening,
materialization, or score.

- Cases: the 36-case inventory committed in `INVENTORY-COMMITMENTS.json`.
- Models and call ceiling: `EXECUTION-CONFIG.confirmatory.json`.
- Parent threshold: `0.85`, selected by the committed development result.
- Hidden fractions: `0.05, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95`.
- Primary fraction: `0.40`.
- Bootstrap: 10,000 resamples of whole cases with replacement, seed `20260808`.
- Primary success: at least 30 complete cases; root-pair F1 at least `0.60`;
  and the lower 95% case-bootstrap bound for declared advantage survival
  strictly above `0.25`.
- Undefined survival bootstrap replicates are excluded and counted. If no
  replicate is defined, the survival condition fails.
- Parent, root-count, all-fraction, no-text, no-time, model usage, source
  adherence, retries, and missing records are diagnostics and cannot rescue a
  failed primary criterion.
- No threshold, mutation, prompt, source, model, retry, exclusion, or success
  rule changes after the first confirmatory request.

The scorer consumes the sealed labels only after all model responses are closed.
Inference receives `ClaimInstance.feature_view()` only.
