#!/usr/bin/env python3
"""Run KL-011 against the endpoints registered in preregistration-v0.2.json.

This program reports against the registration. It does not choose the endpoints,
the pass conditions or the invalidation clauses; it reads them from the frozen
document and evaluates them. Anything it decides for itself would be a result
chosen after seeing the data.

Usage:
    python3 run_kl011.py [--json results/RESULTS-v0.2.json]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))

from crossing import INJECTIONS, INJECTORS, ScopeSuppliedError, cross, direct  # noqa: E402

PREREG = json.loads((HERE / "preregistration-v0.2.json").read_text())
POPULATION = HERE / "fixtures/population"


def compare(endpoint_id: str, a: dict, b: dict) -> tuple[bool, str]:
    """Evaluate one registered endpoint on one (direct, crossed) pair."""
    if "__error__" in a or "__error__" in b:
        # Both arms must agree even about refusing. A transaction the evaluator
        # rejects must be rejected identically on both sides, or the transport
        # changed what the receiving system was willing to accept.
        same = a.get("__error__") == b.get("__error__")
        return same, ("both arms refused identically" if same else
                      f"refusal differs: {a.get('__error__')!r} vs {b.get('__error__')!r}")

    if endpoint_id == "E1":
        pa = (set(a["evidence"]["supportingRoots"]), set(a["evidence"]["opposingRoots"]))
        pb = (set(b["evidence"]["supportingRoots"]), set(b["evidence"]["opposingRoots"]))
        return pa == pb, f"{pa} vs {pb}"
    if endpoint_id == "E2":
        keys = ("declared", "searched", "unavailable", "complete")
        pa = {k: a["search"][k] for k in keys}
        pb = {k: b["search"][k] for k in keys}
        return pa == pb, f"{pa} vs {pb}"
    if endpoint_id == "E3":
        return a["uncertainty"] == b["uncertainty"], f"{a['uncertainty']} vs {b['uncertainty']}"
    if endpoint_id == "E4":
        return a["conclusion"] == b["conclusion"], f"{a['conclusion']} vs {b['conclusion']}"
    if endpoint_id == "E5":
        # No field may grant, imply or upgrade authority to execute. The receipt
        # schema is fixed, so this is checked as an absence over both arms.
        banned = {"authorized", "permitted", "mayExecute", "authority", "grant",
                  "approval", "token", "capability"}
        found = sorted(banned & (set(a) | set(b)))
        return not found, ("no authority-bearing field" if not found
                           else f"authority-bearing field(s): {found}")
    raise ValueError(f"unregistered endpoint {endpoint_id}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()

    transactions = sorted(POPULATION.glob("*.json"))
    endpoints = [e["id"] for e in PREREG["primaryEndpoints"]]

    rows: list[dict] = []
    void: list[str] = []
    for path in transactions:
        payload = json.loads(path.read_text())
        for injection in INJECTIONS:
            mutated = INJECTORS[injection](payload)
            try:
                a = direct(mutated)
            except ScopeSuppliedError as exc:      # invalidation clause I3
                void.append(f"{path.stem}/{injection}: {exc}")
                continue
            b = cross(mutated)
            for endpoint in endpoints:
                ok, detail = compare(endpoint, a, b)
                rows.append({"transaction": path.stem, "injection": injection,
                             "endpoint": endpoint, "preserved": ok, "detail": detail})

    # I2: every registered injection must have been applied.
    applied = {r["injection"] for r in rows}
    incomplete = sorted(set(INJECTIONS) - applied)

    per_endpoint = {}
    for endpoint in endpoints:
        failures = [r for r in rows if r["endpoint"] == endpoint and not r["preserved"]]
        per_endpoint[endpoint] = {
            "checked": sum(1 for r in rows if r["endpoint"] == endpoint),
            "failures": len(failures),
            "verdict": "PASS" if not failures else "FAIL",
            "firstCounterexample": failures[0] if failures else None,
        }

    passed = (not incomplete and not void
              and all(v["verdict"] == "PASS" for v in per_endpoint.values()))

    report = {
        "schema": "minority-prophet.kl011-result.v0.2",
        "protocolVersion": PREREG["protocolVersion"],
        "evaluator": PREREG["evaluator"]["path"],
        "transactions": len(transactions),
        "injections": list(INJECTIONS),
        "comparisons": len(rows),
        "perEndpoint": per_endpoint,
        "invalidations": {"I2_incompleteInjections": incomplete, "I3_suppliedScope": void},
        "verdict": "PASS" if passed else "FAIL",
        "claimAllowed": (PREREG["claimAllowedOnPass"] if passed
                         else PREREG["claimAllowedOnFail"]),
    }
    if args.json:
        out = pathlib.Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({**report, "rows": rows}, indent=2) + "\n")

    print(f"  {len(transactions)} transactions x {len(INJECTIONS)} injections "
          f"x {len(endpoints)} endpoints = {len(rows)} comparisons\n")
    for endpoint in endpoints:
        v = per_endpoint[endpoint]
        name = next(e["name"] for e in PREREG["primaryEndpoints"] if e["id"] == endpoint)
        print(f"  {endpoint}  {name:24s} {v['verdict']:4s}  "
              f"{v['checked'] - v['failures']}/{v['checked']} preserved")
        if v["firstCounterexample"]:
            c = v["firstCounterexample"]
            print(f"        counterexample: {c['transaction']} / {c['injection']}")
            print(f"        {c['detail'][:150]}")
    if incomplete:
        print(f"\n  I2 VIOLATED: injections never applied: {incomplete}")
    if void:
        print(f"\n  I3: {len(void)} void transaction(s)")
    print(f"\n  VERDICT: {report['verdict']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
