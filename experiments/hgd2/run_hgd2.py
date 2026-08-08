"""Frozen HGD-2 cross-domain confirmatory runner."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import random
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.hgd1.run_hgd1 import (
    EVENT_THRESHOLD,
    assess,
    binary_vote,
    component,
    load_epa_cases,
    receipt,
    run_synthetic,
)


PROTOCOL = ROOT / "experiments" / "HGD-2-PREREGISTRATION.md"
MANIFEST = ROOT / "experiments" / "hgd2" / "source-manifest.json"
SOFTWARE = ROOT / "experiments" / "hgd2" / "software-detector-records.json"
SOURCE = Path(__file__).resolve()
PROTOCOL_COMMIT = "721278f"
EVIDENCE_COMMIT = "22c5afe"
BOOTSTRAP_SEED = 20260810
BOOTSTRAP_RESAMPLES = 10_000
SHIFTS = (-20.0, -10.0, -5.0, 5.0, 10.0, 20.0)
METHODS = ("head", "origin", "family", "midpoint", "interval")


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def simple_vote(votes: list[int]) -> tuple[str, int | None]:
    if votes.count(0) == votes.count(1):
        return "ABSTAIN", None
    return "ANSWER", int(votes.count(1) > votes.count(0))


def epa_outcome(case: dict, shift: float, method: str) -> tuple[str, int | None]:
    collocated = [value + shift for value in case["pocs"].values()]
    reference = list(case["referencePocs"].values())
    if method in {"head", "origin"}:
        return simple_vote(binary_vote(collocated + reference))
    return simple_vote(binary_vote([
        __import__("statistics").median(collocated),
        __import__("statistics").median(reference),
    ]))


def metric(records: list[dict]) -> dict:
    cases = len(records)
    answered = sum(item["state"] == "ANSWER" for item in records)
    errors = sum(item["state"] == "ANSWER" and item["answer"] != item["truth"] for item in records)
    return {
        "cases": cases,
        "answered_coverage": answered / cases if cases else None,
        "false_confident_error": errors / cases if cases else None,
        "conditional_accuracy": 1 - errors / answered if answered else None,
        "abstention_rate": 1 - answered / cases if cases else None,
    }


def bootstrap_upper(records: list[dict], seed_offset: int) -> float | None:
    if not records:
        return None
    grouped = defaultdict(list)
    for item in records:
        grouped[item["cluster"]].append(item)
    clusters = sorted(grouped); rng = random.Random(BOOTSTRAP_SEED + seed_offset); values = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [grouped[clusters[rng.randrange(len(clusters))]] for _ in clusters]
        flat = [item for group in sample for item in group]
        values.append(sum(item["state"] == "ANSWER" and item["answer"] != item["truth"]
                          for item in flat) / len(flat))
    values.sort(); pos = (len(values) - 1) * 0.975; lo, hi = math.floor(pos), math.ceil(pos)
    return values[lo] if lo == hi else values[lo] + (values[hi] - values[lo]) * (pos - lo)


def run_epa() -> dict:
    cases, structure = load_epa_cases()
    controls = {method: [] for method in METHODS}
    activated = {"negative": {method: [] for method in METHODS},
                 "positive": {method: [] for method in METHODS}}
    by_shift = {}
    for index, case in enumerate(cases):
        unchanged = list(case["pocs"].values()) + list(case["referencePocs"].values())
        truth = int(__import__("statistics").median(unchanged) >= EVENT_THRESHOLD)
        base_state, base_answer = epa_outcome(case, 0.0, "head")
        for method in METHODS:
            state, answer = epa_outcome(case, 0.0, method)
            controls[method].append({"cluster": index, "truth": truth, "state": state, "answer": answer})
        for shift in SHIFTS:
            direction = "negative" if shift < 0 else "positive"
            head_state, head_answer = epa_outcome(case, shift, "head")
            is_activated = (base_state == "ANSWER" and base_answer == truth and
                            head_state == "ANSWER" and head_answer != truth)
            if not is_activated:
                continue
            for method in METHODS:
                state, answer = epa_outcome(case, shift, method)
                activated[direction][method].append(
                    {"cluster": index, "shift": shift, "truth": truth, "state": state, "answer": answer}
                )
    for shift in SHIFTS:
        direction = "negative" if shift < 0 else "positive"
        by_shift[str(int(shift))] = {
            method: metric([item for item in activated[direction][method] if item["shift"] == shift])
            for method in METHODS
        }
    directions = {}
    for offset, direction in enumerate(("negative", "positive")):
        directions[direction] = {method: metric(activated[direction][method]) for method in METHODS}
        directions[direction]["interval"]["relative_risk_upper_95"] = bootstrap_upper(
            activated[direction]["interval"], offset
        )
    return {"structure": structure, "controls": {m: metric(v) for m, v in controls.items()},
            "activated_by_direction": directions, "activated_by_shift": by_shift}


def software_records() -> tuple[list[dict], dict]:
    packet = json.loads(SOFTWARE.read_text())
    records = [item for item in packet["records"] if item["split"] == "confirmatory"]
    return sorted(records, key=lambda item: item["case"]), packet["detectorFamilies"]


def software_outcome(item: dict, families: dict, method: str, overrides: dict[str, int] | None = None):
    overrides = overrides or {}; records = []; components = []
    for family, names in families.items():
        members = []
        for name in names:
            detector = item["detectors"][name]
            state = detector["state"]
            vote = overrides.get(name, detector["vote"])
            origin = f"{item['case']}:{name}"; members.append(origin)
            records.append(receipt(origin, int(vote) if vote is not None else 0, support=state))
        components.append(component(f"{item['case']}:{family}", members, 1.0, 1.0, 1.0))
    return assess(records, components, method)


def run_software() -> dict:
    records, families = software_records()
    controls = {method: [] for method in METHODS}
    activated = defaultdict(lambda: {method: [] for method in METHODS})
    cells = defaultdict(lambda: {method: [] for method in METHODS})
    previous = {family: None for family in families}
    for item in records:
        truth = item["truth"]; base = software_outcome(item, families, "head")
        for method in METHODS:
            outcome = software_outcome(item, families, method)
            controls[method].append({"cluster": item["case"], "truth": truth,
                                     "state": outcome["state"], "answer": outcome["answer"]})
        for family, names in families.items():
            attacks = {}
            if truth == 1:
                attacks["false_negative"] = {name: 0 for name in names}
            if truth == 0:
                attacks["false_positive"] = {name: 1 for name in names}
            if previous[family] is not None:
                attacks["stale_replay"] = dict(zip(names, previous[family]))
            for attack, overrides in attacks.items():
                head = software_outcome(item, families, "head", overrides)
                active = (base["state"] == "ANSWER" and base["answer"] == truth and
                          head["state"] == "ANSWER" and head["answer"] != truth)
                if not active:
                    continue
                cell = f"{family}:{attack}"
                for method in METHODS:
                    outcome = software_outcome(item, families, method, overrides)
                    row = {"cluster": item["case"], "truth": truth,
                           "state": outcome["state"], "answer": outcome["answer"]}
                    activated[attack][method].append(row); cells[cell][method].append(row)
            previous[family] = [item["detectors"][name]["vote"] for name in names]
    attack_metrics = {}; seed_offset = 10
    for attack in ("false_negative", "false_positive", "stale_replay"):
        attack_metrics[attack] = {method: metric(activated[attack][method]) for method in METHODS}
        attack_metrics[attack]["interval"]["relative_risk_upper_95"] = bootstrap_upper(
            activated[attack]["interval"], seed_offset
        ); seed_offset += 1
    cell_metrics = {cell: {method: metric(rows) for method, rows in methods.items()}
                    for cell, methods in sorted(cells.items())}
    pooled = {method: metric([row for attack in activated.values() for row in attack[method]])
              for method in METHODS}
    pooled["interval"]["relative_risk_upper_95"] = bootstrap_upper(
        [row for attack in activated.values() for row in attack["interval"]], 20
    )
    return {"structure": {"confirmatory_records": len(records), "families": families},
            "controls": {m: metric(v) for m, v in controls.items()}, "activated": attack_metrics,
            "cells": cell_metrics, "pooled_activated": pooled}


def run() -> tuple[dict, dict]:
    started = time.perf_counter(); epa = run_epa(); software = run_software()
    synthetic, _ = run_synthetic(); partial = synthetic["partial_calibration_8"]["interval"]
    epa_safety = all(epa["activated_by_direction"][d]["interval"]["relative_risk_upper_95"] is not None and
                     epa["activated_by_direction"][d]["interval"]["relative_risk_upper_95"] <= 0.50
                     for d in ("negative", "positive"))
    attack_cells_complete = all(
        software["activated"][a]["interval"]["cases"] > 0 and
        software["activated"][a]["interval"]["relative_risk_upper_95"] is not None
        for a in ("false_negative", "false_positive", "stale_replay")
    )
    expected_cells = {f"{family}:{attack}" for family in ("compiler", "flawfinder", "lexical")
                      for attack in ("false_negative", "false_positive", "stale_replay")}
    cell_gate = all(cell in software["cells"] and software["cells"][cell]["interval"]["cases"] > 0 and
                    software["cells"][cell]["interval"]["false_confident_error"] <= 0.75
                    for cell in expected_cells)
    software_safety = (attack_cells_complete and cell_gate and
        software["pooled_activated"]["interval"]["relative_risk_upper_95"] <= 0.50 and
        all(cell["interval"]["false_confident_error"] <= 0.75
            for cell in software["cells"].values()))
    def control_gate(domain, field):
        head = domain["controls"]["head"][field]; interval = domain["controls"]["interval"][field]
        return head is not None and interval is not None and interval >= 0.95 * head
    h = {
        "HGD-2a": epa_safety,
        "HGD-2b": software_safety,
        "HGD-2c": all(control_gate(domain, "conditional_accuracy") for domain in (epa, software)),
        "HGD-2d": all(control_gate(domain, "answered_coverage") for domain in (epa, software)),
        "HGD-2e": (all(epa["activated_by_direction"][d]["interval"]["answered_coverage"] is not None and
                         epa["activated_by_direction"][d]["interval"]["answered_coverage"] >= 0.50
                         for d in ("negative", "positive")) and
                    software["pooled_activated"]["interval"]["answered_coverage"] is not None and
                    software["pooled_activated"]["interval"]["answered_coverage"] >= 0.50),
        "HGD-2f": (partial["true_mass_interval_coverage"] >= 0.95 and
                    partial["mean_interval_width"] < 2.0),
        "HGD-2g": (assess([receipt("r", 1, support="unknown")], [], "interval")["state"] == "ESCALATE" and
                    assess([receipt("r", 1, support="conflicting")], [], "interval")["state"] == "ESCALATE"),
    }
    h["primary_claim"] = all(h.values())
    scientific = {
        "schema": "minority-prophet.hgd2.scientific-result.v1", "experiment": "HGD-2",
        "protocol_commit": PROTOCOL_COMMIT, "evidence_commit": EVIDENCE_COMMIT,
        "implementation_commit": git_head(),
        "hashes": {"protocol": sha(PROTOCOL), "manifest": sha(MANIFEST),
                   "software_evidence": sha(SOFTWARE), "runner": sha(SOURCE)},
        "configuration": {"bootstrap_seed": BOOTSTRAP_SEED,
                          "bootstrap_resamples": BOOTSTRAP_RESAMPLES, "shifts": list(SHIFTS)},
        "epa": epa, "software": software,
        "synthetic_calibration": partial, "hypotheses": h,
        "claim_boundary": "Declared-family controlled-failure replication; no hidden-cause discovery, tool certification, historical error claim, or authority."
    }
    timing = {"schema": "minority-prophet.hgd2.timing.v1", "elapsed_seconds": time.perf_counter() - started,
              "environment": {"python": sys.version, "platform": platform.platform()}}
    return scientific, timing


def main() -> None:
    scientific, timing = run()
    print(json.dumps(scientific, sort_keys=True, separators=(",", ":")))
    print(json.dumps(timing, sort_keys=True, separators=(",", ":")), file=sys.stderr)


if __name__ == "__main__":
    main()
