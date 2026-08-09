#!/usr/bin/env python3
"""Measure the blind-spot rate: how much can break without any test noticing.

BL-056. Every other control in this programme checks for a defect someone named
first. `mutation_harness.py` is clause-directed -- it asks "can clause C fire?".
This asks the question that has no list behind it:

    If the reference were wrong in a way nobody anticipated,
    would the registered battery notice?

Mutants are applied to the semantics, not to the clauses, and the battery is run
unchanged. A mutant that no registered test detects is a **survivor**, and a
survivor is a blind spot -- a way the reference could be wrong in production with
every test green. The survival rate is the number this exists to report.

This cannot enumerate unknown unknowns. It can measure how many there are, which
is the difference between a hope and an estimate.

Usage:
    python3 scripts/mutation_coverage.py [--json OUT] [--max-claims 4]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

LINEAGE = pathlib.Path("research/knowledge-ledger/lineage")


def battery(L2, L3, max_claims: int) -> dict:
    """Every registered check, run over a small exhaustive phase.

    Deliberately the registered battery and nothing else: adding a check here
    that the registration does not require would flatter the result.
    """
    worlds = list(L2.exhaustive_worlds(max_claims))
    digest = hashlib.sha256()
    for w in worlds:
        digest.update((L2.canonical_world(w) + "\n").encode("ascii"))

    counters = dict(t1PosChecked=0, t1PosViolations=0, t1NecChecked=0,
                    t1NecVerdictChanges=0, t1IdChecked=0, t1IdViolations=0)
    for w in worlds:
        L3.t1_readings(w, counters)

    l1_pos_viol = l1_neg_hits = shallow = count_abl = 0
    for w in worlds:
        consistent, matches = L3.l1_status(w)
        if consistent and not matches:
            l1_pos_viol += 1
        if not consistent and not matches:
            l1_neg_hits += 1
        shallow += L3.ablation_shallow_catches(w)
        count_abl += L3.ablation_claimcount_catches(w)

    return {
        "worlds": len(worlds),
        "streamDigest": digest.hexdigest(),
        "t1PosViolations": counters["t1PosViolations"],
        "t1IdViolations": counters["t1IdViolations"],
        "t1NecVerdictChanges": counters["t1NecVerdictChanges"],
        "l1PosViolations": l1_pos_viol,
        "l1NegHits": l1_neg_hits,
        "ablShallowCaught": shallow,
        "ablCountCaught": count_abl,
        "conformance": [r["digest"] for r in L3.conformance_vector()],
        # Behavioural fingerprint, deliberately NOT part of the registered
        # battery. It exists only to tell a blind spot from an equivalent
        # mutant: a mutant that evades the battery AND changes no behaviour has
        # not found a gap, it changed nothing.
        "_behaviour": hashlib.sha256("|".join(
            f"{sorted(L3.s_sets(w)[0])}{sorted(L3.s_sets(w)[1])}"
            f"{L3.verdict(w)}{L3.is_side_consistent(w)}"
            f"{[L3.root_of(w, i) for i in range(len(w))]}"
            for w in worlds).encode()).hexdigest(),
    }


def mutants(L2, L3):
    """Perturbations of the semantics, not of the clauses.

    Chosen to be the kind of thing a competent implementer gets wrong -- an
    off-by-one, a swapped side, a shallow walk, a comparison flipped -- rather
    than defects this programme has already recorded.
    """
    real = {"root_of": L3.root_of, "s_sets": L3.s_sets, "verdict": L3.verdict,
            "is_side_consistent": L3.is_side_consistent,
            "root_set": L3.root_set, "l1_status": L3.l1_status,
            "v2_s_sets": L2.s_sets, "v2_verdict": L2.verdict,
            "v2_is_side_consistent": L2.is_side_consistent}

    def restore():
        L3.root_of, L3.s_sets, L3.verdict = real["root_of"], real["s_sets"], real["verdict"]
        L3.is_side_consistent, L3.root_set = real["is_side_consistent"], real["root_set"]
        L3.l1_status = real["l1_status"]
        L2.s_sets, L2.verdict = real["v2_s_sets"], real["v2_verdict"]
        L2.is_side_consistent = real["v2_is_side_consistent"]

    def shallow_root(world, index):
        p = world[index]["parentIndex"]
        return index if p is None else p

    def set_all(name, fn):
        setattr(L3, name, fn)
        if hasattr(L2, name):
            setattr(L2, name, fn)

    yield "M-root-shallow: root() walks one edge, not the chain", \
        lambda: set_all("root_of", shallow_root)
    yield "M-root-identity: root() returns the claim itself", \
        lambda: set_all("root_of", lambda w, i: i)
    yield "M-sides-swapped: S_0 and S_1 exchanged", \
        lambda: set_all("s_sets", lambda w: tuple(reversed(real["s_sets"](w))))
    yield "M-verdict-strict: ties resolve to 1 instead of abstain", \
        lambda: set_all("verdict", lambda w: "1" if len(real["s_sets"](w)[1]) >=
                        len(real["s_sets"](w)[0]) else "0")
    yield "M-verdict-inverted: comparison flipped (minority wins)", \
        lambda: set_all("verdict", lambda w: {"1": "0", "0": "1"}.get(
            real["verdict"](w), "abstain"))
    yield "M-consistency-vs-root: edge compared to root's side, not parent's", \
        lambda: set_all("is_side_consistent", lambda w: all(
            c["parentIndex"] is None or
            w[real["root_of"](w, i)]["side"] == c["side"]
            for i, c in enumerate(w)))
    yield "M-consistency-always: every world declared side-consistent", \
        lambda: set_all("is_side_consistent", lambda w: True)
    yield "M-rootset-count: root set replaced by its cardinality class", \
        lambda: setattr(L3, "root_set", lambda w: frozenset(
            range(sum(1 for c in w if c["parentIndex"] is None))))
    yield "M-l1-lenient: L1 compares cardinalities, not sets", \
        lambda: setattr(L3, "l1_status", lambda w: (
            real["is_side_consistent"](w),
            len(real["s_sets"](w)[0]) == len(
                [i for i, c in enumerate(w)
                 if c["parentIndex"] is None and c["side"] == 0])))
    yield "M-selfroot: a root's own side ignored when building S_a", \
        lambda: set_all("s_sets", lambda w: (
            frozenset(real["root_of"](w, i) for i, c in enumerate(w)
                      if c["side"] == 0 and c["parentIndex"] is not None),
            frozenset(real["root_of"](w, i) for i, c in enumerate(w)
                      if c["side"] == 1 and c["parentIndex"] is not None)))
    return restore


MUTANT_IDS = [
    "root-shallow", "root-identity", "sides-swapped", "verdict-strict",
    "verdict-inverted", "consistency-vs-root", "consistency-always",
    "rootset-count", "l1-lenient", "selfroot",
]


def _child(mutant: str, max_claims: int) -> dict:
    """Run one mutant in this process. Called only in a fresh subprocess, so no
    mutation can leak into the next: the first version patched modules in-process
    and every mutant after the first ran on the previous one's wreckage, which
    made a 0% survival rate an artifact rather than a measurement."""
    sys.path.insert(0, str(LINEAGE))
    import lineage_v2 as L2, lineage_v3 as L3
    if mutant != "BASELINE":
        gen = mutants(L2, L3)
        for name, apply_mutation in gen:
            if name.split(":")[0] == f"M-{mutant}":
                apply_mutation()
                break
        else:
            raise SystemExit(f"unknown mutant {mutant}")
    return battery(L2, L3, max_claims)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--max-claims", type=int, default=4)
    ap.add_argument("--run-mutant", help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.run_mutant:
        print(json.dumps(_child(args.run_mutant, args.max_claims)))
        return 0

    import subprocess
    def run(m):
        out = subprocess.run([sys.executable, __file__, "--run-mutant", m,
                              "--max-claims", str(args.max_claims)],
                             capture_output=True, text=True)
        if out.returncode != 0:
            return {"_error": out.stderr.strip()[:120]}
        return json.loads(out.stdout)

    baseline = run("BASELINE")
    results = []
    for m in MUTANT_IDS:
        observed = run(m)
        if "_error" in observed:
            differing = [f"raised: {observed['_error'][:60]}"]
        else:
            differing = sorted(k for k in baseline
                               if k != "_behaviour" and baseline[k] != observed.get(k))
        # EQUIVALENT-MUTANT CHECK. A "survivor" whose observable behaviour is
        # identical to the reference has not evaded the tests -- it changed
        # nothing. Reporting it as a blind spot inflates the rate and sends
        # someone to decide a question that does not exist, which is exactly what
        # happened with the parent-vs-root side-consistency mutant: provably the
        # same predicate, 0 disagreements in 50,362 worlds, reported as a finding.
        # Computed, not asserted: identical observable behaviour on every world.
        equivalent = (not differing and "_error" not in observed
                      and observed.get("_behaviour") == baseline.get("_behaviour"))
        results.append({"mutant": m, "detectedBy": differing,
                        "survived": bool(not differing and not equivalent),
                        "equivalentMutant": bool(equivalent),
                        "note": ("behaviourally identical to the reference: not a blind "
                                 "spot, an equivalent mutant") if equivalent else None})

    survivors = [r for r in results if r["survived"]]
    equivalents = [r for r in results if r.get("equivalentMutant")]
    report = {"maxClaims": args.max_claims, "mutants": len(results),
              "survivors": len(survivors), "equivalentMutants": len(equivalents),
              "survivalRate": round(len(survivors) / max(len(results) - len(equivalents), 1), 3),
              "survivalRateNote": ("equivalent mutants are excluded from the denominator: "
                                   "they change no behaviour, so evading detection is not "
                                   "evidence of a gap"),
              "isolation": "one subprocess per mutant",
              "detail": results}
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(report, indent=2) + "\n")

    for r in results:
        mark = ("EQUIV" if r.get("equivalentMutant")
                else "SURVIVED" if r["survived"] else "caught")
        print(f"  [{mark:8s}] {r['mutant']}")
        if not r["survived"]:
            print(f"             by: {', '.join(r['detectedBy'][:4])}")
    print()
    print(f"  mutants {len(results)}   survivors {len(survivors)}   "
          f"survival rate {report['survivalRate']:.1%}")
    if survivors:
        print("\n  SURVIVORS ARE BLIND SPOTS -- ways the reference could be wrong "
              "with every registered test green:", file=sys.stderr)
        for s in survivors:
            print(f"    - {s['mutant']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
