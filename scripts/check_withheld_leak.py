#!/usr/bin/env python3
"""Reject additions that publish a live commission's withheld outcome values.

The public-boundary check catches SECRETS leaving. This catches ANSWERS leaving,
which no pattern can recognise: the values are ordinary integers in a results
table, indistinguishable from any other figure by shape alone. They are
identifiable only relative to a declaration of what is currently withheld.

Why this exists (M27). RUN-20260807-10's draft run report proposed commissioning
LIN-000 and, in the same commit, published twelve of the fourteen outcome
counters that would have falsified it. The proposal and the numbers that test it
travelled together and nothing checked for it. The pass condition had to be
rebuilt around stream digests after the fact.

Publication is a leak surface, and the leak runs forward in time: it does not
expose today's secret, it retires tomorrow's experiment.

Declarations live in research/knowledge-ledger/LIVE-COMMISSIONS.json. An entry
with status "live" contributes its results file's integers, minus its declared
bounds, to the blocked set. Closing a commission removes the block, because the
answer is then legitimately publishable -- that is what closing means.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

DECLARATION = pathlib.Path("research/knowledge-ledger/LIVE-COMMISSIONS.json")
SELF_EXEMPT = {
    "scripts/check_withheld_leak.py",
    "tests/test_withheld_leak.py",
    "research/knowledge-ledger/LIVE-COMMISSIONS.json",
}
# Values small enough to appear coincidentally in unrelated prose. A blocked set
# containing 2 or 7 would make every document a violation.
MIN_INTERESTING = 100
# Above MIN_INTERESTING but below this, a value collides with ordinary code
# constants -- slice lengths, buffer sizes, thresholds -- often enough that
# enforcing it produces noise rather than protection. BL-057's L1-DISC histogram
# contains 120, which matched `stderr.strip()[:120]` in an unrelated script.
#
# Such values are reported as UNPROTECTABLE rather than enforced or dropped. A
# control that quietly stops covering something is worse than one that says so:
# the declaration then has to decide whether the experiment can tolerate it.
COLLISION_FLOOR = 1000


# Structurally derivable metadata, not outcomes. prefixDigestCount is
# worlds // prefixDigestsEvery by definition; blocking it would block the
# integer 100 across the whole repository.
DERIVABLE_KEYS = {"prefixDigests", "prefixDigestCount", "prefixDigestsEvery"}


def _integers(value) -> set[int]:
    found: set[int] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in DERIVABLE_KEYS:
                continue
            found |= _integers(item)
    elif isinstance(value, list):
        for item in value:
            found |= _integers(item)
    elif isinstance(value, int) and not isinstance(value, bool):
        found.add(value)
    return found


def withheld_sets(root: pathlib.Path) -> dict[str, set[int]]:
    """Blocked integers per live commission id."""
    declaration = root / DECLARATION
    if not declaration.is_file():
        return {}
    document = json.loads(declaration.read_text())
    blocked: dict[str, set[int]] = {}
    for entry in document.get("commissions", []):
        if entry.get("status") != "live":
            continue
        results = root / entry["resultsFile"]
        if not results.is_file():
            # Two safety rules of this programme collided here, and both are
            # right. "A live commission's results must not be committed" --
            # publishing them defeats the commission. "A live commission with
            # missing results fails closed" -- otherwise a forgotten file
            # silently disables the control.
            #
            # They are only distinguishable if the declaration says which case it
            # is. An absent file that is DECLARED absent is the first; an absent
            # file that is not is the second, and still fails closed.
            if entry.get("resultsWithheldFromRepo"):
                UNENFORCEABLE.append(
                    f"{entry['id']}: results deliberately unpublished, so its "
                    f"withheld set cannot be computed here. Enforcement of this "
                    f"commission is LOCAL ONLY -- CI cannot protect it.")
                continue
            raise SystemExit(
                f"{entry['id']}: declared live but {entry['resultsFile']} is absent "
                f"and not declared withheld; cannot compute its withheld set"
            )
        bounds = set(entry.get("declaredBounds", []))
        values = {v for v in _integers(json.loads(results.read_text()))
                  if v not in bounds and abs(v) >= MIN_INTERESTING}
        unprotectable = {v for v in values if abs(v) < COLLISION_FLOOR}
        blocked[entry["id"]] = values - unprotectable
        if unprotectable:
            UNPROTECTABLE[entry["id"]] = sorted(unprotectable)
    return blocked


UNPROTECTABLE: dict[str, list[int]] = {}
UNENFORCEABLE: list[str] = []


def _spellings(value: int) -> list[str]:
    """Bare and comma-grouped. LEAK-101 screened only bare digits while the
    documents used commas, so the screen could not have failed."""
    return [str(value), f"{value:,}"]


def added_lines(base: str, head: str) -> list[tuple[str, int, str]]:
    command = ["git", "diff", "--unified=0", "--no-color", f"{base}...{head}", "--"]
    diff = subprocess.run(command, capture_output=True, text=True, check=True).stdout
    path, number, out = None, 0, []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            number = int(match.group(1)) if match else 0
        elif line.startswith("+") and not line.startswith("+++") and path:
            out.append((path, number, line[1:]))
            number += 1
    return out


def violations(lines, blocked: dict[str, set[int]]) -> list[str]:
    out: list[str] = []
    for path, number, text in lines:
        if path in SELF_EXEMPT:
            continue
        for commission, values in blocked.items():
            for value in sorted(values):
                if any(re.search(rf"(?<![\d,_]){re.escape(s)}(?![\d,_])", text)
                       for s in _spellings(value)):
                    out.append(
                        f"{path}:{number}: publishes a withheld outcome value of "
                        f"{commission}. Publishing it retires that commission's "
                        f"pass condition before it is answered; withhold it, or "
                        f"close the commission first."
                    )
                    break
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = pathlib.Path(args.root)
    blocked = withheld_sets(root)
    if not blocked:
        for msg in UNENFORCEABLE:
            print(f"  NOT ENFORCED HERE: {msg}")
        print("Withheld-leak check: nothing enforceable in this checkout.")
        return 0

    problems = violations(added_lines(args.base, args.head), blocked)
    if problems:
        print("Withheld-leak check failed. Only newly added lines were inspected:",
              file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    total = sum(len(v) for v in blocked.values())
    print(f"Withheld-leak check passed: {total} withheld value(s) across "
          f"{len(blocked)} live commission(s), none published.")
    for msg in UNENFORCEABLE:
        print(f"  NOT ENFORCED HERE: {msg}")
    for cid, vals in UNPROTECTABLE.items():
        print(f"  UNPROTECTED in {cid}: {vals} -- below the collision floor, so "
              f"enforcing them would flag ordinary code constants. They are NOT "
              f"covered by this check; the commission must tolerate their exposure "
              f"or the experiment must not depend on them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
