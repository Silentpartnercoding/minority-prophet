"""DRI-4 scoring and criterion. DRAFT, NOT FROZEN.

Decisions are scored exactly as in DRI-3 (`experiments.dri3.scoring.score_decision`)
by the frozen DRI-3 arms. Results are kept per family and per (missing, spurious)
cell, and are never pooled across cells.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from experiments.dri2.stats import holm, mcnemar_exact
from experiments.dri3.arms import ALL_ARMS, act
from experiments.dri3.scoring import (
    CORRECT_SETTLEMENT,
    FALSE_SETTLEMENT,
    score_decision,
    zero_event_upper_bound,
)
from experiments.dri3.world import IRREVERSIBLE, REVERSIBLE, SETTLED
from experiments.dri4.world import cell_key, iter_cell_worlds, world_hash_row


def _parse(cell: str) -> tuple[float, float]:
    m, s = cell.split("|")
    return float(m.split("=")[1]), float(s.split("=")[1])


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
        manifest.update(world_hash_row(cell, world))
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
                    if outcome == FALSE_SETTLEMENT:
                        t[f"{scope}:{'flagged' if stamped else 'silent'}FalseSettlements"] += 1
            p = paired[key]
            agreement_silent = results["agreement_rule"][0] == FALSE_SETTLEMENT and not results["agreement_rule"][1]
            tiered_silent = results["tiered_rule"][0] == FALSE_SETTLEMENT and not results["tiered_rule"][1]
            p["agreementSilent"] += agreement_silent
            p["tieredSilent"] += tiered_silent
            p["agreementOnlySilent"] += agreement_silent and not tiered_silent
            p["tieredOnlySilent"] += tiered_silent and not agreement_silent
            if decision.decision_class == REVERSIBLE:
                robust, agreement = results["robustness_everywhere"], results["agreement_rule"]
                p["reversibleExtraLooks"] += max(robust[2] - agreement[2], 0)
                p["reversiblePrevented"] += agreement[0] == FALSE_SETTLEMENT and robust[0] != FALSE_SETTLEMENT

    families: dict[str, dict[str, Any]] = {}
    for (family, cell), by_arm in sorted(tallies.items()):
        p = paired[(family, cell)]
        prevented = p["reversiblePrevented"]
        families.setdefault(family, {})[cell] = {
            "arms": {arm: dict(sorted(counter.items())) for arm, counter in by_arm.items()},
            "silentComparison": {
                "agreementSilent": p["agreementSilent"],
                "tieredSilent": p["tieredSilent"],
                "agreementOnlySilent": p["agreementOnlySilent"],
                "tieredOnlySilent": p["tieredOnlySilent"],
                "p": mcnemar_exact(p["agreementOnlySilent"], p["tieredOnlySilent"]),
            },
            "reversibleScorecard": {
                "extraLooks": p["reversibleExtraLooks"],
                "preventedFalseSettlements": prevented,
                "extraLooksPerPrevented": p["reversibleExtraLooks"] / prevented if prevented else None,
            },
        }
    return {
        "schema": "minority-prophet.dri4-semantic-result.v0-draft",
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
            missing, _ = _parse(cell)
            comparison = row["silentComparison"]
            tiered = row["arms"]["tiered_rule"]
            label = f"{family}:{cell}"
            if missing == 0:
                checks[f"{label}:noSilentFalseSettlement"] = comparison["tieredSilent"] == 0
                checks[f"{label}:silentRateBoundBelow"] = (
                    zero_event_upper_bound(tiered.get("all:decisions", 0)) or 1
                ) < bound
                continue
            checks[f"{label}:tieredSilentNotMoreThanAgreement"] = (
                comparison["tieredSilent"] <= comparison["agreementSilent"]
            )
            if missing in rule["significance_missing_rates"]:
                if comparison["agreementSilent"] >= rule["minimum_agreement_silent_for_test"]:
                    powered[label] = comparison["p"]
                else:
                    underpowered.append(label)
    adjusted = holm(powered)
    for label, value in adjusted.items():
        family, cell = label.split(":", 1)
        comparison = semantic["families"][family][cell]["silentComparison"]
        checks[f"{label}:fewerSilentThanAgreement"] = (
            value < config["familywise_alpha"]
            and comparison["agreementOnlySilent"] > comparison["tieredOnlySilent"]
        )
    checks["semanticResultReproducible"] = reproducible
    irreversible = {
        f"{family}:{cell}": {
            "falseSettlements": row["arms"]["tiered_rule"].get(f"{IRREVERSIBLE}:{FALSE_SETTLEMENT}", 0),
            "decisions": row["arms"]["tiered_rule"].get(f"{IRREVERSIBLE}:decisions", 0),
        }
        for family in rule["families"]
        for cell, row in semantic["families"][family].items()
    }
    return {
        "tests": checks,
        "underpoweredComparisons": underpowered,
        "irreversibleFalseSettlementsReported": irreversible,
        "supported": all(checks.values()),
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


__all__ = ["CORRECT_SETTLEMENT", "cell_key", "evaluate", "evaluate_criterion", "semantic_hash"]
