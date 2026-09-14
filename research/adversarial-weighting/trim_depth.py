#!/usr/bin/env python3
"""How deep should you trim, and is trimming worth it in a room you trust?

`experiment.py` established that trimming survives an adversary where weighting
does not, at a frozen depth. It did not say how to choose the depth, which is the
question a practitioner actually has, and it did not price the insurance.

Three questions, measured. Exploratory characterisation of a parameter, not
hypothesis testing: no preregistration, and none is claimed.

Run:  .venv/bin/python research/adversarial-weighting/trim_depth.py
"""

from __future__ import annotations

import math
import random

N = 15
HONEST_LO, HONEST_HI = 0.55, 0.95
TRIALS = 40000
SEED = 1601
DEPTHS = range(0, 7)
FRACTIONS = [0.0, 0.10, 0.20, 0.30, 0.40]


def logodds(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def world(rng, f):
    truth = rng.random() < 0.5
    n_adv = round(f * N)
    votes, weights = [], []
    for i in range(N):
        if i < n_adv:
            votes.append(not truth)
            weights.append(logodds(0.99))          # declares the maximum
        else:
            p = rng.uniform(HONEST_LO, HONEST_HI)
            votes.append(truth if rng.random() < p else not truth)
            weights.append(logodds(p))
    return truth, votes, weights


def trimmed(votes, weights, depth):
    if depth == 0:
        keep = list(range(len(votes)))
    else:
        order = sorted(range(len(weights)), key=lambda i: weights[i])
        keep = order[depth:len(order) - depth] or order
    t = sum(1 for i in keep if votes[i])
    f = len(keep) - t
    return None if t == f else t > f


def accuracy(rng, f, depth, trials=TRIALS):
    got = 0.0
    for _ in range(trials):
        truth, votes, weights = world(rng, f)
        r = trimmed(votes, weights, depth)
        got += 0.5 if r is None else (1.0 if r == truth else 0.0)
    return got / trials


def main() -> None:
    rng = random.Random(SEED)
    surface = {d: {f: accuracy(rng, f, d) for f in FRACTIONS} for d in DEPTHS}

    print("Accuracy by trim depth per side and adversary fraction. 15 sources.\n")
    print("    depth" + "".join(f"{f:>9.2f}" for f in FRACTIONS))
    for d in DEPTHS:
        print(f"    {d:>5}" + "".join(f"{surface[d][f]:>9.4f}" for f in FRACTIONS))

    print("\nQ1  If adversaries are present, the best depth equals their number.")
    for f in FRACTIONS:
        best = max(DEPTHS, key=lambda d: surface[d][f])
        print(f"    f={f:<5} best depth {best}   adversaries present: {round(f * N)}")

    print("\nQ2  You do not know f. Adversaries appear with probability p, at f=0.20.")
    print(f"    {'p':>6}" + "".join(f"{d:>9}" for d in DEPTHS) + "   best")
    for p in (0.0, 0.05, 0.10, 0.20, 0.50, 1.0):
        exp = {d: (1 - p) * surface[d][0.0] + p * surface[d][0.20] for d in DEPTHS}
        print(f"    {p:>6.2f}" + "".join(f"{exp[d]:>9.4f}" for d in DEPTHS)
              + f"   {max(exp, key=exp.get)}")

    print("\nQ3  Trimming is not more precise. It is insurance. The premium:")
    for d in (1, 2, 3):
        premium = surface[0][0.0] - surface[d][0.0]
        payout = surface[d][0.20] - surface[0][0.20]
        print(f"    depth {d}: costs {premium:.4f} in a clean room, "
              f"saves {payout:+.4f} at f=0.20, break-even p={premium/(premium+payout):.3f}")

    print(f"\nSeed {SEED}, {TRIALS} trials per cell. Exploratory, not preregistered.")


if __name__ == "__main__":
    main()
