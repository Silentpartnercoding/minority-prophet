#!/usr/bin/env python3
"""EXP007A: preregistered optimizing adversary for the EXP003 synthetic model."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import sys
from pathlib import Path

VOCAB = 5000
SYN_OFFSET = 100000
TRAIN_SEED = 101
SEARCH_SEED = 7007
TRAIN_WORLDS = 80
HOLDOUT_SEEDS = tuple(range(201, 211))
HOLDOUT_WORLDS = 150
Params = tuple[float, float, float, float]


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def make_world(rng: random.Random, params: Params) -> dict[str, object]:
    paraphrase, false_citation, sybil, timing = params
    truth = rng.randint(0, 1)
    copy_pressure = rng.random() < 0.6
    origin_assertion = 1 - truth if copy_pressure else truth
    claims: list[dict[str, object]] = []

    def payload() -> set[int]:
        return set(rng.sample(range(VOCAB), 12))

    origin_time = 10.0 - 9.5 * timing
    claims.append({"id": 0, "t": origin_time, "assertion": origin_assertion,
                   "tokens": payload(), "cite": None, "true_parent": None})
    for _ in range(6):
        assertion = truth if rng.random() < 0.9 else 1 - truth
        claims.append({"id": len(claims), "t": 1.0 + rng.random() * 8,
                       "assertion": assertion, "tokens": payload(), "cite": None,
                       "true_parent": None})

    tree = [0]
    for _ in range(40):
        parent = claims[rng.choice(tree)]
        tokens = set(parent["tokens"])
        for _ in range(2):
            if tokens:
                tokens.discard(rng.choice(sorted(tokens)))
            tokens.add(rng.randrange(VOCAB))
        is_sybil = rng.random() < sybil
        paraphrase_rate = paraphrase + (1.0 - paraphrase) * (0.8 if is_sybil else 0.0)
        tokens = {token + SYN_OFFSET if rng.random() < paraphrase_rate else token
                  for token in tokens}
        if is_sybil:
            citation = None
            claim_time = origin_time + 0.2 + rng.random() * 3
        else:
            citation = (rng.randrange(1, 7) if rng.random() < false_citation
                        else parent["id"])
            claim_time = float(parent["t"]) + 0.5 + rng.random() * 5
        claim = {"id": len(claims), "t": claim_time,
                 "assertion": parent["assertion"], "tokens": tokens,
                 "cite": citation, "true_parent": parent["id"]}
        claims.append(claim)
        tree.append(int(claim["id"]))
    return {"truth": truth, "claims": claims}


def jaccard(left: set[int], right: set[int]) -> float:
    union = len(left | right)
    return len(left & right) / union if union else 0.0


def infer_parents(claims: list[dict[str, object]]) -> dict[int, int]:
    ordered = sorted(claims, key=lambda claim: float(claim["t"]))
    parents: dict[int, int] = {}
    for index, claim in enumerate(ordered):
        best = None
        best_score = 0.25
        for candidate in ordered[:index]:
            delta = float(claim["t"]) - float(candidate["t"])
            score = (0.45 * jaccard(set(claim["tokens"]), set(candidate["tokens"]))
                     + 0.25 * math.exp(-delta / 5.0)
                     + 0.30 * (claim["cite"] == candidate["id"]))
            if score > best_score:
                best, best_score = int(candidate["id"]), score
        if best is not None:
            parents[int(claim["id"])] = best
    return parents


def roots(claims: list[dict[str, object]], parents: dict[int, int]) -> dict[int, int]:
    memo: dict[int, int] = {}

    def root(claim_id: int) -> int:
        if claim_id not in memo:
            memo[claim_id] = claim_id if claim_id not in parents else root(parents[claim_id])
        return memo[claim_id]

    return {int(claim["id"]): root(int(claim["id"])) for claim in claims}


def verdict(claims: list[dict[str, object]], parents: dict[int, int]) -> int | None:
    root_map = roots(claims, parents)
    sides = {0: set(), 1: set()}
    for claim in claims:
        sides[int(claim["assertion"])].add(root_map[int(claim["id"])])
    total = len(sides[0]) + len(sides[1])
    probability = len(sides[1]) / total if total else 0.5
    return None if abs(probability - 0.5) < 0.02 else int(probability > 0.5)


def honest_margin(claims: list[dict[str, object]]) -> int:
    declared = {int(claim["id"]): int(claim["true_parent"])
                for claim in claims if claim["true_parent"] is not None}
    root_map = roots(claims, declared)
    sides = {0: set(), 1: set()}
    for claim in claims:
        sides[int(claim["assertion"])].add(root_map[int(claim["id"])])
    return abs(len(sides[1]) - len(sides[0]))


def evaluate(params: Params, seed: int, worlds: int, include_margins: bool = False) -> dict[str, object]:
    rng = random.Random(seed)
    correct = 0
    decided = 0
    incorrect_margins: list[int] = []
    correct_margins: list[int] = []
    for _ in range(worlds):
        world = make_world(rng, params)
        claims = world["claims"]
        decision = verdict(claims, infer_parents(claims))
        if decision is None:
            continue
        decided += 1
        is_correct = decision == world["truth"]
        correct += int(is_correct)
        if include_margins:
            (correct_margins if is_correct else incorrect_margins).append(honest_margin(claims))
    result: dict[str, object] = {
        "accuracy": round(correct / decided, 12) if decided else None,
        "abstentions": worlds - decided,
        "correct": correct,
        "decided": decided,
        "seed": seed,
        "worlds": worlds,
    }
    if include_margins:
        result["correct_margins"] = correct_margins
        result["incorrect_margins"] = incorrect_margins
    return result


def optimize(worlds: int = TRAIN_WORLDS) -> tuple[Params, list[dict[str, object]]]:
    rng = random.Random(SEARCH_SEED)
    history: list[dict[str, object]] = []
    seen: set[Params] = set()

    def score(params: Params, restart: int, proposal: int) -> float:
        rounded = tuple(round(value, 6) for value in params)
        if rounded in seen:
            # Deterministically nudge the active coordinate until unique.
            values = list(rounded)
            index = proposal % 4
            values[index] = round((values[index] + 0.137 * (restart + 1)) % 1.0, 6)
            rounded = tuple(values)  # type: ignore[assignment]
        seen.add(rounded)
        result = evaluate(rounded, TRAIN_SEED, worlds)
        accuracy = result["accuracy"]
        if accuracy is None:
            accuracy = 1.0
        history.append({"accuracy": accuracy, "params": list(rounded),
                        "proposal": proposal, "restart": restart})
        return float(accuracy)

    incumbents: list[tuple[float, Params]] = []
    for restart in range(3):
        current: Params = tuple(round(rng.random(), 6) for _ in range(4))  # type: ignore[assignment]
        current_score = score(current, restart, 0)
        for proposal in range(1, 15):
            step = 0.5 if proposal <= 8 else 0.25
            dimension = (proposal - 1) % 4
            direction = -1.0 if rng.random() < 0.5 else 1.0
            candidate_values = list(current)
            candidate_values[dimension] = min(1.0, max(0.0, candidate_values[dimension] + direction * step))
            candidate: Params = tuple(candidate_values)  # type: ignore[assignment]
            candidate_score = score(candidate, restart, proposal)
            if (candidate_score, candidate) < (current_score, current):
                current, current_score = candidate, candidate_score
        incumbents.append((current_score, current))
    assert len(history) == 45
    return min(incumbents)[1], history


def welch_t(incorrect: list[int], correct: list[int]) -> float | None:
    if len(incorrect) < 2 or len(correct) < 2:
        return None
    numerator = statistics.mean(correct) - statistics.mean(incorrect)
    denominator = math.sqrt(statistics.variance(correct) / len(correct)
                            + statistics.variance(incorrect) / len(incorrect))
    return numerator / denominator if denominator else None


def run() -> dict[str, object]:
    selected, history = optimize()
    attacks = {
        "none": (0.0, 0.0, 0.0, 0.0),
        "selected": selected,
        "uniform_0_5": (0.5, 0.5, 0.5, 0.5),
        "uniform_1_0": (1.0, 1.0, 1.0, 1.0),
    }
    holdout: dict[str, list[dict[str, object]]] = {}
    for name, params in attacks.items():
        holdout[name] = [evaluate(params, seed, HOLDOUT_WORLDS, name == "selected")
                         for seed in HOLDOUT_SEEDS]
    means = {name: round(statistics.mean(float(row["accuracy"]) for row in rows), 12)
             for name, rows in holdout.items()}
    incorrect_margins = [margin for row in holdout["selected"]
                         for margin in row.get("incorrect_margins", [])]
    correct_margins = [margin for row in holdout["selected"]
                       for margin in row.get("correct_margins", [])]
    statistic = welch_t(incorrect_margins, correct_margins)
    h1 = means["selected"] < min(means["uniform_0_5"], means["uniform_1_0"])
    h2 = (statistic is not None and statistics.mean(incorrect_margins)
          < statistics.mean(correct_margins) and statistic > 1.96)
    return {
        "config": {"holdout_seeds": list(HOLDOUT_SEEDS), "holdout_worlds": HOLDOUT_WORLDS,
                   "search_seed": SEARCH_SEED, "training_seed": TRAIN_SEED,
                   "training_worlds": TRAIN_WORLDS, "unique_evaluation_budget": 45},
        "holdout": holdout,
        "holdout_mean_accuracy": means,
        "hypotheses": {"H7A-1": "supported" if h1 else "rejected",
                       "H7A-2": "supported" if h2 else ("inconclusive" if statistic is None else "rejected")},
        "margin_analysis": {
            "correct_mean": round(statistics.mean(correct_margins), 12) if correct_margins else None,
            "correct_n": len(correct_margins),
            "incorrect_mean": round(statistics.mean(incorrect_margins), 12) if incorrect_margins else None,
            "incorrect_n": len(incorrect_margins),
            "welch_t": round(statistic, 12) if statistic is not None else None,
        },
        "overall_verdict": "supported" if h1 and h2 else ("inconclusive" if statistic is None else "rejected"),
        "selected_params": list(selected),
        "training_evaluations": history,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--protocol-commit", required=True)
    args = parser.parse_args()
    result = run()
    source = Path(__file__).read_bytes()
    result["provenance"] = {
        "environment": {"implementation": platform.python_implementation(),
                        "platform": platform.platform(), "python": sys.version},
        "protocol_commit": args.protocol_commit,
        "source_sha256": hashlib.sha256(source).hexdigest(),
    }
    data = canonical_json(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(hashlib.sha256(data).hexdigest())
    print(json.dumps({"overall_verdict": result["overall_verdict"],
                      "selected_params": result["selected_params"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
