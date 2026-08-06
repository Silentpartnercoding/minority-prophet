"""Two reference models of the Minority Prophet core, kept deliberately separate.

`forest` reproduces the structure actually formalized in formal/PROOFS.md,
formal/MinorityProphetV2.lean and verification/independent_check_2026-08.py:
a partial function parent : C -> Option C, i.e. every claim has AT MOST ONE
parent and therefore EXACTLY ONE root.

`dag` reproduces the structure actually implemented in provenance/graph.py and
described in FOUNDATIONS.md: copied_from is a tuple, roots() returns a
frozenset, i.e. every claim has ARBITRARILY MANY parents and roots.

Nothing here is a theorem. Everything here is a finite executable model used to
generate witnesses. Acyclicity is imposed structurally in both models by
requiring every parent index to be strictly smaller than the child index, which
is exactly the "time order" assumption PROOFS.md relies on.
"""

from __future__ import annotations

from itertools import combinations, product

# --------------------------------------------------------------------------
# Forest model: p[c] == -1 means "root", else p[c] < c
# --------------------------------------------------------------------------


def forest_all_parent_fns(n: int):
    return product(*[range(-1, c) for c in range(n)])


def forest_all_worlds(n: int):
    for p in forest_all_parent_fns(n):
        for a in product((0, 1), repeat=n):
            yield p, a


def forest_root(p, c: int) -> int:
    while p[c] != -1:
        c = p[c]
    return c


def forest_roots(p) -> frozenset[int]:
    return frozenset(c for c in range(len(p)) if p[c] == -1)


def forest_side_consistent(p, a) -> bool:
    return all(a[c] == a[p[c]] for c in range(len(p)) if p[c] != -1)


def forest_S(p, a, side: int) -> frozenset[int]:
    return frozenset(forest_root(p, c) for c in range(len(p)) if a[c] == side)


# --------------------------------------------------------------------------
# DAG model: parents[c] is a frozenset of indices strictly below c
# --------------------------------------------------------------------------


def dag_all_parent_sets(n: int):
    """All acyclic multi-parent structures on n claims (index order = time)."""
    per_claim = []
    for c in range(n):
        subsets = []
        for k in range(c + 1):
            subsets.extend(frozenset(s) for s in combinations(range(c), k))
        per_claim.append(subsets)
    return product(*per_claim)


def dag_all_worlds(n: int):
    for ps in dag_all_parent_sets(n):
        for a in product((0, 1), repeat=n):
            yield ps, a


def dag_roots_of(ps, c: int) -> frozenset[int]:
    """Mirrors EvidenceGraph.roots(): union of ancestors with no parents."""
    if not ps[c]:
        return frozenset({c})
    out: set[int] = set()
    for parent in ps[c]:
        out |= dag_roots_of(ps, parent)
    return frozenset(out)


def dag_roots(ps) -> frozenset[int]:
    return frozenset(c for c in range(len(ps)) if not ps[c])


def dag_side_consistent(ps, a) -> bool:
    return all(a[parent] == a[c] for c in range(len(ps)) for parent in ps[c])


def dag_S(ps, a, side: int) -> frozenset[int]:
    out: set[int] = set()
    for c in range(len(ps)):
        if a[c] == side:
            out |= dag_roots_of(ps, c)
    return frozenset(out)


# --------------------------------------------------------------------------
# Shared verdict / margin, defined once on a pair of side-root sets
# --------------------------------------------------------------------------


def verdict_of(s1: int, s0: int):
    """F as specified in PROOFS.md: 1 / 0 / None(abstain)."""
    return 1 if s1 > s0 else (0 if s0 > s1 else None)


def forest_verdict(p, a):
    return verdict_of(len(forest_S(p, a, 1)), len(forest_S(p, a, 0)))


def dag_verdict(ps, a):
    return verdict_of(len(dag_S(ps, a, 1)), len(dag_S(ps, a, 0)))


def forest_margin(p, a) -> int:
    return abs(len(forest_S(p, a, 1)) - len(forest_S(p, a, 0)))


def dag_margin(ps, a) -> int:
    return abs(len(dag_S(ps, a, 1)) - len(dag_S(ps, a, 0)))
