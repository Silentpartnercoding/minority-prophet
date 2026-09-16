"""DRI-10 scoring. Fail-closed when nothing was tested.

Reuses DRI-9 outcomes and the reversible scope. Changes the bar:

- An experiment with no powered hidden-family cell is **not** supported.
- The 25% floor is scored only on `marked_hidden_pair` (the one family where
  bait's assumption is true). `unmarked_hidden_pair` is the mechanism contrast,
  not a second floor.
- At the lowest leak, prevention on the marked hidden pair must beat prevention
  on the unmarked pair by the stated margin. If they match, the mark is not
  what did the work.
- Harm families keep the method's correct-settlement floor. `common_carrier`
  also fails the method if it systematically merges the library.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from experiments.dri2.stats import holm, mcnemar_exact
from experiments.dri3.world import REVERSIBLE, SETTLED
from experiments.dri10.arms import ARMS, METHOD, SIGNAL_ARMS, run_campaign
from experiments.dri9.rule import is_pivotal
from experiments.dri10.world import Campaign, Decision, campaign_hash_row, cell_key, iter_cell_campaigns

CORRECT_SETTLEMENT = "correct_settlement"
FALSE_SETTLEMENT = "false_settlement"
UNNEEDED_ABSTENTION = "unneeded_abstention"
REQUIRED_ABSTENTION = "required_abstention"
CONTENDERS = tuple(arm for arm in ARMS if arm not in ("tiered_rule", "oracle_reference"))


def score_decision(decision: Decision, terminal: str) -> str:
    if terminal in SETTLED:
        return CORRECT_SETTLEMENT if terminal == decision.reference else FALSE_SETTLEMENT
    return UNNEEDED_ABSTENTION if decision.reference in SETTLED else REQUIRED_ABSTENTION


def _merge_counts(belief: Any, campaign: Campaign) -> tuple[int, int]:
    component = {s.source_id: s.component for s in campaign.sources}
    true_merges = false_merges = 0
    for left, right in belief.pairs():
        shared = component.get(left) is not None and component.get(left) == component.get(right)
        true_merges += shared
        false_merges += not shared
    return true_merges, false_merges


def evaluate(
    config: Mapping[str, Any], salt: str, campaigns_per_family: int | None = None
) -> dict[str, Any]:
    tallies: dict[tuple[str, str], dict[str, Counter]] = defaultdict(lambda: {arm: Counter() for arm in ARMS})
    paired: dict[tuple[str, str], Counter] = defaultdict(Counter)
    manifest = hashlib.sha256()
    campaigns = 0
    for cell, campaign in iter_cell_campaigns(config, salt, campaigns_per_family):
        campaigns += 1
        manifest.update(campaign_hash_row(cell, campaign))
        key = (campaign.family, cell)
        pivotal = tuple(is_pivotal(d, campaign.focus_group) for d in campaign.decisions)
        results: dict[str, list] = {}
        for arm in ARMS:
            outcomes, belief = run_campaign(arm, campaign, config, salt)
            results[arm] = outcomes
            counter = tallies[key][arm]
            if arm in SIGNAL_ARMS:
                true_merges, false_merges = _merge_counts(belief, campaign)
                counter["trueMerges"] += true_merges
                counter["falseMerges"] += false_merges
            for decision, outcome, critical in zip(campaign.decisions, outcomes, pivotal, strict=True):
                result = score_decision(decision, outcome.terminal)
                reversible = decision.decision_class == REVERSIBLE
                scopes = ["all", decision.decision_class]
                if reversible:
                    scopes.append("reversible:critical" if critical else "reversible:slack")
                for scope in scopes:
                    counter[f"{scope}:decisions"] += 1
                    counter[f"{scope}:{result}"] += 1
                    counter[f"{scope}:interventions"] += outcome.interventions
                    if result == FALSE_SETTLEMENT:
                        counter[f"{scope}:{'flagged' if outcome.stamped else 'silent'}FalseSettlements"] += 1

        p = paired[key]
        for index, decision in enumerate(campaign.decisions):
            if decision.decision_class != REVERSIBLE:
                continue
            critical = pivotal[index]

            def silent(arm: str) -> bool:
                outcome = results[arm][index]
                return score_decision(decision, outcome.terminal) == FALSE_SETTLEMENT and not outcome.stamped

            p["reversibleTieredSilent"] += silent("tiered_rule")
            if critical:
                p["criticalTieredSilent"] += silent("tiered_rule")
            for arm in CONTENDERS:
                p[f"{arm}:silent"] += silent(arm)
                p[f"{arm}:tieredOnlySilent"] += silent("tiered_rule") and not silent(arm)
                p[f"{arm}:armOnlySilent"] += silent(arm) and not silent("tiered_rule")
                if critical:
                    p[f"{arm}:criticalSilent"] += silent(arm)
                    p[f"{arm}:criticalPrevented"] += silent("tiered_rule") and not silent(arm)

    families: dict[str, dict[str, Any]] = {}
    for (family, cell), by_arm in sorted(tallies.items()):
        p = paired[(family, cell)]
        families.setdefault(family, {})[cell] = {
            "arms": {arm: dict(sorted(counter.items())) for arm, counter in by_arm.items()},
            "reversibleTieredSilent": p["reversibleTieredSilent"],
            "criticalTieredSilent": p["criticalTieredSilent"],
            "comparisons": {
                arm: {
                    "silent": p[f"{arm}:silent"],
                    "criticalSilent": p[f"{arm}:criticalSilent"],
                    "criticalPrevented": p[f"{arm}:criticalPrevented"],
                    "tieredOnlySilent": p[f"{arm}:tieredOnlySilent"],
                    "armOnlySilent": p[f"{arm}:armOnlySilent"],
                    "p": mcnemar_exact(p[f"{arm}:tieredOnlySilent"], p[f"{arm}:armOnlySilent"]),
                }
                for arm in CONTENDERS
            },
        }
    return {
        "schema": "minority-prophet.dri10-semantic-result.v1",
        "campaigns": campaigns,
        "campaignManifestSha256": manifest.hexdigest(),
        "scope": "criterion on reversible decisions; irreversible reported without a pass mark",
        "families": families,
    }


def _share(row: Mapping[str, Any], arm: str) -> float | None:
    critical = row["criticalTieredSilent"]
    if critical <= 0:
        return None
    return row["comparisons"][arm]["criticalPrevented"] / critical


def evaluate_criterion(
    semantic: Mapping[str, Any], config: Mapping[str, Any], reproducible: bool
) -> dict[str, Any]:
    rule = config["success_criterion"]
    method = rule["method_under_test"]
    checks: dict[str, bool] = {}
    powered: dict[str, float] = {}
    underpowered: list[str] = []
    floor_family = rule["floor_family"]

    for cell, row in semantic["families"][floor_family].items():
        label = f"{floor_family}:{cell}"
        critical = row["criticalTieredSilent"]
        comparison = row["comparisons"][method]
        if critical < rule["minimum_critical_silent_for_test"]:
            underpowered.append(label)
            continue
        powered[label] = comparison["p"]
        checks[f"{label}:preventsEnoughOfCritical"] = (
            comparison["criticalPrevented"] >= rule["minimum_prevented_share_of_critical"] * critical
        )

    checks["hasPoweredFloorComparison"] = bool(powered)
    adjusted = holm(powered)
    for label, value in adjusted.items():
        family, cell = label.split(":", 1)
        comparison = semantic["families"][family][cell]["comparisons"][method]
        checks[f"{label}:significantlyFewerSilent"] = (
            value < config["familywise_alpha"] and comparison["tieredOnlySilent"] > comparison["armOnlySilent"]
        )

    contrast = rule["mechanism_contrast_family"]
    min_leak = min(config["marker_leaks"])
    margin = rule["minimum_mark_advantage"]
    for pickup in config["marker_pickups"]:
        marked_cell = cell_key(pickup, min_leak)
        unmarked_cell = cell_key(pickup, min_leak)
        marked = semantic["families"][floor_family][marked_cell]
        unmarked = semantic["families"][contrast][unmarked_cell]
        if (
            marked["criticalTieredSilent"] < rule["minimum_critical_silent_for_test"]
            or unmarked["criticalTieredSilent"] < rule["minimum_critical_silent_for_test"]
        ):
            checks[f"pickup={pickup}|leak={min_leak}:markContrastUnderpowered"] = False
            continue
        marked_share = _share(marked, method)
        unmarked_share = _share(unmarked, method)
        checks[f"pickup={pickup}|leak={min_leak}:markDoesTheWork"] = (
            marked_share is not None
            and unmarked_share is not None
            and marked_share >= unmarked_share + margin
        )

    for family in rule["harm_families"]:
        for cell, row in semantic["families"][family].items():
            comparison = row["comparisons"][method]
            worse = (
                comparison["armOnlySilent"] > comparison["tieredOnlySilent"]
                and comparison["p"] < config["familywise_alpha"]
            )
            checks[f"{family}:{cell}:{method}:noSignificantHarm"] = not worse
            tiered = row["arms"]["tiered_rule"].get(f"{REVERSIBLE}:{CORRECT_SETTLEMENT}", 0)
            mine = row["arms"][method].get(f"{REVERSIBLE}:{CORRECT_SETTLEMENT}", 0)
            checks[f"{family}:{cell}:{method}:correctSettlementFloor"] = (
                mine >= rule["correct_settlement_floor"] * tiered
            )
            if family == "common_carrier":
                false_merges = row["arms"][method].get("falseMerges", 0)
                campaigns = config["campaigns_per_family"]
                checks[f"{family}:{cell}:{method}:didNotCollapseTheLibrary"] = (
                    false_merges <= rule["maximum_false_merges_per_campaign"] * campaigns
                )

    for family, by_cell in semantic["families"].items():
        for cell, row in by_cell.items():
            if family != floor_family:
                continue
            tiered = row["arms"]["tiered_rule"].get(f"{REVERSIBLE}:{CORRECT_SETTLEMENT}", 0)
            mine = row["arms"][method].get(f"{REVERSIBLE}:{CORRECT_SETTLEMENT}", 0)
            checks[f"{family}:{cell}:{method}:correctSettlementFloor"] = (
                mine >= rule["correct_settlement_floor"] * tiered
            )
            comparison = row["comparisons"][method]
            prevented = comparison["tieredOnlySilent"] - comparison["armOnlySilent"]
            spent = row["arms"][method].get(f"{REVERSIBLE}:interventions", 0)
            checks[f"{family}:{cell}:{method}:interventionCeiling"] = (
                (prevented <= 0 and spent == 0)
                or (prevented > 0 and spent / prevented <= rule["maximum_interventions_per_prevented"])
            )

    checks["semanticResultReproducible"] = reproducible
    return {
        "tests": checks,
        "poweredComparisons": sorted(powered),
        "underpoweredComparisons": underpowered,
        "irreversibleReportedOnly": True,
        "supported": all(checks.values()),
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
