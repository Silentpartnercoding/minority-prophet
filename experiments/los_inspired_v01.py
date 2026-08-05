"""CANONICAL (exploratory) frozen finite Łoś-inspired experiment v0.1.

Run with:
    python -m experiments.los_inspired_v01

The experiment is deliberately synthetic.  It tests behavior under declared
lineage and competence assumptions; it does not show that those inputs can be
recovered reliably in the real world.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from random import Random
from time import perf_counter_ns
from typing import Callable, Iterable

from aggregation.semantic import (
    Assignment,
    SemanticResult,
    evidence_root_vote,
    proposition_majority,
    semantic_coalition,
)


@dataclass(frozen=True)
class WorldModelClaim:
    claim_id: str
    assignment: Assignment
    root_id: str | None
    confidence: float
    competence: float


@dataclass(frozen=True)
class SemanticWorld:
    world_id: str
    regime: str
    truth: Assignment
    claims: tuple[WorldModelClaim, ...]


@dataclass(frozen=True)
class RegimeMetrics:
    method: str
    regime: str
    worlds: int
    exact_truth_accuracy: float
    proposition_accuracy: float
    logical_consistency: float
    abstention_rate: float
    mean_compute_microseconds: float


VALID_MODELS: tuple[Assignment, ...] = (
    (False, False, False),
    (False, True, False),
    (True, False, False),
    (True, True, True),
)


def conjunction_constraint(model: Assignment) -> bool:
    """The third proposition must equal the conjunction of the first two."""
    return len(model) == 3 and model[2] == (model[0] and model[1])


def _claim(
    world_id: str,
    index: int,
    assignment: Assignment,
    root_id: str | None,
    confidence: float,
    competence: float,
) -> WorldModelClaim:
    return WorldModelClaim(
        f"{world_id}-claim-{index}", assignment, root_id, confidence, competence
    )


def generate_semantic_world(*, seed: int, index: int, regime: str) -> SemanticWorld:
    rng = Random((seed << 32) + index)
    world_id = f"los-{seed}-{regime}-{index:05d}"
    truth = rng.choice((VALID_MODELS[0], VALID_MODELS[3]))
    false_models = [model for model in VALID_MODELS if model != truth]
    false = rng.choice(false_models)
    claims: list[WorldModelClaim] = []

    if regime in {"copied_false_majority", "corrupted_lineage"}:
        for observer in range(3):
            claims.append(
                _claim(
                    world_id,
                    len(claims),
                    truth,
                    f"instrument-{observer}",
                    0.94 + rng.random() * 0.05,
                    0.96,
                )
            )
        for copier in range(95):
            root_id = "rumor-root" if regime == "copied_false_majority" else f"forged-{copier}"
            claims.append(
                _claim(
                    world_id,
                    len(claims),
                    false,
                    root_id,
                    0.75 + rng.random() * 0.20,
                    0.50,
                )
            )
    elif regime == "independent_true_majority":
        for observer in range(95):
            claims.append(
                _claim(world_id, len(claims), truth, f"truth-{observer}", 0.9, 0.95)
            )
        for observer in range(3):
            claims.append(
                _claim(world_id, len(claims), false, f"false-{observer}", 0.8, 0.5)
            )
    elif regime == "unsupported_false_minority":
        for observer in range(7):
            claims.append(
                _claim(world_id, len(claims), truth, f"truth-{observer}", 0.9, 0.95)
            )
        for _ in range(3):
            claims.append(_claim(world_id, len(claims), false, None, 0.99, 0.5))
    elif regime == "doctrinal_split":
        truth = VALID_MODELS[3]
        claims.extend(
            (
                _claim(world_id, 0, VALID_MODELS[3], "expert-root", 0.99, 0.99),
                _claim(world_id, 1, VALID_MODELS[2], "partial-root-a", 0.80, 0.72),
                _claim(world_id, 2, VALID_MODELS[1], "partial-root-b", 0.80, 0.72),
            )
        )
    else:
        raise ValueError(f"unknown regime: {regime}")

    rng.shuffle(claims)
    return SemanticWorld(world_id, regime, truth, tuple(claims))


def generate_corruption_world(
    *, seed: int, index: int, forged_roots: int
) -> SemanticWorld:
    """Vary how many of 95 copied claims falsely appear independent."""
    if not 0 <= forged_roots <= 95:
        raise ValueError("forged_roots must be between 0 and 95")
    rng = Random((seed << 32) + index)
    regime = f"lineage_corruption_{forged_roots}"
    world_id = f"los-{seed}-{regime}-{index:05d}"
    truth = rng.choice((VALID_MODELS[0], VALID_MODELS[3]))
    false = rng.choice([model for model in VALID_MODELS if model != truth])
    claims: list[WorldModelClaim] = []
    for observer in range(3):
        claims.append(
            _claim(
                world_id,
                len(claims),
                truth,
                f"instrument-{observer}",
                0.94 + rng.random() * 0.05,
                0.96,
            )
        )
    for copier in range(95):
        root_id = f"forged-{copier}" if copier < forged_roots else "rumor-root"
        claims.append(
            _claim(
                world_id,
                len(claims),
                false,
                root_id,
                0.75 + rng.random() * 0.20,
                0.50,
            )
        )
    rng.shuffle(claims)
    return SemanticWorld(world_id, regime, truth, tuple(claims))


Method = Callable[[Iterable[WorldModelClaim], Callable[[Assignment], bool]], SemanticResult]


def run_experiment(*, worlds_per_regime: int = 2_000, seed: int = 20260803) -> dict[str, object]:
    regimes = (
        "copied_false_majority",
        "independent_true_majority",
        "unsupported_false_minority",
        "doctrinal_split",
        "corrupted_lineage",
    )
    methods: dict[str, Method] = {
        "proposition_majority": proposition_majority,
        "evidence_root_vote": evidence_root_vote,
        "semantic_coalition": semantic_coalition,
    }
    rows: list[dict[str, object]] = []

    for regime in regimes:
        worlds = tuple(
            generate_semantic_world(seed=seed, index=index, regime=regime)
            for index in range(worlds_per_regime)
        )
        for method_name, method in methods.items():
            exact = proposition_correct = consistent = abstained = elapsed = 0
            for world in worlds:
                started = perf_counter_ns()
                result = method(world.claims, conjunction_constraint)
                elapsed += perf_counter_ns() - started
                if result.assignment is None:
                    abstained += 1
                else:
                    exact += result.assignment == world.truth
                    proposition_correct += sum(
                        observed == expected
                        for observed, expected in zip(
                            result.assignment, world.truth, strict=True
                        )
                    )
                    consistent += conjunction_constraint(result.assignment)
            answered = len(worlds) - abstained
            metrics = RegimeMetrics(
                method=method_name,
                regime=regime,
                worlds=len(worlds),
                exact_truth_accuracy=exact / len(worlds),
                proposition_accuracy=proposition_correct / (len(worlds) * 3),
                logical_consistency=consistent / answered if answered else 0.0,
                abstention_rate=abstained / len(worlds),
                mean_compute_microseconds=elapsed / len(worlds) / 1_000,
            )
            rows.append(asdict(metrics))

    corruption_sweep: list[dict[str, object]] = []
    sweep_worlds = max(200, worlds_per_regime // 4)
    for forged_roots in range(13):
        worlds = tuple(
            generate_corruption_world(
                seed=seed + 1, index=index, forged_roots=forged_roots
            )
            for index in range(sweep_worlds)
        )
        for method_name, method in {
            "evidence_root_vote": evidence_root_vote,
            "semantic_coalition": semantic_coalition,
        }.items():
            correct = abstained = 0
            for world in worlds:
                result = method(world.claims, conjunction_constraint)
                correct += result.assignment == world.truth
                abstained += result.assignment is None
            corruption_sweep.append(
                {
                    "method": method_name,
                    "forged_roots": forged_roots,
                    "worlds": len(worlds),
                    "exact_truth_accuracy": correct / len(worlds),
                    "abstention_rate": abstained / len(worlds),
                }
            )

    return {
        "experiment": "finite-los-inspired-semantic-aggregation",
        "version": "0.1",
        "seed": seed,
        "worlds_per_regime": worlds_per_regime,
        "total_worlds": worlds_per_regime * len(regimes),
        "constraint": "r iff (p and q)",
        "results": rows,
        "lineage_corruption_sweep": corruption_sweep,
        "caveat": (
            "Finite proxy with declared lineage and competence; not a literal "
            "ultraproduct and not evidence that real-world provenance is reliable."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worlds-per-regime", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=20260803)
    parser.add_argument("--output")
    args = parser.parse_args()
    report = run_experiment(worlds_per_regime=args.worlds_per_regime, seed=args.seed)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
