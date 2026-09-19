# A frozen criterion that no possible result could satisfy

`probe.py` beside this file reproduces every number from the frozen result. It
reads `results/hgd1-v1/result.json` and computes nothing that is not already
there. Nothing in this document changes that result, and nothing in it should.

## The finding

HGD-1's primary claim was rejected because HGD-1g failed. HGD-1g required, on
the frozen EPA counterfactuals, that interval accounting show a
false-confident-error reduction against head count of **at least 5 percentage
points at one or more injected shifts**.

`experiments/hgd1/run_hgd1.py` scores this on the pooled block only. The pooled
head-count false-confident error was:

| shift | head-count error | achievable reduction | achieved |
|---|---|---|---|
| 5 | 0.220% | 0.220 points | 0.165 |
| 10 | 0.651% | 0.651 points | 0.573 |
| 20 | 4.349% | 4.349 points | 4.227 |

The achievable reduction is the head-count error itself, because an error rate
is a proportion and cannot fall below zero. Driving interval accounting's error
to exactly zero at every shift would have produced a maximum reduction of
**4.349 points, against a threshold of 5.000**.

**HGD-1g could not have been satisfied by any possible result.** Not by a better
method, not by a perfect one. The hypothesis was unpassable at the moment it was
frozen, and the arithmetic needed to see that requires no data — only the
observation that the demanded effect exceeded the metric's range.

The run achieved 4.227 points: **97.2% of the arithmetic maximum**, and was
recorded false.

## What this does not say

It does not say the result is wrong, and it does not ask for it to be changed.
The measurement is honest, reproducible, byte-identical across two runs at
different worktrees, and `results/hgd1-v1/README.md` states the directional
finding plainly rather than burying it: "a strong directional safety signal but
do not satisfy the frozen absolute-effect threshold. The criterion remains
unchanged."

That last sentence is the discipline working. The threshold was frozen before
any value was inspected, and the protocol forbids tuning thresholds after
inspection. A criterion that can be adjusted once it has been missed is not a
criterion. **The frozen record stands exactly as it is.** This finding sits
beside it, and the correct response to an unreachable criterion is never to edit
the criterion.

It also does not say the rejection was harmless. It means "HGD-1's primary claim
was rejected" is weak evidence about graded dependence. The directional result
underneath is strong: pooled false-confident error fell from 4.349% to 0.122% at
shift 20, a thirty-six-fold relative reduction, with 93.97% answered coverage.

## A second, smaller observation

The hypothesis says "at every injected shift" without stating whether it is
scored pooled or per cell. The Track B amendment requires results "separately by
sample duration and pooled" and does not say which basis scores the claim. The
runner chose pooled.

In the unscored 24-hour cell at shift 20, head-count error is 5.275% against
interval accounting's 0.077% — a **5.198-point reduction** with 93.72% answered
coverage, above the amendment's 25% floor. That cell clears the threshold the
pooled block could not reach.

This is recorded as an ambiguity in the protocol, not as an argument that HGD-1g
should have passed. A criterion whose outcome depends on an evaluation basis the
protocol never fixed is underspecified, and choosing the basis after seeing both
answers is the exact move the integrity controls exist to prevent. The lesson is
to fix the basis when the criterion is frozen.

## Why no existing gate caught this

Every integrity check in this repository examines an artifact: a digest that
moved, a link that broke, a preregistration that no longer matches its pinned
commit, a coverage claim citing a file that does not exist. They are good checks
and they all passed on HGD-1.

None of them examines a **criterion**. The repository has strong controls
against changing a threshold after the data is seen, and no control at all
asking whether a threshold is attainable before the data exists. The second
question is cheaper than the first — it needs only the metric's bounds — and it
is the one that would have caught this at preregistration time, when fixing it
was free.

`scripts/check_criterion_reachability.py` is that check, wired into
`make verify-integrity`. It is deliberately narrow: it models absolute-difference
criteria over metrics with a declared floor, which is the class that produced
this defect, and refuses to score forms it does not model. HGD-2's criteria are
ratios and relative risks; a reachability argument for those is a different and
harder claim, and inventing one would repeat the error this finding documents in
a more expensive place.

## Relation to the weighting question

This finding is about a threshold, not about whether weighted dependence
accounting is worth having. On that question the evidence is elsewhere and is
not improved by anything here.

`research/weight-sensitivity/FINDINGS.md` finds that weighting is "ceremony"
unless weights differ by large factors, and that treating weights as unknown
within a range gets *worse* with more evidence — useless at scale. HGD-1's own
data says something narrower and sharper: across every pooled observational
cell, the `interval` arm is numerically identical to the unweighted `family`
arm, to sixteen significant digits, and `mean_interval_width` is exactly 0.0 in
seven of the nine synthetic arms. Whatever HGD-1g measured, it compared interval
accounting against *head count*. It never tested the weights against their
absence.
