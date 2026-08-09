"""LIN-000 v0.4 reference.

Written from REGISTRATION-v0.4.md, which is self-contained: nothing here is
justified by a document the commission package does not ship. That was v0.3's
failure and it cost the regression arm of a whole commission.

Carried unchanged from v0.2/v0.3 by IMPORT, not by prose reference -- the
registration restates them in full, so an implementer needs no other document,
while the reference avoids a second copy that could drift.
"""
from __future__ import annotations

import collections

from lineage_v2 import (                                   # unchanged semantics
    SEED, Words, canonical_world, declared_exhaustive_count, exhaustive_worlds,
    is_side_consistent, randomized_worlds, root_of, s_sets, stream_digests,
    verdict,
)
from lineage_v3 import (
    CONFORMANCE_DRAWS, CONFORMANCE_MODULI, ablation_claimcount_catches,
    ablation_shallow_catches, conformance_vector, rewirings, root_set,
)


def roots_asserting(world: list[dict], side: int) -> frozenset[int]:
    return frozenset(i for i, c in enumerate(world)
                     if c["parentIndex"] is None and c["side"] == side)


def t1_readings(world: list[dict], counters: dict) -> None:
    """T1-POS, T1-NEC and T1-ID, as v0.4 registers them.

    T1-NEC differs from v0.3's reference: v0.3 said side-consistency was
    "removed" from W, which this implementation read as the complement and an
    independent one read as unrestricted. v0.4 registers UNRESTRICTED, so the
    population is T1-POS's plus the complement's. The counts are withheld while
    BL-057 is live and are in the results file, which is not committed for the
    same reason.
    """
    base_consistent = is_side_consistent(world)
    base_verdict = verdict(world)
    base_roots = root_set(world)
    base_root_of = [root_of(world, i) for i in range(len(world))]

    for rewired in rewirings(world):
        same_root_set = root_set(rewired) == base_roots
        rewired_consistent = is_side_consistent(rewired)
        changed = verdict(rewired) != base_verdict

        if same_root_set and base_consistent and rewired_consistent:
            counters["t1PosChecked"] += 1
            counters["t1PosViolations"] += changed
        if same_root_set and rewired_consistent:            # W unrestricted
            counters["t1NecChecked"] += 1
            counters["t1NecVerdictChanges"] += changed
        if all(root_of(rewired, i) == base_root_of[i] for i in range(len(world))):
            counters["t1IdChecked"] += 1
            counters["t1IdViolations"] += changed


def l1_status(world: list[dict]) -> tuple[bool, bool]:
    s0, s1 = s_sets(world)
    return (is_side_consistent(world),
            s0 == roots_asserting(world, 0) and s1 == roots_asserting(world, 1))


def l1_disc_histogram(worlds, s_sets_fn=s_sets) -> dict[int, int]:
    """L1-DISC. Replaces L1-NEG, which fired on every eligible world and so
    measured the population rather than the checker. This measures HOW MUCH
    S_a differs, which nothing implies."""
    h: collections.Counter = collections.Counter()
    for w in worlds:
        if is_side_consistent(w):
            continue
        s0, s1 = s_sets_fn(w)
        h[len(s0 ^ roots_asserting(w, 0)) + len(s1 ^ roots_asserting(w, 1))] += 1
    return dict(sorted(h.items()))


def shallow_s_sets(world: list[dict]) -> tuple[frozenset[int], frozenset[int]]:
    """The shallow ablation's S_a, used as L1-DISC's comparison."""
    out: tuple[set, set] = (set(), set())
    for i, c in enumerate(world):
        out[c["side"]].add(i if c["parentIndex"] is None else c["parentIndex"])
    return frozenset(out[0]), frozenset(out[1])
