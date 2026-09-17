#!/usr/bin/env python3
"""Fail when the estate's record of an external reproduction goes stale.

The defect this exists for, in the words of the record that found it
(KL-011/EXTERNAL-EVIDENCE.md): a 2026-09-02 independent execution "was thirteen
days old and invisible from this experiment, which still listed both clauses as
untested. This is the stale-self-description family [...] occurring for the
first time ACROSS repositories rather than within one. [...] No such review
spans repositories, so this one was caught by the owner's memory instead."

This is that review. What it can and cannot do, stated plainly so nobody reads
a pass as more than it is:

  * It CANNOT discover a reproduction nobody entered. It is an index checker,
    not a crawler. A reproduction that exists and is not in the file is exactly
    as invisible as before.
  * It CAN fail when an entry stops being self-consistent: a detail record that
    moved or vanished, an entry that omits what it does not discharge, a
    reproduction silently promoted to a stronger claim, or an entry nobody has
    re-derived inside the review interval.

The last one is the load-bearing one for cross-repository staleness. We cannot
reliably diff another repository from here, so we do not pretend to. Instead
the index carries `lastReconciled` per entry and this check fails when that
date ages out, which forces a human to re-derive rather than re-read -- the fix
KL-011 already prescribed. It enforces cadence, not truth.

Exit 0 on success, 1 on any problem.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "research/knowledge-ledger/EXTERNAL-REPRODUCTIONS.json"

# How long an entry may sit without being re-derived. Long enough not to be
# noise, short enough that the thirteen-day miss would have been caught.
REVIEW_INTERVAL_DAYS = 30

# Entries whose detail record lives in THIS repository can be checked directly.
# Entries recorded elsewhere cannot; they are reported, not silently passed.
THIS_REPOSITORY = "minority-prophet"

REQUIRED = (
    "id",
    "reproducer",
    "date",
    "strength",
    "controlDomainIndependence",
    "artifactRepository",
    "artifact",
    "pin",
    "detailRecord",
    "detailRecordRepository",
    "establishes",
    "doesNotDischarge",
    "lastReconciled",
)


def _today() -> datetime.date:
    """Overridable so the cadence rule itself can be tested both ways."""
    override = os.environ.get("EXTERNAL_REPRODUCTIONS_TODAY")
    if override:
        return datetime.date.fromisoformat(override)
    return datetime.date.today()


def main() -> int:
    problems: list[str] = []
    unverifiable: list[str] = []
    document = json.loads(INDEX.read_text(encoding="utf-8"))
    strengths = set(document["strengths"])
    today = _today()

    entries = document["reproductions"]
    if not entries:
        problems.append("EXTERNAL-REPRODUCTIONS.json has no entries; delete it or populate it")

    seen: set[str] = set()
    for entry in entries:
        name = entry.get("id", "<no id>")

        missing = [field for field in REQUIRED if not entry.get(field)]
        if missing:
            problems.append(f"{name}: missing required field(s): {', '.join(missing)}")
            continue

        if name in seen:
            problems.append(f"{name}: duplicate id")
        seen.add(name)

        if entry["strength"] not in strengths:
            problems.append(f"{name}: unknown strength {entry['strength']!r}")

        # A reproduction never establishes organizational independence by
        # existing. Upgrading this field needs its own evidence, so the index
        # refuses to carry the upgrade silently.
        if entry["controlDomainIndependence"] != "not-established":
            problems.append(
                f"{name}: controlDomainIndependence is {entry['controlDomainIndependence']!r}. "
                "A reproduction does not establish control-domain independence; if separate "
                "evidence exists, cite it in the detail record and amend this check deliberately."
            )

        if not entry["pin"]:
            problems.append(f"{name}: a reproduction must pin what was run")

        # Detail records in this repository must actually be here.
        if entry["detailRecordRepository"] == THIS_REPOSITORY:
            target = ROOT / entry["detailRecord"]
            if not target.exists():
                problems.append(
                    f"{name}: detail record is missing: {entry['detailRecord']}. "
                    "The reproduction is now cited by an index with nothing behind it."
                )
        else:
            unverifiable.append(
                f"{name} (detail record lives in {entry['detailRecordRepository']}, not checked from here)"
            )

        # The cadence rule. This is what would have caught the thirteen-day miss.
        try:
            reconciled = datetime.date.fromisoformat(entry["lastReconciled"])
        except ValueError:
            problems.append(f"{name}: lastReconciled is not an ISO date: {entry['lastReconciled']!r}")
            continue
        if reconciled > today:
            problems.append(f"{name}: lastReconciled {reconciled} is in the future")
            continue
        age = (today - reconciled).days
        if age > REVIEW_INTERVAL_DAYS:
            problems.append(
                f"{name}: last re-derived {age} days ago (limit {REVIEW_INTERVAL_DAYS}). "
                "Re-derive it against its source repository -- do not re-read this entry -- "
                "then update lastReconciled."
            )

    if problems:
        print("External-reproduction check FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    strongest = sorted({e["strength"] for e in entries})
    print(
        f"External-reproduction check passed: {len(entries)} reproductions across "
        f"{len({e['artifactRepository'] for e in entries})} repositories ({', '.join(strongest)}); "
        "every entry pinned, every entry states what it does not discharge, none claims "
        f"control-domain independence, none older than {REVIEW_INTERVAL_DAYS} days unreconciled."
    )
    if unverifiable:
        print(f"  {len(unverifiable)} detail record(s) NOT CHECKED from this repository:")
        for item in unverifiable:
            print(f"    - {item}")
    print(
        "  This check cannot discover a reproduction that was never entered here. "
        "A pass means the index is self-consistent and current, not that it is complete."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
