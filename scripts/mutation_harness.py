#!/usr/bin/env python3
"""Break the reference on purpose and require the invalidation clauses to fire.

BL-055. The pre-flight's T2 read the reference's own reported
`invalidationReasons`, so it detected a clause that was WRONG and not one that
was ABSENT. A registration whose clauses are too weak to catch anything passed.

A clause nothing can trigger is decorative. The only way to know a clause has
teeth is to break the thing it guards and watch it bite, so this injects a
defect per clause and reports which clauses fired.

Output is a mutation report consumed by `preflight_commission.py`:

    {"clauses": {"<clause id>": ["<mutation that fired it>", ...]}, ...}

A clause with an empty list is decorative and fails pre-flight.

Usage:
    python3 scripts/mutation_harness.py --experiment lin000 [--json OUT]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

LINEAGE = pathlib.Path("research/knowledge-ledger/lineage")

# The clauses v0.3 registers, as amended by v0.3.1.
CLAUSES = {
    "C1": "exhaustive count != 50,362",
    "C2": "either phase digest differs from the v0.2 published value",
    "C3": "any MUST-be-0 observed non-zero",
    "C4": "any MUST-be->0 observed zero",
    "C5": "uniform_below implemented with a float",
    "C6": "a modulus with rejection probability > 1/1000 consuming exactly 1000 words",
}


def _digest(worlds) -> str:
    import lineage_v2 as L2
    h = hashlib.sha256()
    for w in worlds:
        h.update((L2.canonical_world(w) + "\n").encode("ascii"))
    return h.hexdigest()


def mutations(pinned: dict) -> dict[str, list[str]]:
    """Run each mutation; return clause id -> mutations that fired it."""
    sys.path.insert(0, str(LINEAGE))
    import lineage_v2 as L2, lineage_v3 as L3

    fired: dict[str, list[str]] = {c: [] for c in CLAUSES}

    # M1 -- wrong exhaustive bound.
    if sum(1 for _ in L2.exhaustive_worlds(5)) != 50362:
        fired["C1"].append("M1 exhaustive bound k<=5 instead of k<=6")

    # M2 -- wrong seed. The stream must move.
    if _digest(L2.randomized_worlds(2000, L2.SEED + 1)) != \
       _digest(L2.randomized_worlds(2000, L2.SEED)):
        fired["C2"].append("M2 seed off by one")

    # M3 -- try to fire "MUST-be-0 observed non-zero" through each MUST-be-0 test
    # in turn. Which mutations can fire it, and which cannot, is itself the result.
    #
    # First attempt broke `verdict` to ignore S_a. It fired nothing: a rewiring
    # preserves k and sides, so a length-based verdict moves both worlds
    # identically. Kept as a recorded non-firing mutation rather than deleted --
    # a mutation that fails to fire is evidence about the clause, not a bug.
    real_verdict, real_s_sets = L3.verdict, L3.s_sets
    try:
        L3.verdict = lambda w: "1" if len(w) % 2 else "0"
        c = dict(t1PosChecked=0, t1PosViolations=0, t1NecChecked=0,
                 t1NecVerdictChanges=0, t1IdChecked=0, t1IdViolations=0)
        for w in L2.exhaustive_worlds(4):
            L3.t1_readings(w, c)
        if c["t1PosViolations"] > 0:
            fired["C3"].append("M3a verdict ignores S_a -- T1-POS non-zero")
    finally:
        L3.verdict = real_verdict

    # M3b -- break S_a itself. This is the only route that works, and why matters:
    # T1-POS and T1-ID cannot fail while S_a is correct, so the clause is reachable
    # only through L1-POS. The harness rediscovers the BL-053 implementer's finding
    # mechanically -- T1-POS carries no independent evidential load.
    try:
        L3.s_sets = lambda w: (frozenset({0}), frozenset({0}))   # constant, wrong
        broken = sum(1 for w in L2.exhaustive_worlds(5)
                     if L2.is_side_consistent(w) and not L3.l1_status(w)[1])
        if broken > 0:
            fired["C3"].append(f"M3b S_a constant -- L1-POS non-zero on {broken} worlds "
                               f"(ONLY route: T1-POS/T1-ID cannot fail while S_a is correct)")
    finally:
        L3.s_sets = real_s_sets

    # M4 -- restrict to side-consistent worlds only; L1-NEG must collapse to zero.
    neg = sum(1 for w in L2.exhaustive_worlds(6)
              if L2.is_side_consistent(w) and not L3.l1_status(w)[1])
    if neg == 0:
        fired["C4"].append("M4 side-consistent worlds only -- L1-NEG witnesses hit zero")

    # M5 -- float sampler. Registered as its own clause; observable only through
    # the stream it produces, which is the finding, not a bug in the harness.
    class FloatWords(L2.Words):
        def uniform_below(self, n):                      # int(random()*n), no rejection
            return int((self.next_word() / (1 << 32)) * n)
    fw, rw = FloatWords(L2.SEED), L2.Words(L2.SEED)
    if [fw.uniform_below(20) for _ in range(200)] != [rw.uniform_below(20) for _ in range(200)]:
        fired["C5"].append("M5 float sampler -- stream diverges (via C2/C6, not independently)")

    # M6 -- drop the rejection rule; word counts collapse to exactly 1,000.
    class NoReject(L2.Words):
        def uniform_below(self, n):
            return self.next_word() % n
    for row in L3.conformance_vector():
        if row["rejectionRegion"] <= (1 << 32) / 1000:
            continue
        w = NoReject(L2.SEED)
        for _ in range(1000):
            w.uniform_below(row["modulus"])
        if w.consumed == 1000:
            fired["C6"].append(f"M6 no rejection at n={row['modulus']} -- 1,000 words exactly")
            break
    return fired


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", default="lin000")
    ap.add_argument("--json")
    args = ap.parse_args()
    if args.experiment != "lin000":
        print(f"no mutation set for {args.experiment!r}", file=sys.stderr)
        return 2

    pinned = json.loads((LINEAGE / "results/lin000-v2-result.json").read_text())
    fired = mutations(pinned)
    report = {"experiment": "lin000", "clauses": fired,
              "clauseText": CLAUSES,
              "decorative": [c for c, m in fired.items() if not m]}
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(report, indent=2) + "\n")

    for cid, text in CLAUSES.items():
        hits = fired[cid]
        mark = "FIRED" if hits else "DECORATIVE"
        print(f"  [{mark:10s}] {cid}  {text}")
        for h in hits:
            print(f"                 <- {h}")
    print()
    if report["decorative"]:
        print(f"DECORATIVE CLAUSES: {report['decorative']} -- nothing triggers them.",
              file=sys.stderr)
        return 1
    print("Every registered invalidation clause is triggerable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
