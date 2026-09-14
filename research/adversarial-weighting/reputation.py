#!/usr/bin/env python3
"""Does reputation defend against a patient liar? It makes it worse.

The natural objection to requiring a bond is that reputation should do the job
for free: behave badly, get downgraded, lose influence. Over repeated rounds,
game theory ought to punish the liar even if it cannot stop the first offence.

This measures it, and the answer is not merely "reputation is too slow". A
reputation system actively **manufactures** the attacker it is supposed to deter.

The mechanism, once seen, is obvious. Reputation concentrates weight on whoever
has been most consistently right. An honest source with genuine competence below
one is wrong sometimes and gets downgraded for it. A patient adversary who simply
agrees with the emerging consensus is never wrong, is never downgraded, and rises.
By the round that matters, the highest-reputation sources are exactly the ones
waiting to defect.

Reputation is a weighting scheme, so it inherits every weighting failure measured
in this directory, and adds one of its own: it selects for the attack.

Run:  .venv/bin/python research/adversarial-weighting/reputation.py
"""

from __future__ import annotations

import random

N = 15
HONEST_COMPETENCE = 0.75
SEED = 2101
TRIALS = 4000


def run(rng, rounds, n_adv, defence, trials=TRIALS):
    """Share of final rounds the attacker successfully corrupts.

    Sleepers vote with the truth for every round but the last, then defect
    together. `defence` is one of:

        none        every source counts one, always
        reputation  a source wrong in a round has its weight halved, afterwards
        bond        a source that defects forfeits and is barred in that round
    """
    corrupted = total = 0
    for _ in range(trials):
        rep = [1.0] * N
        barred = [False] * N
        for r in range(rounds):
            truth = rng.random() < 0.5
            defect = (r == rounds - 1)
            votes, weights = [], []
            for i in range(N):
                adversarial = i < n_adv
                if adversarial and defect:
                    v = not truth
                elif adversarial:
                    v = truth                       # perfect record, cheaply bought
                else:
                    v = truth if rng.random() < HONEST_COMPETENCE else not truth
                votes.append(v)
                if defence == "bond" and adversarial and defect:
                    barred[i] = True
                weights.append(0.0 if barred[i] else rep[i])

            t = sum(w for v, w in zip(votes, weights) if v)
            f = sum(w for v, w in zip(votes, weights) if not v)
            verdict = None if t == f else t > f

            if defect:
                total += 1
                if verdict is not None and verdict != truth:
                    corrupted += 1

            if defence == "reputation":             # punishment lands after the round
                for i in range(N):
                    if votes[i] != truth:
                        rep[i] *= 0.5
    return corrupted / total


def main() -> None:
    rng = random.Random(SEED)
    print("A sleeper votes with the truth for every round but the last.")
    print("Share of final rounds the attacker corrupts. Lower is better.\n")
    print(f"  {'rounds':>7} {'adversaries':>12} {'no defence':>12}"
          f" {'reputation':>12} {'bond':>8}")
    for rounds in (2, 5, 20):
        for n_adv in (5, 7):
            a = run(rng, rounds, n_adv, "none")
            b = run(rng, rounds, n_adv, "reputation")
            c = run(rng, rounds, n_adv, "bond")
            print(f"  {rounds:>7} {n_adv:>12} {a:>12.3f} {b:>12.3f} {c:>8.3f}")

    print("\n  Reputation is worse than no defence at all, and the gap grows with")
    print("  the number of rounds, because a longer history is a larger reward for")
    print("  patience. At twenty rounds it hands the attacker every single verdict.")
    print("\n  A bond works for one reason only: it acts in the round it is needed,")
    print("  not in the round afterwards.")
    print(f"\nSeed {SEED}, {TRIALS} trials per cell. Exploratory, not preregistered.")


if __name__ == "__main__":
    main()
