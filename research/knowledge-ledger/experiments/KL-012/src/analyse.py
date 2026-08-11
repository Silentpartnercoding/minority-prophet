#!/usr/bin/env python3
"""KL-012 analysis. Written before the data existed; see the commit that added it.

Endpoint (frozen): does rootCount predict time-to-death better than voiceCount,
on the conditioned population?

Metric is Harrell's concordance index, because the outcome is right-censored and
a censored observation still carries information -- a token alive at 720 hours
outlived every token that died at 300, and throwing that away is what made the
pilot's binary outcome so weak. C is the fraction of comparable pairs a predictor
orders correctly. 0.5 is a coin flip.

Significance is a paired permutation test on the DIFFERENCE in C between the two
predictors, because they are measured on the same tokens and are not independent.

Stdlib only.
"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect import SPEC, load

BAND = (0.20, 0.80)


def c_index(pred, time, dead):
    """Harrell's C. A pair is comparable when the earlier of the two died.
    Higher predictor value should mean SHORTER survival."""
    conc = disc = tied = 0
    n = len(time)
    for i in range(n):
        for j in range(i+1, n):
            if time[i] == time[j] and dead[i] and dead[j]:
                continue
            if time[i] < time[j] and dead[i]:
                early, late = i, j
            elif time[j] < time[i] and dead[j]:
                early, late = j, i
            else:
                continue                     # not comparable: censored too soon
            if pred[early] == pred[late]: tied += 1
            elif pred[early] > pred[late]:  conc += 1
            else:                           disc += 1
    total = conc + disc + tied
    return (conc + 0.5*tied) / total if total else None, total


def permutation_p(a, b, time, dead, iters=10000, seed=20260811):
    """Paired permutation on the C difference. Swapping the two predictors within
    a token is the null: they carry the same information about that token."""
    rng = random.Random(seed)
    ca, _ = c_index(a, time, dead)
    cb, _ = c_index(b, time, dead)
    if ca is None or cb is None: return None, None, None
    obs = ca - cb
    hits = 0
    for _ in range(iters):
        pa, pb = [], []
        for x, y in zip(a, b):
            if rng.random() < 0.5: pa.append(x); pb.append(y)
            else:                  pa.append(y); pb.append(x)
        da = c_index(pa, time, dead)[0] - c_index(pb, time, dead)[0]
        if abs(da) >= abs(obs) - 1e-12: hits += 1
    return ca, cb, (hits+1)/(iters+1)


def main():
    out = load("outcomes.json", {})
    rc = load("rootcounts.json", {})
    mints = [m for m in out if m in rc]
    print(f"  tokens with both an outcome and a root count: {len(mints)}")
    if len(mints) < 20:
        print("  too few to analyse; collection still running"); return

    time = [out[m]["hoursToDeath"] if not out[m]["censored"]
            else SPEC["outcome"]["OBSERVATION_HOURS"] for m in mints]
    dead = [not out[m]["censored"] for m in mints]
    rate = sum(dead)/len(dead)
    print(f"  death rate: {rate:.0%}")
    if not (BAND[0] <= rate <= BAND[1]):
        print(f"  effectRequires outcome-variance band {BAND[0]:.0%}-{BAND[1]:.0%}: FAILED")
        print( "  the spec says STOP and report. No endpoint is evaluated.")
        return
    print(f"  effectRequires outcome-variance band: SATISFIED\n")

    voice = [rc[m]["voiceCount"] for m in mints]
    root  = [rc[m]["rootCount"] for m in mints]
    disagree = sum(1 for v, r in zip(voice, root) if v != r)
    print(f"  voice/root disagreement: {disagree}/{len(mints)} tokens "
          f"({disagree/len(mints):.0%})")
    if disagree == 0:
        print("  the two predictors are identical on this population; endpoint "
              "unreachable. STOP."); return

    # fewer independent roots should mean shorter survival, so negate
    cr, cv, p = permutation_p([-x for x in root], [-x for x in voice], time, dead)
    print(f"\n  C(rootCount)  = {cr:.4f}")
    print(f"  C(voiceCount) = {cv:.4f}")
    print(f"  difference    = {cr-cv:+.4f}")
    print(f"  paired permutation p = {p:.4f}")
    print(f"\n  ENDPOINT: {'root count predicts better' if p < 0.05 and cr > cv else 'NOT MET -- no evidence root count predicts better'}")

    # the analysis must be able to detect a difference at all
    print(f"\n  ABLATION -- can this analysis see a real effect?")
    rng = random.Random(7)
    perfect = [-t for t in time]                      # knows the answer
    noise   = [rng.random() for _ in mints]           # knows nothing
    cp, _ = c_index(perfect, time, dead)
    cn, _ = c_index(noise, time, dead)
    print(f"    oracle predictor C = {cp:.3f}   (must be near 1.0)")
    print(f"    random predictor C = {cn:.3f}   (must be near 0.5)")
    ok = cp > 0.9 and 0.35 < cn < 0.65
    print(f"    analysis discriminates: {ok}"
          f"{'' if ok else '  <- the metric is broken; the result above means nothing'}")


if __name__ == "__main__":
    main()
