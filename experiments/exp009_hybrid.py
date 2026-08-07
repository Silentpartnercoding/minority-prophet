"""Run the preregistered EXP009 selective-provenance experiment.

The policy, seeds, sample size, bootstrap seed, and thresholds are frozen in
``EXP009-HYBRID-PREREGISTRATION.md``.  This runner deliberately has no command
line knobs for changing confirmatory parameters.
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
from collections.abc import Callable
from pathlib import Path

from experiments.exp008_shootout import (
    K,
    accu_lite,
    cluster_vote,
    dawid_skene,
    gen_world,
    infer_parents,
    majority,
    truthfinder,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "experiments" / "EXP009-HYBRID-PREREGISTRATION.md"
SOURCE = Path(__file__).resolve()
GENERATOR_SOURCE = ROOT / "experiments" / "exp008_shootout.py"
SEEDS = tuple(range(301, 321))
WORLDS_PER_SEED = 200
BOOTSTRAP_SEED = 20260806
BOOTSTRAP_RESAMPLES = 10_000
MARGIN_THRESHOLD = 3
PROTOCOL_COMMIT = "c8c10f321393c711d861c20b327c1c4edf511a5c"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def root_vote_details(src: list[dict], parent: dict[int, int]) -> tuple[list[int], list[int], list[bool]]:
    memo: dict[int, int] = {}

    def root(item: int) -> int:
        if item not in memo:
            memo[item] = item if item not in parent else root(parent[item])
        return memo[item]

    answers: list[int] = []
    margins: list[int] = []
    ties: list[bool] = []
    for proposition in range(K):
        sides = {0: set(), 1: set()}
        for source in src:
            sides[source["ans"][proposition]].add(root(source["id"]))
        count0, count1 = len(sides[0]), len(sides[1])
        answers.append(1 if count1 > count0 else 0)
        margins.append(abs(count1 - count0))
        ties.append(count0 == count1)
    return answers, margins, ties


def selective(maj: list[int], root_answer: list[int], margins: list[int], ties: list[bool]) -> list[int]:
    return [
        root_answer[k]
        if not ties[k] and root_answer[k] != maj[k] and margins[k] >= MARGIN_THRESHOLD
        else maj[k]
        for k in range(K)
    ]


def empty_counts() -> dict[str, int]:
    return {
        "correct": 0,
        "decisions": 0,
        "minority_correct": 0,
        "minority_cases": 0,
        "false_reversals": 0,
        "overrides": 0,
        "correct_overrides": 0,
    }


def score(truth: list[int], maj: list[int], answer: list[int]) -> dict[str, int]:
    counts = empty_counts()
    for k in range(K):
        is_correct = answer[k] == truth[k]
        majority_correct = maj[k] == truth[k]
        changed = answer[k] != maj[k]
        counts["correct"] += int(is_correct)
        counts["decisions"] += 1
        counts["minority_cases"] += int(not majority_correct)
        counts["minority_correct"] += int(not majority_correct and is_correct)
        counts["false_reversals"] += int(majority_correct and changed and not is_correct)
        counts["overrides"] += int(changed)
        counts["correct_overrides"] += int(changed and is_correct)
    return counts


def add_counts(total: dict[str, int], value: dict[str, int]) -> None:
    for key in total:
        total[key] += value[key]


def divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def metrics(counts: dict[str, int]) -> dict[str, float | int]:
    return {
        **counts,
        "accuracy": divide(counts["correct"], counts["decisions"]),
        "copied_minority_recovery": divide(counts["minority_correct"], counts["minority_cases"]),
        "false_reversal_rate": divide(counts["false_reversals"], counts["decisions"]),
        "override_rate": divide(counts["overrides"], counts["decisions"]),
        "override_precision": divide(counts["correct_overrides"], counts["overrides"]),
    }


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def bootstrap_attack(worlds: list[dict[str, dict[str, int]]]) -> dict[str, list[float]]:
    rng = random.Random(BOOTSTRAP_SEED)
    accuracy_delta: list[float] = []
    recovery_delta: list[float] = []
    false_reversal: list[float] = []
    size = len(worlds)
    for _ in range(BOOTSTRAP_RESAMPLES):
        maj = empty_counts()
        challenger = empty_counts()
        for _ in range(size):
            world = worlds[rng.randrange(size)]
            add_counts(maj, world["majority"])
            add_counts(challenger, world["selective_inferred"])
        maj_metrics = metrics(maj)
        challenger_metrics = metrics(challenger)
        accuracy_delta.append(challenger_metrics["accuracy"] - maj_metrics["accuracy"])
        recovery_delta.append(
            challenger_metrics["copied_minority_recovery"]
            - maj_metrics["copied_minority_recovery"]
        )
        false_reversal.append(challenger_metrics["false_reversal_rate"])
    return {
        "accuracy_delta_95ci": [percentile(accuracy_delta, 0.025), percentile(accuracy_delta, 0.975)],
        "recovery_delta_95ci": [percentile(recovery_delta, 0.025), percentile(recovery_delta, 0.975)],
        "false_reversal_rate_95ci": [percentile(false_reversal, 0.025), percentile(false_reversal, 0.975)],
    }


def run() -> tuple[dict, dict]:
    method_functions: dict[str, Callable[[list[dict]], list[int]]] = {
        "majority": majority,
        "dawid_skene": dawid_skene,
        "truthfinder": truthfinder,
        "accu_lite": accu_lite,
        "cluster_vote": cluster_vote,
    }
    regimes: dict[str, dict] = {}
    timing: dict[str, dict[str, float]] = {}
    attack_worlds: list[dict[str, dict[str, int]]] = []

    for attack in (False, True):
        regime_name = "attack" if attack else "no_attack"
        totals = {name: empty_counts() for name in (*method_functions, "root_inferred", "root_declared", "selective_inferred", "selective_declared")}
        elapsed = {name: 0.0 for name in totals}
        escalation_count = 0
        world_records: list[dict[str, dict[str, int]]] = []

        for seed in SEEDS:
            rng = random.Random(seed)
            for _ in range(WORLDS_PER_SEED):
                truth, src = gen_world(rng, attack)
                world_scores: dict[str, dict[str, int]] = {}

                started = time.perf_counter()
                maj = majority(src)
                elapsed["majority"] += time.perf_counter() - started
                world_scores["majority"] = score(truth, maj, maj)

                for name, function in method_functions.items():
                    if name == "majority":
                        continue
                    started = time.perf_counter()
                    answer = function(src)
                    elapsed[name] += time.perf_counter() - started
                    world_scores[name] = score(truth, maj, answer)

                started = time.perf_counter()
                inferred_parent = infer_parents(src)
                inferred, inferred_margins, inferred_ties = root_vote_details(src, inferred_parent)
                elapsed["root_inferred"] += time.perf_counter() - started

                started = time.perf_counter()
                declared_parent = {
                    source["id"]: source["true_parent"]
                    for source in src
                    if source["true_parent"] is not None
                }
                declared, declared_margins, declared_ties = root_vote_details(src, declared_parent)
                elapsed["root_declared"] += time.perf_counter() - started

                started = time.perf_counter()
                selected_inferred = selective(maj, inferred, inferred_margins, inferred_ties)
                elapsed["selective_inferred"] += time.perf_counter() - started
                started = time.perf_counter()
                selected_declared = selective(maj, declared, declared_margins, declared_ties)
                elapsed["selective_declared"] += time.perf_counter() - started

                world_scores["root_inferred"] = score(truth, maj, inferred)
                world_scores["root_declared"] = score(truth, maj, declared)
                world_scores["selective_inferred"] = score(truth, maj, selected_inferred)
                world_scores["selective_declared"] = score(truth, maj, selected_declared)
                escalation_count += sum(
                    1
                    for k in range(K)
                    if inferred[k] != maj[k]
                    and (inferred_ties[k] or inferred_margins[k] < MARGIN_THRESHOLD)
                )

                for name, counts in world_scores.items():
                    add_counts(totals[name], counts)
                world_records.append(world_scores)

        regimes[regime_name] = {
            "configuration": {
                "seeds": list(SEEDS),
                "worlds_per_seed": WORLDS_PER_SEED,
                "propositions_per_world": K,
                "decisions": len(SEEDS) * WORLDS_PER_SEED * K,
            },
            "methods": {name: metrics(value) for name, value in totals.items()},
            "execution_safety_diagnostic": {
                "escalation_rate": escalation_count / (len(SEEDS) * WORLDS_PER_SEED * K)
            },
        }
        timing[regime_name] = {
            name: elapsed[name] / (len(SEEDS) * WORLDS_PER_SEED) for name in elapsed
        }
        if attack:
            attack_worlds = world_records

    bootstrap = bootstrap_attack(attack_worlds)
    attack_metrics = regimes["attack"]["methods"]
    primary = attack_metrics["selective_inferred"]
    declared = attack_metrics["selective_declared"]
    verdicts = {
        "H9-1": bootstrap["accuracy_delta_95ci"][0] >= -0.010,
        "H9-2": bootstrap["false_reversal_rate_95ci"][1] <= 0.010,
        "H9-3": primary["copied_minority_recovery"] >= 0.015
        and bootstrap["recovery_delta_95ci"][0] > 0.0,
        "H9-4": declared["copied_minority_recovery"] >= 0.80
        and declared["false_reversal_rate"] <= 0.005,
    }
    verdicts["primary_claim"] = verdicts["H9-1"] and verdicts["H9-2"] and verdicts["H9-3"]

    scientific = {
        "schema": "minority-prophet.exp009.scientific-result.v1",
        "experiment": "EXP009",
        "protocol_commit": PROTOCOL_COMMIT,
        "implementation_commit": git_head(),
        "source_sha256": sha256(SOURCE),
        "generator_sha256": sha256(GENERATOR_SOURCE),
        "protocol_sha256": sha256(PROTOCOL),
        "configuration": {
            "seeds": list(SEEDS),
            "worlds_per_seed": WORLDS_PER_SEED,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "margin_threshold": MARGIN_THRESHOLD,
        },
        "regimes": regimes,
        "attack_bootstrap": bootstrap,
        "hypotheses": verdicts,
        "claim_boundary": "Frozen synthetic-model result; not external deployment evidence or authority.",
    }
    observational = {
        "schema": "minority-prophet.exp009.observational-timing.v1",
        "experiment": "EXP009",
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
        },
        "mean_seconds_per_world": timing,
        "note": "Timing is descriptive and excluded from byte-identity requirements.",
    }
    return scientific, observational


def main() -> None:
    scientific, observational = run()
    json.dump(scientific, sys.stdout, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")
    json.dump(observational, sys.stderr, sort_keys=True, separators=(",", ":"))
    sys.stderr.write("\n")


if __name__ == "__main__":
    main()
