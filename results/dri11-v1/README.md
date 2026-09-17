# DRI-11 v1 confirmatory result

**Outcome: not supported.** 66 of 134 checks. Both methods were named before the
world existed, and both failed: `fragile_refusal` (primary) on 38 checks,
`composite` (secondary) on 30.

The world was written by the adversarial review, not by the author of the
methods, and it contains the two families that had never been tested: one where
refusing is expensive, and one where a single external shock makes two genuinely
independent sources fail together *and* carry the same mark.

## 1. Refusal: blind where it must see, ruinous where it must not act

| Family | Baseline silent | Prevented | Unneeded abstentions | Correct settlements |
|---|---:|---:|---:|---:|
| `marked_hidden_pair` | 772–809 | 406–417 | 369–419 | 1,591–1,628 → 1,195–1,249 |
| `unmarked_hidden_pair` | 743–832 | 378–413 | 361–399 | 1,568–1,657 → 1,193–1,262 |
| **`unmarked_hidden_trio`** | 925–961 | **0** | 340–358 | 1,008–1,066 → unchanged |
| **`fragile_correct`** | **0** | 0 | **2,400 of 2,400** | 2,400 → **0** |
| `shared_shock` | 0 | 0 | 977–1,006 | 2,400 → 1,394–1,423 |
| `common_carrier` | 0 | 0 | 0 | unchanged |
| `robust_correct` | 0 | 0 | 0 | unchanged |

Two failures, and they are opposite in kind.

**Blind to trios.** It prevented **0** of 925–961 critical errors in every
`unmarked_hidden_trio` cell. It quantifies over *pairs*: it asks whether some two
winning-side sources could be one, and never whether some three could be. DRI-9
measured the same zero in its trio family; DRI-10 contained no trio, and refusal
was named primary on the strength of DRI-10. That selection error is the author's,
and it is recorded in full in section 4.

**Ruinous where the answer is fragile but right.** In `fragile_correct` it
refused **every one of 2,400** reversible decisions and settled **none**, against
a baseline that got all 2,400 right and made no silent errors at all. In
`shared_shock` it refused ~1,000 per cell, again where the baseline was already
correct. On a development sample, every refusal in both families landed on a
decision the baseline had settled correctly, and none on one it got silently
wrong.

The cause is structural: refusal fires on *fragility alone*. "Could some winning
pair be one source?" is true constantly when votes are close, and says nothing
about whether anyone actually shares an origin.

## 2. Composite: one shock satisfies both signals

| Family | False merges | True merges | Correct settlements |
|---|---:|---:|---:|
| **`shared_shock`** | **342–439** | **0** | 2,400 → 1,361–1,456 |
| `common_carrier` | 3–24 | 0 | 2,257–2,270 → 2,246–2,260 |
| `marked_hidden_pair` | 0–56 | — | 1,591–1,628 → 1,198–1,299 |
| `unmarked_hidden_trio` | 0–11 | — | 1,008–1,066 → 1,017–1,066 |

The composite demanded that two signals agree before believing a merge. In
`shared_shock` one event flips both sources to the wrong answer *and* marks both,
so the mark and the co-error record agree for a single cause. The result is
**342–439 wrong merges per cell with zero right ones**, and about a thousand
correct settlements lost. It also failed `didNotCollapse` in every
`common_carrier` cell, and **never beat refusal on cost anywhere**, which was its
entire justification.

## 3. What this establishes

- **Corroboration is not independence.** Requiring two signals protects only if
  the signals cannot share a cause. One shock defeated the rule that was built
  precisely to be harder to fool than a single mark.
- **Fragility is not evidence.** A rule that refuses whenever an answer *could*
  turn on a hidden pair refuses constantly in worlds where answers are close and
  correct, at a cost of every settlement in `fragile_correct`.
- **Pair-quantified reasoning cannot see groups.** Two independent experiments
  now measure exactly zero prevention on trios.
- **Behaviour cannot separate a shared source from a shared shock.** On the
  development salt, joint-error rates were 0.38–0.42 for the genuinely dependent
  pairs and **0.58** for the independent shocked pair: the innocents fail together
  *more* than the dependent do.

## 4. Disclosure: how the primary method was chosen

DRI-9 measured `fragile_refusal` at 0.00 prevented in all four of its trio cells.
DRI-10 contained no trio family. The author named refusal primary after DRI-10,
describing it as having "worked everywhere", which was true only of a world whose
dependence families were all pairs. That is the same selection error the author
had criticised in DRI-9's bait result one experiment earlier, and the reviewer
identified it before this run. The world here restored the trio family and put it
on the prevention floor, which is why the failure is visible rather than hidden.

## Run

- **Scope:** criterion on reversible decisions. 7 families × 4 cells (marker
  pickup × leak).
- **Reproducibility:** two executions gave identical semantic results, SHA-256
  `c80d11c87cffcbcd5c0fee44e52bcde224563f0f5cb98e09fbf24963215f7cb1`.
- **Output:** `result.json`, SHA-256
  `dcea2a7d43507f367eaaa43489b76d5f05685c997c8617e26f8ac671836d5c04`.
- **When:** 2026-09-16, 23:03:06 to 23:25:42 UTC.
- **Environment:** CPython 3.12 on macOS arm64, commit `a3080ad`, clean worktree.
- **Failures by check:** `correctSettlementFloor` 20, `costBound` 14,
  `preventsEnoughOfCritical` 10, `beatsRefusalOnCost` 10, `didNotCollapse` 8,
  `significantlyFewerSilent` 6.

## What it does not establish

- **That no rule works.** Two named rules failed; the space is not exhausted.
- **That the shock family should count as dependence.** Its pair is two units in
  the reference grouping, so merging them is scored as error. Whether a common
  cause of *error* ought to count as dependence is a modelling question this
  result raises and does not answer.
- **Real-world rates** for shocks, marks, leaks or library sharing.
- **Independent validation.** The world shares the control domain with the engine
  and was written after DRI-10's result was public.
