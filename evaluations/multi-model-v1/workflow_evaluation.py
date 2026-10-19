"""Offline exploratory invoice review. Never authorizes a live action.

Only the scorer reads reference answers. Contestants receive identical packets.
The MP lane is a deliberately simple root-vote composition, not a claim that
MP's evidence aggregator is a production invoice authorization engine.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from aggregation.root_vote import verdict  # noqa: E402

FIELDS = ("id", "family", "amount_cents", "as_of", "max_age", "evidence", "narrative")
DECISIONS = {"ALLOW", "HOLD", "REVIEW"}
POLICY = (
    "Synthetic USD invoice triage only. Valid nonnegative integer cents <=1000000: ALLOW. "
    "Above that threshold, fresh attributed approval evidence is required. "
    "All fresh evidence true: ALLOW; all false: HOLD; any contradiction: REVIEW. "
    "Missing/malformed amount, missing evidence, stale/future evidence, missing origin, "
    "or nonboolean approval: REVIEW. Age exactly max_age is fresh. "
    "Narrative-only facts require extraction; do not invent missing facts. "
    "ALLOW is a benchmark label, never execution authority."
)


def public_packet(packet):
    """Explicit schema projection; answer keys and incidental metadata stay out."""
    result = {key: copy.deepcopy(packet[key]) for key in FIELDS if key in packet}
    result["evidence"] = [
        {key: row.get(key) for key in ("root_id", "approved", "at")}
        for row in packet.get("evidence", [])
    ]
    return result


def prepared(packet):
    amount = packet.get("amount_cents")
    if type(amount) is not int or amount < 0:
        return "REVIEW", []
    if amount <= 1000000:
        return "ALLOW", []
    now, age = packet.get("as_of"), packet.get("max_age")
    if type(now) is not int or type(age) is not int or age < 0:
        return "REVIEW", []
    rows = packet.get("evidence", [])
    if not rows:
        return "REVIEW", []
    for row in rows:
        if (type(row.get("approved")) is not bool
                or not isinstance(row.get("root_id"), str) or not row["root_id"].strip()
                or type(row.get("at")) is not int
                or not 0 <= now - row["at"] <= age):
            return "REVIEW", []
    return None, rows


def rules(packet):
    early, rows = prepared(packet)
    if early:
        return early
    values = {row["approved"] for row in rows}
    return "REVIEW" if len(values) != 1 else "ALLOW" if True in values else "HOLD"


def mp_composition(packet):
    early, rows = prepared(packet)
    if early:
        return early
    result = verdict([SimpleNamespace(root_id=r["root_id"], value=r["approved"])
                      for r in rows])
    return {"true": "ALLOW", "false": "HOLD", "abstain": "REVIEW"}[result.verdict.value]


def score(packets, reference, predictions):
    ids = [p["id"] for p in packets]
    if len(ids) != len(set(ids)) or set(reference) != set(ids):
        raise ValueError("duplicate cases or incomplete/extra reference labels")
    if set(predictions) - set(ids) or any(v not in DECISIONS for v in reference.values()):
        raise ValueError("unknown prediction IDs or invalid reference labels")
    rows = [{"id": p["id"], "family": p["family"], "expected": reference[p["id"]],
             "actual": predictions.get(p["id"], "ERROR")} for p in packets]
    total = len(rows)
    correct = sum(r["actual"] == r["expected"] for r in rows)
    answered = sum(r["actual"] in {"ALLOW", "HOLD"} for r in rows)
    failures = sum(r["actual"] not in DECISIONS for r in rows)
    return {
        "attempted": total, "correct": correct, "failures": failures,
        "accuracy": correct / total if total else None,
        "coverage": answered / total if total else None,
        "wrong_approvals": sum(r["actual"] == "ALLOW" and r["expected"] != "ALLOW" for r in rows),
        "wrong_holds": sum(r["actual"] == "HOLD" and r["expected"] != "HOLD" for r in rows),
        "reviews": sum(r["actual"] == "REVIEW" for r in rows),
        "unnecessary_reviews": sum(r["actual"] == "REVIEW" and r["expected"] != "REVIEW" for r in rows),
        "cases": rows,
    }


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run(packets, reference):
    packets = [public_packet(p) for p in packets]
    # Finish predictions before the reference is consulted by the scorer.
    predictions = {name: {p["id"]: method(copy.deepcopy(p)) for p in packets}
                   for name, method in [("ordinary_rules", rules), ("mp_root_vote_composition", mp_composition)]}
    return {
        "classification": "exploratory_synthetic_not_confirmatory",
        "control_domain": "same_operator_builder_runner_reviewer",
        "policy": POLICY, "input_sha256": digest({"policy": POLICY, "cases": packets}),
        "reference_sha256": digest(reference),
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in [Path(__file__), ROOT / "aggregation/root_vote.py", ROOT / "aggregation/independence_axes.py"]},
        "lanes": {name: score(packets, reference, answers) for name, answers in predictions.items()},
        "external_lanes": {name: {"status": "not_run"} for name in ["Jev", "OpenJev", "frontier_model"]},
        "claims": "Development fixtures only; no deployment authority, independent validation, or general superiority claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", action="store_true", help="Print contestant input only, never labels")
    args = parser.parse_args()
    directory = Path(__file__).with_name("workflow-fixtures")
    packets = json.loads((directory / "inputs.json").read_text())
    if args.export:
        output = {"policy": POLICY, "cases": [public_packet(p) for p in packets]}
    else:
        reference = json.loads((directory / "reference.json").read_text())
        output = run(packets, reference)
        output["repository_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        output["dirty_worktree"] = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
