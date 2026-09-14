#!/usr/bin/env python3
"""Can we tell whether a source ranking transfers between domains?

`readiness.py` found that weighting needs the *order* of competence to carry over,
not its level, and that a half-scrambled order is already worse than counting.
That is only useful if the transfer can be checked. This measures whether it can,
and how little data it takes.

The check is deliberately crude: rank sources by score in each of two domains
where truth arrives, then count over every pair of sources how often the two
domains order them the same way. Chance is 0.50.

Run:  .venv/bin/python research/weight-sensitivity/transfer_test.py
"""

from __future__ import annotations

import itertools
import random

SEED = 83
TRIALS = 3000


def pair_agreement(a, b) -> float:
    """Share of source pairs ordered alike in both domains. Ties are skipped."""
    same = total = 0
    for i, j in itertools.combinations(range(len(a)), 2):
        if a[i] == a[j] or b[i] == b[j]:
            continue
        total += 1
        same += (a[i] > a[j]) == (b[i] > b[j])
    return same / total if total else 0.5


def one_trial(rng, sources: int, scores: int, transfers: bool) -> float:
    home = [rng.uniform(0.45, 0.95) for _ in range(sources)]
    away = home[:] if transfers else [rng.uniform(0.45, 0.95) for _ in range(sources)]
    tally = lambda ps: [sum(1 for _ in range(scores) if rng.random() < p) for p in ps]
    return pair_agreement(tally(home), tally(away))


def main() -> None:
    rng = random.Random(SEED)
    print("Rank sources in two domains where truth arrives; compare the orders.")
    print("Chance is 0.500. The test needs to separate 'transfers' from 'does not'.\n")
    print(f"  {'sources':>8} {'scores each':>12} {'transfers':>11} {'does not':>10} {'gap':>7}")
    for m in (3, 5, 10, 20):
        for k in (12, 30, 100):
            yes = sum(one_trial(rng, m, k, True) for _ in range(TRIALS)) / TRIALS
            no = sum(one_trial(rng, m, k, False) for _ in range(TRIALS)) / TRIALS
            print(f"  {m:>8} {k:>12} {yes:>11.3f} {no:>10.3f} {yes - no:>7.3f}")

    print("\n  The ceiling is not 1.000 and that matters. Perfect transfer measured")
    print("  with 12 scores looks like 0.75, not 1.00, because the rankings are")
    print("  themselves noisy. Compare against the ceiling for your sample size,")
    print("  never against certainty, or perfect transfer reads as partial.")
    print(f"\nSeed {SEED}, {TRIALS} trials per cell. Exploratory, not preregistered.")


if __name__ == "__main__":
    main()
