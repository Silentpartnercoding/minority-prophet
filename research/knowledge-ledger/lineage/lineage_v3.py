"""LIN-000 v0.3 reference: the semantics under test, defined.

Written from REGISTRATION-v0.3.md, committed first (d3422c2). The generator,
draw schedules, enumeration order and canonical form are imported unchanged from
v0.2 — BL-051 established they are sufficient, and v0.3 must reproduce their
digests rather than re-pin them.

What is new here is only what is tested:

  T1-POS  the paper's Theorem 1: ROOT-SET-preserving, both worlds side-consistent
  T1-NEC  the same with clause (ii) dropped -- MUST fail, or the precondition is
          decorative
  T1-ID   root(c)-preserving -- an identity, kept as a self-check and excluded
          from Theorem 1's evidence
"""
from __future__ import annotations

import hashlib
from typing import Iterator

from lineage_v2 import (                                    # unchanged in v0.3
    Words, canonical_world, declared_exhaustive_count, exhaustive_worlds,
    is_side_consistent, randomized_worlds, root_of, s_sets, stream_digests,
    verdict, SEED,
)

CONFORMANCE_MODULI = (2863311531, 2576980378, 1717986919, 20, 10, 2, 1)
CONFORMANCE_DRAWS = 1000


# --- D7: force the rejection rule --------------------------------------------

def conformance_vector() -> list[dict]:
    """Each modulus drawn 1,000 times from a freshly seeded generator.

    The word count is the observable: an implementation that omits the rejection
    rule consumes exactly CONFORMANCE_DRAWS words and produces different values.
    """
    out = []
    for n in CONFORMANCE_MODULI:
        words = Words(SEED)
        values = [words.uniform_below(n) for _ in range(CONFORMANCE_DRAWS)]
        payload = ",".join(str(v) for v in values).encode("ascii")
        rejection_region = (1 << 32) % n
        out.append({
            "modulus": n,
            "digest": hashlib.sha256(payload).hexdigest(),
            "wordsConsumed": words.consumed,
            "rejections": words.consumed - CONFORMANCE_DRAWS,
            "rejectionRegion": rejection_region,
        })
    return out


# --- the three T1 readings, kept distinct ------------------------------------

def root_set(world: list[dict]) -> frozenset[int]:
    """The set of claims that are roots -- the paper's clause (i)."""
    return frozenset(i for i, c in enumerate(world) if c["parentIndex"] is None)


def rewirings(world: list[dict]) -> Iterator[list[dict]]:
    """Same k, same sides, at least one parentIndex changed, each null or earlier."""
    k = len(world)
    choices = [[None, *range(i)] for i in range(k)]
    current = [c["parentIndex"] for c in world]
    odometer = [0] * k
    while True:
        candidate = [choices[i][odometer[i]] for i in range(k)]
        if candidate != current:
            yield [{"parentIndex": p, "side": world[i]["side"]}
                   for i, p in enumerate(candidate)]
        for i in range(k - 1, -1, -1):
            odometer[i] += 1
            if odometer[i] < len(choices[i]):
                break
            odometer[i] = 0
            if i == 0:
                return


def t1_readings(world: list[dict], counters: dict) -> None:
    """Accumulate T1-POS, T1-NEC and T1-ID over one world's rewirings."""
    base_consistent = is_side_consistent(world)
    base_verdict = verdict(world)
    base_roots = root_set(world)
    base_root_of = [root_of(world, i) for i in range(len(world))]

    for rewired in rewirings(world):
        same_root_set = root_set(rewired) == base_roots
        rewired_consistent = is_side_consistent(rewired)
        changed = verdict(rewired) != base_verdict

        # T1-POS -- the paper: clause (i) root SET, clause (ii) side-consistency
        if same_root_set and base_consistent and rewired_consistent:
            counters["t1PosChecked"] += 1
            if changed:
                counters["t1PosViolations"] += 1

        # T1-NEC -- clause (ii) dropped from the ORIGINAL. Must produce changes.
        if same_root_set and rewired_consistent and not base_consistent:
            counters["t1NecChecked"] += 1
            if changed:
                counters["t1NecVerdictChanges"] += 1

        # T1-ID -- the v0.2 condition, retained and declared an identity
        if all(root_of(rewired, i) == base_root_of[i] for i in range(len(world))):
            counters["t1IdChecked"] += 1
            if changed:
                counters["t1IdViolations"] += 1


# --- D6: ablations, constructed and with catch criteria ----------------------

def ablation_shallow_catches(world: list[dict]) -> bool:
    """Depth-one attribution instead of chain-walking."""
    shallow: tuple[set[int], set[int]] = (set(), set())
    for i, c in enumerate(world):
        shallow[c["side"]].add(i if c["parentIndex"] is None else c["parentIndex"])
    s0, s1 = s_sets(world)
    return frozenset(shallow[0]) != s0 or frozenset(shallow[1]) != s1


def ablation_claimcount_catches(world: list[dict]) -> bool:
    """Count claims per side instead of roots per side."""
    n0 = sum(1 for c in world if c["side"] == 0)
    n1 = len(world) - n0
    ablated = "1" if n1 > n0 else "0" if n0 > n1 else "abstain"
    return ablated != verdict(world)


# --- L1, per phase (D9) -------------------------------------------------------

def l1_status(world: list[dict]) -> tuple[bool, bool]:
    """(side_consistent, s_a_equals_roots_asserting)."""
    s0, s1 = s_sets(world)
    r0 = frozenset(i for i, c in enumerate(world)
                   if c["parentIndex"] is None and c["side"] == 0)
    r1 = frozenset(i for i, c in enumerate(world)
                   if c["parentIndex"] is None and c["side"] == 1)
    return is_side_consistent(world), (s0 == r0 and s1 == r1)
