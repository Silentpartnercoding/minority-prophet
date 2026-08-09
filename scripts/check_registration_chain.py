#!/usr/bin/env python3
"""Verify that every preregistration still matches the commit its sidecar pins.

WHAT THIS DOES NOT DO, and why (BL-049 / FINDING-CHAIN-101.md).

The obvious check is "does `git log -1 -- preregistration.json` equal the pinned
SHA?". That is a proxy for the property anyone actually needs, and it is wrong in
both directions:

  * It reports RED on an intact repository whenever history is merged from a line
    that duplicates a registration commit. This repository's main branch contains
    two byte-identical copies of its registration history -- introduced by its own
    delivery of the research work, not by tampering -- so the proxy has been red
    since, on registrations that verify perfectly.
  * It would report GREEN on a genuine tampering that preserved commit identity
    while altering content, because it never compares bytes at all.

The property that matters is:

  1. the pinned commit exists;
  2. it is an ancestor of the branch being published;
  3. the preregistration at HEAD is byte-identical to the preregistration at that
     pinned commit.

That survives merges, duplicated history and rebases, and it is exactly what a
reader must confirm to trust that a protocol was frozen before its results.

Usage:
    python3 scripts/check_registration_chain.py [--ref HEAD]
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

EXPERIMENTS = pathlib.Path("research/knowledge-ledger/experiments")
UNMATCHED: list[str] = []
# Two components or three: v0.3 and v1.3.0 are both real version strings in this
# programme, and the three-component form silently skipped PROTOCOL-COMMIT-v0.3.txt
# -- leaving KL-001's newest registration unpinned as far as this check was
# concerned. A sidecar that does not match is now reported, not ignored: a control
# that quietly stops covering something is the defect it exists to prevent.
SIDECAR = re.compile(r"^PROTOCOL-COMMIT(?:-(v\d+(?:\.\d+){1,2}))?\.txt$")
UNMATCHED_SIDECAR = re.compile(r"^PROTOCOL-COMMIT.*\.txt$")


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(("git",) + args, capture_output=True, text=True)


def pairs(root: pathlib.Path) -> list[tuple[pathlib.Path, pathlib.Path]]:
    """(sidecar, preregistration) for every registration binding in the tree."""
    found = []
    base = root / EXPERIMENTS
    if not base.is_dir():
        return found
    for directory in sorted(p for p in base.iterdir() if p.is_dir()):
        for entry in sorted(directory.iterdir()):
            match = SIDECAR.match(entry.name)
            if not match:
                if UNMATCHED_SIDECAR.match(entry.name):
                    UNMATCHED.append(f"{directory.name}/{entry.name}")
                continue
            version = match.group(1)
            prereg = directory / (f"preregistration-{version}.json" if version
                                  else "preregistration.json")
            found.append((entry, prereg))
    return found


def check(root: pathlib.Path, ref: str) -> list[str]:
    problems: list[str] = []
    for sidecar, prereg in pairs(root):
        label = f"{prereg.parent.name}/{prereg.name}"
        pinned = sidecar.read_text().strip().split()[0] if sidecar.read_text().strip() else ""
        if not re.fullmatch(r"[0-9a-f]{7,40}", pinned):
            problems.append(f"{label}: sidecar {sidecar.name} holds no commit id")
            continue
        if _git("cat-file", "-e", f"{pinned}^{{commit}}").returncode != 0:
            problems.append(f"{label}: pinned commit {pinned[:9]} does not exist")
            continue
        if _git("merge-base", "--is-ancestor", pinned, ref).returncode != 0:
            problems.append(
                f"{label}: pinned commit {pinned[:9]} is not an ancestor of {ref}; "
                "the registration is not on the branch it claims to bind")
            continue
        rel = prereg.relative_to(root).as_posix()
        at_pin = _git("rev-parse", f"{pinned}:{rel}")
        at_ref = _git("rev-parse", f"{ref}:{rel}")
        if at_pin.returncode != 0:
            problems.append(f"{label}: absent at its own pinned commit {pinned[:9]}")
        elif at_ref.returncode != 0:
            problems.append(f"{label}: present at the pin but absent at {ref}")
        elif at_pin.stdout.strip() != at_ref.stdout.strip():
            problems.append(
                f"{label}: CONTENT CHANGED since registration. "
                f"blob at pin {at_pin.stdout.strip()[:9]}, "
                f"at {ref} {at_ref.stdout.strip()[:9]}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", default="HEAD", help="branch or commit to verify")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = pathlib.Path(args.root)
    bindings = pairs(root)
    if not bindings:
        print("Registration chain: no PROTOCOL-COMMIT sidecars found.")
        return 0

    problems = check(root, args.ref)
    for name in UNMATCHED:
        problems.append(f"{name}: looks like a sidecar but does not match the naming "
                        f"pattern, so nothing it pins is being verified")
    if problems:
        print("Registration chain check FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"Registration chain verified: {len(bindings)} binding(s); every "
          f"preregistration is byte-identical to its pinned commit and every pin "
          f"is an ancestor of {args.ref}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
