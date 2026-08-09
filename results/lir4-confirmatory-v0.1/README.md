# LIR-4 confirmatory result

The preregistered graceful-degradation criterion is **rejected**.

With intact reply-target identity, the frozen LIR-3 rule again achieved root
precision, recall, and F1 of `1.0`. Removing identity from half of the records
whose exact parent edge was hidden preserved precision at `1.0`, but recall fell
to `0.4329`, F1 to `0.6043`, and root-count MAE rose to `2.405`. The registered
recall floor was `0.65` and F1 floor was `0.78`; both failed.

## Degradation envelope

| Missing reply identity | Recall | F1 | Root-count MAE |
| ---: | ---: | ---: | ---: |
| 0% | 1.0000 | 1.0000 | 0.0000 |
| 25% | 0.6764 | 0.8069 | 1.1625 |
| 50% | 0.4329 | 0.6043 | 2.4050 |
| 75% | 0.2926 | 0.4527 | 3.5475 |
| 100% | 0.2096 | 0.3466 | 4.6150 |

Precision remained `1.0` at every level. Under honest missingness, this method
therefore failed by fragmenting a recorded family into too many apparent roots,
not by merging distinct recorded roots. The 95% whole-case bootstrap interval
for recall at 50% missingness was `0.3855–0.4858`.

## Collision and hostile-identity boundary

Coarsening identity into as few as one bucket per case left aggregate metrics
perfect. That is not evidence of collision robustness: 399 of 400 selected
cases have only one recorded root, so merging identities within a case usually
cannot create a cross-root error under this label structure.

Only one case supported a cross-root test, and only one hidden record was
eligible for white-box misbinding. The preregistered minimum was 20 of each.
The safety diagnostic is therefore underpowered and no resistance claim is made,
regardless of its perfect point estimate.

## Defensible finding

Reply-target identity is load-bearing, not decorative. It can bridge missing
exact edges extremely well when present, but the frozen author-only method does
not degrade gracefully when much of that identity disappears. A production
knowledge ledger should preserve typed counterpart identity when possible and
must expose uncertainty or fragmentation when it is absent. This experiment
still concerns recorded PHEME reply components, not causal evidence ancestry,
independence, or truth.
