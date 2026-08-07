#!/usr/bin/env python3
"""KL-000 confirmatory runner.

Executes the preregistered phases in order and writes one result document. It
computes the preregistered statistics and nothing else: no alternative endpoint
is calculated in the primary result.

    python3 src/run_kl000.py --phase all --out results/

Exit status is 0 when the run completes, whatever the scientific outcome. A
rejected invariant is a result, not a crash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
REPO = EXPERIMENT.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from knowledge_ledger import evaluate_transaction  # noqa: E402

import kl000_worlds as worlds  # noqa: E402
from kl000_baselines import BASELINES  # noqa: E402
from kl000_invariants import check_world  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_fixture_phase(prereg: dict) -> dict:
    """Registered control fixtures against their hand-derived expected values.

    The fixture set is the preregistration's `controls` array, so each protocol
    version runs exactly the controls it registered: v1.0.0 registered C01-C10
    (`fixtures/*.json`), v1.1.0 additionally registered C11 under
    `fixtures/v1.1.0/`, outside the v1.0.0 set. A fixture whose `expected`
    block carries a `contentDigest` (v1.1.0 R4) has that digest compared too.
    """
    results, mismatches = [], []
    for control in prereg["controls"]:
        path = EXPERIMENT / control["fixture"]
        doc = json.loads(path.read_text())
        receipt = evaluate_transaction(doc["input"])
        expected = doc["expected"]
        diffs = []
        if receipt["conclusion"] != expected["conclusion"]:
            diffs.append(f"conclusion {receipt['conclusion']!r} != {expected['conclusion']!r}")
        for block in ("search", "evidence"):
            for key, want in expected[block].items():
                got = receipt[block][key]
                if got != want:
                    diffs.append(f"{block}.{key} {got!r} != {want!r}")
        if "contentDigest" in expected and receipt["contentDigest"] != expected["contentDigest"]:
            diffs.append(
                f"contentDigest {receipt['contentDigest']!r} != {expected['contentDigest']!r}"
            )
        results.append({"control": doc["control"], "fixture": path.name,
                        "passed": not diffs, "differences": diffs})
        if diffs:
            mismatches.append(doc["control"])
    return {"phase": "fixture", "controls": results,
            "mismatchedControls": mismatches, "passed": not mismatches}


def run_world_phase(phase: str, evaluate, limit: int | None = None,
                    stop_on_first: bool = True) -> dict:
    """Exhaustive or randomized enumeration under one evaluator."""
    if phase == "exhaustive":
        stream = worlds.exhaustive_worlds()
    elif phase == "randomized":
        stream = worlds.randomized_worlds(limit or worlds.RANDOM_WORLD_COUNT)
    else:
        raise ValueError(phase)

    started = time.monotonic()
    checked = out_of_bounds = fail_closed = 0
    conclusions: dict[str, int] = {}
    per_invariant: dict[str, int] = {}
    preserved: list[dict] = []
    # A bare counter cannot tell a designed refusal from an implementation
    # defect: a KeyError from an unhandled payload shape and a deliberate
    # ValueError both just increment it. Bucket by cause and keep a bounded
    # sample of each, so the distribution itself is the evidence that the
    # refusals are by design.
    fail_closed_by_cause: dict[str, int] = {}
    fail_closed_samples: dict[str, list[dict]] = {}

    for world in stream:
        if limit is not None and checked >= limit:
            break
        checked += 1
        if not worlds.world_within_declared_bounds(world, phase):
            out_of_bounds += 1
            continue
        try:
            receipt = evaluate(world)
            conclusions[receipt["conclusion"]] = conclusions.get(receipt["conclusion"], 0) + 1
        except Exception as exc:  # noqa: BLE001
            fail_closed += 1
            cause = f"{type(exc).__name__}: {exc}"
            fail_closed_by_cause[cause] = fail_closed_by_cause.get(cause, 0) + 1
            bucket = fail_closed_samples.setdefault(cause, [])
            if len(bucket) < 3:
                bucket.append(world)
        for violation in check_world(evaluate, world):
            per_invariant[violation.invariant] = per_invariant.get(violation.invariant, 0) + 1
            if len(preserved) < 20:
                preserved.append({"invariant": violation.invariant,
                                  "detail": violation.detail, "world": violation.world})
            if stop_on_first:
                return _phase_report(phase, checked, out_of_bounds, fail_closed,
                                     fail_closed_by_cause, fail_closed_samples,
                                     conclusions, per_invariant, preserved,
                                     True, started)

    return _phase_report(phase, checked, out_of_bounds, fail_closed,
                         fail_closed_by_cause, fail_closed_samples,
                         conclusions, per_invariant, preserved, False, started)


# Refusals the protocol expects. Anything outside this set is a candidate
# implementation defect and is surfaced rather than absorbed into a total.
EXPECTED_FAIL_CLOSED_CAUSES = (
    "ValueError: One root cannot support opposing sides.",
)


def _phase_report(phase, checked, out_of_bounds, fail_closed, by_cause,
                  samples, conclusions, per_invariant, preserved,
                  halted, started):
    total = sum(per_invariant.values())
    unexpected = {c: n for c, n in by_cause.items()
                  if c not in EXPECTED_FAIL_CLOSED_CAUSES}
    return {
        "phase": phase,
        "worldsChecked": checked,
        "outOfDeclaredBounds": out_of_bounds,
        "failClosedRejections": fail_closed,
        "failClosedByCause": dict(sorted(by_cause.items(), key=lambda kv: -kv[1])),
        "failClosedUnexpectedCauses": unexpected,
        "failClosedSamples": {c: samples[c] for c in sorted(samples)},
        "receiptProducingWorlds": sum(conclusions.values()),
        "conclusionDistribution": conclusions,
        "violationsByInvariant": per_invariant,
        "totalViolations": total,
        "preservedViolations": preserved,
        "stopConditionArmed": True,
        "stopConditionTriggered": halted,
        "stopConditionNote": (
            "Halted on the first hard violation."
            if halted else
            "Not triggered: no hard violation occurred. The stop condition was "
            "armed throughout -- the run returns immediately on the first "
            "violation -- and simply had no occasion to fire."
        ),
        "elapsedSeconds": round(time.monotonic() - started, 3),
        # An unexpected refusal cause is an implementation defect, not a pass.
        "passed": total == 0 and out_of_bounds == 0 and not unexpected,
    }


def run_baselines(sample: int | None) -> dict:
    """Power of the test: every ablated baseline MUST be caught.

    `sample=None` runs the full exhaustive set, which is what PROTOCOL.md means
    by "the same worlds and the same checker". A subsample would still settle
    the vacuity question, but "the same worlds" and "2% of them" are different
    claims and the protocol only writes down one of them.
    """
    out = {}
    for name, fn in BASELINES.items():
        report = run_world_phase("exhaustive", fn, limit=sample, stop_on_first=False)
        out[name] = {"worldsChecked": report["worldsChecked"],
                     "coverage": "full exhaustive set" if sample is None
                                 else f"first {sample} of {worlds.DECLARED_WORLD_COUNT}",
                     "totalViolations": report["totalViolations"],
                     "violationsByInvariant": report["violationsByInvariant"],
                     "caught": report["totalViolations"] > 0}
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", default="all",
                        choices=["all", "fixture", "exhaustive", "randomized", "baselines"])
    parser.add_argument("--out", default=str(EXPERIMENT / "results"))
    parser.add_argument("--randomized-count", type=int, default=worlds.RANDOM_WORLD_COUNT)
    parser.add_argument("--baseline-sample", type=int, default=None,
                        help="worlds per baseline; default None = full exhaustive set")
    parser.add_argument("--label", default="confirmatory")
    parser.add_argument("--preregistration", default="preregistration.json",
                        help="registration to run against, relative to the "
                             "experiment directory; the default is the v1.0.0 "
                             "registration, preregistration-v1.1.0.json selects "
                             "protocol v1.1.0")
    args = parser.parse_args()

    prereg_path = EXPERIMENT / args.preregistration
    drifts = worlds.verify_bounds_against_preregistration(prereg_path)
    evaluator_hash = sha256_file(REPO / "knowledge_ledger" / "transaction.py")
    prereg = json.loads(prereg_path.read_text())
    expected_hash = prereg["evaluatorUnderTest"]["sha256"]

    document = {
        "schema": "minority-prophet.kl000-result.v0.1",
        "experimentId": "KL-000",
        "protocolVersion": prereg["protocolVersion"],
        "label": args.label,
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "evaluatorUnderTest": {
            "path": "knowledge_ledger/transaction.py",
            "sha256": evaluator_hash,
            "matchesPreregistration": evaluator_hash == expected_hash,
        },
        "boundsDriftFromPreregistration": drifts,
        "derivedExhaustiveCount": worlds.expected_exhaustive_count(),
        "declaredExhaustiveCount": worlds.DECLARED_WORLD_COUNT,
        "phases": {},
    }

    # Invalidation conditions are checked before any phase runs.
    invalid = []
    if drifts:
        invalid.append("generator bounds drifted from the preregistration")
    if evaluator_hash != expected_hash:
        invalid.append("evaluator hash differs from the preregistered value")
    if worlds.expected_exhaustive_count() != worlds.DECLARED_WORLD_COUNT:
        invalid.append("derived world count differs from the declared count")

    if not invalid:
        if args.phase in ("all", "fixture"):
            document["phases"]["fixture"] = run_fixture_phase(prereg)
        if args.phase in ("all", "baselines"):
            baselines = run_baselines(args.baseline_sample)
            document["phases"]["baselines"] = baselines
            uncaught = [n for n, r in baselines.items() if not r["caught"]]
            if uncaught:
                invalid.append(f"baselines not caught, suite is vacuous: {uncaught}")
        if args.phase in ("all", "exhaustive"):
            document["phases"]["exhaustive"] = run_world_phase("exhaustive", evaluate_transaction)
        if args.phase in ("all", "randomized"):
            document["phases"]["randomized"] = run_world_phase(
                "randomized", evaluate_transaction, limit=args.randomized_count)

    # An unrecognised refusal cause is an implementation defect surfacing as a
    # count. Per the run protocol that is "incomplete", never negative or
    # positive, so it belongs in invalidation rather than in the verdict.
    for name in ("exhaustive", "randomized"):
        phase = document["phases"].get(name)
        if phase and phase.get("failClosedUnexpectedCauses"):
            invalid.append(
                f"{name} phase produced unexpected fail-closed causes: "
                f"{phase['failClosedUnexpectedCauses']}"
            )

    document["invalidationReasons"] = invalid

    # The baselines phase is shaped differently from the world phases: it maps
    # baseline name -> report and carries no top-level "passed". Folding it in
    # explicitly avoids a baselines-only run reporting "failed" merely because
    # nothing in `phases` had the key the check was looking for.
    outcomes = []
    for name, phase in document["phases"].items():
        if name == "baselines":
            outcomes.append(all(r["caught"] for r in phase.values()))
        elif isinstance(phase, dict) and "passed" in phase:
            outcomes.append(phase["passed"])

    if invalid:
        document["result"] = "incomplete"
    elif outcomes and all(outcomes):
        document["result"] = "passed"
    elif not outcomes:
        document["result"] = "incomplete"
    else:
        document["result"] = "failed"

    # Rule of three, reported only when the randomized phase ran clean.
    rnd = document["phases"].get("randomized")
    if rnd and rnd["passed"] and rnd["worldsChecked"]:
        n = rnd["worldsChecked"]
        document["uncertainty"] = {
            "randomizedWorlds": n,
            "observedViolations": 0,
            "ruleOfThreeUpperBound95": 3 / n,
            "bonferroniAdjustedUpperBound": 5.3 / n,
            "interpretation": (
                "Bounds a per-world violation rate. Does not establish zero, and "
                "says nothing about worlds outside the declared bounds."
            ),
        }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"kl000-{args.label}.json"
    target.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": document["result"],
                      "invalidationReasons": invalid,
                      "phases": {k: v.get("passed") if isinstance(v, dict) else None
                                 for k, v in document["phases"].items()}}, indent=2))
    print(f"written: {target}")


if __name__ == "__main__":
    main()
