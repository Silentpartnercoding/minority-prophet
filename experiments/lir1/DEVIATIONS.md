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

## D2 — 2026-08-08 — LIR-1E first command failed local schema validation

The first development command was rejected locally by Claude Code because its
structured-output option does not accept the JSON Schema draft declaration.
No prompt reached a model and no answer was generated. The runner's fail-fast
control stopped before the other 59 requests. The private command receipt and
invalid response wrapper are preserved under
`artifacts/lir1/llm_echo/development/invalid-preflight-20260808T2032Z/`.

The adapter now removes only the `$schema` and `$id` metadata before passing the
otherwise unchanged answer schema to Claude Code. This does not change any
case, prompt, model assignment, answer field, validation constraint, label, or
analysis rule. The development run may start cleanly because the failure
occurred before provider execution or outcome inspection.
