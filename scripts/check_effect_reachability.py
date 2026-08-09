#!/usr/bin/env python3
"""BL-060 — refuse to run an experiment whose population cannot exhibit the effect.

KL-001 v0.2 registered a primary endpoint, froze the protocol before the results,
instrumented both arms identically, and produced an honest number that could not
have come out any other way. Its corpus contained zero instances of the feature
its mechanism acts on, so the endpoint was pinned to the baseline *before any data
existed*. Nothing in preregistration, ablation, or mutation testing catches that:
every one of those interrogates the instrument, and the instrument was fine.

The check is narrow on purpose. It does not ask "can this population exhibit the
effect", which would require knowing the effect -- the thing under study. It asks
the author to name the **population property their own mechanism depends on**,
which they must already know in order to explain why the mechanism works, and then
verifies the population contains it.

    "the ledger returns not_established when the scanner skipped a file"
     -> property: a file the scanner cannot decode
     -> corpus v1: 0   corpus v2: 22

A probe is a command, not a shell string, for the same reason Epistemic CI uses
argument arrays: no implicit expansion, no quoting ambiguity. It prints one
integer to stdout.

THE PROBE ITSELF IS TESTED. A probe that reports a large number for any input
would pass this check while proving nothing -- the same vacuity that made a
MUST-be-0 test decoration in LIN-000. So every declaration must also name a
`negativeControl` population where the property is absent, and the probe must
report *below* the minimum there. A probe that cannot distinguish the two is
rejected as unfalsifiable, and the check says so rather than passing.

Usage:
    python3 scripts/check_effect_reachability.py --preregistration P [--root DIR]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

PLACEHOLDER = "{population}"


class Unreachable(Exception):
    """The declaration is absent, malformed, or fails against the population."""


def _run_probe(probe: list[str], population: pathlib.Path, root: pathlib.Path) -> int:
    argv = [population.as_posix() if part == PLACEHOLDER else part for part in probe]
    try:
        result = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                                timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unreachable(f"probe could not be executed: {exc}") from exc
    if result.returncode != 0:
        raise Unreachable(
            f"probe exited {result.returncode}: {result.stderr.strip()[:200]}")
    text = result.stdout.strip()
    try:
        return int(text)
    except ValueError:
        raise Unreachable(
            f"probe must print one integer to stdout; got {text[:80]!r}") from None


def check(prereg: pathlib.Path, root: pathlib.Path) -> list[str]:
    problems: list[str] = []
    document = json.loads(prereg.read_text())
    requirements = document.get("effectRequires")

    # An undeclared requirement is a failure, not a skip. "This experiment's
    # mechanism depends on no property of its population" is a strong claim; if it
    # is true the author can declare it explicitly and this check has nothing to
    # do. Treating silence as consent is how v0.2 shipped.
    if not requirements:
        return [f"{prereg.name}: declares no `effectRequires`. Name the population "
                f"property the mechanism depends on, or state explicitly that it "
                f"depends on none."]
    if not isinstance(requirements, list):
        return [f"{prereg.name}: `effectRequires` must be a list"]

    for index, requirement in enumerate(requirements):
        label = f"{prereg.name}[{index}]"
        prop = requirement.get("property")
        probe = requirement.get("probe")
        population = requirement.get("population")
        control = requirement.get("negativeControl")
        minimum = requirement.get("minimum", 1)

        if not prop or not isinstance(probe, list) or not probe:
            problems.append(f"{label}: needs `property` and a non-empty `probe` "
                            f"argument array")
            continue
        if not population:
            problems.append(f"{label}: needs a `population` path to check")
            continue
        if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
            problems.append(f"{label}: `minimum` must be a positive integer")
            continue
        if not control:
            problems.append(
                f"{label}: needs a `negativeControl` population where the property "
                f"is absent. Without one, a probe that reports a large number for "
                f"any input passes this check and proves nothing.")
            continue

        try:
            found = _run_probe(probe, pathlib.Path(population), root)
        except Unreachable as exc:
            problems.append(f"{label}: on the population, {exc}")
            continue
        try:
            in_control = _run_probe(probe, pathlib.Path(control), root)
        except Unreachable as exc:
            problems.append(f"{label}: on the negative control, {exc}")
            continue

        # Order matters: report an unfalsifiable probe before a reachability
        # verdict, because a probe that cannot fail makes the verdict meaningless
        # in either direction.
        if in_control >= minimum:
            problems.append(
                f"{label}: PROBE IS UNFALSIFIABLE. It reports {in_control} on the "
                f"negative control ({control}), which is at or above the minimum "
                f"of {minimum}. A probe that fires on a population lacking the "
                f"property cannot demonstrate that another population has it.")
            continue
        if found < minimum:
            problems.append(
                f"{label}: EFFECT UNREACHABLE. The mechanism depends on "
                f"'{prop}', and the population {population} contains {found} "
                f"(needs {minimum}). The endpoint is pinned to its baseline by "
                f"construction; running this changes nothing that data could "
                f"decide.")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    prereg = pathlib.Path(args.preregistration)
    problems = check(prereg, root)
    if problems:
        print("Effect-reachability check FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    document = json.loads(prereg.read_text())
    print(f"Effect reachability verified: {len(document['effectRequires'])} "
          f"declared population propert(ies) present, each demonstrated absent "
          f"in a negative control.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
