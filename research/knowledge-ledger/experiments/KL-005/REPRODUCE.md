# Reproducing KL-005's first gate

## Status of this output: UNREGISTERED PROBE

This is **not a result**. It lives in `probe/`, not `results/`, and the
experiment's state stays `seeded`.

The protocol's completion route requires the registration to be committed
*before* confirmatory inspection. This check was run first, so registering it
now and calling the outcome a result would be back-dating a registration after
seeing the answer -- the defect DRI-7 exists to name. Its function is to
**inform** the registration that has not been written yet.

The repository's own `test_no_experiment_claims_progress_without_the_evidence_for_it`
refused an earlier version of this work that placed these files under
`results/`. That refusal was correct and is recorded here rather than worked
around.

```
python3 run_first_gate.py        # writes probe/first-gate.json
python3 -m pytest tests -q
```

No network, no inference, no randomness.

## What this establishes

**Two gates, both holding.**

1. **Syndication cannot manufacture independence.** Five wire reports collapse
   to one origin; seven syndicated reports collapse to one; three genuinely
   independent originals stay three. A three-outlet citation cycle resolves to
   **zero** originals — fail-closed, refusing to mint an origin that does not
   exist.

2. **The two-sided metric denies silence the win.** This is the blocker the
   protocol names: *a single-endpoint design would let indefinite abstention
   win.* Measured:

   | system | one-sided | delay cost | two-sided |
   |---|---:|---:|---:|
   | `silent` (never confirms) | **0.000** ← ties for best | 1.000 | 1.000 |
   | `count_reports` (3+ reports) | 1.000 | 0.033 | 1.033 |
   | `root_aware` (2+ origins) | **0.000** ← ties for best | 0.533 | **0.533** ← wins |

   Under the one-sided endpoint the degenerate system that says nothing scores
   perfectly, and the endpoint cannot separate it from `root_aware`. Under the
   two-sided score it loses: `root_aware` takes it at 0.533.

   **Silence is not made worst, and this file previously said it was.**
   `count_reports` scores 1.033 against silence at 1.000, because confirming
   both false events costs more than confirming nothing. What the second term
   does is remove silence from the winning set, which is exactly the blocker
   this section names; it does not make silence the worst available strategy.
   Corrected 2026-09-16. The test guarding this had been written as a
   disjunction that passed either way and so could not catch the overstatement;
   it now asserts the full ordering `aware < silent < counting`.

   The defect is demonstrated, not asserted, which is why the broken metric is
   kept in `src/metric.py` rather than deleted.

## What it does not establish

- **This is a structural fixture, not a news corpus.** No rate is reported and
  none is derivable. KL-005 proper needs timestamped closed real events.
- **Weights are declared equal, not fitted.** Any weighting that lets one term
  dominate reintroduces the single-endpoint defect in the other direction.
- **Root collapse trusts declared descent.** It does not detect an undisclosed
  wire relationship — the journalism analogue of ADV-001's under-declared
  search space.
- The fail-closed cycle rule has a cost: a genuine original reachable only
  through a cycle is discarded. That trade is chosen, not incidental.
