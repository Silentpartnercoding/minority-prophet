"""Frozen HEO-1 confirmatory runner."""

from __future__ import annotations

import hashlib, json, math, platform, random, re, subprocess, sys, time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "experiments/HEO-1-PREREGISTRATION.md"
SCHEMA = ROOT / "experiments/heo1/derivation-receipt.schema.json"
VECTORS = ROOT / "experiments/heo1/conformance-vectors.json"
SOURCE = Path(__file__).resolve()
PROTOCOL_COMMIT = "cd1208bc0d628bf38a69a0d0b9f6940d500903f8"
SEEDS = tuple(range(501, 521)); WORLDS_PER_SEED = 250
BOOTSTRAP_SEED = 20260808; BOOTSTRAP_RESAMPLES = 10_000
VARIANTS = ("single_origin", "byte_copy_8", "paraphrase_8", "translation_8",
            "summary_8", "model_transform_8", "mixed_transform_32",
            "unknown_origin_8", "forged_parent_8", "genuine_origins_8")
TRANSFORMS = VARIANTS[1:7]
METHODS = ("head_count", "byte_digest", "controller_domain", "token_jaccard",
           "normalized_text", "evidence_origin")

def sha(data: bytes) -> str: return "sha256:" + hashlib.sha256(data).hexdigest()
def stable(*parts) -> str: return sha("|".join(map(str, parts)).encode())
def file_sha(path: Path) -> str: return sha(path.read_bytes())
def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

def base_world(rng: random.Random, seed: int, index: int) -> dict:
    truth = rng.randint(0, 1)
    honest = [truth if rng.random() < .85 else 1 - truth for _ in range(6)]
    adverse = truth if rng.random() < .25 else 1 - truth
    return {"id": f"s{seed}-w{index}", "truth": truth, "honest": honest, "adverse": adverse}

def text_for(kind: str, claim: int, index: int) -> str:
    core = "the observed proposition is " + ("supported" if claim else "opposed")
    forms = {
        "byte": core,
        "paraphrase": f"independent wording {index}: evidence says the proposition is {'supported' if claim else 'opposed'}",
        "translation": f"translation language {index}: {core}",
        "summary": f"summary {index}: {core}",
        "model": f"model rendering {index}: {core}",
    }
    return forms[kind]

def receipt(*, world: str, index: int, claim: int, controller: str,
            origin: str | None, relationship: str, status: str = "supported",
            text: str | None = None, artifact_digest: str | None = None) -> dict:
    content = text or text_for("byte", claim, index)
    return {
        "id": f"receipt:{world}:{index}", "claim": claim, "text": content,
        "artifactDigest": artifact_digest or stable("artifact", world, index, content),
        "producerControlDomain": controller, "relationship": relationship,
        "originDigest": origin, "parentDigest": origin if relationship != "origin" else None,
        "support": {"status": status, "receiptDigest": stable("support", world, index) if status == "supported" else None},
        "_hiddenOrigin": origin,
    }

def materialize(base: dict, variant: str) -> list[dict]:
    world = base["id"] + ":" + variant; out = []
    for i, claim in enumerate(base["honest"]):
        root = stable("honest-origin", base["id"], i)
        out.append(receipt(world=world, index=i, claim=claim, controller=f"honest-controller:{i}",
                           origin=root, relationship="origin"))
    start = 6; claim = base["adverse"]; adverse_root = stable("adverse-origin", base["id"])
    if variant == "single_origin": count, kind = 1, "byte"
    elif variant == "byte_copy_8": count, kind = 8, "byte"
    elif variant == "paraphrase_8": count, kind = 8, "paraphrase"
    elif variant == "translation_8": count, kind = 8, "translation"
    elif variant == "summary_8": count, kind = 8, "summary"
    elif variant == "model_transform_8": count, kind = 8, "model"
    elif variant == "mixed_transform_32": count, kind = 32, "mixed"
    else: count, kind = 8, "paraphrase"
    shared_byte_digest = stable("shared-byte-copy", base["id"], claim)
    for j in range(count):
        relationship = kind if kind != "mixed" else ("paraphrase", "translation", "summary", "model_transform")[j % 4]
        if relationship == "byte": relationship = "copy"
        text_kind = "byte" if relationship == "copy" else "model" if relationship == "model_transform" else relationship
        origin = adverse_root; status = "supported"
        if variant == "unknown_origin_8": origin, status = None, "unknown"
        elif variant == "forged_parent_8": origin, status = stable("unbound", base["id"], j), "conflicting"
        elif variant == "genuine_origins_8": origin = stable("genuine-origin", base["id"], j)
        out.append(receipt(
            world=world, index=start + j, claim=claim, controller=f"separate-controller:{j}",
            origin=origin, relationship="origin" if variant in {"single_origin", "genuine_origins_8"} else relationship,
            status=status, text=text_for(text_kind, claim, j),
            artifact_digest=shared_byte_digest if variant == "byte_copy_8" else None,
        ))
    return out

def normalize(text: str) -> str:
    tokens = re.findall(r"[a-z]+", text.lower())
    ignored = {"independent", "wording", "translation", "language", "summary", "model", "rendering"}
    return " ".join(token for token in tokens if token not in ignored)

def jaccard(a: str, b: str) -> float:
    left, right = set(re.findall(r"[a-z]+", a.lower())), set(re.findall(r"[a-z]+", b.lower()))
    return len(left & right) / len(left | right)

def groups(records: list[dict], method: str) -> tuple[str, list[list[dict]]]:
    if method == "evidence_origin":
        for item in records:
            if item["support"]["status"] != "supported" or not item["originDigest"]:
                return "ESCALATE", []
            if item["relationship"] != "origin" and item["parentDigest"] != item["originDigest"]:
                return "ESCALATE", []
        key = lambda item: item["originDigest"]
    elif method == "byte_digest": key = lambda item: item["artifactDigest"]
    elif method == "controller_domain": key = lambda item: item["producerControlDomain"]
    elif method == "normalized_text": key = lambda item: normalize(item["text"])
    elif method == "head_count": key = lambda item: item["id"]
    elif method == "token_jaccard":
        clusters = []
        for item in records:
            for cluster in clusters:
                if jaccard(item["text"], cluster[0]["text"]) >= .85:
                    cluster.append(item); break
            else: clusters.append([item])
        return "ASSESS", clusters
    else: raise ValueError(method)
    grouped = defaultdict(list)
    for item in records: grouped[key(item)].append(item)
    return "ASSESS", list(grouped.values())

def decide(records: list[dict], method: str) -> dict:
    state, clustered = groups(records, method)
    if state == "ESCALATE": return {"state": state, "answer": None, "mass": 0}
    votes = [cluster[0]["claim"] for cluster in clustered]
    if votes.count(0) == votes.count(1): return {"state": "ABSTAIN", "answer": None, "mass": len(clustered)}
    return {"state": "ANSWER", "answer": int(votes.count(1) > votes.count(0)), "mass": len(clustered)}

def hidden_roots(records: list[dict]) -> int:
    return len({item["_hiddenOrigin"] for item in records if item["_hiddenOrigin"]})

def run() -> tuple[dict, dict]:
    totals = {v: {m: defaultdict(float) for m in METHODS} for v in VARIANTS}
    paired = []; timing = {m: 0.0 for m in METHODS}
    for seed in SEEDS:
        rng = random.Random(seed)
        for wi in range(WORLDS_PER_SEED):
            base = base_world(rng, seed, wi); sample = {m: [0, 0] for m in METHODS}; baseline_mass = None
            for variant in VARIANTS:
                records = materialize(base, variant); hidden = hidden_roots(records); possible = max(0, len(records) - hidden); outcomes = {}
                for method in METHODS:
                    started = time.perf_counter(); outcome = decide(records, method); timing[method] += time.perf_counter() - started
                    outcomes[method] = outcome; metric = totals[variant][method]
                    metric["worlds"] += 1; metric["mass"] += outcome["mass"]
                    metric["escalate"] += outcome["state"] == "ESCALATE"; metric["abstain"] += outcome["state"] == "ABSTAIN"
                    metric["answered"] += outcome["state"] == "ANSWER"; metric["errors"] += outcome["state"] == "ANSWER" and outcome["answer"] != base["truth"]
                    metric["false"] += max(0, outcome["mass"] - hidden); metric["possible"] += possible
                    if method == "evidence_origin":
                        metric["retained"] += min(outcome["mass"], hidden); metric["hidden"] += hidden
                        if variant == "single_origin": baseline_mass = outcome["mass"]
                        if variant in TRANSFORMS: metric["delta"] += abs(outcome["mass"] - baseline_mass)
                if outcomes["evidence_origin"]["state"] == "ANSWER":
                    for method, outcome in outcomes.items():
                        if outcome["state"] == "ANSWER":
                            sample[method][1] += 1; sample[method][0] += outcome["answer"] != base["truth"]
            paired.append(sample)
    metrics = {}
    for variant in VARIANTS:
        metrics[variant] = {}
        for method in METHODS:
            x = totals[variant][method]
            metrics[variant][method] = {
                "worlds": int(x["worlds"]), "mean_root_mass": x["mass"] / x["worlds"],
                "decision_error": x["errors"] / x["answered"] if x["answered"] else None,
                "abstention_rate": x["abstain"] / x["worlds"], "escalation_rate": x["escalate"] / x["worlds"],
                "false_root_rate": x["false"] / x["possible"] if x["possible"] else 0.0,
                "origin_retention": x["retained"] / x["hidden"] if x["hidden"] else None,
                "transformation_mass_delta_total": int(x["delta"]),
            }
    boot = bootstrap(paired, metrics)
    h = {"HEO-1a": all(metrics[v]["evidence_origin"]["transformation_mass_delta_total"] == 0 for v in TRANSFORMS),
         "HEO-1b": metrics["unknown_origin_8"]["evidence_origin"]["escalation_rate"] == 1.0,
         "HEO-1c": metrics["forged_parent_8"]["evidence_origin"]["escalation_rate"] == 1.0,
         "HEO-1d": metrics["genuine_origins_8"]["evidence_origin"]["origin_retention"] >= .95,
         "HEO-1e": boot["false_root_delta_origin_minus_controller_95ci"][1] <= -.80,
         "HEO-1f": boot["decision_error_delta_origin_minus_best_comparator_95ci"][1] <= .02}
    h["primary_claim"] = all(h.values())
    scientific = {"schema": "minority-prophet.heo1.scientific-result.v1", "experiment": "HEO-1",
                  "protocol_commit": PROTOCOL_COMMIT, "implementation_commit": git_head(),
                  "hashes": {"protocol": file_sha(PROTOCOL), "schema": file_sha(SCHEMA), "vectors": file_sha(VECTORS), "runner": file_sha(SOURCE)},
                  "configuration": {"seeds": list(SEEDS), "worlds_per_seed": WORLDS_PER_SEED, "variants": list(VARIANTS), "bootstrap_seed": BOOTSTRAP_SEED, "bootstrap_resamples": BOOTSTRAP_RESAMPLES},
                  "metrics": metrics, "bootstrap": boot, "hypotheses": h,
                  "claim_boundary": "Synthetic supported-origin conformance; no hidden-source discovery, truth, or authority."}
    observed = {"schema": "minority-prophet.heo1.timing.v1", "environment": {"python": sys.version, "platform": platform.platform()},
                "mean_seconds_per_matched_world": {m: timing[m] / (len(SEEDS) * WORLDS_PER_SEED * len(VARIANTS)) for m in METHODS}}
    return scientific, observed

def bootstrap(records: list[dict], metrics: dict) -> dict:
    rng = random.Random(BOOTSTRAP_SEED); false_delta = []
    origin_false = sum(metrics[v]["evidence_origin"]["false_root_rate"] for v in TRANSFORMS) / len(TRANSFORMS)
    controller_false = sum(metrics[v]["controller_domain"]["false_root_rate"] for v in TRANSFORMS) / len(TRANSFORMS)
    deltas = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [records[rng.randrange(len(records))] for _ in range(len(records))]; false_delta.append(origin_false - controller_false)
        oe = sum(x["evidence_origin"][0] for x in sample); on = sum(x["evidence_origin"][1] for x in sample)
        baseline = min(sum(x[m][0] for x in sample) / sum(x[m][1] for x in sample) for m in METHODS if m != "evidence_origin")
        deltas.append(oe / on - baseline)
    return {"false_root_delta_origin_minus_controller_95ci": ci(false_delta), "decision_error_delta_origin_minus_best_comparator_95ci": ci(deltas)}

def ci(values):
    values = sorted(values)
    def q(p):
        pos = (len(values) - 1) * p; lo, hi = math.floor(pos), math.ceil(pos)
        return values[lo] if lo == hi else values[lo] + (values[hi] - values[lo]) * (pos - lo)
    return [q(.025), q(.975)]

def main():
    scientific, timing = run(); print(json.dumps(scientific, sort_keys=True, separators=(",", ":")))
    print(json.dumps(timing, sort_keys=True, separators=(",", ":")), file=sys.stderr)

if __name__ == "__main__": main()
