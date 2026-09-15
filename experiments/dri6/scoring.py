"""DRI-6 scoring and criterion.

Decisions are scored exactly as in DRI-3 (`experiments.dri3.scoring.score_decision`).
A decision with a lookup counts as decidable even when the lookup errs, so abstaining
there is an unneeded abstention. Results are kept per family and per lookup-error
cell and are never pooled.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from experiments.dri2.stats import holm, mcnemar_exact
from experiments.dri3.scoring import (
    CORRECT_SETTLEMENT,
    FALSE_SETTLEMENT,
    UNNEEDED_ABSTENTION,
    score_decision,
    zero_event_upper_bound,
)
from experiments.dri3.world import SETTLED, world_hash_row
from experiments.dri6.arms import ALL_ARMS, act
from experiments.dri6.world import ImperfectLook, cell_key, cells, iter_worlds, parse_cell

METHODS = ("checked_tiered_rule", "confirmed_tiered_rule")


def evaluate(
    config: Mapping[str, Any], salt: str, worlds_per_family: int | None = None
) -> dict[str, Any]:
    tallies: dict[tuple[str, str], dict[str, Counter]] = defaultdict(lambda: {arm: Counter() for arm in ALL_ARMS})
    paired: dict[tuple[str, str], Counter] = defaultdict(Counter)
    manifest = hashlib.sha256()
    worlds = 0
    look_ms, action_ms = config["look_cost_ms"], config["action_cost_ms"]
    error_cells = cells(config)
    for world in iter_worlds(config, salt, worlds_per_family):
        worlds += 1
        manifest.update(world_hash_row(world))
        for split, merge in error_cells:
            key = (world.family, cell_key(split, merge))
            for decision in world.decisions:
                results = {}
                for arm in ALL_ARMS:
                    look = ImperfectLook(decision, salt, split, merge)
                    terminal, stamped, looks = act(arm, decision, look)
                    outcome = score_decision(decision, terminal)
                    results[arm] = (outcome, stamped, looks)
                    t = tallies[key][arm]
                    for scope in ("all", world.condition, decision.decision_class):
                        t[f"{scope}:decisions"] += 1
                        t[f"{scope}:{outcome}"] += 1
                        t[f"{scope}:looks"] += looks
                        t[f"{scope}:virtualMs"] += looks * look_ms + action_ms
                        if terminal in SETTLED and stamped:
                            t[f"{scope}:stampedSettlements"] += 1
                        if outcome == FALSE_SETTLEMENT:
                            t[f"{scope}:{'flagged' if stamped else 'silent'}FalseSettlements"] += 1
                            if looks:
                                t[f"{scope}:falseSettlementsAfterLook"] += 1

                def silent(arm: str) -> bool:
                    return results[arm][0] == FALSE_SETTLEMENT and not results[arm][1]

                p = paired[key]
                p["tieredSilent"] += silent("tiered_rule")
                for method in METHODS:
                    p[f"{method}:silent"] += silent(method)
                    p[f"{method}:tieredOnlySilent"] += silent("tiered_rule") and not silent(method)
                    p[f"{method}:methodOnlySilent"] += silent(method) and not silent("tiered_rule")
                    p[f"{method}:extraLooks"] += max(results[method][2] - results["tiered_rule"][2], 0)
                    p[f"{method}:prevented"] += (
                        results["tiered_rule"][0] == FALSE_SETTLEMENT and results[method][0] != FALSE_SETTLEMENT
                    )
                    p[f"{method}:extraUnneededAbstentions"] += (
                        results["tiered_rule"][0] == CORRECT_SETTLEMENT and results[method][0] == UNNEEDED_ABSTENTION
                    )

    families: dict[str, dict[str, Any]] = {}
    for (family, cell), by_arm in sorted(tallies.items()):
        p = paired[(family, cell)]
        comparisons = {}
        for method in METHODS:
            prevented = p[f"{method}:prevented"]
            comparisons[method] = {
                "silent": p[f"{method}:silent"],
                "tieredOnlySilent": p[f"{method}:tieredOnlySilent"],
                "methodOnlySilent": p[f"{method}:methodOnlySilent"],
                "p": mcnemar_exact(p[f"{method}:tieredOnlySilent"], p[f"{method}:methodOnlySilent"]),
                "extraLooks": p[f"{method}:extraLooks"],
                "preventedFalseSettlements": prevented,
                "extraUnneededAbstentions": p[f"{method}:extraUnneededAbstentions"],
                "extraLooksPerPrevented": p[f"{method}:extraLooks"] / prevented if prevented else None,
            }
        families.setdefault(family, {})[cell] = {
            "arms": {arm: dict(sorted(counter.items())) for arm, counter in by_arm.items()},
            "tieredSilent": p["tieredSilent"],
            "comparisons": comparisons,
        }
    return {
        "schema": "minority-prophet.dri6-semantic-result.v1",
        "worlds": worlds,
        "worldManifestSha256": manifest.hexdigest(),
        "families": families,
    }


def evaluate_criterion(
    semantic: Mapping[str, Any], config: Mapping[str, Any], reproducible: bool
) -> dict[str, Any]:
    rule = config["success_criterion"]
    bound = rule["maximum_rate_bound"]
    checks: dict[str, bool] = {}
    powered: dict[str, float] = {}
    underpowered: list[str] = []
    for family in rule["families"]:
        for cell, row in semantic["families"][family].items():
            split, merge = parse_cell(cell)
            label = f"{family}:{cell}"
            for method in METHODS:
                checks[f"{label}:{method}:neverSilentWhereTieredIsNot"] = (
                    row["comparisons"][method]["methodOnlySilent"] == 0
                )
            if split == 0 and merge == 0:
                decisions = row["arms"]["confirmed_tiered_rule"].get("all:decisions", 0)
                checks[f"{label}:noSilentFalseSettlement"] = row["comparisons"]["confirmed_tiered_rule"]["silent"] == 0
                checks[f"{label}:silentRateBoundBelow"] = (zero_event_upper_bound(decisions) or 1) < bound
                continue
            if row["tieredSilent"] >= rule["minimum_tiered_silent_for_test"]:
                powered[label] = row["comparisons"]["confirmed_tiered_rule"]["p"]
            else:
                underpowered.append(label)
    adjusted = holm(powered)
    for label, value in adjusted.items():
        family, cell = label.split(":", 1)
        comparison = semantic["families"][family][cell]["comparisons"]["confirmed_tiered_rule"]
        checks[f"{label}:confirmedFewerSilentThanTiered"] = (
            value < config["familywise_alpha"]
            and comparison["tieredOnlySilent"] > comparison["methodOnlySilent"]
        )
    checks["semanticResultReproducible"] = reproducible
    return {
        "tests": checks,
        "poweredComparisons": sorted(powered),
        "underpoweredComparisons": underpowered,
        "supported": all(checks.values()),
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
