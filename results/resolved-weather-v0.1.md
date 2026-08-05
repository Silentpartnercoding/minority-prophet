# Experiment 002 — Resolved Weather Markets

**Artifact status: CANONICAL (preregistered, incomplete).** Matched-coverage and price-uncertainty controls remain pending. The underlying raw market data and
identifiers are not included in this release.

## Summary

The Minority Prophet property has two requirements: recover independently
grounded minorities, and reject ungrounded ones. Experiment 1 tested recovery
in constructed worlds with declared lineage. This preregistered Experiment 2
tests both halves in the wild: 5,729 resolved weather markets, chosen as a
deliberately hostile, low-independence domain where many participants are
likely drawing from the same small set of forecast roots.

The recovery result is a clear preregistered null: no head-count method beat
market price, and dependence adjustment added no truth-recovery advantage
(H2a and H2b rejected). The key finding is the rejection half. When the
dependence-adjusted method overruled a one-wallet majority, its false-reversal
rate was 0.10%, versus 9.50% for exposure weighting. Its abstaining version
also lifted answered-case accuracy by 4.6 percentage points at 88.9% coverage.

This does not establish that behavioral similarity proves copying or that the
method beats market price. It is a real-market calibration point for the
provenance-threshold account: below sufficient independence structure, the
method should be reluctant to overrule the crowd. Weather appears to sit below
that threshold for this proxy.

## Preregistered protocol

The protocol, eligibility rules, cutoff, methods, hypotheses, and decision
rules were committed before acquisition in
`experiments/EXPERIMENT-002-PREREGISTRATION.md`. The study used public,
historical market metadata, price history, and public trade records only; it
placed no trades.

The primary comparison was at the final public observation at or before 24
hours before market end. Eligible markets required weather tagging, a binary
resolved outcome, adequate duration and volume, an available pre-cutoff price,
at least ten classifiable wallets, and retrievable complete public trade
history within pagination bounds.

## Confirmatory results

| Method | Markets | Accuracy | Brier score |
| --- | ---: | ---: | ---: |
| Market price | 5,729 | 89.72% | 0.07441 |
| One-wallet vote | 5,729 | 83.98% | 0.12207 |
| Dependence-adjusted components | 5,729 | 83.91% | 0.12228 |
| Exposure-weighted vote | 5,729 | 83.14% | 0.12892 |

### H2a — calibration improvement over one-wallet voting

**Rejected.** The paired Brier difference for dependence adjustment versus
one-wallet voting was -0.000207 (95% bootstrap CI [-0.000276, -0.000142]).
The sign is statistically resolved at this sample size but the magnitude is
practically negligible: dependence adjustment added no useful calibration in
this dataset.

### H2b — correct-underdog recovery without false reversals

**Rejected.** Dependence adjustment recovered 1 correct underdog, compared
with 58 for exposure weighting. Its false-majority reversal rate was much
lower (0.10% versus 9.50%), so the two methods occupy different
precision/recall positions; nevertheless, the preregistered claim that
dependence adjustment would recover more underdogs than exposure weighting
was not supported.

### H2c — abstention

**Supported only in the preregistered narrow sense; not a market-beating
claim.** The abstaining dependence-adjusted method answered 5,094 of 5,729
markets (88.92% coverage) with 88.52% accuracy, compared with 83.91% for the
non-abstaining dependence-adjusted method. That satisfies the preregistered
comparison. However, market price achieved 91.42% accuracy on those exact
same 5,094 answered markets. Abstention identified a harder slice of markets;
it did not produce a better forecast than the market.

## Exploratory Stage 2c — stake-weighted root counting

We then tested the obvious follow-up: let components contribute according to
their net stake exposure rather than treating every wallet/component equally.
This was exploratory and used a fresh public historical pull, so it is not a
byte-for-byte rerun of the confirmatory frame.

On 5,173 eligible markets from 10,191 candidates:

| Method | Accuracy | Brier score |
| --- | ---: | ---: |
| Market price | 89.89% | 0.07363 |
| Stake-weighted root counting | 83.12% | 0.12880 |

**Result:** stake weighting did not close the gap. In this weather dataset,
neither head-counting, component-counting, nor this first stake-weighted
root-aware method improved on the market price.

## Interpretation and limits

Market price already aggregates information with real financial exposure. In
weather, many traders may rely on the same forecast sources, so visible
behavioral similarity need not reveal enough independent provenance to add
predictive value. These results do not show that provenance-aware aggregation
cannot help in other domains; they show that this proxy did not help here.

A wallet is not necessarily a person. Public trades may not reconstruct full
positions or private hedges; correlated timing is not proof of copying; and
weather markets can share underlying events. The acquisition/scoring runner,
aggregation code, tests, and a hash manifest of the derived result are public.
Raw trade data and pseudonymous identifiers are intentionally not retained in
the repository, so the committed derived record is canonical while a
byte-identical replay of the mutable upstream API response is not claimed.

## Public conclusion

**In a low-independence real-market domain, dependence adjustment correctly
declined to overrule the crowd almost all the time (0.10% false reversals), but
did not recover enough grounded minorities to beat market price. The result
supports the rejection half of the Minority Prophet property; recovery awaits
a domain with more independent evidence structure.**

The first exploratory stake-weighted root-counting follow-up also did not add
value over market price.
