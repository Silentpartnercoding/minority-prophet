#!/usr/bin/env python3
"""Reproduce every number in FINDINGS.md from the frozen HGD-1 result.

Read-only. Computes nothing that is not already in
`results/hgd1-v1/result.json`; the arithmetic is subtraction and a comparison
against the threshold quoted in `experiments/HGD-1-PREREGISTRATION.md`.

    python3 research/criterion-reachability/probe.py
"""

from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT = ROOT / "results/hgd1-v1/result.json"

#: From HGD-1g, quoted in CRITERIA.json. An error rate is a proportion, so the
#: floor is zero and the achievable reduction is the head-count error itself.
THRESHOLD = 0.05
FLOOR = 0.0


def main() -> int:
    document = json.loads(RESULT.read_text(encoding="utf-8"))
    pooled = document["observational"]["pooled"]

    print("HGD-1g, as scored: pooled, `any` shift, head - interval >= 0.05\n")
    print(f"{'shift':>6}  {'head':>9}  {'interval':>9}  {'ceiling':>9}  {'achieved':>9}")
    ceilings = {}
    achieved = {}
    for shift in sorted(pooled, key=int):
        head = pooled[shift]["head"]["false_confident_error"]
        interval = pooled[shift]["interval"]["false_confident_error"]
        ceilings[shift] = head - FLOOR
        achieved[shift] = head - interval
        print(f"{shift:>6}  {head:>9.6f}  {interval:>9.6f}  "
              f"{ceilings[shift]:>9.6f}  {achieved[shift]:>9.6f}")

    best_ceiling = max(ceilings.values())
    best_achieved = max(achieved.values())
    print(f"\nbest achievable reduction : {best_ceiling:.6f} "
          f"({best_ceiling * 100:.3f} points)")
    print(f"threshold                 : {THRESHOLD:.6f} "
          f"({THRESHOLD * 100:.3f} points)")
    print(f"reachable                 : {best_ceiling >= THRESHOLD}")
    print(f"shortfall                 : {THRESHOLD - best_ceiling:.6f} "
          f"({(THRESHOLD - best_ceiling) * 100:.3f} points)")
    print(f"run reached               : {best_achieved / best_ceiling:.1%} "
          f"of the arithmetic maximum")

    print("\nThe unscored per-cell reading:")
    by_duration = document["observational"]["by_sample_duration"]
    for shift in sorted(by_duration, key=int):
        for cell, arms in sorted(by_duration[shift].items()):
            gap = (arms["head"]["false_confident_error"]
                   - arms["interval"]["false_confident_error"])
            if gap >= THRESHOLD:
                print(f"  shift {shift}, {cell}: reduction {gap:.6f} "
                      f"({gap * 100:.3f} points) CLEARS the threshold, "
                      f"answered coverage {arms['interval']['answered_coverage']:.4f}")

    print("\nWeights against their absence, on the same data:")
    for shift in sorted(pooled, key=int):
        interval = pooled[shift]["interval"]["false_confident_error"]
        family = pooled[shift]["family"]["false_confident_error"]
        print(f"  shift {shift:>2}: interval {interval:.16f} "
              f"family {family:.16f} identical={interval == family}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
