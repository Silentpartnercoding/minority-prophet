"""DRI-2 scoring and evaluation. DRAFT, NOT FROZEN.

Junction scoring (hidden junction type, arm's terminal action):

- hand-over junction: escalating is a required hand-over; settling is a fall.
- settle or gather junction: escalating is an incorrect stall. The scripted human
  answers and the run continues, with the stall logged.
- gather junction: settling without having probed is a fall, even when the side
  happens to be right, because the evidence in hand did not justify it.
- otherwise settling on the side the true causal grouping settles is correct,
  and any other settlement is a fall.

A fall ends the run. A run with no fall is CROSSED; a crossing with no incorrect
stall is also clean.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from experiments.dri2.arms import COMPARISON_ARMS, CONTESTANT_ARMS, ESCALATE, REFERENCE_ARMS, act
from experiments.dri2.stats import (
    holm,
    mcnemar_exact,
    mean_interval,
    paired_difference_interval,
    wilcoxon_signed_rank,
    wilson_interval,
)
from experiments.dri2.world import GATHER, HAND_OVER, SETTLE, World, iter_worlds, with_probe, world_hash_row

CORRECT = "correct"
REQUIRED_HANDOVER = "required_handover"
INCORRECT_STALL = "incorrect_stall"
FALL = "fall"
ALL_ARMS = tuple(CONTESTANT_ARMS) + tuple(REFERENCE_ARMS)


def score_junction(junction: str, reference: str, terminal: str, probed: bool) -> str:
    if junction == HAND_OVER:
        return REQUIRED_HANDOVER if terminal == ESCALATE else FALL
    if terminal == ESCALATE:
        return INCORRECT_STALL
    if junction == GATHER and not probed:
        return FALL
    return CORRECT if terminal == reference else FALL


@dataclass(frozen=True)
class RunRecord:
    arm: str
    world_id: str
    crossed: bool
    clean: bool
    junction_results: tuple[tuple[str, str], ...]
    human_calls: int
    required_calls: int
    probes: int
    virtual_ms: int
    looked_before_asking: int
    premature_handovers: int
    over_reach: int


def run_arm(arm: str, world: World, config: Mapping[str, Any]) -> RunRecord:
    results: list[tuple[str, str]] = []
    human_calls = required_calls = probes = virtual_ms = 0
    looked = premature = over_reach = 0
    crossed = True
    wrong_time_cost = config.get("wrong_time_escalation_cost_ms") or 0
    for decision in world.decisions:
        terminal, calls = act(arm, decision)
        probed = calls > 0 or arm in REFERENCE_ARMS
        result = score_junction(decision.junction, decision.reference, terminal, probed)
        probes += calls
        virtual_ms += calls * config["probe_cost_ms"] + config["action_cost_ms"]
        required_calls += decision.junction == HAND_OVER
        if terminal == ESCALATE:
            human_calls += 1
            looked += calls > 0
            if decision.junction != HAND_OVER:
                premature += 1
                virtual_ms += wrong_time_cost
        elif decision.junction == HAND_OVER:
            over_reach += 1
        results.append((decision.junction, result))
        if result == FALL:
            crossed = False
            break
    return RunRecord(
        arm=arm,
        world_id=world.world_id,
        crossed=crossed,
        clean=crossed and all(result != INCORRECT_STALL for _, result in results),
        junction_results=tuple(results),
        human_calls=human_calls,
        required_calls=required_calls,
        probes=probes,
        virtual_ms=virtual_ms,
        looked_before_asking=looked,
        premature_handovers=premature,
        over_reach=over_reach,
    )


def twin_discrimination(arm: str, twin: World) -> tuple[int, int]:
    """Across a twin pair, count flipped junctions where the arm probes and settles
    with the probe available and escalates without it."""
    available = with_probe(twin, True)
    discriminating = eligible = 0
    for on, off in zip(available.decisions, twin.decisions):
        if on.junction != GATHER or off.junction != HAND_OVER:
            continue
        eligible += 1
        on_terminal, on_calls = act(arm, on)
        off_terminal, _ = act(arm, off)
        discriminating += on_calls > 0 and on_terminal != ESCALATE and off_terminal == ESCALATE
    return discriminating, eligible


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 9) if denominator else None


def _summarize_arm(records: list[RunRecord]) -> dict[str, Any]:
    n = len(records)
    crossed = sum(r.crossed for r in records)
    low, high = wilson_interval(crossed, n)
    by_type: dict[str, list[int]] = {SETTLE: [0, 0], GATHER: [0, 0], HAND_OVER: [0, 0]}
    for record in records:
        for junction, result in record.junction_results:
            by_type[junction][1] += 1
            by_type[junction][0] += result in (CORRECT, REQUIRED_HANDOVER)
    crossed_ms = [r.virtual_ms for r in records if r.crossed]
    return {
        "worlds": n,
        "crossed": crossed,
        "crossingRate": _rate(crossed, n),
        "crossingRateWilson95": [round(low, 9), round(high, 9)] if n else None,
        "cleanCrossed": sum(r.clean for r in records),
        "fell": n - crossed,
        "humanCalls": sum(r.human_calls for r in records),
        "excessHumanCalls": sum(max(r.human_calls - r.required_calls, 0) for r in records),
        "probes": sum(r.probes for r in records),
        "lookedBeforeAsking": sum(r.looked_before_asking for r in records),
        "prematureHandovers": sum(r.premature_handovers for r in records),
        "overReach": sum(r.over_reach for r in records),
        "meanVirtualMsWhenCrossed": _rate(sum(crossed_ms), len(crossed_ms)),
        "junctionAccuracy": {
            junction: {"correct": c, "reached": t, "rate": _rate(c, t)}
            for junction, (c, t) in by_type.items()
        },
    }


def _primary(records: Mapping[str, list[RunRecord]], alpha: float) -> dict[str, Any]:
    mut = records["method_under_test"]
    crossing: dict[str, Any] = {}
    timing: dict[str, Any] = {}
    for arm in COMPARISON_ARMS:
        other = records[arm]
        first_only = sum(m.crossed and not o.crossed for m, o in zip(mut, other))
        second_only = sum(o.crossed and not m.crossed for m, o in zip(mut, other))
        difference, low, high = paired_difference_interval(first_only, second_only, len(mut))
        crossing[arm] = {
            "methodOnlyCrossed": first_only,
            "armOnlyCrossed": second_only,
            "difference": difference,
            "difference95": [low, high],
            "p": mcnemar_exact(first_only, second_only),
        }
        differences = [m.virtual_ms - o.virtual_ms for m, o in zip(mut, other) if m.crossed and o.crossed]
        mean, low, high = mean_interval(differences)
        timing[arm] = {
            "bothCrossed": len(differences),
            "meanDifferenceMs": mean,
            "meanDifference95": [low, high],
            **{f"wilcoxon_{k}": v for k, v in wilcoxon_signed_rank(differences).items()},
        }
    for table in (crossing, timing):
        key = "p" if table is crossing else "wilcoxon_p"
        adjusted = holm({arm: row[key] for arm, row in table.items()})
        for arm, value in adjusted.items():
            table[arm]["holmP"] = value
            table[arm]["significant"] = value < alpha
    return {"crossing": crossing, "timeToCrossing": timing}


def evaluate(
    config: Mapping[str, Any], salt: str, worlds_per_path_type: int | None = None
) -> dict[str, Any]:
    records: dict[str, dict[str, list[RunRecord]]] = {
        family: {arm: [] for arm in ALL_ARMS} for family in config["families"]
    }
    twins: dict[str, dict[str, list[int]]] = {
        family: {arm: [0, 0] for arm in ALL_ARMS} for family in config["families"]
    }
    manifest = hashlib.sha256()
    worlds = 0
    for world in iter_worlds(config, salt, worlds_per_path_type):
        worlds += 1
        manifest.update(world_hash_row(world))
        for arm in ALL_ARMS:
            records[world.family][arm].append(run_arm(arm, world, config))
            if world.path_type == "twin":
                discriminating, eligible = twin_discrimination(arm, world)
                twins[world.family][arm][0] += discriminating
                twins[world.family][arm][1] += eligible
    families = {}
    for family, by_arm in records.items():
        families[family] = {
            "arms": {arm: _summarize_arm(rows) for arm, rows in by_arm.items()},
            "twinDiscrimination": {
                arm: {"discriminating": d, "eligible": e, "rate": _rate(d, e)}
                for arm, (d, e) in twins[family].items()
            },
            "tests": _primary(by_arm, config["familywise_alpha"]),
        }
    return {
        "schema": "minority-prophet.dri2-semantic-result.v0-draft",
        "worlds": worlds,
        "worldManifestSha256": manifest.hexdigest(),
        "families": families,
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
