#!/usr/bin/env python3
"""Remove the prior. Choosing a trim depth does not require a belief.

`TRIM-DEPTH.md` ended on "how sure are you the room is clean", which is a
probability somebody has to supply, and a probability is not a derivation. That
was a real weakness in the answer, not a philosophical flourish.

Decision theory removes it. Two prior-free rules, both classical:

    minimax          choose the depth whose WORST case over a declared range of
                     adversary fractions is best
    minimax regret   choose the depth whose worst shortfall against the best
                     possible choice for that fraction is smallest

Neither needs a probability. Both need a **declared range**, which is a bound
rather than a belief, and a bound is auditable in a way a belief is not.

Run:  .venv/bin/python research/adversarial-weighting/minimax.py
"""

from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).parent

#: Measured in trim_depth.py. depth -> {adversary fraction: accuracy}
SURFACE = {
    0: {0.0: 0.9822, 0.10: 0.9202, 0.20: 0.8418, 0.30: 0.7158, 0.40: 0.2988},
    1: {0.0: 0.9748, 0.10: 0.9571, 0.20: 0.9072, 0.30: 0.8126, 0.40: 0.4228},
    2: {0.0: 0.9637, 0.10: 0.9801, 0.20: 0.9508, 0.30: 0.8874, 0.40: 0.5493},
    3: {0.0: 0.9464, 0.10: 0.9662, 0.20: 0.9769, 0.30: 0.9425, 0.40: 0.6821},
    4: {0.0: 0.9257, 0.10: 0.9498, 0.20: 0.9598, 0.30: 0.9732, 0.40: 0.7957},
    5: {0.0: 0.8923, 0.10: 0.9195, 0.20: 0.9344, 0.30: 0.9502, 0.40: 0.8873},
    6: {0.0: 0.8423, 0.10: 0.8719, 0.20: 0.8875, 0.30: 0.9091, 0.40: 0.9538},
}
FRACTIONS = [0.0, 0.10, 0.20, 0.30, 0.40]


def minimax(bound):
    """Best guaranteed accuracy when adversaries may reach `bound` and no more."""
    live = [f for f in FRACTIONS if f <= bound]
    worst = {d: min(SURFACE[d][f] for f in live) for d in SURFACE}
    d = max(worst, key=worst.get)
    return d, worst[d]


def minimax_regret(bound):
    """Smallest worst-case shortfall against the best depth for each fraction."""
    live = [f for f in FRACTIONS if f <= bound]
    regret = {d: max(max(SURFACE[e][f] for e in SURFACE) - SURFACE[d][f] for f in live)
              for d in SURFACE}
    d = min(regret, key=regret.get)
    return d, regret[d]


def sybil_bound(attacker_budget, cost_per_identity, honest_sources):
    """Where the declared range itself comes from, when identities cost something.

    An attacker who can spend `attacker_budget` on identities costing
    `cost_per_identity` each can field at most that many. The adversary fraction
    is then arithmetic rather than opinion.

    At zero cost this returns 1.0, which is Douceur's impossibility: without a
    costly identity substrate the bound is everything and no aggregation rule
    survives. The paper already inherits that endpoint; this is where it bites.
    """
    if cost_per_identity <= 0:
        return 1.0
    fielded = attacker_budget / cost_per_identity
    return fielded / (fielded + honest_sources)


def main() -> None:
    print("The prior was an input, not a derivation. Two prior-free rules.\n")
    print(f"    {'adversaries up to':>19} {'minimax':>9} {'guarantees':>12}"
          f" {'regret rule':>13} {'never behind by':>17}")
    for bound in (0.10, 0.20, 0.30, 0.40):
        d1, g = minimax(bound)
        d2, r = minimax_regret(bound)
        print(f"    {bound:>19.2f} {'trim ' + str(d1):>9} {g:>12.4f}"
              f" {'trim ' + str(d2):>13} {r:>17.4f}")

    print("\nBoth rules agree, which is reassuring rather than surprising:")
    print("the surface is well behaved and the two criteria rarely diverge on one.\n")

    print("Where the declared range comes from, when an identity costs something:")
    print(f"    {'attacker budget':>16} {'cost per identity':>19} {'max fraction':>14}")
    for budget, cost in ((1000, 500), (1000, 200), (1000, 50), (1000, 0)):
        b = sybil_bound(budget, cost, honest_sources=15)
        label = f"{b:.3f}" if cost > 0 else "1.000  (free identities)"
        print(f"    {budget:>16} {cost:>19} {label:>14}")

    print("\nAt zero cost the bound is everything, which is Douceur 2002 and is")
    print("cited in the paper as an inherited endpoint. The chain does not end in")
    print("a judgment about how trusting to feel. It ends in a named impossibility,")
    print("and the only local input is what an identity costs here, which is a fact")
    print("about the deployment rather than an opinion about the room.")


if __name__ == "__main__":
    main()
