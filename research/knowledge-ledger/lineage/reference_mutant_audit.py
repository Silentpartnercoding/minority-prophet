#!/usr/bin/env python3
"""A mutant audit that satisfies AMENDMENT-BL058's own standard.

WHY THIS EXISTS. `results/independent-v4/IND-v4-RESULTS.json` reports a mutant
audit as names and firing counts. It publishes no mutant implementations, no
behavioural fingerprints and no equivalence classification, and it does not state
what "checked" counts. So two of its entries fire zero and no reader can tell
whether that means "the mutation is harmless" or "the checker is blind" -- opposite
conclusions from the same number. Amendment 2 of BL-058 requires audits not to do
that. This is the programme's reference audit under that rule.

IT DOES NOT REPLICATE THE INDEPENDENT AUDIT and must not be compared to it
number-for-number. Their unit of counting is not stated in their artefact, so any
correspondence would be a coincidence I arranged. This audit defines its own unit
explicitly, below, and stands on its own.

WHAT IS BEING TESTED. Theorem 1's immunity claim: if a rewiring preserves the root
set and both worlds are side-consistent, the verdict must not change. `verdict`
depends on `root_of` through `s_sets`, so a broken `root_of` can break immunity.

    unit      one (world, rewiring) pair
    checked   pairs eligible under the reading -- root set preserved, and both
              the base and rewired world side-consistent under that reading
    fired     eligible pairs where the verdict changed: an immunity violation

READINGS. The two differ only in the side-consistency predicate used for
eligibility, which is the BL-058 question:

    parentLocal   every claim's side equals its PARENT's side
    rootBased     every claim's side equals its ROOT's side (uses root_of, so the
                  eligible population itself moves when root_of is mutated)

CONTROL. The unmutated implementation must fire zero under both readings. If it
fires, immunity is false and every other row is meaningless.

Usage:
    python3 reference_mutant_audit.py [--max-claims N] [--json OUT]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lineage_v2                                             # noqa: E402
from lineage_v2 import exhaustive_worlds, root_of as reference_root_of  # noqa: E402
from lineage_v3 import rewirings, root_set                    # noqa: E402


# --- mutants, published in full, which is the entire point ------------------

def m_correct(world, index):
    return reference_root_of(world, index)


def m_depth0(world, index):
    """Never walk up: every claim is its own root."""
    return index


def m_depth1(world, index):
    """Walk up at most one generation."""
    parent = world[index]["parentIndex"]
    return index if parent is None else parent


def m_depth2(world, index):
    """Walk up at most two generations."""
    parent = world[index]["parentIndex"]
    if parent is None:
        return index
    grandparent = world[parent]["parentIndex"]
    return parent if grandparent is None else grandparent


def m_always_zero(world, index):
    """Every claim's root is claim 0."""
    return 0


def m_off_by_one_stop(world, index):
    """Stop one generation short of the root."""
    while world[index]["parentIndex"] is not None:
        parent = world[index]["parentIndex"]
        if world[parent]["parentIndex"] is None:
            return index
        index = parent
    return index


def m_min_index_in_chain(world, index):
    """Smallest index seen while walking to the root."""
    smallest = index
    while world[index]["parentIndex"] is not None:
        index = world[index]["parentIndex"]
        smallest = min(smallest, index)
    return smallest


def m_grandparent_skip(world, index):
    """Walk up two generations at a time, falling back to one at the end."""
    while world[index]["parentIndex"] is not None:
        parent = world[index]["parentIndex"]
        grandparent = world[parent]["parentIndex"]
        index = parent if grandparent is None else grandparent
    return index


MUTANTS = {
    "correct": m_correct,
    "depth0": m_depth0,
    "depth1": m_depth1,
    "depth2": m_depth2,
    "alwaysZero": m_always_zero,
    "offByOneStop": m_off_by_one_stop,
    "minIndexInChain": m_min_index_in_chain,
    "grandparentSkip": m_grandparent_skip,
}


def parent_local_consistent(world, _root_of) -> bool:
    return all(c["parentIndex"] is None or world[c["parentIndex"]]["side"] == c["side"]
               for c in world)


def root_based_consistent(world, root_of_fn) -> bool:
    return all(world[root_of_fn(world, i)]["side"] == c["side"]
               for i, c in enumerate(world))


READINGS = {"parentLocal": parent_local_consistent,
            "rootBased": root_based_consistent}


def _verdict_with(root_of_fn, world) -> str:
    """`verdict` via `s_sets`, both of which call the module-level `root_of`."""
    original = lineage_v2.root_of
    lineage_v2.root_of = root_of_fn
    try:
        return lineage_v2.verdict(world)
    finally:
        lineage_v2.root_of = original


def is_equivalent(root_of_fn, max_claims: int) -> tuple[bool, int, int]:
    """Does this mutation change root_of's output anywhere in the space?

    Reported separately from firing counts because it is what makes a zero
    interpretable: a zero from an equivalent mutant is forced and says nothing
    about the checker, while a zero from a behaviour-changing mutant is a blind
    spot.
    """
    differing = total = 0
    for world in exhaustive_worlds(max_claims):
        for i in range(len(world)):
            total += 1
            if root_of_fn(world, i) != reference_root_of(world, i):
                differing += 1
    return differing == 0, differing, total


def audit(root_of_fn, reading_fn, max_claims: int) -> tuple[int, int]:
    checked = fired = 0
    for world in exhaustive_worlds(max_claims):
        base_roots = root_set(world)
        if not reading_fn(world, root_of_fn):
            continue
        base_verdict = _verdict_with(root_of_fn, world)
        for rewired in rewirings(world):
            if root_set(rewired) != base_roots:
                continue
            if not reading_fn(rewired, root_of_fn):
                continue
            checked += 1
            if _verdict_with(root_of_fn, rewired) != base_verdict:
                fired += 1
    return checked, fired


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-claims", type=int, default=lineage_v2.MAX_CLAIMS_EXHAUSTIVE)
    ap.add_argument("--json")
    args = ap.parse_args()

    rows = []
    for name, fn in MUTANTS.items():
        equivalent, differing, total = is_equivalent(fn, args.max_claims)
        row = {"mutant": name,
               "equivalent": equivalent,
               "rootOfCallsDiffering": differing,
               "rootOfCallsTotal": total,
               "classification": "EQUIVALENT" if equivalent else "BEHAVIOUR_CHANGING",
               "readings": {}}
        for reading, predicate in READINGS.items():
            checked, fired = audit(fn, predicate, args.max_claims)
            row["readings"][reading] = {"checked": checked, "fired": fired}
        rows.append(row)

    control = next(r for r in rows if r["mutant"] == "correct")
    control_clean = all(v["fired"] == 0 for v in control["readings"].values())

    # A mutant that changes behaviour and is never caught is the finding this
    # audit exists to be able to state. Reported explicitly rather than left for a
    # reader to derive from two columns.
    blind_spots = [r["mutant"] for r in rows
                   if not r["equivalent"]
                   and all(v["fired"] == 0 for v in r["readings"].values())]
    divergent = [r["mutant"] for r in rows
                 if r["readings"]["parentLocal"]["checked"]
                 != r["readings"]["rootBased"]["checked"]]

    report = {
        "schema": "minority-prophet.lin000-reference-mutant-audit.v0.1",
        "unit": "one (world, rewiring) pair",
        "checkedMeans": ("root set preserved, and both worlds side-consistent under "
                         "the reading"),
        "firedMeans": "the verdict changed on an eligible pair: an immunity violation",
        "maxClaims": args.max_claims,
        "doesNotReplicate": ("IND-v4-RESULTS.json does not state its unit of "
                             "counting, so these figures are not comparable to it "
                             "number-for-number and no correspondence is claimed"),
        "controlFiresZero": control_clean,
        "readingsWithDivergentPopulations": divergent,
        "behaviourChangingButNeverCaught": blind_spots,
        "results": rows,
    }
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(report, indent=2) + "\n")

    print(f"  {'mutant':18s} {'class':20s} {'parentLocal':>18s} {'rootBased':>18s}")
    for r in rows:
        p, b = r["readings"]["parentLocal"], r["readings"]["rootBased"]
        print(f"  {r['mutant']:18s} {r['classification']:20s} "
              f"{p['checked']:>8d}/{p['fired']:<9d} {b['checked']:>8d}/{b['fired']:<9d}")
    print()
    print(f"  control fires zero under both readings : {control_clean}")
    print(f"  populations diverge between readings   : {divergent or 'none'}")
    print(f"  behaviour-changing but never caught    : {blind_spots or 'none'}")
    return 0 if control_clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
