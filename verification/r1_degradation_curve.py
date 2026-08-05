"""R1 DEGRADATION CURVE — VERIFICATION TRACK, NOT A CANONICAL EXPERIMENT.
Question opened by C. He's 33% single-error result: P(verdict change) as a
function of k ACCIDENTAL root-set-disturbing edge errors (ops bugs), vs the
ADVERSARIAL case which is exact by T4': targeted phantom flow of margin
forces abstention, margin+1 forces reversal.
Method: all side-consistent worlds n=6; k random root-disturbing
side-consistent single-edge edits applied jointly (sampled 60/world/k);
report P(any change), P(reversal), split by original margin."""
import itertools, random
from collections import defaultdict

def all_worlds(n):
    for p in itertools.product(*[range(-1, c) for c in range(n)]):
        for a in itertools.product((0, 1), repeat=n):
            yield p, a

def side_consistent(p, a):
    return all(a[c] == a[p[c]] for c in range(len(p)) if p[c] != -1)

def root(p, c):
    while p[c] != -1: c = p[c]
    return c

def roots(p): return frozenset(c for c in range(len(p)) if p[c] == -1)

def verdict_margin(p, a):
    s1 = frozenset(root(p, c) for c in range(len(p)) if a[c] == 1)
    s0 = frozenset(root(p, c) for c in range(len(p)) if a[c] == 0)
    d = len(s1) - len(s0)
    return (1 if d > 0 else 0 if d < 0 else None), abs(d)

def rootchanging_edits(p, a):
    n = len(p); R = roots(p); out = []
    for c in range(n):
        for np_ in range(-1, c):
            if np_ == p[c]: continue
            if np_ != -1 and a[np_] != a[c]: continue  # keep SC
            q = list(p); q[c] = np_
            if roots(tuple(q)) != R: out.append((c, np_))
    return out

def main(n=6, samples=60, seed=7):
    rng = random.Random(seed)
    stats = defaultdict(lambda: [0, 0, 0])  # (k, margin_bucket) -> [trials, changed, reversed]
    for p, a in all_worlds(n):
        if not side_consistent(p, a): continue
        v0, m0 = verdict_margin(p, a)
        if v0 is None: continue
        edits = rootchanging_edits(p, a)
        if not edits: continue
        mb = min(m0, 4)
        for k in range(1, 5):
            for _ in range(samples):
                q = list(p)
                chosen = rng.sample(edits, min(k, len(edits)))
                ok = True
                for c, np_ in chosen:
                    if np_ != -1 and a[np_] != a[c]: ok = False; break
                    q[c] = np_
                if not ok: continue
                qt = tuple(q)
                if not side_consistent(qt, a): continue
                v1, _ = verdict_margin(qt, a)
                s = stats[(k, mb)]
                s[0] += 1
                s[1] += (v1 != v0)
                s[2] += (v1 is not None and v1 != v0)
    print("k errors | margin | P(any change) | P(full reversal) | n")
    agg = defaultdict(lambda: [0, 0, 0])
    for (k, mb), (t, ch, rv) in sorted(stats.items()):
        print(f"   {k}     |   {mb}    |    {ch/t:.3f}      |     {rv/t:.3f}       | {t}")
        A = agg[k]; A[0]+=t; A[1]+=ch; A[2]+=rv
    print("\nk errors | P(any change) | P(full reversal)   [all margins pooled]")
    for k,(t,ch,rv) in sorted(agg.items()):
        print(f"   {k}     |    {ch/t:.3f}      |     {rv/t:.3f}")

if __name__ == "__main__":
    main()
