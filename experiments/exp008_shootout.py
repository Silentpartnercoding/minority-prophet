"""EXP008 -- best-in-class shootout on multi-item worlds.
Sources answer K=8 binary propositions. Observers (n=6, r=0.9/item) are
independent roots. An originator (r=0.75/item -- plausible but wrong on ~2
items) is copied by m=40 copiers. Under attack: copied answers flipped w.p.
0.15 (answer-paraphrase), citations forged w.p. 0.9, 35% sybils (no cite,
early clustered timing) -- an archived exploratory mixture historically
attributed to the unfinished optimizer; it is not EXP007A's selected attack.

Baselines (stdlib implementations, standard formulations):
  majority        per-item head count
  dawid_skene     EM with per-source sensitivity/specificity (20 iters)
  truthfinder     iterative reliability weighting (10 iters)
  accu_lite       dependence-discounted iterative voting: per-source copy
                  probability from best answer-agreement with an earlier
                  source, weight = logit(rel)*(1-copyprob)  [Dong-style]
  cluster_vote    collapse near-identical answer vectors (Hamming<=1),
                  one vote per cluster
  ev_root_inf     OURS: per-source lineage inference (answers+time+cite),
                  per-item side root counting
  ev_root_decl    ours with oracle lineage (upper bound)
Metrics: per-item accuracy; minority recovery (items where copied majority is
wrong); false reversals (wrong overrule of a correct majority)."""
import random, statistics, math, sys
from collections import defaultdict

K = 8

def gen_world(rng, attack):
    truth = [rng.randint(0, 1) for _ in range(K)]
    src = []  # (id, t, answers, cite, is_root, true_parent)
    t0 = 10.0
    orig = [truth[k] if rng.random() < 0.75 else 1 - truth[k] for k in range(K)]
    src.append(dict(id=0, t=t0, ans=orig, cite=None, true_parent=None))
    for i in range(6):
        a = [truth[k] if rng.random() < 0.9 else 1 - truth[k] for k in range(K)]
        src.append(dict(id=len(src), t=1 + rng.random() * 8, ans=a, cite=None,
                        true_parent=None))
    tree = [0]
    pf = 0.15 if attack else 0.03
    fc = 0.9 if attack else 0.0
    sy = 0.35 if attack else 0.0
    for i in range(40):
        p = src[rng.choice(tree)]
        a = [1 - x if rng.random() < pf else x for x in p["ans"]]
        is_syb = rng.random() < sy
        cite = None if is_syb else (rng.randrange(1, 7) if rng.random() < fc
                                    else p["id"])
        t = (t0 + 0.2 + rng.random() * 3) if is_syb else p["t"] + 0.5 + rng.random() * 5
        s = dict(id=len(src), t=t, ans=a, cite=cite, true_parent=p["id"])
        src.append(s); tree.append(s["id"])
    return truth, src

def majority(src):
    return [1 if sum(s["ans"][k] for s in src) * 2 > len(src) else 0
            for k in range(K)]

def dawid_skene(src, iters=20):
    n = len(src)
    p = [0.5 + 0.5 * (sum(s["ans"][k] for s in src) / n - 0.5) * 2 for k in range(K)]
    p = [min(.99, max(.01, x)) for x in p]
    sens = [0.7] * n; spec = [0.7] * n
    for _ in range(iters):
        for i, s in enumerate(src):
            a = sum(p[k] if s["ans"][k] == 1 else 0 for k in range(K))
            b = sum(p[k] for k in range(K))
            sens[i] = min(.99, max(.01, (a + 1) / (b + 2)))
            c = sum((1 - p[k]) if s["ans"][k] == 0 else 0 for k in range(K))
            d = sum(1 - p[k] for k in range(K))
            spec[i] = min(.99, max(.01, (c + 1) / (d + 2)))
        for k in range(K):
            l1 = l0 = 0.0
            for i, s in enumerate(src):
                if s["ans"][k] == 1:
                    l1 += math.log(sens[i]); l0 += math.log(1 - spec[i])
                else:
                    l1 += math.log(1 - sens[i]); l0 += math.log(spec[i])
            p[k] = 1 / (1 + math.exp(min(50, max(-50, l0 - l1))))
    return [1 if x > 0.5 else 0 for x in p]

def truthfinder(src, iters=10):
    w = [1.0] * len(src)
    est = majority(src)
    for _ in range(iters):
        for i, s in enumerate(src):
            agr = sum(1 for k in range(K) if s["ans"][k] == est[k]) / K
            w[i] = min(.99, max(.01, agr))
        est = []
        for k in range(K):
            v1 = sum(math.log(w[i] / (1 - w[i])) for i, s in enumerate(src)
                     if s["ans"][k] == 1)
            v0 = sum(math.log(w[i] / (1 - w[i])) for i, s in enumerate(src)
                     if s["ans"][k] == 0)
            est.append(1 if v1 > v0 else 0)
    return est

def accu_lite(src, iters=10):
    n = len(src)
    order = sorted(range(n), key=lambda i: src[i]["t"])
    copyprob = [0.0] * n
    for pos, i in enumerate(order):
        best = 0.0
        for j in order[:pos]:
            agr = sum(1 for k in range(K)
                      if src[i]["ans"][k] == src[j]["ans"][k]) / K
            best = max(best, agr)
        # independence given ~0.8 accuracy predicts agr ~ .68; excess => copying
        copyprob[i] = min(1.0, max(0.0, (best - 0.75) / 0.25))
    w = [1.0] * n; est = majority(src)
    for _ in range(iters):
        for i, s in enumerate(src):
            agr = sum(1 for k in range(K) if s["ans"][k] == est[k]) / K
            w[i] = min(.99, max(.01, agr))
        est = []
        for k in range(K):
            v1 = v0 = 0.0
            for i, s in enumerate(src):
                lw = math.log(w[i] / (1 - w[i])) * (1 - copyprob[i])
                if s["ans"][k] == 1: v1 += lw
                else: v0 += lw
            est.append(1 if v1 > v0 else 0)
    return est

def cluster_vote(src):
    clusters = []
    for s in src:
        for c in clusters:
            if sum(1 for k in range(K) if s["ans"][k] != c[0]["ans"][k]) <= 1:
                c.append(s); break
        else:
            clusters.append([s])
    reps = [c[0] for c in clusters]
    return [1 if sum(r["ans"][k] for r in reps) * 2 > len(reps) else 0
            for k in range(K)]

def infer_parents(src):
    order = sorted(src, key=lambda s: s["t"])
    parent = {}
    for pos, s in enumerate(order):
        best, bs = None, 0.55
        for p in order[:pos]:
            agr = sum(1 for k in range(K) if s["ans"][k] == p["ans"][k]) / K
            score = 0.55 * agr + 0.25 * math.exp(-(s["t"] - p["t"]) / 5) \
                    + 0.20 * (1.0 if s["cite"] == p["id"] else 0.0)
            if score > bs: best, bs = p["id"], score
        if best is not None: parent[s["id"]] = best
    return parent

def ev_root(src, parent):
    memo = {}
    def root(i):
        if i in memo: return memo[i]
        memo[i] = i if i not in parent else root(parent[i])
        return memo[i]
    byid = {s["id"]: s for s in src}
    out = []
    for k in range(K):
        sides = {0: set(), 1: set()}
        for s in src:
            sides[s["ans"][k]].add(root(s["id"]))
        out.append(1 if len(sides[1]) > len(sides[0])
                   else 0 if len(sides[0]) > len(sides[1])
                   else byid[0]["ans"][k])  # tie -> follow majority side
    return out

def run(worlds=100, seeds=(1, 2, 3, 4, 5)):
    methods = dict(majority=lambda s: majority(s),
                   dawid_skene=lambda s: dawid_skene(s),
                   truthfinder=lambda s: truthfinder(s),
                   accu_lite=lambda s: accu_lite(s),
                   cluster_vote=lambda s: cluster_vote(s),
                   ev_root_inf=lambda s: ev_root(s, infer_parents(s)),
                   ev_root_decl=lambda s: ev_root(
                       s, {x["id"]: x["true_parent"] for x in s
                           if x["true_parent"] is not None}))
    for attack in (False, True):
        agg = {m: dict(acc=[], mrec=[], frev=[]) for m in methods}
        for seed in seeds:
            rng = random.Random(seed)
            stats = {m: [0, 0, 0, 0, 0] for m in methods}  # ok,n, mrec_ok,mrec_n, frev
            for w in range(worlds):
                truth, src = gen_world(rng, attack)
                maj = majority(src)
                for m, fn in methods.items():
                    est = fn(src)
                    for k in range(K):
                        ok = est[k] == truth[k]
                        stats[m][0] += ok; stats[m][1] += 1
                        if maj[k] != truth[k]:
                            stats[m][2] += ok; stats[m][3] += 1
                        elif est[k] != maj[k]:
                            stats[m][4] += 1
            for m in methods:
                s = stats[m]
                agg[m]["acc"].append(s[0] / s[1])
                agg[m]["mrec"].append(s[2] / max(1, s[3]))
                agg[m]["frev"].append(s[4] / s[1])
        label = "ATTACK (optimizer mix)" if attack else "NO ADVERSARY"
        print(f"\n== {label} == (5 seeds x 100 worlds x 8 items; mean [95% CI])")
        print(f"{'method':13s} {'accuracy':>22s} {'minority-recovery':>22s} {'false-rev':>10s}")
        for m in methods:
            def fmt(v):
                mu = statistics.mean(v)
                h = 1.96 * statistics.stdev(v) / math.sqrt(len(v))
                return f"{mu:.3f} [{mu-h:.3f},{mu+h:.3f}]"
            print(f"{m:13s} {fmt(agg[m]['acc']):>22s} {fmt(agg[m]['mrec']):>22s} "
                  f"{statistics.mean(agg[m]['frev']):>9.3f}")

if __name__ == "__main__":
    run()
