#!/usr/bin/env python3
"""Offline illustration and bounded checks; not a proof or a new research run."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CITATION = runpy.run_path(str(ROOT / "interop/nist-agentic-research-probes/independence_demo.py"))
CHECKS = runpy.run_path(str(ROOT / "tests/test_lineage_t1_l1.py"))
CHECK_NAMES = (
    "test_declared_count_is_derivable_and_matches_the_result",
    "test_t1_holds_live_on_the_exhaustive_prefix",
    "test_t1_protection_does_not_extend_past_its_preconditions",
    "test_l1_holds_live_and_fails_where_it_must",
    "test_ablations_are_caught_live",
    "test_committed_result_meets_every_registered_expectation",
)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args], text=True, stderr=subprocess.PIPE,
    ).strip()


def check_citations() -> None:
    rows = CITATION["CITATIONS"]
    claims = [CITATION["Citation"](True, root, basis) for _, root, basis in rows]
    result = CITATION["verdict"](claims)
    if len(rows) != 3 or result.support_true != frozenset({"MIL-2291"}):
        raise ValueError(f"expected 3 citations and root MIL-2291; got {len(rows)}, {result.support_true}")


def main() -> int:
    # Reused research regression tests contain assertions: reject -O rather
    # than silently turning those checks into a misleading pass.
    if sys.flags.optimize:
        print("FAIL: Python optimization disables assertions; unset PYTHONOPTIMIZE and omit -O")
        return 1
    label = "source receipt"
    try:
        commit = git("rev-parse", "HEAD")
        state = "modified" if git("status", "--porcelain", "--untracked-files=normal") else "clean"
        print(f"SOURCE: commit={commit} worktree={state}")
        print(f"UTC={datetime.now(timezone.utc).isoformat(timespec='seconds')}")
        label = "citation fixture"
        check_citations()
        print("PASS: 3 citations resolve to 1 declared root (constructed fixture)")
        for label in CHECK_NAMES:
            CHECKS[label]()
            print(f"PASS: {label}")
        print(f"PASS: bounded immunity checks and negative controls ({len(CHECK_NAMES)} checks)")
        print("Scope: live finite forest checks plus archived-result consistency; no new confirmatory result.")
        print("Proof: pinned Lean build is separate; see docs/CHECK.md.")
        return 0
    except Exception as exc:
        print(f"FAIL: {label}: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
