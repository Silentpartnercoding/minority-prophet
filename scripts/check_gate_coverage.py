#!/usr/bin/env python3
"""Fail when a declared gate-coverage entry goes stale.

The defect this exists for: an experiment can declare a prerequisite unsolved
while the artifact that solves it sits elsewhere in this repository. That
happened six times (see CROSS-PROGRAMME-RECONCILIATION.md) and every instance
was caught by a person remembering, because no review spans series.

This cannot detect coverage that nobody has noticed yet -- it is a staleness
check over a hand-maintained map, not a discovery engine. What it does is make
the map fail loudly instead of rotting quietly:

  * a cited artifact that no longer exists is an error;
  * a gatePhrase no longer present in the experiment's STATUS.json is an error,
    because the gate was rewritten and the coverage claim may no longer apply;
  * a coverage entry on an experiment whose state advanced is an error, because
    coverage must never be the reason a state moved;
  * an `adjacent` entry that omits what it does not discharge is an error.

Exit 0 on success, 1 on any problem.
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "research/knowledge-ledger"
MAP = PROGRAM / "GATE-COVERAGE.json"

# States an experiment may hold while carrying a coverage entry. Coverage
# records that a gate is answerABLE elsewhere; it is never evidence for the
# experiment itself, so it must not accompany a promotion.
UNPROMOTED = {"seeded", "fixture-passed"}


def main() -> int:
    problems: list[str] = []
    document = json.loads(MAP.read_text(encoding="utf-8"))
    strengths = set(document["strengths"])

    if not document["entries"]:
        problems.append("GATE-COVERAGE.json has no entries; delete it or populate it")

    for entry in document["entries"]:
        experiment = entry["experiment"]
        directory = PROGRAM / "experiments" / experiment

        if entry["strength"] not in strengths:
            problems.append(f"{experiment}: unknown strength {entry['strength']!r}")

        if not entry.get("doesNotDischarge"):
            problems.append(f"{experiment}: every entry must state what it does NOT discharge")

        status_path = directory / "STATUS.json"
        if not status_path.exists():
            problems.append(f"{experiment}: no STATUS.json to check the gate against")
            continue
        status = json.loads(status_path.read_text(encoding="utf-8"))

        haystack = json.dumps(status).lower()
        if entry["gatePhrase"].lower() not in haystack:
            problems.append(
                f"{experiment}: gate phrase {entry['gatePhrase']!r} is no longer in STATUS.json. "
                "The gate moved; re-check whether the cited coverage still applies."
            )

        if status.get("state") not in UNPROMOTED:
            problems.append(
                f"{experiment}: state is {status.get('state')!r} while carrying a coverage entry. "
                "Coverage is never evidence for the experiment it covers."
            )

        for relative in entry["coveredBy"]:
            if not (ROOT / relative).exists():
                problems.append(f"{experiment}: cited artifact is missing: {relative}")

    # Pending entries cite artifacts on unmerged branches. Assert they are still
    # ABSENT: when the branch merges, this fails and forces the entry to be
    # promoted into entries[] and checked properly, rather than sitting as an
    # unverifiable citation.
    for entry in document.get("pendingEntries", []):
        present = [r for r in entry["coveredBy"] if (ROOT / r).exists()]
        if present:
            problems.append(
                f"{entry['experiment']}: pending coverage from PR #{entry['pendingPullRequest']} "
                f"has landed ({', '.join(present)}). Move this entry into entries[] so it is checked."
            )
        if not entry.get("pendingPullRequest"):
            problems.append(f"{entry['experiment']}: a pending entry must name the pull request it waits on")

    if problems:
        print("Gate-coverage check FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    covered = {e["experiment"] for e in document["entries"]}
    pending = document.get("pendingEntries", [])
    print(
        f"Gate-coverage check passed: {len(document['entries'])} declared entries across "
        f"{len(covered)} experiments; every cited artifact present, every gate phrase intact, "
        "no covered experiment promoted." + (
            f" {len(pending)} pending unmerged "
            f"({', '.join('#' + str(e['pendingPullRequest']) for e in pending)}), all still absent as expected."
            if pending else " No entries pending an unmerged branch."
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
