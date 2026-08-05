# Experiment 002 — Resolved Weather Markets

**Artifact status: CANONICAL (preregistration).** The completed analysis retains explicit pending checks; it is not a substitute for the planned canonical reruns.

## Status

Preregistered before downloading market records or resolved outcomes. Protocol changes after the preregistration commit must be versioned and reported as deviations.

## Question

Can dependence-adjusted aggregation of visible trading behavior improve calibration or recover correct underdogs in repeated, externally resolved binary weather markets without increasing false majority reversals?

## Scope

This is a historical observational study. It places no trades and uses only public market metadata, price history, and public transaction records.

## Data source

One public prediction-market API will supply:

- closed market metadata and resolution;
- historical prices;
- public trades with pseudonymous wallet identifiers where available.

Provider-specific fields will be normalized into a provider-neutral snapshot. The provider is a data source and benchmark, not a project dependency or sponsor.

## Eligibility fixed before acquisition

Include a market only when all conditions hold:

1. tagged as weather;
2. exactly two outcomes;
3. closed with an unambiguous `0/1` resolution;
4. fixed start and end timestamps;
5. duration between 24 hours and 90 days;
6. at least USD 1,000 reported volume;
7. at least one historical price at or before 24 hours before the end timestamp;
8. at least 10 pseudonymous wallets with classifiable net direction before the cutoff;
9. no cancellation, split resolution, or outcome value other than exactly 0 or 1;
10. the complete public trade history is retrievable within documented API pagination bounds, with no detected truncation.

The primary cutoff is the last public observation at or before 24 hours before the recorded end timestamp. Secondary cutoffs at 72 and 6 hours are descriptive and cannot replace the primary result.

If fewer than 100 markets satisfy the rules, the confirmatory run terminates as **insufficient eligible data**. Any smaller analysis must be labeled exploratory and cannot satisfy the hypothesis.

## Frozen methods

1. **Market probability:** last YES-token price at or before the cutoff.
2. **One-wallet vote:** each wallet's net signed pre-cutoff exposure contributes one binary direction; repeated trades do not add votes.
3. **Exposure-weighted:** absolute net exposure weights each wallet direction.
4. **Dependence-adjusted:** wallets with cosine similarity at least `0.90` across hourly signed-trade vectors, with at least three jointly active bins, form a connected component. Each component contributes one vote based on aggregate direction.
5. **Abstaining dependence-adjusted:** same probability as method 4, but abstains when there are fewer than 10 effective components or the probability is between `0.45` and `0.55` inclusive.

`Dependence-adjusted` is a behavioral-correlation proxy. It does not prove copying, common evidence, shared control, or identity.

## Outcomes and metrics

Primary metric: Brier score at the 24-hour cutoff.

Secondary metrics:

- forced-choice accuracy at threshold `0.50`;
- expected calibration error using ten fixed bins;
- correct-underdog recovery where one-wallet probability is below `0.50` for an outcome that resolves `1`;
- false-majority reversal rate where one-wallet voting is correct but another method selects the opposite outcome;
- abstention rate and selective accuracy among answered markets;
- effective component count and wallet concentration.

## Hypotheses

**H2a:** Dependence adjustment has lower Brier score than one-wallet voting.

**H2b:** Dependence adjustment recovers more correct-underdog cases than exposure weighting without a higher false-majority reversal rate.

**H2c:** The abstaining method has higher answered-case accuracy than non-abstaining dependence adjustment, at the cost of lower coverage.

## Null hypotheses

The dependence-adjusted method does not improve Brier score or correct-underdog recovery, and abstention does not improve answered-case accuracy.

## Decision rules

- Report paired bootstrap 95% confidence intervals over markets using seed `20260805` and 10,000 resamples.
- H2a requires the full confidence interval for paired Brier improvement over one-wallet voting to be above zero.
- H2b requires positive underdog net gain and no increase greater than 2 percentage points in false-majority reversals.
- H2c requires at least 2 percentage points higher selective accuracy with at least 50% coverage.
- Market price remains the strongest external benchmark; failure to beat it must be reported prominently.

## Leakage controls

- No trade or price after the cutoff enters a forecast.
- Resolution fields are used only for scoring after predictions are frozen.
- Market eligibility cannot depend on whether a method predicted correctly.
- All eligible markets are retained; no manual removal based on surprising results.
- Raw pseudonymous identifiers are hashed in committed derived data.

## Known limitations

- A wallet is not necessarily a person.
- Public trades may not reconstruct complete positions or private hedges.
- Correlated timing is not proof of dependence.
- Market end timestamps may imperfectly represent the moment information became public.
- Weather contracts can share underlying events and therefore may not be statistically independent.
- Resolution rules and measurement stations can introduce label error.
