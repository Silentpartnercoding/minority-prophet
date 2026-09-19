#!/usr/bin/env python3
"""Fail when a preregistered criterion could not have been met by any result.

Every integrity gate in this repository checks an ARTIFACT: a digest that moved,
a link that broke, a claim promoted without evidence. This one checks a
CRITERION, and it exists because of a defect none of the others could see.

HGD-1g required interval accounting to beat head count by at least 5 percentage
points of false-confident error on the frozen EPA data. The pooled head-count
error was 4.349 points. You cannot remove 5 points of error from a baseline
containing 4.349 of them, so no possible result could have satisfied HGD-1g --
not a perfect method, not a method scoring zero error at every shift. The run
achieved 4.227 points, 97.2% of the arithmetic maximum, and was recorded false.

The existing controls all worked. The threshold was frozen before any value was
inspected, and `HGD-1-PREREGISTRATION.md` forbids tuning it afterwards. That
discipline is why the result stands and why it must not be edited now. What no
control checked was whether the threshold was ATTAINABLE at the moment it was
frozen -- a question that needs only the metric's bounds, and that would have
cost nothing to ask before the data existed.

DELIBERATELY NARROW. This checks absolute-difference criteria over metrics with
a declared floor, which is the class that produced the defect. It refuses to
score forms it does not model rather than guessing at them: HGD-2's criteria are
ratios and relative risks, and a reachability argument for those is a different
and harder claim. Twice tonight a validator was written stricter than the
contract it enforced; a checker that invented verdicts for criterion shapes it
does not understand would be the same error in a costlier place.

WHAT IT CANNOT DO. It cannot tell whether a reachable threshold is a WELL-CHOSEN
one, and it cannot read a protocol's prose. Every entry in `CRITERIA.json` is
hand-declared and hand-checked against the protocol it quotes. This is a
staleness check over a maintained registry, not a discovery engine -- the same
honest limitation `check_gate_coverage.py` states about its own map.

Exit 0 when every registered criterion was reachable, or was unreachable and
acknowledged in writing. Exit 1 on an unacknowledged unreachable criterion.

    python3 scripts/check_criterion_reachability.py
    python3 scripts/check_criterion_reachability.py --json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "research/criterion-reachability/CRITERIA.json"

SCHEMA = "minority-prophet.criterion-reachability.v1"

#: The only criterion shapes this checker models. A form outside this set is an
#: error in the registry, never something to approximate.
SUPPORTED_FORMS = ("absolute-difference",)

REQUIRED_KEYS = (
    "id", "experiment", "protocol", "result", "quoted", "form", "comparison",
    "threshold", "quantifier", "minuend", "subtrahend", "subtrahendFloor",
    "floorBasis", "scoredOn",
)


class RegistryError(ValueError):
    """The criteria registry cannot be read as written."""


def resolve(document: Any, path: str) -> dict[str, float]:
    """Every value a dotted path selects, keyed by the cell it came from.

    A `*` segment iterates the keys at that level, which is how one criterion
    quantified over several shifts or cells is expressed. Anything missing is an
    error: a registry naming a path the result does not contain is stale, and
    silently skipping it would report a criterion as reachable because its
    operands could not be found.
    """
    values: dict[str, float] = {}

    def walk(node: Any, parts: list[str], label: str) -> None:
        if not parts:
            if not isinstance(node, (int, float)) or isinstance(node, bool):
                raise RegistryError(f"{path}: {label or '<root>'} is not a number")
            values[label] = float(node)
            return
        head, rest = parts[0], parts[1:]
        if head == "*":
            if not isinstance(node, dict):
                raise RegistryError(f"{path}: cannot iterate a non-object at {label}")
            for key in sorted(node):
                walk(node[key], rest, key if not label else f"{label}/{key}")
            return
        if not isinstance(node, dict) or head not in node:
            raise RegistryError(f"{path}: missing segment {head!r}")
        walk(node[head], rest, label)

    walk(document, path.split("."), "")
    if not values:
        raise RegistryError(f"{path}: selected nothing")
    return values


def assess(entry: dict[str, Any], root: pathlib.Path) -> dict[str, Any]:
    """Whether any possible result could have satisfied this criterion."""
    missing = [key for key in REQUIRED_KEYS if key not in entry]
    if missing:
        raise RegistryError(
            f"{entry.get('id', '<unnamed>')} is missing " + ", ".join(missing)
        )
    if entry["form"] not in SUPPORTED_FORMS:
        raise RegistryError(
            f"{entry['id']}: unsupported form {entry['form']!r}; this checker "
            f"models only {', '.join(SUPPORTED_FORMS)} and will not guess"
        )
    if entry["comparison"] != ">=":
        raise RegistryError(f"{entry['id']}: unsupported comparison {entry['comparison']!r}")
    if entry["quantifier"] not in ("any", "every"):
        raise RegistryError(f"{entry['id']}: unsupported quantifier {entry['quantifier']!r}")

    result_path = root / entry["result"]
    if not result_path.is_file():
        raise RegistryError(f"{entry['id']}: result not found: {entry['result']}")
    document = json.loads(result_path.read_text(encoding="utf-8"))

    minuends = resolve(document, entry["minuend"])
    subtrahends = resolve(document, entry["subtrahend"])
    if set(minuends) != set(subtrahends):
        raise RegistryError(
            f"{entry['id']}: minuend and subtrahend select different cells"
        )

    floor = float(entry["subtrahendFloor"])
    threshold = float(entry["threshold"])

    # The best any result could do in a cell is drive the subtrahend to its
    # floor. That is the ceiling on the difference, and it depends only on the
    # metric's bounds -- never on what was measured.
    ceilings = {cell: value - floor for cell, value in minuends.items()}
    achieved = {cell: minuends[cell] - subtrahends[cell] for cell in minuends}

    if entry["quantifier"] == "any":
        best_ceiling = max(ceilings.values())
        reachable = best_ceiling >= threshold
    else:
        best_ceiling = min(ceilings.values())
        reachable = best_ceiling >= threshold

    return {
        "id": entry["id"],
        "experiment": entry["experiment"],
        "threshold": threshold,
        "quantifier": entry["quantifier"],
        "ceilingByCell": ceilings,
        "achievedByCell": achieved,
        "bestCeiling": best_ceiling,
        "bestAchieved": (max(achieved.values()) if entry["quantifier"] == "any"
                         else min(achieved.values())),
        "reachable": reachable,
        "shortfall": None if reachable else threshold - best_ceiling,
        "acknowledged": entry.get("acknowledged"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()
    root = pathlib.Path(args.root)

    registry = json.loads((root / REGISTRY.relative_to(ROOT)).read_text(encoding="utf-8"))
    if registry.get("schema") != SCHEMA:
        print(f"criteria registry must declare schema {SCHEMA}", file=sys.stderr)
        return 1

    entries = registry.get("criteria")
    if not isinstance(entries, list) or not entries:
        print("criteria registry has no entries; delete it or populate it", file=sys.stderr)
        return 1

    assessments = []
    problems: list[str] = []
    for entry in entries:
        try:
            assessment = assess(entry, root)
        except RegistryError as exc:
            problems.append(str(exc))
            continue
        assessments.append(assessment)
        if not assessment["reachable"]:
            acknowledged = assessment["acknowledged"]
            if not acknowledged:
                problems.append(
                    f"{assessment['id']} was UNREACHABLE as scored "
                    f"(threshold {assessment['threshold']}, ceiling "
                    f"{assessment['bestCeiling']:.6f}) and is not acknowledged "
                    f"anywhere. Record the finding beside the result; never edit "
                    f"a frozen criterion to make it reachable."
                )
            elif not (root / acknowledged).is_file():
                problems.append(
                    f"{assessment['id']}: acknowledgement is missing: {acknowledged}"
                )

    if args.json:
        print(json.dumps({"criteria": assessments, "problems": problems},
                         indent=2, sort_keys=True))
        return 1 if problems else 0

    for assessment in assessments:
        verdict = "reachable" if assessment["reachable"] else "UNREACHABLE"
        print(f"{assessment['id']} ({assessment['experiment']}): {verdict}")
        print(f"  threshold        {assessment['threshold']:.6f}")
        print(f"  best ceiling     {assessment['bestCeiling']:.6f}"
              f"  ({assessment['quantifier']} cell)")
        print(f"  best achieved    {assessment['bestAchieved']:.6f}")
        if not assessment["reachable"]:
            attained = assessment["bestAchieved"] / assessment["bestCeiling"]
            print(f"  shortfall        {assessment['shortfall']:.6f} "
                  f"-- no possible result could satisfy this")
            print(f"  the run reached  {attained:.1%} of the arithmetic maximum")
            print(f"  acknowledged in  {assessment['acknowledged']}")

    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if problems:
        return 1

    print(f"\nCriterion-reachability check passed: {len(assessments)} registered "
          f"criterion(s); every unreachable one is acknowledged in writing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
