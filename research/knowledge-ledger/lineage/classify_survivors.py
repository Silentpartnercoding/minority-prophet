#!/usr/bin/env python3
"""BL-058b — classify the two mutants that fired zero under both readings.

IND-v4-RESULTS.json reports a mutant audit as fired-counts only. Two entries,
`minIndexInChain` and `grandparentSkip`, fire 0 under both the parent-local and
root-based readings. Nothing in the results file distinguishes the two things a
zero can mean:

    EQUIVALENT   the mutant does not change behaviour, so nothing could fire
                 -- a harmless result, and not a gap in the checker
    UNDETECTED   the mutant changes behaviour and the checker does not notice
                 -- a blind spot, and the most serious kind of finding here

This tool settles the first half only: whether behaviour changes. It does not run
the checker, so it reports BEHAVIOUR_CHANGING rather than UNDETECTED, and a
separate run is needed to conclude "blind spot".

RECONSTRUCTION CAVEAT, and it is the important one. The independent implementation
is not in this repository. The two mutants below are reconstructed from their
NAMES. If a reconstruction is equivalent, that is a fact about the reconstruction,
not proof the original was harmless -- the same name admits other implementations.
What is established either way is that IND-v4-RESULTS.json records mutants by name
and fired-count with no implementation, no fingerprint and no equivalence
classification, so no reader can tell which of the two meanings a zero carries.
An audit whose zeros cannot be interpreted is not falsifiable.

Those are opposite conclusions from an identical number. BL-056 established
behavioural fingerprinting as the way to separate them, and it was not applied to
this audit. Neither mutant is named in any finding; they appear only in the raw
results, and FINDING-BL057 describes "five" mutants where the data has seven.

Usage:
    python3 classify_survivors.py [--json OUT]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lineage_v2 import exhaustive_worlds, root_of  # noqa: E402


def mutant_min_index_in_chain(world: list[dict], index: int) -> int:
    """Return the smallest index seen while walking to the root."""
    smallest = index
    seen = set()
    while world[index]["parentIndex"] is not None:
        if index in seen:
            raise ValueError("lineage cycle")
        seen.add(index)
        index = world[index]["parentIndex"]
        smallest = min(smallest, index)
    return min(smallest, index)


def mutant_grandparent_skip(world: list[dict], index: int) -> int:
    """Walk up two generations at a time, falling back to one at the end."""
    seen = set()
    while world[index]["parentIndex"] is not None:
        if index in seen:
            raise ValueError("lineage cycle")
        seen.add(index)
        parent = world[index]["parentIndex"]
        grandparent = world[parent]["parentIndex"]
        index = parent if grandparent is None else grandparent
    return index


def control_off_by_one(world: list[dict], index: int) -> int:
    """POSITIVE CONTROL: genuinely broken, must not be classified EQUIVALENT.

    Stops one generation short of the root. A classifier that reports EQUIVALENT
    for everything would be vacuous -- it would "prove" any mutant harmless,
    including a real blind spot -- so it has to be shown capable of returning the
    other answer. This is the same discipline as the negative control in
    check_effect_reachability.py.
    """
    seen = set()
    while world[index]["parentIndex"] is not None:
        parent = world[index]["parentIndex"]
        if world[parent]["parentIndex"] is None:
            return index                      # stop short: return the child
        if index in seen:
            raise ValueError("lineage cycle")
        seen.add(index)
        index = parent
    return index


MUTANTS = {
    "minIndexInChain": mutant_min_index_in_chain,
    "grandparentSkip": mutant_grandparent_skip,
    "control:offByOneStop": control_off_by_one,
}


def classify(name: str, mutant) -> dict:
    worlds = 0
    differing_worlds = 0
    differing_calls = 0
    total_calls = 0
    first_example = None

    for world in exhaustive_worlds():
        worlds += 1
        differs_here = False
        for i in range(len(world)):
            total_calls += 1
            if mutant(world, i) != root_of(world, i):
                differing_calls += 1
                differs_here = True
                if first_example is None:
                    first_example = {"world": world, "index": i,
                                     "reference": root_of(world, i),
                                     "mutant": mutant(world, i)}
        differing_worlds += differs_here

    # If behaviour never differs, a zero firing count is forced and carries no
    # information about the checker. If it does differ, a zero would be worth
    # investigating -- but firing is not measured here, so that stays conditional.
    equivalent = differing_calls == 0
    return {
        "mutant": name,
        "worldsExamined": worlds,
        "rootOfCalls": total_calls,
        "callsWhereBehaviourDiffers": differing_calls,
        "worldsWhereBehaviourDiffers": differing_worlds,
        # Deliberately NOT called "undetected". This measures whether the
        # mutation changes root_of's output; it does not run the checker, so it
        # cannot say whether the checker fires. Naming the second class
        # "undetected" would assert a result never measured -- the exact overclaim
        # this programme keeps finding.
        "classification": "EQUIVALENT" if equivalent else "BEHAVIOUR_CHANGING",
        "meaning": ("the mutation cannot change root_of's output on any world in "
                    "the exhaustive space, so a firing count of zero is forced and "
                    "implies nothing about checker power"
                    if equivalent else
                    "the mutation does change root_of's output, so a firing count "
                    "of zero for it WOULD indicate a blind spot -- firing is not "
                    "measured here"),
        "firstDifferingExample": first_example,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()

    results = [classify(name, fn) for name, fn in MUTANTS.items()]
    report = {
        "schema": "minority-prophet.lin000-survivor-classification.v0.1",
        "scope": ("classified against this repository's v4 reference; the "
                  "independent implementation that produced IND-v4-RESULTS.json "
                  "is not in this repository"),
        "results": results,
    }
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(report, indent=2) + "\n")

    for r in results:
        print(f"  {r['mutant']:18s} {r['classification']:12s} "
              f"differs on {r['callsWhereBehaviourDiffers']}/{r['rootOfCalls']} calls "
              f"in {r['worldsWhereBehaviourDiffers']}/{r['worldsExamined']} worlds")
    print()
    for r in results:
        print(f"  {r['mutant']}: {r['meaning']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
