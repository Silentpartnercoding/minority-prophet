#!/usr/bin/env python3
"""Run the traps against a commission package before it ships.

Every defect this checks for was committed, by the author of this file, in a
registration that had already been reviewed. Review did not catch any of them.
Running the registration against itself caught all of them, afterwards. This
moves that step before the shipping instead of after.

    T1 CLOSURE      a document referenced by name must be in the package
    T2 SELF-VALID   the reference run must satisfy the registration's own
                    invalidation conditions
    T3 ARITHMETIC   every number asserted in the prose must be reproducible
    T4 VACUITY      a MUST-be-0 test claimed as paper evidence must be able
                    to fail
    T5 REACHABILITY a figure cited as validation must be reachable from the
                    registration's own definitions
    T6 LEAKAGE      no live commission's withheld values in the package

T2 requires a mutation report from scripts/mutation_harness.py (BL-055): every
registered invalidation clause must be shown to fire under a deliberate defect,
or it is decorative. Without the report T2 fails, because a trap that is optional
is a trap that will be omitted on the day it matters.

Usage:
    python3 scripts/preflight_commission.py --package DIR --results FILE \
        [--registration FILE ...] [--claims-json FILE]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


class Trap:
    def __init__(self, tid: str, name: str) -> None:
        self.id, self.name, self.failures, self.notes = tid, name, [], []

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)


# --- T1 -----------------------------------------------------------------------

REFERENCE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|json|py|txt))`")


def trap_closure(package: pathlib.Path, registrations: list[pathlib.Path]) -> Trap:
    """A registration that says "carried unchanged from X" must ship X.

    LIN-000 v0.3 carried v0.2's draw schedule and canonical form by reference and
    shipped neither. The commissioned regression could not be attempted: the
    package pinned the digests without the notation that produces them. The
    implementer's phrase was "it ships the answer key without the question".
    """
    t = Trap("T1", "closure — referenced documents are in the package")
    present = {p.name for p in package.rglob("*") if p.is_file()}
    for reg in registrations:
        text = reg.read_text()
        declared_absent = set(re.findall(r"NOT SHIPPED: *`?([A-Za-z0-9_./-]+)`?", text))
        for ref in sorted(set(REFERENCE.findall(text))):
            name = pathlib.PurePath(ref).name
            if name in present or name in declared_absent or name == reg.name:
                continue
            # Only flag references the text leans on normatively.
            for line in text.splitlines():
                if ref in line and re.search(
                        r"unchanged|carried|per |as (?:defined|specified|registered)|see ",
                        line, re.I):
                    t.fail(f"{reg.name} relies on `{ref}`, which is not in the package "
                           f"and is not declared NOT SHIPPED")
                    break
    return t


# --- T2 -----------------------------------------------------------------------

def trap_self_valid(results: dict, mutation_report: dict | None = None) -> Trap:
    """The reference run must pass the registration's own invalidation clauses.

    v0.3's clause invalidated a run for observing zero rejections at a modulus
    whose rejection probability is 3.7e-9 -- the correct outcome. It fired on the
    reference's own run. A MUST clause red on correct behaviour is the BL-049
    defect in registration form.
    """
    t = Trap("T2", "self-validity — the reference satisfies its own invalidation clauses")
    reasons = results.get("invalidationReasons", [])
    if reasons:
        for r in reasons:
            t.fail(f"the reference run is invalid under its own registration: {r}")
    if results.get("valid") is False and not reasons:
        t.fail("results declare valid=false with no reason given")

    # BL-055. Reading the reference's own reasons detects a clause that is WRONG,
    # never one that is ABSENT: a registration whose clauses catch nothing passed
    # this trap. The mutation report closes that -- every clause must be shown to
    # fire under a deliberate defect, or it is decorative.
    if mutation_report is None:
        t.fail("no mutation report supplied; clause STRENGTH is unverified and a "
               "registration with decorative clauses would pass (BL-055)")
        return t
    for cid, fired in mutation_report.get("clauses", {}).items():
        if not fired:
            text = mutation_report.get("clauseText", {}).get(cid, "")
            t.fail(f"invalidation clause {cid} is decorative: no mutation triggers it "
                   f"-- {text}")
    return t


# --- T3 -----------------------------------------------------------------------

NUMBER = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d{4,})(?![\w.])")


def trap_arithmetic(registrations: list[pathlib.Path], results: dict,
                    allow: set[int]) -> Trap:
    """Every number asserted in a registration is a normative statement.

    v0.3 stated two rejection regions wrong: 1,717,986,164 for 1,717,986,918 and
    1,431,655,763 for 858,993,458. Both were arithmetic, both in prose, neither
    caught by reading.
    """
    t = Trap("T3", "arithmetic — asserted numbers are reproducible")
    produced = set()

    def collect(o):
        if isinstance(o, dict):
            for v in o.values(): collect(v)
        elif isinstance(o, list):
            for v in o: collect(v)
        elif isinstance(o, int) and not isinstance(o, bool):
            produced.add(o)
    collect(results)

    for reg in registrations:
        for n, line in ((int(m.group(1).replace(",", "")), line)
                        for line in reg.read_text().splitlines()
                        for m in NUMBER.finditer(line)):
            if n < 1000 or n in allow or n in produced:
                continue
            t.note(f"{reg.name}: {n:,} is asserted but appears in no computed result "
                   f"-- verify by hand: {line.strip()[:90]}")
    return t


# --- T4 / T5 -------------------------------------------------------------------

def trap_vacuity(claims: dict | None) -> Trap:
    """A MUST-be-0 test offered as evidence for a paper claim must be able to fail.

    v0.2's T1-positive could not fail by construction. v0.3's replacement could
    not fail either -- it is a corollary of L1-POS, so it cannot go red while
    L1-POS is green. Both were listed as evidence for Theorem 1.
    """
    t = Trap("T4", "vacuity — MUST-be-0 tests cited as paper evidence can fail")
    if claims is None:
        t.note("no claims file supplied; vacuity not checked")
        return t
    for test in claims.get("tests", []):
        if test.get("mustBe") != 0 or not test.get("citesPaperClaim"):
            continue
        # A self-declared label is not evidence. v0.3 would have passed this trap
        # by relabelling one string, so the label is ignored entirely: what is
        # required is a WITNESS -- a concrete input under which the test fails.
        witness = test.get("witness")
        if not witness:
            t.fail(f"{test['id']} is cited as evidence for {test['citesPaperClaim']} "
                   f"but supplies no witness: no input is offered under which it "
                   f"fails. Supply one, or stop citing it as evidence.")
        elif not (witness.get("input") and witness.get("observedOutcome")):
            t.fail(f"{test['id']}'s witness names no input and outcome; a witness "
                   f"that cannot be replayed is a label")
        if test.get("impliedBy"):
            t.fail(f"{test['id']} is implied by {test['impliedBy']} and therefore "
                   f"carries no independent evidential load for "
                   f"{test['citesPaperClaim']}")
    # Silence is not compliance: a paper claim with no test behind it is a gap.
    cited = {x.get("citesPaperClaim") for x in claims.get("tests", [])}
    for claim in claims.get("paperClaimsAsserted", []):
        if claim not in cited:
            t.fail(f"{claim} is asserted as tested but no test cites it")
    return t


def trap_reachability(claims: dict | None, results: dict) -> Trap:
    """A figure cited as validation must be reachable from the registration's
    own definitions.

    v0.3 cited 121,944 as blind confirmation of its reading of Theorem 1. Its own
    definition of a rewiring excludes the identity and yields 116,032. The
    evidence for the reading was unreachable from the reading.
    """
    t = Trap("T5", "reachability — cited validation figures follow from the definitions")
    if claims is None:
        t.note("no claims file supplied; reachability not checked")
        return t
    produced = set()

    def collect(o):
        if isinstance(o, dict):
            for v in o.values(): collect(v)
        elif isinstance(o, list):
            for v in o: collect(v)
        elif isinstance(o, int) and not isinstance(o, bool):
            produced.add(o)
    collect(results)
    # Auto-extract: v0.3 would have passed by citing nothing, so the list is
    # harvested from the registration prose rather than supplied.
    for reg in claims.get("_registrationTexts", []):
        for line in reg.splitlines():
            if not re.search(r"matches|confirm|validat|evidence that|agreement", line, re.I):
                continue
            for m in NUMBER.finditer(line):
                v = int(m.group(1).replace(",", ""))
                if v >= 1000 and v not in produced:
                    t.fail(f"{v:,} is used as validation in the registration prose but "
                           f"the reference produces no such figure: {line.strip()[:80]}")
    for cite in claims.get("citedFigures", []):
        if cite["value"] not in produced:
            t.fail(f"{cite['value']:,} is cited as {cite.get('as','validation')} but the "
                   f"reference produces no such figure -- it is not reachable from the "
                   f"registration's own definitions")
    return t


# --- T6 -----------------------------------------------------------------------

def trap_leakage(package: pathlib.Path, repo: pathlib.Path) -> Trap:
    t = Trap("T6", "leakage — no live commission's withheld values in the package")
    sys.path.insert(0, str(repo / "scripts"))
    try:
        from check_withheld_leak import withheld_sets, _spellings
    except Exception as exc:                                    # pragma: no cover
        t.note(f"withheld-leak checker unavailable: {exc}")
        return t
    blocked = withheld_sets(repo)
    for f in sorted(p for p in package.rglob("*") if p.is_file()):
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        for cid, values in blocked.items():
            for v in sorted(values):
                if any(re.search(rf"(?<![\d,_]){re.escape(s)}(?![\d,_])", text)
                       for s in _spellings(v)):
                    t.fail(f"{f.name} carries {v:,}, a withheld value of {cid}")
                    break
    return t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--registration", action="append", default=[])
    ap.add_argument("--claims-json")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--allow", default="", help="comma-separated numbers exempt from T3")
    ap.add_argument("--mutation-report", help="output of scripts/mutation_harness.py")
    args = ap.parse_args()

    package = pathlib.Path(args.package)
    repo = pathlib.Path(args.repo)
    results = json.loads(pathlib.Path(args.results).read_text())
    regs = [pathlib.Path(r) for r in args.registration]
    claims = json.loads(pathlib.Path(args.claims_json).read_text()) if args.claims_json else None
    # The registration prose is injected here, not taken from the claims file.
    # T5 was gameable by supplying an empty citation list; the caller no longer
    # chooses what gets audited.
    if claims is not None:
        claims["_registrationTexts"] = [r.read_text() for r in regs]
    allow = {int(x) for x in args.allow.split(",") if x.strip()}

    mutation = (json.loads(pathlib.Path(args.mutation_report).read_text())
                if args.mutation_report else None)
    traps = [trap_closure(package, regs), trap_self_valid(results, mutation),
             trap_arithmetic(regs, results, allow), trap_vacuity(claims),
             trap_reachability(claims, results), trap_leakage(package, repo)]

    failed = 0
    for t in traps:
        mark = "FAIL" if t.failures else "pass"
        print(f"[{mark}] {t.id} {t.name}")
        for f in t.failures:
            print(f"        ! {f}")
            failed += 1
        for n in t.notes:
            print(f"        - {n}")
    print()
    if failed:
        print(f"PRE-FLIGHT FAILED: {failed} problem(s). Do not ship this package.",
              file=sys.stderr)
        return 1
    print("Pre-flight passed. Notes above are advisory and still worth reading.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
