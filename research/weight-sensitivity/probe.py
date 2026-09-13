#!/usr/bin/env python3
"""When does weighting change anything, and can uncertainty about weights be bounded?

Three questions, all measured rather than argued. Exploratory: no preregistration,
so these are observations about a synthetic generator and not claims about the
world. The generator is uniform and symmetric, which is stated because it is the
main thing that could be driving the answers.

Run:  .venv/bin/python research/weight-sensitivity/probe.py
"""

from __future__ import annotations

import random
from dataclasses import dataclass

SEED = 23
TRIALS = 20000


@dataclass
class Claim:
    value: bool
    w: float


def side(t: float, f: float) -> str:
    return "true" if t > f else ("false" if f > t else "abstain")


def counted(cs) -> str:
    t = sum(1 for c in cs if c.value)
    return side(t, len(cs) - t)


def weighted(cs) -> str:
    return side(sum(c.w for c in cs if c.value), sum(c.w for c in cs if not c.value))


def weighted_is_determined(cs, band: float) -> bool:
    """Bracket every weighting within +/- band. Determined when both ends agree."""
    hi = lambda c: min(1.0, c.w + band)
    lo = lambda c: max(0.0, c.w - band)
    best_true = side(sum(hi(c) for c in cs if c.value),
                     sum(lo(c) for c in cs if not c.value))
    best_false = side(sum(lo(c) for c in cs if c.value),
                      sum(hi(c) for c in cs if not c.value))
    return best_true == best_false


def filter_is_determined(cs, band: float, threshold: float = 0.5) -> bool:
    """Admit or exclude at a threshold, then count admitted sources equally.

    The courtroom alternative: put the discrimination at the gate, none in the
    tally. Only sources within `band` of the threshold are in doubt.
    """
    admitted = [c for c in cs if c.w - band >= threshold]
    doubtful = [c for c in cs if abs(c.w - threshold) < band]
    t = sum(1 for c in admitted if c.value)
    f = len(admitted) - t
    dt = sum(1 for c in doubtful if c.value)
    df = len(doubtful) - dt
    return side(t + dt, f) == side(t, f + df)


def q1_when_does_weighting_matter(rng):
    print("Q1  weights known exactly, no zeros. Does weighting change the verdict?")
    print(f"    {'claims':>7} {'weight spread':>16} {'differs':>9}")
    for n in (3, 5, 9, 25):
        for lo, hi, label in ((0.8, 1.0, "narrow .8-1.0"),
                              (0.4, 1.0, "wide .4-1.0"),
                              (0.05, 1.0, "extreme .05-1")):
            d = 0
            for _ in range(TRIALS):
                cs = [Claim(rng.random() < 0.5, rng.uniform(lo, hi)) for _ in range(n)]
                d += counted(cs) != weighted(cs)
            print(f"    {n:>7} {label:>16} {d / TRIALS * 100:>8.1f}%")


def q2_does_bracketing_scale(rng):
    print("\nQ2  weights uncertain. Bracket every admissible weighting.")
    print(f"    {'claims':>7} {'uncertainty':>12} {'determined':>11}")
    for n in (3, 9, 25, 60):
        for band in (0.1, 0.25, 0.5):
            d = 0
            for _ in range(TRIALS):
                cs = [Claim(rng.random() < 0.5, rng.uniform(0.2, 1.0)) for _ in range(n)]
                d += weighted_is_determined(cs, band)
            print(f"    {n:>7} {'+/- ' + str(band):>12} {d / TRIALS * 100:>10.1f}%")


def q3_is_a_filter_better(rng):
    print("\nQ3  same uncertainty, but admit/exclude then count equally.")
    print(f"    {'claims':>7} {'uncertainty':>12} {'weighted':>9} {'filter':>8}")
    for n in (3, 9, 25, 60):
        for band in (0.1, 0.25, 0.5):
            dw = df = 0
            for _ in range(TRIALS):
                cs = [Claim(rng.random() < 0.5, rng.uniform(0.2, 1.0)) for _ in range(n)]
                dw += weighted_is_determined(cs, band)
                df += filter_is_determined(cs, band)
            print(f"    {n:>7} {'+/- ' + str(band):>12} "
                  f"{dw / TRIALS * 100:>8.1f}% {df / TRIALS * 100:>7.1f}%")


def main() -> None:
    rng = random.Random(SEED)
    q1_when_does_weighting_matter(rng)
    q2_does_bracketing_scale(rng)
    q3_is_a_filter_better(rng)
    print("\nGenerator: uniform weights, symmetric true/false, independent draws.")
    print(f"Seed {SEED}, {TRIALS} trials per cell. Exploratory, not preregistered.")


if __name__ == "__main__":
    main()
