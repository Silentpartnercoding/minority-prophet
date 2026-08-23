"""Frozen DRI-1A generator and confirmatory scorer.

This is a synthetic policy-value experiment. The rules selector reads an
explicit failure-domain field; it does not infer causality from prose.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from provenance.decision_relative import DecisionContext, DecisionEvidence, assess_decision


CONFIG_SHA256 = "42078e86815cd5b806e1a44f23aaff4b002f94af7193b5c422adf0c948bb7d1b"
PREREGISTRATION_SHA256 = "6f47faa5aaa3d856e7d9e990b40b086288a9d05507a2b7ec053f85ef720248ce"
FIXED_METHODS = {
    "agent_headcount": "agent",
    "fixed_machine": "machine",
    "fixed_controller": "controller",
    "fixed_evidence_origin": "evidence_origin",
    "fixed_upstream_component": "upstream_component",
}
TOPOLOGY = {
    "machine_local": {
        "relevant": "machine",
        "fine": {"agent", "evidence_origin"},
        "coarse": {"controller", "upstream_component"},
    },
    "shared_controller": {
        "relevant": "controller",
        "fine": {"agent", "machine"},
        "coarse": {"evidence_origin", "upstream_component"},
    },
    "copied_source": {
        "relevant": "evidence_origin",
        "fine": {"agent", "machine", "controller"},
        "coarse": {"upstream_component"},
    },
    "shared_upstream_component": {
        "relevant": "upstream_component",
        "fine": {"agent", "machine", "controller", "evidence_origin"},
        "coarse": set(),
    },
}
MOST_COMMON_CUT = "controller"


@dataclass(frozen=True)
class World:
    world_id: str
    failure_domain: str
    accuracy: float
    amplification: int
    decision_class: str
    threshold: int
    truth: bool
    relevant_cut: str
    evidence: tuple[DecisionEvidence, ...]


@dataclass
class Counts:
    total: int = 0
    false_settlement: int = 0
    correct_settlement: int = 0
    abstention: int = 0
    unsupported_settlement: int = 0
    unnecessary_abstention: int = 0
    oracle_disposition_agreement: int = 0
    minority_reversal_eligible: int = 0
    minority_reversal_recovered: int = 0

    def add(
        self,
        *,
        settlement: str,
        truth: bool,
        oracle_settlement: str,
        reversal_side: bool | None,
    ) -> None:
        self.total += 1
        side = _settled_side(settlement)
        oracle_side = _settled_side(oracle_settlement)
        if side is None:
            self.abstention += 1
        elif side == truth:
            self.correct_settlement += 1
        else:
            self.false_settlement += 1
        if side is not None and oracle_side is None:
            self.unsupported_settlement += 1
        if side is None and oracle_side == truth:
            self.unnecessary_abstention += 1
        if settlement == oracle_settlement:
            self.oracle_disposition_agreement += 1
        if reversal_side is not None:
            self.minority_reversal_eligible += 1
            if side == reversal_side:
                self.minority_reversal_recovered += 1

    def render(self) -> dict[str, Any]:
        return {
            "worlds": self.total,
            "falseSettlements": self.false_settlement,
            "falseSettlementRate": _rate(self.false_settlement, self.total),
            "correctSettlements": self.correct_settlement,
            "correctSettlementRate": _rate(self.correct_settlement, self.total),
            "abstentions": self.abstention,
            "abstentionRate": _rate(self.abstention, self.total),
            "unsupportedSettlements": self.unsupported_settlement,
            "unsupportedSettlementRate": _rate(self.unsupported_settlement, self.total),
            "unnecessaryAbstentions": self.unnecessary_abstention,
            "unnecessaryAbstentionRate": _rate(self.unnecessary_abstention, self.total),
            "oracleDispositionAgreementRate": _rate(
                self.oracle_disposition_agreement, self.total
            ),
            "minorityReversalEligible": self.minority_reversal_eligible,
            "minorityReversalRecovered": self.minority_reversal_recovered,
            "minorityReversalRecoveryRate": _rate(
                self.minority_reversal_recovered, self.minority_reversal_eligible
            ),
        }


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 9) if denominator else None


def _settled_side(settlement: str) -> bool | None:
    if settlement == "settled_true":
        return True
    if settlement == "settled_false":
        return False
    return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen_config(path: Path, preregistration: Path) -> dict[str, Any]:
    if _sha256(path) != CONFIG_SHA256:
        raise ValueError("execution config differs from the preregistered file")
    if _sha256(preregistration) != PREREGISTRATION_SHA256:
        raise ValueError("preregistration differs from the committed protocol")
    config = json.loads(path.read_text())
    expected_worlds = (
        len(config["failure_domains"])
        * len(config["independent_root_accuracies"])
        * len(config["erroneous_root_amplifications"])
        * len(config["decision_classes"])
        * config["replicates_per_cell"]
    )
    if expected_worlds != 8192:
        raise ValueError("DRI-1A requires exactly 8,192 worlds")
    if config["cut_policy"] != {
        domain: spec["relevant"] for domain, spec in TOPOLOGY.items()
    }:
        raise ValueError("cut policy differs from the frozen topology")
    return config


def _seed(config: dict[str, Any], cell: str, replicate: int) -> int:
    digest = hashlib.sha256(
        f"{config['generator_salt']}|{cell}|{replicate}".encode()
    ).digest()
    return int.from_bytes(digest, "big")


def _root_id(cut: str, kind: str, group: int, copy: int) -> str:
    if kind == "relevant":
        return f"{cut}:causal:{group}"
    if kind == "fine":
        return f"{cut}:observation:{group}:{copy}"
    if kind == "coarse":
        return f"{cut}:coarse:{group // 2}"
    raise ValueError(f"unknown topology kind: {kind}")


def generate_world(
    config: dict[str, Any],
    *,
    failure_domain: str,
    accuracy: float,
    amplification: int,
    decision_class: str,
    replicate: int,
) -> World:
    cell = f"{failure_domain}|{accuracy:.2f}|{amplification}|{decision_class}"
    world_id = f"{cell}|{replicate:03d}"
    rng = random.Random(_seed(config, cell, replicate))
    truth = bool(rng.getrandbits(1))
    topology = TOPOLOGY[failure_domain]
    evidence: list[DecisionEvidence] = []
    for group in range(config["causal_roots_per_world"]):
        correct = rng.random() < accuracy
        value = truth if correct else not truth
        copies = 1 if correct else amplification
        for copy in range(copies):
            roots: dict[str, str] = {}
            for cut in config["candidate_cuts"]:
                if cut == topology["relevant"]:
                    kind = "relevant"
                elif cut in topology["fine"]:
                    kind = "fine"
                elif cut in topology["coarse"]:
                    kind = "coarse"
                else:
                    raise ValueError(f"cut {cut} has no topology in {failure_domain}")
                roots[cut] = _root_id(cut, kind, group, copy)
            evidence.append(
                DecisionEvidence(
                    observation_id=f"{world_id}|root:{group}|copy:{copy}",
                    proposition_id=world_id,
                    value=value,
                    roots=roots,
                    basis={cut: "attested" for cut in roots},
                )
            )
    return World(
        world_id=world_id,
        failure_domain=failure_domain,
        accuracy=accuracy,
        amplification=amplification,
        decision_class=decision_class,
        threshold=config["decision_classes"][decision_class],
        truth=truth,
        relevant_cut=topology["relevant"],
        evidence=tuple(evidence),
    )


def iter_worlds(config: dict[str, Any]) -> Iterable[World]:
    for failure_domain in config["failure_domains"]:
        for accuracy in config["independent_root_accuracies"]:
            for amplification in config["erroneous_root_amplifications"]:
                for decision_class in config["decision_classes"]:
                    for replicate in range(config["replicates_per_cell"]):
                        yield generate_world(
                            config,
                            failure_domain=failure_domain,
                            accuracy=accuracy,
                            amplification=amplification,
                            decision_class=decision_class,
                            replicate=replicate,
                        )


def _context(world: World, cut: str, threshold: int, cuts: tuple[str, ...]) -> DecisionContext:
    return DecisionContext(
        decision_id=world.world_id,
        proposition_id=world.world_id,
        failure_domain=world.failure_domain,
        independence_cut=cut,
        minimum_winning_roots=threshold,
        consequence=world.decision_class,
        reversibility="reversible" if world.decision_class == "low_reversible" else "irreversible",
        cut_selection_basis="rules-engine",
        candidate_cuts=cuts,
    )


def _outcomes(world: World, cut: str, threshold: int, cuts: tuple[str, ...]):
    result = assess_decision(world.evidence, _context(world, cut, threshold, cuts))
    return {
        result.selected.independence_cut: result.selected,
        **dict(result.alternatives),
    }, result


def _strata(world: World) -> tuple[str, ...]:
    return (
        "overall",
        f"failure_domain={world.failure_domain}",
        f"accuracy={world.accuracy:.2f}",
        f"amplification={world.amplification}",
        f"decision_class={world.decision_class}",
    )


def _world_hash_row(world: World) -> bytes:
    row = {
        "worldId": world.world_id,
        "truth": world.truth,
        "relevantCut": world.relevant_cut,
        "threshold": world.threshold,
        "evidence": [
            {
                "id": item.observation_id,
                "value": item.value,
                "roots": dict(item.roots),
            }
            for item in world.evidence
        ],
    }
    return (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _percentile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * quantile
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def _latency(values_ns: list[int]) -> dict[str, float | int]:
    milliseconds = [value / 1_000_000 for value in values_ns]
    return {
        "samples": len(values_ns),
        "p50Milliseconds": round(_percentile(milliseconds, 0.50), 6),
        "p95Milliseconds": round(_percentile(milliseconds, 0.95), 6),
        "p99Milliseconds": round(_percentile(milliseconds, 0.99), 6),
    }


def _render_strata(counts: dict[str, dict[str, Counts]]) -> dict[str, Any]:
    return {
        stratum: {method: metric.render() for method, metric in sorted(methods.items())}
        for stratum, methods in sorted(counts.items())
    }


def _choose_matched(
    rows: dict[str, dict[int, Counts]], oracle_abstention: float
) -> dict[str, Any]:
    selected: dict[str, Any] = {}
    for method, thresholds in sorted(rows.items()):
        candidates = []
        for threshold, counts in thresholds.items():
            rendered = counts.render()
            distance = abs(rendered["abstentionRate"] - oracle_abstention)
            candidates.append(
                (distance, rendered["falseSettlementRate"], threshold, rendered)
            )
        distance, _, threshold, rendered = min(candidates)
        selected[method] = {
            "threshold": threshold,
            "abstentionDifference": round(distance, 9),
            "withinTolerance": distance <= 0.01,
            **rendered,
        }
    return selected


def run_once(config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    cuts = tuple(config["candidate_cuts"])
    counts: dict[str, dict[str, Counts]] = defaultdict(lambda: defaultdict(Counts))
    sensitivity: dict[str, dict[int, Counts]] = {
        method: {threshold: Counts() for threshold in config["threshold_sensitivity"]}
        for method in FIXED_METHODS
    }
    manifest = hashlib.sha256()
    latency_ns: list[int] = []
    world_count = material_worlds = rules_oracle_mismatches = 0
    cut_correct = {"oracle_policy": 0, "rules_engine": 0, "most_common_selector": 0}

    for world in iter_worlds(config):
        world_count += 1
        manifest.update(_world_hash_row(world))

        primary, oracle_assessment = _outcomes(
            world, world.relevant_cut, world.threshold, cuts
        )
        oracle_settlement = primary[world.relevant_cut].settlement
        material_worlds += bool(oracle_assessment.material_alternative_cuts)

        started = time.perf_counter_ns()
        rules, _ = _outcomes(
            world,
            config["cut_policy"][world.failure_domain],
            world.threshold,
            cuts,
        )
        latency_ns.append(time.perf_counter_ns() - started)
        rules_settlement = rules[config["cut_policy"][world.failure_domain]].settlement
        rules_oracle_mismatches += rules_settlement != oracle_settlement

        method_settlements = {
            method: primary[cut].settlement for method, cut in FIXED_METHODS.items()
        }
        method_settlements.update(
            {
                "oracle_policy": oracle_settlement,
                "rules_engine": rules_settlement,
                "most_common_selector": primary[MOST_COMMON_CUT].settlement,
            }
        )

        causal_verdict = primary[world.relevant_cut].root_verdict.verdict.value
        agent_verdict = primary["agent"].root_verdict.verdict.value
        reversal_side = None
        if causal_verdict in {"true", "false"} and agent_verdict in {"true", "false"}:
            causal_side = causal_verdict == "true"
            if causal_side != (agent_verdict == "true"):
                reversal_side = causal_side

        for stratum in _strata(world):
            for method, settlement in method_settlements.items():
                counts[stratum][method].add(
                    settlement=settlement,
                    truth=world.truth,
                    oracle_settlement=oracle_settlement,
                    reversal_side=reversal_side,
                )

        for method, cut in FIXED_METHODS.items():
            for threshold in config["threshold_sensitivity"]:
                threshold_outcomes, _ = _outcomes(world, cut, threshold, cuts)
                sensitivity[method][threshold].add(
                    settlement=threshold_outcomes[cut].settlement,
                    truth=world.truth,
                    oracle_settlement=oracle_settlement,
                    reversal_side=reversal_side,
                )

        cut_correct["oracle_policy"] += 1
        cut_correct["rules_engine"] += (
            config["cut_policy"][world.failure_domain] == world.relevant_cut
        )
        cut_correct["most_common_selector"] += MOST_COMMON_CUT == world.relevant_cut

    if world_count != 8192:
        raise AssertionError(f"expected 8,192 worlds, observed {world_count}")

    rendered = _render_strata(counts)
    overall = rendered["overall"]
    oracle_abstention = overall["oracle_policy"]["abstentionRate"]
    matched = _choose_matched(sensitivity, oracle_abstention)
    primary_reductions = {
        method: round(
            overall[method]["falseSettlementRate"]
            - overall["oracle_policy"]["falseSettlementRate"],
            9,
        )
        for method in FIXED_METHODS
    }
    matched_reductions = {
        method: round(
            row["falseSettlementRate"]
            - overall["oracle_policy"]["falseSettlementRate"],
            9,
        )
        for method, row in matched.items()
    }
    checks = {
        "oracleMinimumReductionEveryFixedCut": all(
            value >= config["minimum_false_settlement_reduction"]
            for value in primary_reductions.values()
        ),
        "matchedOracleMinimumReductionEveryFixedCut": all(
            matched[method]["withinTolerance"]
            and matched_reductions[method]
            >= config["minimum_false_settlement_reduction"]
            for method in FIXED_METHODS
        ),
        "allFixedCutsAbstentionMatched": all(
            row["withinTolerance"] for row in matched.values()
        ),
        "rulesEnginePerfectCutSelection": cut_correct["rules_engine"] == world_count,
        "rulesEngineEqualsOracle": rules_oracle_mismatches == 0,
        "mostCommonSelectorAtMostQuarter": (
            cut_correct["most_common_selector"] / world_count <= 0.25
        ),
        "rulesUnnecessaryAbstentionWithinLimit": (
            overall["rules_engine"]["unnecessaryAbstentionRate"]
            - overall["oracle_policy"]["unnecessaryAbstentionRate"]
            <= config["maximum_rules_unnecessary_abstention_increase"]
        ),
        "minimumMaterialWorldFraction": (
            material_worlds / world_count >= config["minimum_material_world_fraction"]
        ),
    }
    semantic = {
        "schema": "minority-prophet.dri1a-semantic-result.v1",
        "status": "confirmatory-scored",
        "worlds": world_count,
        "worldManifestSha256": manifest.hexdigest(),
        "configSha256": CONFIG_SHA256,
        "preregistrationSha256": PREREGISTRATION_SHA256,
        "methodsByStratum": rendered,
        "selectedCutAccuracy": {
            method: _rate(correct, world_count) for method, correct in cut_correct.items()
        },
        "rulesOracleDispositionMismatches": rules_oracle_mismatches,
        "decisionMaterialWorlds": material_worlds,
        "decisionMaterialWorldFraction": _rate(material_worlds, world_count),
        "registeredThresholdFalseSettlementReduction": primary_reductions,
        "abstentionMatched": matched,
        "abstentionMatchedFalseSettlementReduction": matched_reductions,
        "criterionWithoutReproducibility": {
            "tests": checks,
            "supported": all(checks.values()),
        },
        "interpretationBoundary": (
            "Frozen synthetic declared-policy benchmark; no learned cut inference, "
            "real-world lineage validation, joint multi-cut claim, or action authority."
        ),
    }
    return semantic, _latency(latency_ns)


def _semantic_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def run_confirmatory(config: dict[str, Any]) -> dict[str, Any]:
    first, first_latency = run_once(config)
    second, second_latency = run_once(config)
    hashes = [_semantic_hash(first), _semantic_hash(second)]
    reproducible = hashes[0] == hashes[1]
    checks = {
        **first["criterionWithoutReproducibility"]["tests"],
        "semanticResultReproducible": reproducible,
    }
    return {
        "schema": "minority-prophet.dri1a-confirmatory-result.v1",
        "status": "confirmatory-complete",
        "criterion": {"tests": checks, "supported": all(checks.values())},
        "semanticResultSha256Runs": hashes,
        "semanticResult": first,
        "latencyRuns": [first_latency, second_latency],
    }


def main() -> None:
    here = Path(__file__).parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=here / "EXECUTION-CONFIG.json")
    parser.add_argument("--preregistration", type=Path, default=here / "PREREGISTRATION.md")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config = load_frozen_config(args.config, args.preregistration)
    result = run_confirmatory(config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(
        json.dumps(
            {
                "criterionSupported": result["criterion"]["supported"],
                "semanticSha256": result["semanticResultSha256Runs"][0],
                "outputSha256": _sha256(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

