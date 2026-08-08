# LIR-1 deviations

## D1 — 2026-08-08 — first PHEME execution scored all edges, not hidden edges

The first confirmatory command completed, but inspection showed that
`parent_metrics` scored visible and hidden edges together. At 40% hiding, the
remaining 60% of explicit edges were copied directly into predictions, so the
reported parent F1 did not measure hidden-parent recovery as preregistered.

The invalid output is preserved at
`results/lir1-pheme-confirmatory-v0.1/superseded/result-all-edges.json`. Its
criterion verdict is void. No valid confirmatory result is claimed. Because
all original confirmatory cases were passed through the runner, they are no
longer described as untouched.

The metric now accepts an explicit evaluation set and both PHEME runners pass
only claim IDs whose recorded edge was hidden. Development threshold selection
must be repeated under the corrected metric and frozen again. A future
confirmatory claim requires a newly registered disjoint holdout; rerunning the
same cases may be reported only as a post-deviation diagnostic.
