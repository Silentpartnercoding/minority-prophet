#!/usr/bin/env python3
"""Probe six proposed answers to weighting against ground truth.

`probe.py` measured when weighting changes a verdict. This measures whether it
changes it *correctly*, which is the question that decides between the frames.

Worlds have a truth. Each source has a hidden competence p, the probability it
votes correctly, drawn from a stated distribution. Aggregators see votes and,
depending on the frame, some estimate of p.

The optimal weighting for independent sources of known competence is the
log-odds log(p/(1-p)), not p itself. That is the oracle here, so every frame is
measured against the best achievable rather than against a strawman.

Exploratory. Independent sources unless a run says otherwise; not preregistered.

Run:  .venv/bin/python research/weight-sensitivity/frames.py
"""

from __future__ import annotations

import math
import pathlib
import random
import sys

# Run from anywhere: frame 4 uses the shipped authority walk.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

SEED = 41
TRIALS = 40000


def logodds(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def world(rng, n, pmin, pmax, corr=0.0):
    """Return (truth, votes, competences). `corr` makes a bloc share one vote."""
    truth = rng.random() < 0.5
    ps = [rng.uniform(pmin, pmax) for _ in range(n)]
    votes = [truth if rng.random() < p else not truth for p in ps]
    if corr > 0.0:
        bloc = int(n * corr)
        if bloc > 1:                      # the bloc all repeat the first member
            for i in range(1, bloc):
                votes[i] = votes[0]
    return truth, votes, ps


def decide(votes, weights):
    t = sum(w for v, w in zip(votes, weights) if v)
    f = sum(w for v, w in zip(votes, weights) if not v)
    if t == f:
        return None
    return t > f


def score(rng, n, pmin, pmax, weigher, trials=TRIALS, corr=0.0):
    """Fraction of worlds decided correctly. An abstention counts as half."""
    got = 0.0
    for _ in range(trials):
        truth, votes, ps = world(rng, n, pmin, pmax, corr)
        d = decide(votes, weigher(rng, ps))
        got += 0.5 if d is None else (1.0 if d == truth else 0.0)
    return got / trials


# --- the frames, as weighers -------------------------------------------------

def uniform(rng, ps):
    return [1.0] * len(ps)


def oracle(rng, ps):
    """Frame 5's ceiling: true competence, optimally combined."""
    return [logodds(p) for p in ps]


def noisy(sigma):
    """Frame 5: how accurate must an estimate be before it beats counting?"""
    def f(rng, ps):
        return [logodds(min(max(p + rng.gauss(0, sigma), 0.01), 0.99)) for p in ps]
    return f


def from_track_record(k):
    """Frame 3: weight earned from k observed outcomes, not declared."""
    def f(rng, ps):
        out = []
        for p in ps:
            if k == 0:
                out.append(1.0)
                continue
            hits = sum(1 for _ in range(k) if rng.random() < p)
            phat = (hits + 1) / (k + 2)           # Laplace, so k=1 cannot give 0 or 1
            out.append(logodds(phat))
        return out
    return f


def stake(rho):
    """Frame 2: weight by what a source would forfeit. `rho` is how strongly
    stake tracks real competence; 0.0 means the rich are no better informed."""
    def f(rng, ps):
        return [logodds(min(max(rho * p + (1 - rho) * rng.uniform(0.5, 1.0),
                                0.01), 0.99)) for p in ps]
    return f


def gate(threshold):
    """Frame 6: admit or exclude on estimated competence, then count equally."""
    def f(rng, ps):
        return [1.0 if p >= threshold else 0.0 for p in ps]
    return f


def main() -> None:
    rng = random.Random(SEED)
    N, LO, HI = 9, 0.45, 0.95

    print(f"{N} independent sources, competence uniform in [{LO}, {HI}].")
    print("Accuracy against ground truth. Abstention scores 0.5.\n")

    base = score(rng, N, LO, HI, uniform)
    top = score(rng, N, LO, HI, oracle)
    print(f"  {'count everyone equally':<44} {base:.4f}")
    print(f"  {'oracle: true competence, optimally weighted':<44} {top:.4f}")
    print(f"  {'headroom the whole argument is about':<44} {top - base:+.4f}\n")

    print("FRAME 5 -- how good must an estimate be before weighting pays?")
    for s in (0.02, 0.05, 0.10, 0.15, 0.20, 0.30):
        v = score(rng, N, LO, HI, noisy(s))
        mark = "beats counting" if v > base else "WORSE than counting"
        print(f"    estimate error +/-{s:<5} {v:.4f}   {mark}")

    print("\nFRAME 3 -- weight earned from a track record of k outcomes")
    for k in (0, 1, 3, 10, 30, 100):
        v = score(rng, N, LO, HI, from_track_record(k))
        mark = "beats counting" if v > base else "WORSE than counting"
        print(f"    k = {k:<5} {v:.4f}   {mark}")

    print("\nFRAME 2 -- weight by stake, where stake tracks competence with rho")
    for rho in (0.0, 0.25, 0.5, 0.75, 1.0):
        v = score(rng, N, LO, HI, stake(rho))
        mark = "beats counting" if v > base else "WORSE than counting"
        print(f"    rho = {rho:<5} {v:.4f}   {mark}")

    print("\nFRAME 6 -- admit above a threshold, then count equally (oracle threshold)")
    for th in (0.5, 0.6, 0.7, 0.8):
        v = score(rng, N, LO, HI, gate(th))
        mark = "beats counting" if v > base else "WORSE than counting"
        print(f"    admit p >= {th:<5} {v:.4f}   {mark}")

    print("\nOBSERVATION -- is the appetite for weights really an appetite for independence?")
    print("    a bloc of copies, all repeating one member's vote")
    for corr in (0.0, 0.33, 0.66):
        b = score(rng, N, LO, HI, uniform, corr=corr)
        o = score(rng, N, LO, HI, oracle, corr=corr)
        print(f"    {int(corr*100):>3}% copied   count {b:.4f}   oracle-weighted {o:.4f}"
              f"   weighting buys {o-b:+.4f}")

    print("\nFRAME 4 -- does a weight's justification terminate the four ways authority does?")
    from canon.authority_debt import Ground, Link, walk
    chains = {
        "scored track record": {"w": Link("w", Ground.DEFERENCE, defers_to="r"),
                                "r": Link("r", Ground.EVIDENCE, note="k outcomes")},
        "bonded stake": {"w": Link("w", Ground.DEFERENCE, defers_to="b"),
                         "b": Link("b", Ground.MECHANISM, note="forfeiture is checkable")},
        "an owner assigned it": {"w": Link("w", Ground.DEFERENCE, defers_to="o"),
                                 "o": Link("o", Ground.JUDGMENT, note="named, uncertainty stated")},
        "nobody can justify it": {"w": Link("w", Ground.DEFERENCE, defers_to="n"),
                                  "n": Link("n", Ground.UNKNOWN, note="say so")},
        "convention: everyone gets 1": {"w": Link("w", Ground.DEFERENCE, defers_to="c"),
                                        "c": Link("c", Ground.JUDGMENT, note="stipulated and published")},
        "reputation from consensus from weight": {
            "w": Link("w", Ground.DEFERENCE, defers_to="rep"),
            "rep": Link("rep", Ground.DEFERENCE, defers_to="con"),
            "con": Link("con", Ground.DEFERENCE, defers_to="w")},
    }
    for label, c in chains.items():
        r = walk(c, "w")
        print(f"    {label:<38} -> {'LOOP' if r.is_loop else r.terminated_in}")

    print(f"\nSeed {SEED}, {TRIALS} trials per cell. Exploratory, not preregistered.")


if __name__ == "__main__":
    main()
