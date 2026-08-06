# EXP009 — Selective provenance challenger

**Status: preregistered before confirmatory execution**

This experiment tests whether a provenance-aware method can recover grounded
minorities without inheriting the broad error rate of forced-choice inferred
lineage. It does not replace or reinterpret EXP008 or EXP007A.

## Prior exploratory work and separation

The policy and threshold were selected using EXP008's existing seeds `1–5`.
An exploratory local simulation on those seeds motivated a root-margin
threshold of `3`. Those worlds are development data and are excluded from all
confirmatory claims below. No confirmatory world from seeds `301–320` may be
examined before this protocol is committed and publicly timestamped.

## Question

Can simple majority remain the default while an inferred evidence-root
challenger selectively corrects copied false majorities, subject to a frozen
root-margin threshold, with no more than a one-percentage-point loss in
overall accuracy and no more than a one-percent false-reversal rate?

## Frozen world generator

The generator is `experiments/exp008_shootout.py::gen_world` as it exists at
the protocol commit. Each world contains eight binary propositions, one
originator, six independent observers, and forty descendants of the
originator. Evaluation covers both frozen EXP008 regimes:

1. `attack=False`; and
2. `attack=True`, the archived mixture of answer mutation, forged citations,
   sybil presentation, and clustered timing documented in that module.

This synthetic model does not represent a deployed agent population.

## Frozen methods

All existing EXP008 methods are retained as comparators:

1. simple majority;
2. Dawid–Skene;
3. TruthFinder;
4. ACCU-lite dependence discounting;
5. near-identical-answer cluster voting;
6. forced-choice inferred evidence-root voting; and
7. forced-choice declared-lineage evidence-root voting, reported only as an
   upper-bound diagnostic.

Two preregistered challengers are added:

### Primary: inferred selective challenger

For proposition `k`, let `M_k` be majority's answer, `R_k` the inferred-root
answer, and `G_k = |roots_1 - roots_0|` the inferred-root margin.

```text
if R_k is not a tie and R_k != M_k and G_k >= 3:
    answer R_k
else:
    answer M_k
```

The threshold is exactly `3`. It cannot be tuned on confirmatory worlds.

### Diagnostic: declared selective challenger

Apply the identical rule using the generator's true parent links. This is an
attested-provenance ceiling, not a deployable inference result.

## Separate execution-safety interpretation

The primary benchmark tests predictive aggregation and therefore falls back
to majority below threshold. A consequential authorization system must not
silently translate evidential uncertainty into permission. For a runtime
policy, below-threshold disagreement is reported descriptively as
`ESCALATE`, while agreement retains the authority provider's ordinary result.
Authorization coverage and escalation rate are secondary diagnostics and do
not substitute for the predictive hypotheses.

## Confirmatory evaluation set

- untouched PRNG seeds: `301–320` inclusive;
- `200` worlds per seed;
- `8` propositions per world;
- `32,000` proposition decisions per regime;
- both frozen regimes, evaluated independently;
- no threshold selection, optimizer, early stopping, or world exclusion.

## Metrics

For every method and regime report:

- overall accuracy;
- copied-minority recovery: accuracy where majority is wrong;
- false-reversal rate: fraction of all propositions where majority is right
  and the method changes it to a wrong answer;
- override rate relative to majority;
- precision of overrides;
- abstention or escalation rate where applicable; and
- mean computation time per world, reported descriptively.

World-clustered bootstrap 95% confidence intervals use seed `20260806` and
exactly `10,000` resamples. Worlds, not individual propositions, are the
resampling unit.

## Frozen hypotheses

The attack regime is primary.

- **H9-1 — baseline preservation:** the lower bound of the paired 95%
  bootstrap confidence interval for inferred selective-challenger accuracy
  minus simple-majority accuracy is at least `-0.010`.
- **H9-2 — reversal safety:** the upper bound of its 95% bootstrap confidence
  interval for false-reversal rate is at most `0.010`.
- **H9-3 — useful discretion:** its copied-minority recovery point estimate is
  at least `0.015`, and the lower bound of the paired 95% bootstrap confidence
  interval for recovery minus majority recovery is greater than `0`.
- **H9-4 — provenance ceiling:** the declared selective challenger recovers
  at least `0.80` of copied-minority cases with false-reversal rate at most
  `0.005`.

The primary selective-hybrid claim is `supported` only if H9-1, H9-2, and
H9-3 all hold under these frozen confidence-interval rules in the attack
regime. H9-4 is reported separately and cannot rescue a failed primary claim.
All non-attack results must be reported regardless of the verdict.

## Discriminator comparison

No method may be described as globally best. The report must identify, for
each comparator, whether it uses identity, behavior, agreement, timing,
citations, declared ancestry, or hidden generator truth. In particular:

- behavioral similarity is not proof of common evidence;
- signatures establish an issuer, not evidential independence;
- declared lineage is valid only to the degree its root-creation boundary is
  trustworthy; and
- the declared-lineage result is an upper bound, not an inference baseline.

## Leakage and integrity controls

- Seeds `301–320` cannot be used for debugging or threshold selection.
- Any implementation defect discovered after execution starts requires a
  versioned protocol deviation; the original output remains preserved.
- The runner must record the protocol commit, implementation commit, source
  SHA-256, Python/platform environment, configuration, and output SHA-256.
- Two clean detached-worktree executions must produce byte-identical
  scientific JSON before a canonical result is claimed.
- All outcomes, including rejection or practical nulls, must be retained.

## Interpretation boundary

Success would establish a selective policy result inside this frozen
synthetic model. It would not show that inferred ancestry is reliable in an
external deployment, that minorities are generally correct, or that an
evidence assessment itself grants authority. Failure would indicate that the
chosen behavioral discriminator or threshold does not preserve the proposed
tradeoff under the frozen attack.
