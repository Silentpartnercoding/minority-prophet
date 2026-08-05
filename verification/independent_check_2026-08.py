"""Independent re-implementation of 'The Minority Prophet Property' (v1.0 draft) Section 3, by Christopher He, August 2026. Reproduced all formal checks (Lemma 1, Theorems 1–3: zero violations across 5,912 side-consistent worlds, 116,032 root-preserving rewirings, 4,166 duplications); identified the T4 abstention/reversal distinction (correction C2) and the E2 precision misframing (correction C1)."""

"""
Autoformalization of "The Minority Prophet Property" (draft v0.9).

Encodes Section 3 definitions literally, then exhaustively checks Lemma 1 and
Theorems 1-4 as stated, plus the informal prose claims that surround them.

World W = (C, parent, assert):
  C          = {0, ..., n-1}, index doubles as the time order
  parent[c]  = -1 (root) or a claim index < c   (partial function -> forest)
  assert[c]  in {0,1}
  root(c)    = terminal ancestor under parent
  S_a(W)     = { root(c) : assert(c) = a }      (paper's literal definition)
  verdict    = 1 if |S1|>|S0|, 0 if |S0|>|S1|, None (abstain) if equal
"""

from itertools import product
from fractions import Fraction

# ---------------------------------------------------------------- definitions

def all_parent_fns(n):
    return product(*[range(-1, c) for c in range(n)])

def all_worlds(n):
    for p in all_parent_fns(n):
        for a in product((0, 1), repeat=n):
            yield p, a

def root(p, c):
    while p[c] != -1:
        c = p[c]
    return c

def roots(p):
    return frozenset(c for c in range(len(p)) if p[c] == -1)

def side_consistent(p, a):
    return all(a[c] == a[p[c]] for c in range(len(p)) if p[c] != -1)

def S(p, a, side):
    return frozenset(root(p, c) for c in range(len(p)) if a[c] == side)

def verdict(p, a):
    s1, s0 = len(S(p, a, 1)), len(S(p, a, 0))
    return 1 if s1 > s0 else (0 if s0 > s1 else None)

def margin(p, a):
    return abs(len(S(p, a, 1)) - len(S(p, a, 0)))

NMAX = 6

# ------------------------------------------------- Lemma 1 and Theorems 1,2,3

def check_lemma1_and_t1(nmax=NMAX):
    n_sc = 0
    n_pairs = 0
    l1_viol = t1_viol = 0
    # counter-experiment: side-consistent rewirings that do NOT preserve roots
    rootchanging_pairs = 0
    rootchanging_flips = 0
    for n in range(1, nmax + 1):
        for p, a in all_worlds(n):
            if not side_consistent(p, a):
                continue
            n_sc += 1
            # Lemma 1: S_a == a-asserting roots
            for side in (0, 1):
                if S(p, a, side) != frozenset(r for r in roots(p) if a[r] == side):
                    l1_viol += 1
            v = verdict(p, a)
            R = roots(p)
            for q in all_parent_fns(n):
                if q == p or not side_consistent(q, a):
                    continue
                if roots(q) == R:                       # T1 preconditions met
                    n_pairs += 1
                    if verdict(q, a) != v:
                        t1_viol += 1
                else:                                   # only root integrity lost
                    rootchanging_pairs += 1
                    if verdict(q, a) != v:
                        rootchanging_flips += 1
    return dict(side_consistent_worlds=n_sc, t1_rewirings=n_pairs,
                lemma1_violations=l1_viol, t1_violations=t1_viol,
                rootchanging_rewirings=rootchanging_pairs,
                rootchanging_verdict_changes=rootchanging_flips)

def check_t2(nmax=5):
    """Duplicate claim d: new claim with assert[d]=assert[c], parent[d]=c."""
    viol = 0
    tested = 0
    for n in range(1, nmax + 1):
        for p, a in all_worlds(n):
            if not side_consistent(p, a):
                continue
            v = verdict(p, a)
            for c in range(n):
                p2 = tuple(list(p) + [c])
                a2 = tuple(list(a) + [a[c]])
                tested += 1
                if verdict(p2, a2) != v:
                    viol += 1
    return dict(duplications_tested=tested, t2_violations=viol)

def check_t3(nmax=5):
    """(a) majority voting is not copy-invariant; (b) with no lineage
    (every claim treated as a root) evidence-root == majority vote."""
    def majority(a):
        ones = sum(a)
        zeros = len(a) - ones
        return 1 if ones > zeros else (0 if zeros > ones else None)
    maj_broken = 0
    degenerate_mismatch = 0
    for n in range(1, nmax + 1):
        for p, a in all_worlds(n):
            if not side_consistent(p, a):
                continue
            for c in range(n):
                a2 = tuple(list(a) + [a[c]])
                if majority(a2) != majority(a):
                    maj_broken += 1
            # no-lineage world: parent = -1 everywhere
            flat = tuple([-1] * n)
            if verdict(flat, a) != majority(a):
                degenerate_mismatch += 1
    return dict(majority_copy_variance_witnesses=maj_broken,
                nolineage_vs_majority_mismatches=degenerate_mismatch)

# ------------------------------------------------------- Theorem 4 tightness

def check_t4_tightness(nmax=NMAX):
    """T4 as stated: flip requires |net cross-side root flow| >= margin.
    Tight version: a genuine FLIP requires margin+1; exactly margin buys only
    an abstention. Count worlds where flow == margin and outcome is abstain."""
    exact_margin_gives_abstain = 0
    exact_margin_gives_flip = 0
    for n in range(1, nmax + 1):
        for p, a in all_worlds(n):
            if not side_consistent(p, a):
                continue
            v = verdict(p, a)
            if v is None:
                continue
            m = margin(p, a)
            d = len(S(p, a, 1)) - len(S(p, a, 0))
            # adversary applies net cross-side root flow of exactly `margin`,
            # each unit shifting the difference one step toward the loser
            flow = m
            d_after = d - flow if d > 0 else d + flow
            new_v = 1 if d_after > 0 else (0 if d_after < 0 else None)
            if new_v is None:
                exact_margin_gives_abstain += 1
            elif new_v != v:
                exact_margin_gives_flip += 1
    return dict(flow_equals_margin_yields_abstain=exact_margin_gives_abstain,
                flow_equals_margin_yields_flip=exact_margin_gives_flip)

# --------------------------------- what happens when side-consistency is lost

def scan_non_side_consistent(nmax=NMAX):
    """The regime T4 is actually about (cross-side flow) is the regime where
    Lemma 1 does not hold. Check the literal definition S_a = {root(c):...}
    there: a single root can land in BOTH S0 and S1."""
    double_counted = 0
    total = 0
    verdict_from_one_root = []
    for n in range(2, nmax + 1):
        for p, a in all_worlds(n):
            if side_consistent(p, a):
                continue
            total += 1
            s0, s1 = S(p, a, 0), S(p, a, 1)
            if s0 & s1:
                double_counted += 1
            if len(roots(p)) == 1 and verdict(p, a) is not None:
                verdict_from_one_root.append((p, a, verdict(p, a)))
    return dict(non_sc_worlds=total, worlds_with_root_on_both_sides=double_counted,
                decisive_verdicts_from_a_single_root=len(verdict_from_one_root),
                example=verdict_from_one_root[:1])

# ------------------------------------- single-attribution-error flip rate

def single_edge_error_flip_rate(n=6):
    """'Attribution accuracy is irrelevant to the verdict.' Test it: perturb ONE
    edge (one who-copied-whom error), keep side-consistency, measure flips."""
    tot_root_preserving = flips_root_preserving = 0
    tot_root_changing = flips_root_changing = 0
    for p, a in all_worlds(n):
        if not side_consistent(p, a):
            continue
        v = verdict(p, a)
        R = roots(p)
        for c in range(n):
            for newpar in range(-1, c):
                if newpar == p[c]:
                    continue
                q = list(p); q[c] = newpar; q = tuple(q)
                if not side_consistent(q, a):
                    continue
                if roots(q) == R:
                    tot_root_preserving += 1
                    flips_root_preserving += (verdict(q, a) != v)
                else:
                    tot_root_changing += 1
                    flips_root_changing += (verdict(q, a) != v)
    return dict(root_preserving_edits=tot_root_preserving,
                root_preserving_flips=flips_root_preserving,
                root_changing_edits=tot_root_changing,
                root_changing_flips=flips_root_changing,
                root_changing_flip_rate=round(flips_root_changing / max(tot_root_changing, 1), 4))

# ------------------------------- does the verdict depend on copy volume at all?

def copy_volume_dependence():
    """Under R1+R2 the aggregator ignores every non-root claim. So the ratio rho
    (copied majority : independent observers) cannot appear in its accuracy."""
    out = []
    n_obs = 5
    for m in (0, 10, 100, 10_000):
        # 5 independent roots asserting 1, m copies of a single root asserting 0
        p = [-1] * n_obs + [-1] + [n_obs] * m
        a = [1] * n_obs + [0] * (m + 1)
        out.append((m, len(S(tuple(p), tuple(a), 1)), len(S(tuple(p), tuple(a), 0)),
                    verdict(tuple(p), tuple(a))))
    return out

# ------------------------------------------------------ E2 arithmetic recheck

def e2_precision(N=5729):
    rows = []
    for name, recoveries, false_rate in (("dependence-adjusted", 1, 0.0010),
                                         ("exposure-weighted", 58, 0.0950)):
        false_n = false_rate * N
        prec = recoveries / (recoveries + false_n)
        rows.append((name, recoveries, round(false_n, 1), round(100 * prec, 1)))
    return rows

if __name__ == "__main__":
    print("== Lemma 1 / Theorem 1 (all side-consistent worlds, n<=6) ==")
    for k, v in check_lemma1_and_t1().items():
        print(f"  {k}: {v}")
    print("\n== Theorem 2 ==")
    for k, v in check_t2().items():
        print(f"  {k}: {v}")
    print("\n== Theorem 3 ==")
    for k, v in check_t3().items():
        print(f"  {k}: {v}")
    print("\n== Theorem 4 tightness ==")
    for k, v in check_t4_tightness().items():
        print(f"  {k}: {v}")
    print("\n== Non-side-consistent regime (where T4's 'cross-side' lives) ==")
    for k, v in scan_non_side_consistent().items():
        print(f"  {k}: {v}")
    print("\n== One attribution error, n=6 ==")
    for k, v in single_edge_error_flip_rate().items():
        print(f"  {k}: {v}")
    print("\n== Copy-volume dependence (m copies vs 5 honest roots) ==")
    for row in copy_volume_dependence():
        print(f"  m={row[0]:>6}  |S1|={row[1]}  |S0|={row[2]}  verdict={row[3]}")
    print("\n== E2 overrule precision, recomputed ==")
    for row in e2_precision():
        print(f"  {row[0]:>20}: {row[1]} correct, ~{row[2]} false -> precision {row[3]}%")
