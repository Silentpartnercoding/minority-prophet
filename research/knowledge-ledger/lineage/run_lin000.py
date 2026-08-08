#!/usr/bin/env python3
"""LIN-000 confirmatory runner. Executes REGISTRATION.md exactly; the
declared exhaustive count is asserted before any evaluation."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lineage  # noqa: E402


def check_world(world, counters):
    consistent = lineage.is_side_consistent(world)
    s0, s1 = lineage.s_sets(world)
    v = lineage.verdict(world)

    if consistent:
        counters["sideConsistentWorlds"] += 1
        # L1-positive
        if s0 != lineage.asserting_roots(world, 0) or s1 != lineage.asserting_roots(world, 1):
            counters["l1PositiveViolations"] += 1
            counters.setdefault("preserved", []).append({"test": "L1-positive", "world": world})
        # T1-positive over every valid single reparenting
        for rewired in lineage.valid_reparentings(world):
            counters["t1Rewirings"] += 1
            if lineage.s_sets(rewired) != (s0, s1) or lineage.verdict(rewired) != v:
                counters["t1PositiveViolations"] += 1
                if len(counters.setdefault("preserved", [])) < 10:
                    counters["preserved"].append({"test": "T1-positive", "world": world, "rewired": rewired})
        # T1-violation (i): root-set-breaking MUST be able to change the verdict
        for rewired in lineage.root_set_breaking_rewirings(world):
            if lineage.verdict(rewired) != v:
                counters["t1RootSetBreakChangesVerdictWorlds"] += 1
                break
        # ablation LB-shallow: caught when any valid reparenting moves its S-sets
        base = lineage.ablation_shallow_s_sets(world)
        for rewired in lineage.valid_reparentings(world):
            if lineage.ablation_shallow_s_sets(rewired) != base:
                counters["lbShallowCaughtWorlds"] += 1
                break
        # ablation LB-claimcount: caught when it disagrees with L1's roots
        if (lineage.ablation_claimcount_s_sets(world)
                != (lineage.asserting_roots(world, 0), lineage.asserting_roots(world, 1))):
            counters["lbClaimcountCaughtWorlds"] += 1
    else:
        counters["sideInconsistentWorlds"] += 1
        # L1-negative: literal S_a differing from a-asserting roots
        if s0 != lineage.asserting_roots(world, 0) or s1 != lineage.asserting_roots(world, 1):
            counters["l1NegativeWitnessWorlds"] += 1
        if s0 & s1:
            counters["rootOnBothSidesWorlds"] += 1

    # T1-violation (ii): side-breaking rewirings exist and can move S-sets/verdict
    if consistent:
        for rewired in lineage.side_breaking_rewirings(world):
            if lineage.s_sets(rewired) != (s0, s1) or lineage.verdict(rewired) != v:
                counters["t1SideBreakChangesWorlds"] += 1
                break


def fresh_counters():
    return {
        "sideConsistentWorlds": 0, "sideInconsistentWorlds": 0,
        "l1PositiveViolations": 0, "t1PositiveViolations": 0, "t1Rewirings": 0,
        "t1RootSetBreakChangesVerdictWorlds": 0, "t1SideBreakChangesWorlds": 0,
        "l1NegativeWitnessWorlds": 0, "rootOnBothSidesWorlds": 0,
        "lbShallowCaughtWorlds": 0, "lbClaimcountCaughtWorlds": 0,
    }


def run_phase(name, worlds_iter, expected_count=None):
    started = time.monotonic()
    counters = fresh_counters()
    total = 0
    for world in worlds_iter:
        total += 1
        check_world(world, counters)
    report = {"phase": name, "worlds": total, **counters,
              "elapsedSeconds": round(time.monotonic() - started, 3)}
    if expected_count is not None:
        report["declaredCount"] = expected_count
        report["countMatchesDeclared"] = total == expected_count
    report.pop("preserved", None) if not counters.get("preserved") else None
    if "preserved" in counters:
        report["preservedViolations"] = counters["preserved"]
    return report


def main():
    declared = lineage.declared_exhaustive_count(6)
    assert declared == 50362, "registration arithmetic drifted"

    # The declared count is asserted BEFORE evaluation, KL-000 style.
    generated = sum(1 for _ in lineage.exhaustive_worlds(6))
    if generated != declared:
        raise SystemExit(f"INVALID: generated {generated} != declared {declared}")

    exhaustive = run_phase("exhaustive", lineage.exhaustive_worlds(6), declared)

    # Seed reproduction check: two draws, identical streams.
    a = [w for w in lineage.randomized_worlds(1000)]
    b = [w for w in lineage.randomized_worlds(1000)]
    seed_ok = a == b

    randomized = run_phase("randomized", lineage.randomized_worlds(100_000))

    invalid = []
    for phase in (exhaustive, randomized):
        if phase["l1PositiveViolations"] or phase["t1PositiveViolations"]:
            invalid.append(f"{phase['phase']}: positive-test violations -- a finding against the formalisation or the paper")
        for must_be_positive in ("t1RootSetBreakChangesVerdictWorlds", "t1SideBreakChangesWorlds",
                                  "l1NegativeWitnessWorlds", "lbShallowCaughtWorlds",
                                  "lbClaimcountCaughtWorlds"):
            if phase[must_be_positive] == 0:
                invalid.append(f"{phase['phase']}: {must_be_positive} is zero -- checker vacuous or negatives unreachable")
    if not exhaustive["countMatchesDeclared"]:
        invalid.append("exhaustive count mismatch")
    if not seed_ok:
        invalid.append("seed does not reproduce an identical stream")

    result = {
        "schema": "minority-prophet.lin000-result.v0.1",
        "experiment": "LIN-000",
        "registration": "REGISTRATION.md (committed before implementation)",
        "declaredExhaustiveCount": declared,
        "seed": 20260808,
        "seedReproducesIdenticalStream": seed_ok,
        "phases": {"exhaustive": exhaustive, "randomized": randomized},
        "invalidationReasons": invalid,
        "result": "passed" if not invalid else "invalid-or-finding",
        "minimalL1NegativeWitness": {
            "world": [{"parentIndex": None, "side": 0}, {"parentIndex": 0, "side": 1}],
            "note": "root asserts 0; its cross-side child places the SAME root in S_1 -- the paper's "
                    "section 3 scope-note phenomenon (one root on both sides of the literal S_a) in "
                    "the smallest possible world",
        },
    }
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "lin000-result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("result", "invalidationReasons", "seedReproducesIdenticalStream")}, indent=2))
    for name, phase in result["phases"].items():
        print(name, {k: phase[k] for k in ("worlds", "sideConsistentWorlds", "t1Rewirings",
                                            "t1PositiveViolations", "l1PositiveViolations",
                                            "t1RootSetBreakChangesVerdictWorlds",
                                            "l1NegativeWitnessWorlds", "lbShallowCaughtWorlds",
                                            "lbClaimcountCaughtWorlds")})


if __name__ == "__main__":
    main()
