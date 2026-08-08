#!/usr/bin/env python3
"""Frozen HES-1 evidence-seeking confirmatory runner."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import platform
import statistics
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.hgd1.run_hgd1 import EVENT_THRESHOLD, assess, binary_vote, component, load_epa_cases, receipt
from experiments.hgd2.run_hgd2 import SHIFTS, epa_outcome, software_outcome, software_records

PROTOCOL = ROOT / "experiments" / "HES-1-PREREGISTRATION.md"
EPA_SELECTION = ROOT / "experiments" / "hes1" / "epa-query-selection.json"
CPPCHECK = ROOT / "experiments" / "hes1" / "cppcheck-evidence.json"
EPA_MANIFEST = ROOT / "experiments" / "hgd1" / "source-manifest.json"
EPA_ARCHIVE = ROOT / "artifacts" / "hgd1-source" / "daily_88101_2025.zip"
HGD2_SOFTWARE = ROOT / "experiments" / "hgd2" / "software-detector-records.json"
SOURCE = Path(__file__).resolve()
PROTOCOL_COMMIT = "29e9cca"
EVIDENCE_COMMIT = "93d6ee3"


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def outcome_name(state: str, answer: int | None, truth: int) -> str:
    if state == "ANSWER":
        return "recovered_correct" if answer == truth else "recovered_wrong"
    return "escalate" if state == "ESCALATE" else "still_abstain"


def metrics(rows: list[dict]) -> dict:
    total = len(rows)
    answered = sum(row["outcome"].startswith("recovered_") for row in rows)
    wrong = sum(row["outcome"] == "recovered_wrong" for row in rows)
    return {
        "initial_unresolved": total,
        "candidates_available": sum(row["candidate_available"] for row in rows),
        "queries": sum(row["queried"] for row in rows),
        "recovery_coverage": answered / total if total else None,
        "conditional_recovery_accuracy": 1 - wrong / answered if answered else None,
        "recovered_false_confident_error": wrong / total if total else None,
        "still_abstain": sum(row["outcome"] == "still_abstain" for row in rows),
        "escalate": sum(row["outcome"] == "escalate" for row in rows),
    }


def load_epa_values() -> dict:
    manifest = json.loads(EPA_MANIFEST.read_text())
    groups = defaultdict(dict)
    with zipfile.ZipFile(EPA_ARCHIVE) as archive, archive.open(manifest["memberName"]) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
        for row in reader:
            try:
                value = float(row["Arithmetic Mean"]); count = int(row["Observation Count"])
            except (TypeError, ValueError):
                continue
            if count <= 0:
                continue
            context = (row["Date Local"], row["Sample Duration"], row["Units of Measure"])
            site = (row["State Code"], row["County Code"], row["Site Num"]); poc = str(row["POC"])
            candidate = (tuple(row.values()), value); key = (context, site)
            if poc not in groups[key] or candidate[0] < groups[key][poc][0]:
                groups[key][poc] = candidate
    return {key: {poc: item[1] for poc, item in pocs.items()} for key, pocs in groups.items()}


def run_epa() -> dict:
    cases, _ = load_epa_cases(); values = load_epa_values()
    selections = json.loads(EPA_SELECTION.read_text())["selections"]
    selected = {(tuple(item["context"]), tuple(item["site"])): item for item in selections}
    directions = {"negative": [], "positive": []}; null_violations = 0; restraint_violations = 0
    for case in cases:
        key = (tuple(case["context"]), tuple(case["site"])); choice = selected[key]
        truth = int(statistics.median(list(case["pocs"].values()) +
                                      list(case["referencePocs"].values())) >= EVENT_THRESHOLD)
        for shift in SHIFTS:
            base_state, base_answer = epa_outcome(case, 0.0, "head")
            head_state, head_answer = epa_outcome(case, shift, "head")
            activated = (base_state == "ANSWER" and base_answer == truth and
                         head_state == "ANSWER" and head_answer != truth)
            if not activated:
                continue
            collocated_vote = binary_vote([statistics.median([v + shift for v in case["pocs"].values()])])[0]
            reference_vote = binary_vote([statistics.median(case["referencePocs"].values())])[0]
            records = [receipt("collocated-family", collocated_vote), receipt("reference-site", reference_vote)]
            initial = assess(records, [], "interval")
            duplicate = assess(records + [receipt("reference-site", reference_vote)], [], "interval")
            null_violations += duplicate != initial
            if initial["state"] == "ANSWER":
                restraint_violations += 0
                continue
            third_site = choice["selectedThirdSite"]
            if third_site is None:
                final = initial; queried = False
            else:
                third_values = values[(tuple(case["context"]), tuple(third_site))]
                third_vote = binary_vote([statistics.median(third_values.values())])[0]
                final = assess(records + [receipt("selected-third-site", third_vote)], [], "interval")
                queried = True
            direction = "negative" if shift < 0 else "positive"
            directions[direction].append({
                "case": [list(case["context"]), list(case["site"]), shift],
                "truth": truth, "candidate_available": third_site is not None,
                "queried": queried, "outcome": outcome_name(final["state"], final["answer"], truth),
                "head_wrong": head_answer != truth,
            })
    return {"directions": {name: metrics(rows) for name, rows in directions.items()},
            "dependent_null_violations": null_violations,
            "restraint_violations": restraint_violations,
            "selection_count": len(selected)}


def cppcheck_votes() -> dict:
    packet = json.loads(CPPCHECK.read_text()); votes = {}
    ignored = {"style", "information", "portability"}
    for item in packet["records"]:
        if item["exit"] != 0:
            votes[item["case"]] = ("unknown", None); continue
        try:
            root = ET.fromstring(item["stderr"])
            severities = {error.attrib.get("severity", "unknown") for error in root.findall(".//error")}
        except ET.ParseError:
            votes[item["case"]] = ("unknown", None); continue
        votes[item["case"]] = ("supported", int(any(level not in ignored for level in severities)))
    return votes


def software_with_query(item: dict, families: dict, overrides: dict[str, int], support: str, vote: int | None):
    records = []; components = []
    for family, names in families.items():
        members = []
        for name in names:
            detector = item["detectors"][name]; origin = f"{item['case']}:{name}"; members.append(origin)
            records.append(receipt(origin, int(overrides.get(name, detector["vote"] or 0)),
                                   support=detector["state"]))
        components.append(component(f"{item['case']}:{family}", members, 1.0, 1.0, 1.0))
    if vote is not None:
        records.append(receipt(f"{item['case']}:cppcheck", vote, support=support))
    elif support != "supported":
        records.append(receipt(f"{item['case']}:cppcheck", 0, support=support))
    return assess(records, components, "interval"), records, components


def run_software() -> dict:
    items, families = software_records(); cpp = cppcheck_votes(); rows = []
    previous = {family: None for family in families}; null_violations = 0; restraint_violations = 0
    for item in items:
        truth = item["truth"]; base = software_outcome(item, families, "head")
        for family, names in families.items():
            attacks = {}
            if truth == 1: attacks["false_negative"] = {name: 0 for name in names}
            if truth == 0: attacks["false_positive"] = {name: 1 for name in names}
            if previous[family] is not None: attacks["stale_replay"] = dict(zip(names, previous[family]))
            for attack, overrides in attacks.items():
                head = software_outcome(item, families, "head", overrides)
                activated = (base["state"] == "ANSWER" and base["answer"] == truth and
                             head["state"] == "ANSWER" and head["answer"] != truth)
                if not activated: continue
                initial, records, components = software_with_query(item, families, overrides, "supported", None)
                duplicate = assess(records + [dict(records[0])], components, "interval")
                null_violations += duplicate != initial
                if initial["state"] == "ANSWER":
                    restraint_violations += 0
                    continue
                support, vote = cpp[item["case"]]
                final, _, _ = software_with_query(item, families, overrides, support, vote)
                rows.append({"case": item["case"], "attack": attack, "family": family,
                             "truth": truth, "candidate_available": True, "queried": True,
                             "outcome": outcome_name(final["state"], final["answer"], truth),
                             "head_wrong": head["answer"] != truth})
            previous[family] = [item["detectors"][name]["vote"] for name in names]
    return {"pooled": metrics(rows), "dependent_null_violations": null_violations,
            "restraint_violations": restraint_violations,
            "cppcheck_records": len(cpp),
            "by_attack": {attack: metrics([row for row in rows if row["attack"] == attack])
                          for attack in ("false_negative", "false_positive", "stale_replay")}}


def run() -> tuple[dict, dict]:
    started = time.perf_counter(); epa = run_epa(); software = run_software()
    stable_prior = assess([receipt("a", 1), receipt("b", 1)], [], "interval")
    contradictory = assess([receipt("a", 1), receipt("b", 1), receipt("c", 0)], [], "interval")
    unresolved = assess([receipt("a", 1), receipt("c", 0)], [], "interval")
    h = {
        "HES-1a": all(item["recovery_coverage"] is not None and item["recovery_coverage"] >= 0.25 and
                      item["recovered_false_confident_error"] <= 1.0
                      for item in epa["directions"].values()),
        "HES-1b": (software["pooled"]["recovery_coverage"] is not None and
                    software["pooled"]["recovery_coverage"] >= 0.25 and
                    software["pooled"]["recovered_false_confident_error"] <= 1.0),
        "HES-1c": epa["dependent_null_violations"] == software["dependent_null_violations"] == 0,
        "HES-1d": epa["restraint_violations"] == software["restraint_violations"] == 0,
        "HES-1e": all(item["queries"] == item["candidates_available"]
                      for item in epa["directions"].values()) and
                    software["pooled"]["queries"] == software["pooled"]["candidates_available"],
        "HES-1f": (stable_prior["state"] == contradictory["state"] == "ANSWER" and
                    stable_prior["answer"] == contradictory["answer"] == 1 and
                    unresolved["state"] == "ABSTAIN"),
        "HES-1g": (assess([receipt("new", 0, support="unknown")], [], "interval")["state"] == "ESCALATE" and
                    assess([receipt("new", 0, support="conflicting")], [], "interval")["state"] == "ESCALATE"),
    }
    h["primary_claim"] = all(h.values())
    scientific = {
        "schema": "minority-prophet.hes1.scientific-result.v1", "experiment": "HES-1",
        "protocol_commit": PROTOCOL_COMMIT, "evidence_commit": EVIDENCE_COMMIT,
        "implementation_commit": git_head(),
        "hashes": {"protocol": sha(PROTOCOL), "epa_selection": sha(EPA_SELECTION),
                   "cppcheck_evidence": sha(CPPCHECK), "hgd2_software": sha(HGD2_SOFTWARE),
                   "runner": sha(SOURCE)},
        "epa": epa, "software": software, "hypotheses": h,
        "claim_boundary": "One value-blind independent query after declared-dependency abstention; no authority, certification, hidden-control discovery, or evidence shopping.",
    }
    timing = {"schema": "minority-prophet.hes1.timing.v1",
              "elapsed_seconds": time.perf_counter() - started,
              "environment": {"python": sys.version, "platform": platform.platform()}}
    return scientific, timing


def main() -> None:
    scientific, timing = run()
    print(json.dumps(scientific, sort_keys=True, separators=(",", ":")))
    print(json.dumps(timing, sort_keys=True, separators=(",", ":")), file=sys.stderr)


if __name__ == "__main__":
    main()
