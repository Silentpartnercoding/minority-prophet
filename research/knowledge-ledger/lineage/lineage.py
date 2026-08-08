"""LIN-000: the lineage-bearing world model, exactly as registered.

A world is a list of claims [{"parentIndex": int|None, "side": 0|1}] with
parentIndex < own index. root(c) walks to the chain head. S_a is the
paper's LITERAL S_a -- computed over all claims, not restricted to roots --
so Lemma 1 is a theorem about this function rather than baked into it.
"""

from __future__ import annotations

import random
from itertools import product


def roots_of(world: list[dict]) -> list[int]:
    """root(c) for every claim index, chain-head walk with memoisation."""
    heads: list[int] = []
    for i, claim in enumerate(world):
        parent = claim["parentIndex"]
        heads.append(i if parent is None else heads[parent])
    return heads


def s_sets(world: list[dict]) -> tuple[frozenset[int], frozenset[int]]:
    """The literal S_0, S_1: root indices reached from a-asserting claims."""
    heads = roots_of(world)
    s0 = frozenset(heads[i] for i, c in enumerate(world) if c["side"] == 0)
    s1 = frozenset(heads[i] for i, c in enumerate(world) if c["side"] == 1)
    return s0, s1


def verdict(world: list[dict]) -> str:
    s0, s1 = s_sets(world)
    if len(s1) > len(s0):
        return "1"
    if len(s0) > len(s1):
        return "0"
    return "abstain"


def is_side_consistent(world: list[dict]) -> bool:
    return all(
        c["parentIndex"] is None or world[c["parentIndex"]]["side"] == c["side"]
        for c in world
    )


def root_set(world: list[dict]) -> frozenset[int]:
    return frozenset(i for i, c in enumerate(world) if c["parentIndex"] is None)


def asserting_roots(world: list[dict], side: int) -> frozenset[int]:
    return frozenset(
        i for i, c in enumerate(world) if c["parentIndex"] is None and c["side"] == side
    )


def exhaustive_worlds(max_claims: int = 6):
    """All worlds with 1..max_claims claims: position i has (i+1) parent
    choices ({None} + earlier) x 2 sides. Count(k) = k! * 2^k."""
    for k in range(1, max_claims + 1):
        parent_choices = [[None, *range(i)] for i in range(k)]
        for parents in product(*parent_choices):
            for sides in product((0, 1), repeat=k):
                yield [
                    {"parentIndex": parents[i], "side": sides[i]} for i in range(k)
                ]


def declared_exhaustive_count(max_claims: int = 6) -> int:
    import math
    return sum(math.factorial(k) * 2**k for k in range(1, max_claims + 1))


def randomized_worlds(count: int, seed: int = 20260808):
    """The registered draw schedule, in order, per claim: k uniform 1..20;
    root with p=0.3 else parent uniform among earlier; side uniform for
    roots else parent's side with p=0.9."""
    rng = random.Random(seed)
    for _ in range(count):
        k = rng.randint(1, 20)
        world: list[dict] = []
        for i in range(k):
            if i == 0 or rng.random() < 0.3:
                parent = None
            else:
                parent = rng.randrange(i)
            if parent is None:
                side = rng.randint(0, 1)
            else:
                side = world[parent]["side"] if rng.random() < 0.9 else 1 - world[parent]["side"]
            world.append({"parentIndex": parent, "side": side})
        yield world


# --- rewirings ---------------------------------------------------------------

def valid_reparentings(world: list[dict]):
    """Every single-claim reparenting preserving root set AND side-consistency:
    a non-root claim re-attached to a DIFFERENT earlier same-side claim."""
    for i, claim in enumerate(world):
        if claim["parentIndex"] is None:
            continue
        for new_parent in range(i):
            if new_parent == claim["parentIndex"]:
                continue
            if world[new_parent]["side"] != claim["side"]:
                continue
            rewired = [dict(c) for c in world]
            rewired[i]["parentIndex"] = new_parent
            yield rewired


def root_set_breaking_rewirings(world: list[dict]):
    """Orphan a non-root (new root) or attach a root under an earlier
    same-side claim (root removed) -- each breaks exactly the root-set
    precondition."""
    for i, claim in enumerate(world):
        if claim["parentIndex"] is not None:
            rewired = [dict(c) for c in world]
            rewired[i]["parentIndex"] = None
            yield rewired
        else:
            for new_parent in range(i):
                if world[new_parent]["side"] != claim["side"]:
                    continue
                rewired = [dict(c) for c in world]
                rewired[i]["parentIndex"] = new_parent
                yield rewired


def side_breaking_rewirings(world: list[dict]):
    """Reparent a non-root claim to an earlier OPPOSITE-side claim -- breaks
    exactly the side-consistency precondition (root set preserved)."""
    for i, claim in enumerate(world):
        if claim["parentIndex"] is None:
            continue
        for new_parent in range(i):
            if world[new_parent]["side"] == claim["side"]:
                continue
            rewired = [dict(c) for c in world]
            rewired[i]["parentIndex"] = new_parent
            yield rewired


# --- must-fail ablations (checker power) -------------------------------------

def ablation_shallow_s_sets(world: list[dict]):
    """LB-shallow: root() goes only one step up. MUST be caught by T1-positive."""
    def shallow_head(i: int) -> int:
        parent = world[i]["parentIndex"]
        return i if parent is None else parent
    s0 = frozenset(shallow_head(i) for i, c in enumerate(world) if c["side"] == 0)
    s1 = frozenset(shallow_head(i) for i, c in enumerate(world) if c["side"] == 1)
    return s0, s1


def ablation_claimcount_s_sets(world: list[dict]):
    """LB-claimcount: no root collapse at all. MUST be caught by L1-positive."""
    s0 = frozenset(i for i, c in enumerate(world) if c["side"] == 0)
    s1 = frozenset(i for i, c in enumerate(world) if c["side"] == 1)
    return s0, s1
