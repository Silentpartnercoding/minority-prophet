# Preregistration: does weighting survive an adversary who chooses the weights?

**Status: frozen before any code for this experiment was written.** The hash in
`PREREGISTRATION.sha256` covers this file. Nothing below may change because of a result.

**Why this experiment.** Earlier exploratory work in `research/weight-sensitivity`
measured, honestly and without an adversary, that competence must be known to within
about fifteen percentage points before weighting beats counting. The whole combination
literature it rediscovered assumes an honest analyst estimating weights from data. This
programme's setting does not: an adversary may declare its own weight, may build a record
and then defect, and may concentrate weight on a source it controls. Whether the
crossover survives that has not been asked.

**Prior art, searched before designing, so this adopts rather than reinvents.**

- The finding that equal weights beat noisy estimated weights is the **forecast
  combination puzzle**, documented since the 1980s. Not ours.
- Against at most `k` adversaries, discarding the `k` highest and lowest reports and
  averaging the rest is a known optimal aggregator, and the regret depends on the
  **ratio** of adversaries rather than their count. Adopted as a baseline and reported
  as a ratio.
- **Trimmed mean and median** are the standard Byzantine-robust estimators with
  characterised breakdown points. Adopted.
- **Capping any one participant's weight** is the standard concentration defence.
  Adopted.
- **Breakdown point** is the standard robustness metric. Adopted as the primary
  outcome rather than inventing one.
- Whether forecasting skill transfers across domains is empirically studied: domain
  experts degrade across boundaries, while tournament forecasters show persistent
  relative skill over diverse questions. Our earlier note that this was unlocated was
  wrong and is corrected here.

## Hypotheses

**H1 — weighting lowers the breakdown point.** Under the declaration attack below, the
adversary fraction at which weighted aggregation first performs worse than a fair coin
is **strictly lower** than for uniform counting.

**H2 — capping restores it.** Capping any single source at `c = 2/n` of total weight
raises the weighted breakdown point to within **0.05** of uniform counting's, while
costing less than **0.02** accuracy in the adversary-free case.

**H3 — trimming beats plain weighting under attack.** At every adversary fraction from
0.1 to 0.4, symmetric trimming of the highest and lowest declared weights scores **at
least as high** as plain weighted aggregation.

**H4 — the honest crossover tightens under attack.** The competence-estimate tolerance at
which earned weighting beats counting is **tighter** under the sleeper attack than the
approximately 0.15 measured without an adversary.

## Design

Sources vote on a binary proposition with known truth. A fraction `f` are adversarial:
they know the truth and vote against it, and they coordinate.

**Attack A, declaration.** Each adversary declares the maximum permitted weight. Honest
sources declare their true competence. This attacks any scheme that reads a declared
weight.

**Attack B, sleeper.** Each adversary behaves honestly at competence 0.95 for the whole
scoring period, earning a large weight, then votes against the truth in the live round.
This attacks any scheme that reads an earned weight.

**Aggregators, all six run on identical worlds.**

1. `uniform` — one source, one vote.
2. `declared` — weight by the source's own declared competence, log-odds.
3. `earned` — weight by competence estimated from `k` scored outcomes, log-odds.
4. `capped` — as `declared`, with every weight clipped to at most `c = 2/n` of the total.
5. `trimmed` — discard the highest and lowest `ceil(f_max * n)` weights, then count the
   remainder equally.
6. `median` — the weighted median vote.

## Frozen parameters

    sources n                  15
    honest competence          uniform in [0.55, 0.95]
    adversary fractions f      0.00 to 0.50 in steps of 0.05
    scored outcomes k          60
    cap c                      2/n
    trim depth                 ceil(0.20 * n) per side
    trials per cell            40000
    seed                       1401
    tolerance sweep for H4     0.05, 0.10, 0.15, 0.20, 0.25, 0.30

## Outcome measures

- **Accuracy** against ground truth. An abstention scores 0.5.
- **Breakdown point**: the smallest `f` at which an aggregator's accuracy falls below
  0.5. Reported as a fraction, never a count.

## Pass and fail conditions, fixed now

- H1 passes if the weighted breakdown point is strictly below uniform's.
- H2 passes if capped breakdown is within 0.05 of uniform's **and** its adversary-free
  accuracy is within 0.02 of plain weighting's.
- H3 passes if trimmed is greater than or equal to plain weighted at every `f` in
  0.10 to 0.40 inclusive.
- H4 passes if the largest tolerance at which earned weighting still beats uniform is
  smaller under the sleeper attack than without an adversary.

Any hypothesis whose condition is not met is reported as **NOT SUPPORTED**. Thresholds
will not be adjusted afterwards, and a failed hypothesis is a result rather than a bug.

## Declared limits

Synthetic worlds with a known generator, conditionally independent honest sources, and a
single coordinated adversary. This can refute a claim about robustness under these
assumptions and cannot establish one about any real system. No theorem is produced. The
result does not bear on `U3`, which stays `underspecified`.
