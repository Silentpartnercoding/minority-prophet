"""Independent re-implementation of 'The Minority Prophet Property' (v1.0 draft) Section 3, by Christopher He, August 2026. Reproduced all formal checks (Lemma 1, Theorems 1–3: zero violations across 5,912 side-consistent worlds, 116,032 root-preserving rewirings, 4,166 duplications); identified the T4 abstention/reversal distinction (correction C2) and the E2 precision misframing (correction C1).

AMENDED 2026-08-05 (formal-core audit): check_t4_tightness has been rewritten.
The original never constructed a perturbed world and therefore could not fail;
see formal/COUNTEREXAMPLES.md CE-03. The replacement builds W' explicitly under
two adversary shapes and shows that a root CONVERSION costs two units, not one.
No other function in this file was changed; all previously published counts
reproduce exactly."""

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
    """T4 tightness, checked against CONSTRUCTED worlds.

    CORRECTED 2026-08-05. The previous version of this function enumerated
    worlds only to read off `d` and `m`, then computed `d_after = d - flow` in
    closed form and reported the verdict of that integer. It never built a
    second world, so its result ("4,638/4,638") restated the definition of a
    threshold function and could not fail for any input. It was not evidence
    for T4'. See formal/COUNTEREXAMPLES.md CE-03 finding 1.

    This version builds W' explicitly, by two DISTINCT adversary shapes whose
    costs differ by a factor of two:

      ADDITION   append `flow` fresh roots on the losing side.
                 Each is worth 1 unit of p0 - p1.
      CONVERSION move `k` existing roots (and, vacuously here, their subtrees)
                 to the other side. Each is worth 2 units of p0 - p1.

    The theorem T4'/`T4'_flow_eq_margin_abstains` is about UNITS, so it is the
    addition column that must show abstention at flow == margin. The conversion
    column is reported alongside because the repository's prose reads T4' in
    conversion terms, under which it is false by a factor of two.
    """
    add_flow_eq_margin_abstain = 0
    add_flow_eq_margin_flip = 0
    add_flow_margin_plus_one_reverses = 0
    conv_reversed_at_or_below_margin = 0
    conv_min_cost_matches_floor_formula = 0
    conv_worlds = 0
    parity_violations = 0

    for n in range(1, nmax + 1):
        for p, a in all_worlds(n):
            if not side_consistent(p, a):
                continue
            v = verdict(p, a)
            if v is None:
                continue
            m = margin(p, a)
            loser = 0 if v == 1 else 1

            # --- ADDITION: append m fresh roots to the losing side -----------
            p_add = tuple(list(p) + [-1] * m)
            a_add = tuple(list(a) + [loser] * m)
            v_add = verdict(p_add, a_add)
            if v_add is None:
                add_flow_eq_margin_abstain += 1
            elif v_add != v:
                add_flow_eq_margin_flip += 1

            # margin + 1 additions must reverse
            p_rev = tuple(list(p) + [-1] * (m + 1))
            a_rev = tuple(list(a) + [loser] * (m + 1))
            if verdict(p_rev, a_rev) == loser:
                add_flow_margin_plus_one_reverses += 1

            # --- CONVERSION: relabel winning-side roots one at a time --------
            winners = sorted(r for r in roots(p) if a[r] == v)
            conv_worlds += 1
            reversed_at = None
            abstained_at = None
            for k in range(1, len(winners) + 1):
                a_conv = list(a)
                for r in winners[:k]:
                    # flip the root and its whole descendant subtree, so the
                    # perturbed world stays side-consistent
                    for c in range(len(p)):
                        if root(p, c) == r:
                            a_conv[c] = loser
                a_conv = tuple(a_conv)
                assert side_consistent(p, a_conv), "conversion broke side-consistency"
                v_conv = verdict(p, a_conv)
                if v_conv is None and abstained_at is None:
                    abstained_at = k
                if v_conv == loser and reversed_at is None:
                    reversed_at = k
                    break
            if reversed_at is not None:
                if reversed_at <= m:
                    conv_reversed_at_or_below_margin += 1
                if reversed_at == m // 2 + 1:
                    conv_min_cost_matches_floor_formula += 1
            # parity: conversions cannot produce a tie at odd margin
            if m % 2 == 1 and abstained_at is not None:
                parity_violations += 1

    return dict(
        addition_flow_eq_margin_yields_abstain=add_flow_eq_margin_abstain,
        addition_flow_eq_margin_yields_flip=add_flow_eq_margin_flip,
        addition_margin_plus_one_reverses=add_flow_margin_plus_one_reverses,
        conversion_decisive_worlds=conv_worlds,
        conversion_reversed_at_or_below_margin=conv_reversed_at_or_below_margin,
        conversion_min_cost_equals_floor_margin_half_plus_one=conv_min_cost_matches_floor_formula,
        odd_margin_abstentions_via_conversion=parity_violations,
    )

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
    print("\n== Theorem 4 tightness (constructed worlds; addition vs conversion) ==")
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
