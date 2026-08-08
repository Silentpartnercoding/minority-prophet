"""Frozen HGD-1 confirmatory runner."""

from __future__ import annotations

import csv
import hashlib
import io
import itertools
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
import zipfile
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "experiments" / "HGD-1-PREREGISTRATION.md"
SCHEMA = ROOT / "experiments" / "hgd1" / "dependency-receipt.schema.json"
VECTORS = ROOT / "experiments" / "hgd1" / "conformance-vectors.json"
MANIFEST = ROOT / "experiments" / "hgd1" / "source-manifest.json"
SOURCE = Path(__file__).resolve()
ARCHIVE = ROOT / "artifacts" / "hgd1-source" / "daily_88101_2025.zip"
PROTOCOL_COMMIT = "550b08a"
SEEDS = tuple(range(701, 721))
WORLDS_PER_SEED = 250
BOOTSTRAP_SEED = 20260809
BOOTSTRAP_RESAMPLES = 10_000
SHIFTS = (5.0, 10.0, 20.0)
EVENT_THRESHOLD = 35.0
MAX_REFERENCE_KM = 100.0
MIN_MASS = 2.0


def sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def stable(*parts: object) -> str:
    return sha("|".join(map(str, parts)).encode())


def receipt(origin: str, claim: int, components: list[dict] | None = None,
            support: str = "supported") -> dict:
    return {"origin": origin, "claim": claim, "components": components or [], "support": support}


def component(component_id: str, members: list[str], low: float, high: float,
              true_weight: float | None = None) -> dict:
    return {"id": component_id, "members": tuple(members), "low": low, "high": high,
            "true": true_weight}


def _side_mass(records: list[dict], components: list[dict], weights: tuple[float, ...]) -> dict:
    by_origin = {}
    for item in records:
        by_origin.setdefault(item["origin"], item["claim"])
    independent = {origin: 1.0 for origin in by_origin}
    shared = []
    for comp, weight in zip(components, weights):
        members = [origin for origin in comp["members"] if origin in by_origin]
        if len(members) < 2:
            continue
        for origin in members:
            independent[origin] = max(0.0, independent[origin] - weight)
        claims = [by_origin[origin] for origin in members]
        if claims.count(0) == claims.count(1):
            shared.append((None, weight))
        else:
            shared.append((int(claims.count(1) > claims.count(0)), weight))
    sides = {0: 0.0, 1: 0.0}
    for origin, weight in independent.items():
        sides[by_origin[origin]] += weight
    for claim, weight in shared:
        if claim is not None:
            sides[claim] += weight
    return sides


def assess(records: list[dict], components: list[dict], method: str = "interval") -> dict:
    if any(item["support"] != "supported" for item in records):
        return {"state": "ESCALATE", "answer": None, "massLower": 0.0, "massUpper": 0.0}
    origins = {item["origin"] for item in records}
    if method in {"head", "origin"}:
        selected = records if method == "head" else list({item["origin"]: item for item in records}.values())
        sides = {side: sum(item["claim"] == side for item in selected) for side in (0, 1)}
        mass = float(len(selected))
        if mass < MIN_MASS or sides[0] == sides[1]:
            return {"state": "ABSTAIN", "answer": None, "massLower": mass, "massUpper": mass}
        return {"state": "ANSWER", "answer": int(sides[1] > sides[0]),
                "massLower": mass, "massUpper": mass}
    if method == "family":
        fixed = [component(c["id"], list(c["members"]), 1.0, 1.0, 1.0) for c in components]
        components = fixed
    elif method == "midpoint":
        components = [component(c["id"], list(c["members"]),
                                (c["low"] + c["high"]) / 2,
                                (c["low"] + c["high"]) / 2) for c in components]
    corners = list(itertools.product(*[(c["low"], c["high"]) for c in components])) or [()]
    masses = [_side_mass(records, components, corner) for corner in corners]
    lower = {side: min(m[side] for m in masses) for side in (0, 1)}
    upper = {side: max(m[side] for m in masses) for side in (0, 1)}
    mass_lower = min(sum(m.values()) for m in masses)
    mass_upper = max(sum(m.values()) for m in masses)
    if mass_lower < MIN_MASS:
        return {"state": "ABSTAIN", "answer": None, "massLower": mass_lower,
                "massUpper": mass_upper}
    if lower[1] > upper[0]:
        answer = 1
    elif lower[0] > upper[1]:
        answer = 0
    else:
        return {"state": "ABSTAIN", "answer": None, "massLower": mass_lower,
                "massUpper": mass_upper}
    return {"state": "ANSWER", "answer": answer, "massLower": mass_lower,
            "massUpper": mass_upper}


def synthetic_world(rng: random.Random, seed: int, index: int) -> dict:
    truth = rng.randint(0, 1)
    honest = [truth if rng.random() < 0.85 else 1 - truth for _ in range(8)]
    adverse = truth if rng.random() < 0.25 else 1 - truth
    return {"id": f"s{seed}-w{index}", "truth": truth, "honest": honest, "adverse": adverse}


def synthetic_variant(base: dict, variant: str) -> tuple[list[dict], list[dict], float]:
    origins = [stable(base["id"], "sensor", i) for i in range(8)]
    claims = list(base["honest"])
    comps = []
    support = "supported"
    if variant == "duplicate_origin_8":
        origins = [origins[0]] * 8
    elif variant == "shared_station_8":
        comps = [component("station", origins, 1.0, 1.0, 1.0)]
    elif variant == "two_station_4x4":
        comps = [component("station-a", origins[:4], 1.0, 1.0, 1.0),
                 component("station-b", origins[4:], 1.0, 1.0, 1.0)]
    elif variant == "partial_calibration_8":
        comps = [component("calibration", origins, 0.4, 0.6, 0.5)]
    elif variant == "nested_station_model":
        comps = [component("station", origins[:4], 0.3, 0.5, 0.4),
                 component("model", origins, 0.2, 0.4, 0.3)]
    elif variant == "unknown_overlap":
        support = "unknown"
    elif variant == "forged_separation":
        comps = []
    elif variant == "common_mode_flip":
        claims = [1 - base["truth"]] * 8
        comps = [component("station", origins, 1.0, 1.0, 1.0)]
    records = [receipt(origin, claim, support=support) for origin, claim in zip(origins, claims)]
    adverse_origin = stable(base["id"], "adverse")
    records.append(receipt(adverse_origin, base["adverse"], support=support))
    unique = len(set(origins + [adverse_origin]))
    true_reduction = sum((c["true"] or 0) * (len(set(c["members"])) - 1) for c in comps)
    true_mass = max(1.0, unique - true_reduction)
    return records, comps, true_mass


def run_synthetic() -> tuple[dict, list[tuple[int, int]]]:
    variants = ("independent_8", "duplicate_origin_8", "shared_station_8", "two_station_4x4",
                "partial_calibration_8", "nested_station_model", "unknown_overlap",
                "forged_separation", "common_mode_flip")
    methods = ("head", "origin", "family", "midpoint", "interval")
    totals = {v: {m: defaultdict(float) for m in methods} for v in variants}
    paired = []
    for seed in SEEDS:
        rng = random.Random(seed)
        for index in range(WORLDS_PER_SEED):
            base = synthetic_world(rng, seed, index)
            for variant in variants:
                records, comps, true_mass = synthetic_variant(base, variant)
                outcomes = {method: assess(records, comps, method) for method in methods}
                for method, outcome in outcomes.items():
                    metric = totals[variant][method]
                    metric["worlds"] += 1
                    metric["answered"] += outcome["state"] == "ANSWER"
                    metric["abstain"] += outcome["state"] == "ABSTAIN"
                    metric["escalate"] += outcome["state"] == "ESCALATE"
                    metric["errors"] += outcome["state"] == "ANSWER" and outcome["answer"] != base["truth"]
                    metric["width"] += outcome["massUpper"] - outcome["massLower"]
                    metric["covered"] += outcome["massLower"] <= true_mass <= outcome["massUpper"]
                    metric["mass_lower"] += outcome["massLower"]
                    metric["mass_upper"] += outcome["massUpper"]
                if variant == "common_mode_flip":
                    paired.append((int(outcomes["interval"]["state"] == "ANSWER" and
                                       outcomes["interval"]["answer"] != base["truth"]),
                                   int(outcomes["head"]["state"] == "ANSWER" and
                                       outcomes["head"]["answer"] != base["truth"])))
    metrics = {}
    for variant in variants:
        metrics[variant] = {}
        for method in methods:
            x = totals[variant][method]; worlds = x["worlds"]
            metrics[variant][method] = {
                "worlds": int(worlds), "answered_coverage": x["answered"] / worlds,
                "false_confident_error": x["errors"] / worlds,
                "conditional_error": x["errors"] / x["answered"] if x["answered"] else None,
                "abstention_rate": x["abstain"] / worlds,
                "escalation_rate": x["escalate"] / worlds,
                "true_mass_interval_coverage": x["covered"] / worlds,
                "mean_interval_width": x["width"] / worlds,
                "mean_mass_lower": x["mass_lower"] / worlds,
                "mean_mass_upper": x["mass_upper"] / worlds,
            }
    return metrics, paired


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a); lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0088 * 2 * math.asin(math.sqrt(h))


def load_epa_cases() -> tuple[list[dict], dict]:
    manifest = json.loads(MANIFEST.read_text())
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() != manifest["archiveSha256"]:
        raise RuntimeError("EPA archive hash does not match frozen manifest")
    groups = defaultdict(dict); coords = {}
    with zipfile.ZipFile(ARCHIVE) as archive, archive.open(manifest["memberName"]) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
        for row in reader:
            try:
                value = float(row["Arithmetic Mean"]); count = int(row["Observation Count"])
                lat, lon = float(row["Latitude"]), float(row["Longitude"])
            except (TypeError, ValueError):
                continue
            if count <= 0 or not math.isfinite(value):
                continue
            site = (row["State Code"], row["County Code"], row["Site Num"])
            context = (row["Date Local"], row["Sample Duration"], row["Units of Measure"])
            key = context + site
            poc = str(row["POC"])
            candidate = (tuple(row.values()), value)
            if poc not in groups[key] or candidate[0] < groups[key][poc][0]:
                groups[key][poc] = candidate
            coords[site] = (lat, lon)
    summaries = {key: {poc: item[1] for poc, item in pocs.items()} for key, pocs in groups.items()}
    contexts = defaultdict(dict)
    for key, pocs in summaries.items():
        contexts[key[:3]][key[3:]] = pocs
    collocated_sites = sorted({key[3:] for key, pocs in summaries.items() if len(pocs) >= 2})
    development_site = collocated_sites[0]
    neighbor_order = {}
    sites = sorted(coords)
    for site in collocated_sites:
        candidates = sorted((haversine(coords[site], coords[other]), other)
                            for other in sites if other != site)
        neighbor_order[site] = [(distance, other) for distance, other in candidates
                                if distance <= MAX_REFERENCE_KM]
    cases = []
    for context, site_map in sorted(contexts.items()):
        for site, pocs in sorted(site_map.items()):
            if len(pocs) < 2 or site == development_site:
                continue
            reference = next(((d, other, site_map[other]) for d, other in neighbor_order.get(site, [])
                              if other in site_map), None)
            if reference is None:
                continue
            distance, ref_site, ref_pocs = reference
            cases.append({"context": context, "site": site, "pocs": pocs,
                          "referenceSite": ref_site, "referencePocs": ref_pocs,
                          "distanceKm": distance})
    structure = {"archive_rows": sum(len(pocs) for pocs in summaries.values()),
                 "site_day_groups": len(summaries), "collocated_sites": len(collocated_sites),
                 "development_site": list(development_site), "confirmatory_cases": len(cases)}
    return cases, structure


def binary_vote(values: list[float]) -> list[int]:
    return [int(value >= EVENT_THRESHOLD) for value in values]


def observational_outcome(case: dict, shift: float, method: str) -> tuple[str, int | None, int]:
    collocated = [value + shift for value in case["pocs"].values()]
    reference = list(case["referencePocs"].values())
    if method in {"head", "origin"}:
        votes = binary_vote(collocated + reference); mass = len(votes)
    else:
        votes = binary_vote([statistics.median(collocated), statistics.median(reference)]); mass = 2
    if mass < MIN_MASS or votes.count(0) == votes.count(1):
        return "ABSTAIN", None, mass
    return "ANSWER", int(votes.count(1) > votes.count(0)), mass


def run_observational() -> tuple[dict, dict]:
    cases, structure = load_epa_cases()
    methods = ("head", "origin", "family", "correlation", "midpoint", "interval")
    totals = {shift: {method: defaultdict(float) for method in methods} for shift in SHIFTS}
    by_duration = {shift: defaultdict(lambda: defaultdict(lambda: defaultdict(float))) for shift in SHIFTS}
    for case in cases:
        unchanged = list(case["pocs"].values()) + list(case["referencePocs"].values())
        target = int(statistics.median(unchanged) >= EVENT_THRESHOLD)
        duration = case["context"][1]
        for shift in SHIFTS:
            for method in methods:
                state, answer, _ = observational_outcome(case, shift, method)
                for bucket in (totals[shift][method], by_duration[shift][duration][method]):
                    bucket["cases"] += 1; bucket["answered"] += state == "ANSWER"
                    bucket["errors"] += state == "ANSWER" and answer != target
                    bucket["abstain"] += state == "ABSTAIN"
    def finish(bucket):
        return {"cases": int(bucket["cases"]), "answered_coverage": bucket["answered"] / bucket["cases"],
                "false_confident_error": bucket["errors"] / bucket["cases"],
                "conditional_error": bucket["errors"] / bucket["answered"] if bucket["answered"] else None,
                "abstention_rate": bucket["abstain"] / bucket["cases"]}
    metrics = {str(int(shift)): {method: finish(totals[shift][method]) for method in methods}
               for shift in SHIFTS}
    durations = {str(int(shift)): {duration: {method: finish(bucket) for method, bucket in methods_map.items()}
                                  for duration, methods_map in by_duration[shift].items()}
                 for shift in SHIFTS}
    return {"pooled": metrics, "by_sample_duration": durations}, structure


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values); pos = (len(ordered) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    return ordered[lo] if lo == hi else ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def bootstrap_delta(pairs: list[tuple[int, int]]) -> list[float]:
    rng = random.Random(BOOTSTRAP_SEED); values = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        values.append(sum(a - b for a, b in sample) / len(sample))
    return [percentile(values, 0.025), percentile(values, 0.975)]


def run() -> tuple[dict, dict]:
    started = time.perf_counter()
    synthetic, pairs = run_synthetic()
    observational, structure = run_observational()
    ci = bootstrap_delta(pairs)
    partial = synthetic["partial_calibration_8"]["interval"]
    independent = synthetic["independent_8"]["interval"]
    h = {
        "HGD-1a": (assess([receipt("r", 1)] * 8, [], "interval")["massLower"] == 1.0 and
                    assess([receipt(f"r{i}", i % 2) for i in range(8)], [], "interval")["massLower"] == 8.0),
        "HGD-1b": partial["true_mass_interval_coverage"] >= 0.95,
        "HGD-1c": partial["mean_interval_width"] < 2.0,
        "HGD-1d": synthetic["unknown_overlap"]["interval"]["escalation_rate"] == 1.0,
        "HGD-1e": ci[1] <= -0.10,
        "HGD-1f": independent["mean_mass_lower"] >= 8.0 * 0.95,
        "HGD-1g": all(
            observational["pooled"][str(int(shift))]["interval"]["answered_coverage"] >= 0.25 and
            observational["pooled"][str(int(shift))]["interval"]["false_confident_error"] <=
            observational["pooled"][str(int(shift))]["head"]["false_confident_error"]
            for shift in SHIFTS
        ) and any(
            observational["pooled"][str(int(shift))]["head"]["false_confident_error"] -
            observational["pooled"][str(int(shift))]["interval"]["false_confident_error"] >= 0.05
            for shift in SHIFTS
        ),
    }
    h["primary_claim"] = all(h.values())
    scientific = {
        "schema": "minority-prophet.hgd1.scientific-result.v1", "experiment": "HGD-1",
        "protocol_commit": PROTOCOL_COMMIT, "implementation_commit": git_head(),
        "hashes": {"protocol": file_sha(PROTOCOL), "schema": file_sha(SCHEMA),
                   "vectors": file_sha(VECTORS), "manifest": file_sha(MANIFEST), "runner": file_sha(SOURCE)},
        "configuration": {"seeds": list(SEEDS), "worlds_per_seed": WORLDS_PER_SEED,
                          "bootstrap_seed": BOOTSTRAP_SEED, "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                          "shifts": list(SHIFTS), "threshold": EVENT_THRESHOLD,
                          "max_reference_km": MAX_REFERENCE_KM, "minimum_mass": MIN_MASS},
        "synthetic": synthetic, "common_mode_error_delta_interval_minus_head_95ci": ci,
        "observational": observational, "observational_structure": structure,
        "hypotheses": h,
        "claim_boundary": "Declared-dependence and injected-failure evidence only; no hidden-cause discovery, historical measurement truth, or authority."
    }
    timing = {"schema": "minority-prophet.hgd1.timing.v1", "elapsed_seconds": time.perf_counter() - started,
              "environment": {"python": sys.version, "platform": platform.platform(),
                              "pid": os.getpid()}}
    return scientific, timing


def main() -> None:
    scientific, timing = run()
    print(json.dumps(scientific, sort_keys=True, separators=(",", ":")))
    print(json.dumps(timing, sort_keys=True, separators=(",", ":")), file=sys.stderr)


if __name__ == "__main__":
    main()
