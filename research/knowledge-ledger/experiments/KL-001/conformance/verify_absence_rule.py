#!/usr/bin/env python3
"""KL-001 v0.4 — enumerate the absence rule instead of sampling it.

The dual ledger's verdict for an absence claim is a total function of two bits:

    opposing evidence present?      coverage complete?      verdict
    ------------------------------------------------------------------
    yes                             yes                     present
    yes                             no                      present
    no                              yes                     absent_within_declared_scope
    no                              no                      not_established

That is visible in `knowledge_ledger/transaction.py`: three branches, two inputs,
no fallthrough and nothing else consulted. So the claim "the ledger refuses to
call incomplete coverage an absence" does not need a corpus, a sample size, or a
confidence interval. It needs the table enumerated -- all four cells, which is
what this does.

WHY THIS REPLACES THE v0.3 MEASUREMENT RATHER THAN SUPPLEMENTING IT.

v0.3 reported a false-clean rate and a clean-refusal rate over a synthetic corpus.
Because the verdict is deterministic in those two bits, both rates are fixed by
corpus composition:

    cleanRefusalRate = |clean repos with an unreadable file| / |clean repos|
    rescues          = |defective repos, no findings, unreadable file|

Every term is a generator setting. The rates were not measured; they were chosen,
then read back. Enlarging the corpus tightens a confidence interval around an
authored number, which is worse than an underpowered estimate because it looks
like evidence. Those endpoints are retired for synthetic populations. What they
ask -- how often each cell occurs -- is a fact about real repositories.

THE ENUMERATION IS MUTATION-TESTED. A table walked by a rule that ignores one of
its inputs still produces four rows; three of them are even correct. So each cell
must be shown load-bearing: a rule that drops the coverage bit has to break a
specific cell, and if it does not, that cell was carrying no weight.

Usage:
    python3 verify_absence_rule.py [--json OUT]
"""

from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))

from knowledge_ledger import evaluate_transaction  # noqa: E402

EXPECTED = {
    (True, True): "present",
    (True, False): "present",
    (False, True): "absent_within_declared_scope",
    (False, False): "not_established",
}


def transaction(has_opposing: bool, coverage_complete: bool) -> dict:
    """The smallest absence transaction exhibiting one cell of the table."""
    return {
        "schema": "minority-prophet.knowledge-transaction.v0.1",
        "transactionId": f"conf-{int(has_opposing)}{int(coverage_complete)}",
        "claim": {"type": "absence",
                  "statement": "no defect of the declared classes is present"},
        "searchLedger": {"locations": [
            {"id": "loc-1", "status": "searched"},
            {"id": "loc-2", "status": "searched" if coverage_complete else "skipped"},
        ]},
        "evidenceLedger": {"records": (
            [{"recordId": "r1", "rootId": "root-a", "side": "oppose"}]
            if has_opposing else []
        )},
    }


def enumerate_table() -> list[dict]:
    rows = []
    for has_opposing, complete in itertools.product((True, False), repeat=2):
        verdict = evaluate_transaction(transaction(has_opposing, complete))["conclusion"]
        rows.append({"hasOpposing": has_opposing, "coverageComplete": complete,
                     "verdict": verdict,
                     "expected": EXPECTED[(has_opposing, complete)],
                     "match": verdict == EXPECTED[(has_opposing, complete)]})
    return rows


def cells_load_bearing() -> list[dict]:
    """Which cells does an input actually decide?

    For each input bit, hold the other fixed and flip it. A cell whose verdict is
    unchanged by a bit is a cell that bit does not decide. If no cell responds to
    the coverage bit, the rule ignores coverage and the whole experiment is
    measuring nothing -- which is precisely the failure mode this file exists to
    make impossible to miss.
    """
    findings = []
    for bit, name in ((0, "hasOpposing"), (1, "coverageComplete")):
        decided = []
        for other in (True, False):
            args_a = [other, other]; args_b = [other, other]
            args_a[bit], args_b[bit] = True, False
            va = evaluate_transaction(transaction(*args_a))["conclusion"]
            vb = evaluate_transaction(transaction(*args_b))["conclusion"]
            if va != vb:
                decided.append({"otherInput": other, "whenTrue": va, "whenFalse": vb})
        findings.append({"input": name, "decidesCells": len(decided),
                         "detail": decided})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()

    rows = enumerate_table()
    load = cells_load_bearing()
    complete = len(rows) == 4
    all_match = all(r["match"] for r in rows)
    every_input_decides = all(f["decidesCells"] > 0 for f in load)

    report = {
        "schema": "minority-prophet.kl001-conformance.v0.1",
        "claim": ("the absence verdict is a total function of (opposing evidence "
                  "present, coverage complete)"),
        "method": ("exhaustive enumeration of the input space, not sampling; "
                   "4 of 4 cells, no corpus involved"),
        "table": rows,
        "inputSensitivity": load,
        "tableComplete": complete,
        "allCellsMatch": all_match,
        "everyInputDecidesAtLeastOneCell": every_input_decides,
        "pass": complete and all_match and every_input_decides,
        "retiredEndpoints": {
            "falseCleanRate": ("fixed by corpus composition on a synthetic "
                               "population; uninterpretable as evidence"),
            "cleanRefusalRate": ("likewise; carried forward as a registered 15% "
                                 "ceiling for the first real-repository run"),
        },
    }
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(report, indent=2) + "\n")

    for r in rows:
        mark = "ok " if r["match"] else "BAD"
        print(f"  {mark} opposing={str(r['hasOpposing']):5s} "
              f"complete={str(r['coverageComplete']):5s} -> {r['verdict']}")
    print()
    for f in load:
        print(f"  {f['input']:18s} decides {f['decidesCells']} of 2 cell pairs")
    print(f"\n  PASS: {report['pass']}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
