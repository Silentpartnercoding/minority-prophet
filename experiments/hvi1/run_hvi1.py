"""HVI-1 frozen confirmatory runner.

Configuration and hypotheses are fixed in experiments/HVI-1-PREREGISTRATION.md.
This module intentionally exposes no confirmatory tuning arguments.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import random
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "experiments" / "HVI-1-PREREGISTRATION.md"
SCHEMA = ROOT / "experiments" / "hvi1" / "independence-receipt.schema.json"
VECTORS = ROOT / "experiments" / "hvi1" / "conformance-vectors.json"
SOURCE = Path(__file__).resolve()
PROTOCOL_COMMIT = "53d5cfd7d5cc918bdb05f6f11a40e5fd038f10fe"
SEEDS = tuple(range(401, 421))
BASE_WORLDS_PER_SEED = 250
BOOTSTRAP_SEED = 20260807
BOOTSTRAP_RESAMPLES = 10_000
HONEST_DOMAINS = 6
HONEST_RELIABILITY = 0.85
ADVERSARY_RELIABILITY = 0.25
VARIANTS = (
    "single", "alias_2", "alias_8", "alias_32", "key_rotation_8",
    "service_split_8", "self_verified_8", "unknown_control_8",
    "partial_shared_8", "genuine_8",
)
MULTIPLICITY_VARIANTS = (
    "alias_2", "alias_8", "alias_32", "key_rotation_8", "service_split_8",
)
METHODS = (
    "head_count", "unique_key", "unique_identity", "score_mean",
    "score_median", "score_clipped_median", "control_domain",
)


def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def stable_digest(*parts: object) -> str:
    return digest_bytes("|".join(map(str, parts)).encode())


def make_receipt(*, base_id: str, index: int, claim: int, producer_domain: str | None,
                 verifier_domain: str, status: str = "supported", subject: str | None = None,
                 key: str | None = None, service: str | None = None,
                 self_verified: bool = False) -> dict:
    subject_id = subject or f"subject:{base_id}:{index}"
    key_id = key or f"key:{base_id}:{index}"
    service_id = service or f"service:{base_id}:{index}"
    verifier_id = f"verifier:{base_id}:{index}"
    actual_verifier_domain = producer_domain if self_verified else verifier_domain
    support = None if status != "supported" else stable_digest("controller", base_id, index)
    return {
        "schema": "minority-prophet.independence-receipt.v1",
        "receiptId": f"receipt:{base_id}:{index}",
        "claim": {"propositionId": f"proposition:{base_id}", "value": claim},
        "evidence": {
            "digest": stable_digest("evidence", base_id, index, claim),
            "producerSubject": subject_id,
        },
        "producer": {"subjectId": subject_id, "keyId": key_id, "serviceId": service_id},
        "verifier": {
            "subjectId": verifier_id,
            "keyId": f"verifier-key:{base_id}:{index}",
            "serviceId": f"verifier-service:{base_id}:{index}",
        },
        "controllerAssertions": [
            {
                "subjectId": subject_id,
                "controlDomainId": producer_domain,
                "status": status,
                "supportDigest": support,
            },
            {
                "subjectId": verifier_id,
                "controlDomainId": actual_verifier_domain,
                "status": "supported",
                "supportDigest": stable_digest("verifier-controller", base_id, index),
            },
        ],
        "_hiddenProducerDomain": producer_domain,
        "_score": 0.90,
    }


def generate_base(rng: random.Random, seed: int, world_index: int) -> dict:
    truth = rng.randint(0, 1)
    honest_claims = [truth if rng.random() < HONEST_RELIABILITY else 1 - truth
                     for _ in range(HONEST_DOMAINS)]
    adversary_claim = truth if rng.random() < ADVERSARY_RELIABILITY else 1 - truth
    return {
        "id": f"s{seed}-w{world_index}",
        "truth": truth,
        "honestClaims": honest_claims,
        "adversaryClaim": adversary_claim,
    }


def materialize(base: dict, variant: str) -> list[dict]:
    receipts: list[dict] = []
    base_id = base["id"] + ":" + variant
    for index, claim in enumerate(base["honestClaims"]):
        receipts.append(make_receipt(
            base_id=base_id, index=index, claim=claim,
            producer_domain=f"honest-domain:{index}", verifier_domain=f"honest-verifier:{index}",
        ))

    claim = base["adversaryClaim"]
    start = len(receipts)
    if variant == "single":
        count, domains = 1, ["adversary-domain"]
    elif variant == "alias_2":
        count, domains = 2, ["adversary-domain"] * 2
    elif variant in {"alias_8", "key_rotation_8", "service_split_8", "self_verified_8", "unknown_control_8"}:
        count, domains = 8, ["adversary-domain"] * 8
    elif variant == "alias_32":
        count, domains = 32, ["adversary-domain"] * 32
    elif variant == "partial_shared_8":
        count, domains = 8, [f"adversary-domain:{i % 2}" for i in range(8)]
    elif variant == "genuine_8":
        count, domains = 8, [f"genuine-domain:{i}" for i in range(8)]
    else:
        raise ValueError(f"unknown variant: {variant}")

    for offset in range(count):
        index = start + offset
        domain = domains[offset]
        kwargs = {}
        if variant == "key_rotation_8":
            kwargs.update(subject="adversary-subject", service="adversary-service")
        elif variant == "service_split_8":
            kwargs.update(subject="adversary-subject")
        if variant == "unknown_control_8":
            kwargs.update(producer_domain=None, status="unknown")
        else:
            kwargs.update(producer_domain=domain)
        receipts.append(make_receipt(
            base_id=base_id, index=index, claim=claim,
            verifier_domain=f"adversary-verifier:{offset}",
            self_verified=variant == "self_verified_8", **kwargs,
        ))
    return receipts


def controller_assertions(receipt: dict) -> tuple[dict, dict]:
    by_subject = {item["subjectId"]: item for item in receipt["controllerAssertions"]}
    return by_subject[receipt["producer"]["subjectId"]], by_subject[receipt["verifier"]["subjectId"]]


def group_receipts(receipts: list[dict], method: str) -> tuple[str, list[list[dict]]]:
    if method == "control_domain":
        grouped: dict[str, list[dict]] = defaultdict(list)
        for receipt in receipts:
            producer, verifier = controller_assertions(receipt)
            if producer["status"] in {"unknown", "conflicting"}:
                return "ESCALATE", []
            if producer["status"] != "supported" or verifier["status"] != "supported":
                continue
            if producer["controlDomainId"] == verifier["controlDomainId"]:
                continue
            grouped[producer["controlDomainId"]].append(receipt)
        return "ASSESS", list(grouped.values())
    if method == "unique_key":
        key = lambda receipt: receipt["producer"]["keyId"]
    elif method == "unique_identity":
        key = lambda receipt: receipt["producer"]["subjectId"]
    else:
        key = lambda receipt: receipt["receiptId"]
    grouped = defaultdict(list)
    for receipt in receipts:
        grouped[key(receipt)].append(receipt)
    return "ASSESS", list(grouped.values())


def answer(receipts: list[dict], method: str) -> dict:
    state, groups = group_receipts(receipts, method)
    if state == "ESCALATE":
        return {"state": state, "answer": None, "mass": 0}
    representatives = [group[0] for group in groups]
    if method in {"score_mean", "score_median", "score_clipped_median"}:
        if method == "score_clipped_median" and len(representatives) >= 10:
            ordered = sorted(representatives, key=lambda item: (item["_score"], item["receiptId"]))
            trim = math.floor(len(ordered) * 0.10)
            representatives = ordered[trim:len(ordered) - trim]
        scores = {side: [item["_score"] for item in representatives if item["claim"]["value"] == side]
                  for side in (0, 1)}
        if method == "score_mean":
            mass = {side: statistics.mean(values) if values else 0.0 for side, values in scores.items()}
        else:
            mass = {side: statistics.median(values) if values else 0.0 for side, values in scores.items()}
        # Scalar summaries require support multiplicity to break equal valid-score ties.
        weighted = {side: mass[side] * len(scores[side]) for side in (0, 1)}
    else:
        weighted = {side: sum(1 for item in representatives if item["claim"]["value"] == side)
                    for side in (0, 1)}
    if weighted[0] == weighted[1]:
        return {"state": "ABSTAIN", "answer": None, "mass": len(groups)}
    return {"state": "ANSWER", "answer": int(weighted[1] > weighted[0]), "mass": len(groups)}


def hidden_domain_count(receipts: list[dict]) -> int:
    return len({item["_hiddenProducerDomain"] for item in receipts
                if item["_hiddenProducerDomain"] is not None})


def possible_false_units(receipts: list[dict]) -> int:
    return max(0, len(receipts) - hidden_domain_count(receipts))


def evaluate() -> tuple[dict, dict]:
    totals = {variant: {method: defaultdict(float) for method in METHODS} for variant in VARIANTS}
    base_records: list[dict] = []
    timings = {method: 0.0 for method in METHODS}
    worlds = 0

    for seed in SEEDS:
        rng = random.Random(seed)
        for world_index in range(BASE_WORLDS_PER_SEED):
            base = generate_base(rng, seed, world_index)
            record = {"methods": {method: {"errors": 0, "answered": 0} for method in METHODS}}
            single_control_mass = None
            for variant in VARIANTS:
                receipts = materialize(base, variant)
                hidden = hidden_domain_count(receipts)
                possible_false = possible_false_units(receipts)
                variant_outcomes = {}
                for method in METHODS:
                    started = time.perf_counter()
                    outcome = answer(receipts, method)
                    variant_outcomes[method] = outcome
                    timings[method] += time.perf_counter() - started
                    metric = totals[variant][method]
                    metric["worlds"] += 1
                    metric["escalations"] += outcome["state"] == "ESCALATE"
                    metric["abstentions"] += outcome["state"] == "ABSTAIN"
                    metric["answered"] += outcome["state"] == "ANSWER"
                    metric["errors"] += outcome["state"] == "ANSWER" and outcome["answer"] != base["truth"]
                    metric["root_mass_total"] += outcome["mass"]
                    excess = max(0, outcome["mass"] - hidden)
                    metric["false_units"] += excess
                    metric["possible_false_units"] += possible_false
                    if method == "control_domain":
                        metric["retained_domains"] += min(outcome["mass"], hidden)
                        metric["hidden_domains"] += hidden
                        if variant == "single":
                            single_control_mass = outcome["mass"]
                        if variant in MULTIPLICITY_VARIANTS:
                            metric["representation_mass_delta"] += abs(outcome["mass"] - single_control_mass)
                if variant_outcomes["control_domain"]["state"] == "ANSWER":
                    for method, outcome in variant_outcomes.items():
                        if outcome["state"] == "ANSWER":
                            record["methods"][method]["answered"] += 1
                            record["methods"][method]["errors"] += outcome["answer"] != base["truth"]
            base_records.append(record)
            worlds += 1

    summarized = {}
    for variant in VARIANTS:
        summarized[variant] = {}
        for method in METHODS:
            raw = totals[variant][method]
            summarized[variant][method] = {
                "worlds": int(raw["worlds"]),
                "decision_error": raw["errors"] / raw["answered"] if raw["answered"] else None,
                "abstention_rate": raw["abstentions"] / raw["worlds"],
                "escalation_rate": raw["escalations"] / raw["worlds"],
                "mean_root_mass": raw["root_mass_total"] / raw["worlds"],
                "false_independent_root_rate": raw["false_units"] / raw["possible_false_units"]
                if raw["possible_false_units"] else 0.0,
                "supported_root_retention": raw["retained_domains"] / raw["hidden_domains"]
                if raw["hidden_domains"] else None,
                "representation_mass_delta_total": int(raw["representation_mass_delta"]),
            }

    bootstrap = bootstrap_intervals(base_records, summarized)
    control = "control_domain"
    hypotheses = {
        "HVI-1a": all(summarized[v][control]["representation_mass_delta_total"] == 0
                      for v in MULTIPLICITY_VARIANTS),
        "HVI-1b": summarized["self_verified_8"][control]["mean_root_mass"] == HONEST_DOMAINS,
        "HVI-1c": summarized["unknown_control_8"][control]["escalation_rate"] == 1.0,
        "HVI-1d": summarized["genuine_8"][control]["supported_root_retention"] >= 0.95,
        "HVI-1e": bootstrap["false_root_delta_control_minus_unique_key_95ci"][1] <= -0.80,
        "HVI-1f": bootstrap["decision_error_delta_control_minus_best_baseline_95ci"][1] <= 0.02,
    }
    hypotheses["primary_claim"] = all(hypotheses.values())
    scientific = {
        "schema": "minority-prophet.hvi1.scientific-result.v1",
        "experiment": "HVI-1",
        "protocol_commit": PROTOCOL_COMMIT,
        "implementation_commit": git_head(),
        "hashes": {"protocol": file_digest(PROTOCOL), "schema": file_digest(SCHEMA),
                   "vectors": file_digest(VECTORS), "runner": file_digest(SOURCE)},
        "configuration": {
            "seeds": list(SEEDS), "base_worlds_per_seed": BASE_WORLDS_PER_SEED,
            "base_worlds": worlds, "matched_variants": list(VARIANTS),
            "bootstrap_seed": BOOTSTRAP_SEED, "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        },
        "metrics": summarized,
        "bootstrap": bootstrap,
        "hypotheses": hypotheses,
        "claim_boundary": "Synthetic declared-control conformance; no hidden-control discovery or authority.",
    }
    observational = {
        "schema": "minority-prophet.hvi1.observational-timing.v1",
        "environment": {"python": sys.version, "platform": platform.platform()},
        "mean_seconds_per_matched_world": {method: timings[method] / (worlds * len(VARIANTS))
                                            for method in METHODS},
    }
    return scientific, observational


def bootstrap_intervals(records: list[dict], summarized: dict) -> dict:
    rng = random.Random(BOOTSTRAP_SEED)
    false_delta: list[float] = []
    error_delta: list[float] = []
    # The false-root endpoint is deterministic across base-world claims because
    # matched variants change representation only. Preserve the registered
    # world bootstrap by resampling its per-world constant nonetheless.
    control_false = statistics.mean(
        summarized[v]["control_domain"]["false_independent_root_rate"]
        for v in MULTIPLICITY_VARIANTS
    )
    key_false = statistics.mean(
        summarized[v]["unique_key"]["false_independent_root_rate"]
        for v in MULTIPLICITY_VARIANTS
    )
    baseline_methods = [method for method in METHODS if method != "control_domain"]
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [records[rng.randrange(len(records))] for _ in range(len(records))]
        false_delta.append(control_false - key_false)
        control_errors = sum(item["methods"]["control_domain"]["errors"] for item in sample)
        control_answered = sum(item["methods"]["control_domain"]["answered"] for item in sample)
        control_rate = control_errors / control_answered
        baseline_rates = []
        for method in baseline_methods:
            errors = sum(item["methods"][method]["errors"] for item in sample)
            answered = sum(item["methods"][method]["answered"] for item in sample)
            baseline_rates.append(errors / answered)
        error_delta.append(control_rate - min(baseline_rates))
    return {
        "false_root_delta_control_minus_unique_key_95ci": interval(false_delta),
        "decision_error_delta_control_minus_best_baseline_95ci": interval(error_delta),
    }


def interval(values: list[float]) -> list[float]:
    values = sorted(values)
    return [quantile(values, 0.025), quantile(values, 0.975)]


def quantile(values: list[float], probability: float) -> float:
    position = (len(values) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return values[lower]
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def main() -> None:
    scientific, observational = evaluate()
    json.dump(scientific, sys.stdout, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")
    json.dump(observational, sys.stderr, sort_keys=True, separators=(",", ":"))
    sys.stderr.write("\n")


if __name__ == "__main__":
    main()
