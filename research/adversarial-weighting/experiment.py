#!/usr/bin/env python3
"""Does weighting survive an adversary who chooses the weights?

Implements PREREGISTRATION.md exactly. Every parameter below is copied from the
frozen document; none may be tuned to a result.

Run:  .venv/bin/python research/adversarial-weighting/experiment.py
"""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
import random

HERE = pathlib.Path(__file__).parent

# --- frozen parameters, from PREREGISTRATION.md ------------------------------
N = 15
HONEST_LO, HONEST_HI = 0.55, 0.95
FRACTIONS = [round(0.05 * i, 2) for i in range(11)]      # 0.00 .. 0.50
K_SCORED = 60
CAP = 2 / N
TRIM = math.ceil(0.20 * N)
TRIALS = 40000
SEED = 1401
TOLERANCES = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]


def check_preregistration() -> str:
    """Refuse to run against an edited preregistration."""
    doc = (HERE / "PREREGISTRATION.md").read_bytes()
    got = hashlib.sha256(doc).hexdigest()
    want = (HERE / "PREREGISTRATION.sha256").read_text().split()[0]
    if got != want:
        raise SystemExit(f"preregistration hash mismatch\n  frozen {want}\n  now    {got}")
    return got


def logodds(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def tally(votes, weights) -> float:
    """0.0 wrong, 0.5 abstain, 1.0 right. `votes` are booleans for TRUE."""
    t = sum(w for v, w in zip(votes, weights) if v)
    f = sum(w for v, w in zip(votes, weights) if not v)
    if t == f:
        return None
    return t > f


def weighted_median(votes, weights) -> bool | None:
    t = sum(w for v, w in zip(votes, weights) if v)
    f = sum(w for v, w in zip(votes, weights) if not v)
    if t == f:
        return None
    return t > f


def cap_weights(ws, cap_fraction):
    """Clip any single weight to at most `cap_fraction` of the total, iterating
    because clipping one changes the total."""
    ws = [max(w, 0.0) for w in ws]
    for _ in range(20):
        total = sum(ws)
        if total <= 0:
            return [1.0] * len(ws)
        limit = cap_fraction * total
        over = [i for i, w in enumerate(ws) if w > limit + 1e-12]
        if not over:
            return ws
        for i in over:
            ws[i] = limit
    return ws


def trimmed_equal(votes, weights, depth):
    """Discard the `depth` highest and lowest weights, count the rest equally."""
    order = sorted(range(len(weights)), key=lambda i: weights[i])
    keep = order[depth:len(order) - depth] or order
    kept = [votes[i] for i in keep]
    t = sum(1 for v in kept if v)
    f = len(kept) - t
    if t == f:
        return None
    return t > f


def one_world(rng, f, attack):
    """Return (truth, votes, declared, earned) for one world."""
    truth = rng.random() < 0.5
    n_adv = round(f * N)
    votes, declared, earned = [], [], []
    for i in range(N):
        adversarial = i < n_adv
        if adversarial:
            votes.append(not truth)                       # coordinated, knows the truth
            if attack == "declaration":
                declared.append(0.99)                     # claims the maximum
                earned.append(logodds(0.5))               # never scored well
            else:                                         # sleeper
                declared.append(0.95)
                hits = sum(1 for _ in range(K_SCORED) if rng.random() < 0.95)
                earned.append(logodds((hits + 1) / (K_SCORED + 2)))
        else:
            p = rng.uniform(HONEST_LO, HONEST_HI)
            votes.append(truth if rng.random() < p else not truth)
            declared.append(p)
            hits = sum(1 for _ in range(K_SCORED) if rng.random() < p)
            earned.append(logodds((hits + 1) / (K_SCORED + 2)))
    return truth, votes, declared, earned


def score(rng, f, attack, trials=TRIALS):
    acc = {k: 0.0 for k in
           ("uniform", "declared", "earned", "capped", "trimmed", "median")}
    for _ in range(trials):
        truth, votes, declared, earned = one_world(rng, f, attack)
        dec_w = [logodds(p) for p in declared]
        pos = [max(w, 0.0) for w in dec_w]
        results = {
            "uniform": tally(votes, [1.0] * N),
            "declared": tally(votes, dec_w),
            "earned": tally(votes, earned),
            "capped": tally(votes, cap_weights(pos, CAP)),
            "trimmed": trimmed_equal(votes, dec_w, TRIM),
            "median": weighted_median(votes, cap_weights(pos, CAP)),
        }
        for k, d in results.items():
            acc[k] += 0.5 if d is None else (1.0 if d == truth else 0.0)
    return {k: v / trials for k, v in acc.items()}


def breakdown(curve):
    """Smallest f whose accuracy is below 0.5. None if it never breaks."""
    for f in sorted(curve):
        if curve[f] < 0.5:
            return f
    return None


def h4_tolerance_sweep(rng, f=0.20):
    """H4: does the honest crossover tighten under the sleeper attack?

    The honest run has no adversary. The attacked run holds a fraction f of
    sleepers who earned a real record and then defect. In both, our estimate of
    every honest source's competence carries error `tol`.
    """
    print("H4 -- tolerance at which earned weighting still beats counting")
    print(f"    sleeper fraction f = {f}")
    print(f"    {'tolerance':>10} {'honest: earned':>16} {'honest: count':>15}"
          f" {'attacked: earned':>18} {'attacked: count':>17}")
    rows = {}
    for tol in TOLERANCES:
        res = {}
        for label, frac in (("honest", 0.0), ("attacked", f)):
            e = c = 0.0
            for _ in range(TRIALS):
                truth, votes, declared, _ = one_world(rng, frac, "sleeper")
                noisy = [logodds(min(max(p + rng.gauss(0, tol), 0.02), 0.98))
                         for p in declared]
                de = tally(votes, noisy)
                dc = tally(votes, [1.0] * N)
                e += 0.5 if de is None else (1.0 if de == truth else 0.0)
                c += 0.5 if dc is None else (1.0 if dc == truth else 0.0)
            res[label] = (e / TRIALS, c / TRIALS)
        rows[tol] = res
        print(f"    {tol:>10.2f} {res['honest'][0]:>16.4f} {res['honest'][1]:>15.4f}"
              f" {res['attacked'][0]:>18.4f} {res['attacked'][1]:>17.4f}")
    honest_ok = [t for t, r in rows.items() if r["honest"][0] > r["honest"][1]]
    attacked_ok = [t for t, r in rows.items() if r["attacked"][0] > r["attacked"][1]]
    hi_h = max(honest_ok) if honest_ok else None
    hi_a = max(attacked_ok) if attacked_ok else None
    print(f"    largest tolerance where earned still wins -- honest: {hi_h}, "
          f"attacked: {hi_a}")
    return {"rows": {str(k): v for k, v in rows.items()},
            "largest_tolerance_honest": hi_h, "largest_tolerance_attacked": hi_a}


def main() -> None:
    digest = check_preregistration()
    rng = random.Random(SEED)
    print(f"preregistration {digest[:16]}... verified\n")

    out = {"preregistration_sha256": digest, "seed": SEED, "trials": TRIALS,
           "n": N, "cap": CAP, "trim": TRIM, "attacks": {}}

    for attack in ("declaration", "sleeper"):
        print(f"ATTACK: {attack}")
        header = f"    {'f':>5} " + "".join(f"{k:>10}" for k in
                 ("uniform", "declared", "earned", "capped", "trimmed", "median"))
        print(header)
        curves = {k: {} for k in ("uniform", "declared", "earned", "capped",
                                  "trimmed", "median")}
        for f in FRACTIONS:
            r = score(rng, f, attack)
            for k, v in r.items():
                curves[k][f] = v
            print(f"    {f:>5.2f} " + "".join(f"{r[k]:>10.4f}" for k in
                  ("uniform", "declared", "earned", "capped", "trimmed", "median")))
        print("    breakdown points (first f below 0.5):")
        for k in curves:
            b = breakdown(curves[k])
            print(f"      {k:<10} {b if b is not None else 'never in range'}")
        out["attacks"][attack] = {"curves": curves,
                                  "breakdown": {k: breakdown(v) for k, v in curves.items()}}
        print()

    out["h4"] = h4_tolerance_sweep(rng)

    (HERE / "results.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"results written to {HERE / 'results.json'}")


if __name__ == "__main__":
    main()
