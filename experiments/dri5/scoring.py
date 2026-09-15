"""DRI-5 scoring and criterion.

Decisions are scored exactly as in DRI-3 (`experiments.dri3.scoring.score_decision`).
One definition differs, and it applies to every arm alike: a decision counts as
decidable from the record when lineage and content together robustly settle it the
way the true grouping does. Results are kept per family and per (m, p, q) cell and
are never pooled.
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
    score_decision,
    zero_event_upper_bound,
)
from experiments.dri3.world import CUTS, IRREVERSIBLE, SETTLED
from experiments.dri5.arms import ALL_ARMS, act
from experiments.dri5.world import ALL_CUTS, iter_cell_worlds, parse_cell, true_grouping_admissible


def _world_row(cell: str, world: Any) -> bytes:
    row = {
        "cell": cell,
        "worldId": world.world_id,
        "condition": world.condition,
        "decisions": [
            {
                "id": d.decision_id,
                "truth": d.truth,
                "class": d.decision_class,
                "reference": d.reference,
                "evidence": [
                    {"id": item.observation_id, "value": item.value, "roots": dict(item.roots)}
                    for item in d.evidence
                ],
                "units": [list(pair) for pair in d.units],
            }
            for d in world.decisions
        ],
    }
    return (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()


def evaluate(
    config: Mapping[str, Any], salt: str, worlds_per_family: int | None = None
) -> dict[str, Any]:
    tallies: dict[tuple[str, str], dict[str, Counter]] = defaultdict(lambda: {arm: Counter() for arm in ALL_ARMS})
    paired: dict[tuple[str, str], Counter] = defaultdict(Counter)
    manifest = hashlib.sha256()
    worlds = 0
    look_ms, action_ms = config["look_cost_ms"], config["action_cost_ms"]
    for cell, world in iter_cell_worlds(config, salt, worlds_per_family):
        worlds += 1
        manifest.update(_world_row(cell, world))
        key = (world.family, cell)
        for decision in world.decisions:
            results = {}
            for arm in ALL_ARMS:
                terminal, stamped, looks = act(arm, decision)
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
                        if outcome == CORRECT_SETTLEMENT:
                            t[f"{scope}:stampedCorrectSettlements"] += 1
                    if outcome == FALSE_SETTLEMENT:
                        t[f"{scope}:{'flagged' if stamped else 'silent'}FalseSettlements"] += 1

            def silent(arm: str) -> bool:
                return results[arm][0] == FALSE_SETTLEMENT and not results[arm][1]

            lineage_admissible = true_grouping_admissible(decision.evidence, decision.units, CUTS)
            content_admissible = true_grouping_admissible(decision.evidence, decision.units, ALL_CUTS)
            p = paired[key]
            p["decisions"] += 1
            p["lineageAdmissible"] += lineage_admissible
            p["contentAdmissible"] += content_admissible
            p["agreementSilent"] += silent("agreement_rule")
            p["tieredSilent"] += silent("tiered_rule")
            p["contentSilent"] += silent("content_tiered_rule")
            p["tieredOnlySilent"] += silent("tiered_rule") and not silent("content_tiered_rule")
            p["contentOnlySilent"] += silent("content_tiered_rule") and not silent("tiered_rule")
            p["tieredSilentWhereContentRestores"] += (
                silent("tiered_rule") and content_admissible and not lineage_admissible
            )
            p["contentSilentWhereAdmissible"] += silent("content_tiered_rule") and content_admissible

    families: dict[str, dict[str, Any]] = {}
    for (family, cell), by_arm in sorted(tallies.items()):
        p = paired[(family, cell)]
        families.setdefault(family, {})[cell] = {
            "arms": {arm: dict(sorted(counter.items())) for arm, counter in by_arm.items()},
            "admissibility": {
                "decisions": p["decisions"],
                "lineage": p["lineageAdmissible"],
                "lineageAndContent": p["contentAdmissible"],
            },
            "silentComparison": {
                "agreementSilent": p["agreementSilent"],
                "tieredSilent": p["tieredSilent"],
                "contentSilent": p["contentSilent"],
                "tieredOnlySilent": p["tieredOnlySilent"],
                "contentOnlySilent": p["contentOnlySilent"],
                "tieredSilentWhereContentRestores": p["tieredSilentWhereContentRestores"],
                "contentSilentWhereAdmissible": p["contentSilentWhereAdmissible"],
                "p": mcnemar_exact(p["tieredOnlySilent"], p["contentOnlySilent"]),
            },
        }
    return {
        "schema": "minority-prophet.dri5-semantic-result.v1",
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
            missing, _, _ = parse_cell(cell)
            comparison = row["silentComparison"]
            label = f"{family}:{cell}"
            checks[f"{label}:contentNeverSilentWhereTieredIsNot"] = comparison["contentOnlySilent"] == 0
            checks[f"{label}:contentNeverSilentWhereAdmissible"] = comparison["contentSilentWhereAdmissible"] == 0
            if missing == 0:
                decisions = row["arms"]["content_tiered_rule"].get("all:decisions", 0)
                checks[f"{label}:noSilentFalseSettlement"] = comparison["contentSilent"] == 0
                checks[f"{label}:silentRateBoundBelow"] = (zero_event_upper_bound(decisions) or 1) < bound
                continue
            if missing in rule["significance_missing_rates"]:
                if comparison["tieredSilent"] >= rule["minimum_tiered_silent_for_test"]:
                    powered[label] = comparison["p"]
                else:
                    underpowered.append(label)
    adjusted = holm(powered)
    for label, value in adjusted.items():
        family, cell = label.split(":", 1)
        comparison = semantic["families"][family][cell]["silentComparison"]
        checks[f"{label}:fewerSilentThanTiered"] = (
            value < config["familywise_alpha"]
            and comparison["tieredOnlySilent"] > comparison["contentOnlySilent"]
        )
    checks["semanticResultReproducible"] = reproducible
    irreversible = {
        f"{family}:{cell}": {
            arm: row["arms"][arm].get(f"{IRREVERSIBLE}:{FALSE_SETTLEMENT}", 0)
            for arm in ("tiered_rule", "content_tiered_rule")
        }
        for family in rule["families"]
        for cell, row in semantic["families"][family].items()
    }
    return {
        "tests": checks,
        "poweredComparisons": sorted(powered),
        "underpoweredComparisons": underpowered,
        "irreversibleFalseSettlementsReported": irreversible,
        "supported": all(checks.values()),
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
