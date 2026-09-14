#!/usr/bin/env python3
"""When may we start weighting, and can we tell from the inside?

`frames.py` found the crossover: competence must be known to within about fifteen
percentage points before weighting beats counting. That is useless on its own,
because nobody knows their own estimate error.

This asks whether the moment is detectable without knowing the truth. There are
two conditions and they behave completely differently. One is a calculation you
can do today with no data at all. The other cannot be calculated and must be
tested, and it is the one that actually binds.

Run:  .venv/bin/python research/weight-sensitivity/readiness.py
"""

from __future__ import annotations

import math
import random

SEED = 67
TRIALS = 40000
N = 9


def logodds(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def earned(rng, competences, k):
    """A weight estimated from k scored outcomes. Laplace-smoothed so k=1 cannot
    produce a certainty."""
    out = []
    for p in competences:
        hits = sum(1 for _ in range(k) if rng.random() < p)
        out.append(logodds((hits + 1) / (k + 2)))
    return out


def run(rng, *, k=None, shrink=0.0, scramble=0.0, trials=TRIALS):
    """Accuracy against ground truth. `k=None` counts everyone equally.

    `shrink` pulls competence toward a coin flip in the domain being voted on,
    preserving who is best. `scramble` reassigns competences among the sources,
    destroying who is best while preserving the spread.
    """
    got = 0.0
    for _ in range(trials):
        truth = rng.random() < 0.5
        scored = [rng.uniform(0.45, 0.95) for _ in range(N)]
        live = [0.5 + (p - 0.5) * (1 - shrink) for p in scored]
        if scramble and rng.random() < scramble:
            rng.shuffle(live)
        votes = [truth if rng.random() < p else not truth for p in live]
        w = [1.0] * N if k is None else earned(rng, scored, k)
        t = sum(x for v, x in zip(votes, w) if v)
        f = sum(x for v, x in zip(votes, w) if not v)
        got += 0.5 if t == f else (1.0 if (t > f) == truth else 0.0)
    return got / trials


def condition_one(rng):
    """Computable today, from a count, with no truth and no data.

    The standard error of a competence estimated from k scored outcomes is at
    most sqrt(0.25 / k). Setting that equal to the measured crossover gives a
    threshold that needs nothing but a tally of how often this source has been
    scored. The table checks whether the prediction holds.
    """
    print("CONDITION ONE -- have we scored this source enough times?")
    print("    Predicted threshold: k >= 0.25 / tolerance^2.")
    print(f"    For the measured +/-0.15 crossover that is k >= "
          f"{math.ceil(0.25 / 0.15 ** 2)}.\n")
    base = run(rng)
    print(f"    {'k':>5} {'predicted error':>17} {'accuracy':>10} {'vs counting':>13}")
    for k in (1, 3, 7, 12, 25, 60, 200):
        acc = run(rng, k=k)
        print(f"    {k:>5} {math.sqrt(0.25 / k):>17.3f} {acc:>10.4f} {acc - base:>+13.4f}")
    print(f"    counting equally: {base:.4f}")


def condition_two(rng):
    """Not computable. Must be tested, and it is the binding one.

    A source can only be scored where truth arrives. Using that weight anywhere
    else assumes competence transfers. Two ways it can fail to, with opposite
    consequences.
    """
    print("\nCONDITION TWO -- does competence transfer to where we are using it?")
    print("\n    (a) the level collapses but the ranking holds")
    print(f"    {'shrink':>8} {'weighted':>10} {'counting':>10} {'verdict':>22}")
    for s in (0.0, 0.5, 0.9, 1.0):
        a, b = run(rng, k=60, shrink=s), run(rng, shrink=s)
        v = "weighting still pays" if a > b else "WORSE than counting"
        print(f"    {s:>8.2f} {a:>10.4f} {b:>10.4f} {v:>22}")

    print("\n    (b) the ranking is scrambled, whatever the level")
    print(f"    {'scramble':>8} {'weighted':>10} {'counting':>10} {'verdict':>22}")
    for s in (0.0, 0.25, 0.5, 0.75, 1.0):
        a, b = run(rng, k=60, scramble=s), run(rng, scramble=s)
        v = "weighting still pays" if a > b else "WORSE than counting"
        print(f"    {s:>8.2f} {a:>10.4f} {b:>10.4f} {v:>22}")


def main() -> None:
    rng = random.Random(SEED)
    condition_one(rng)
    condition_two(rng)
    print(f"\nSeed {SEED}, {TRIALS} trials per cell, {N} sources, "
          "competence uniform in [0.45, 0.95].")
    print("Exploratory, not preregistered.")


if __name__ == "__main__":
    main()
