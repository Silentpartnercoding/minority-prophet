"""DRI-11 scoring. Criteria copied from the spec that named the methods first.

Fail-closed when underpowered. Cost bound is per family: unneeded abstentions
may not exceed silent false settlements prevented. On a family the baseline
already gets right, any refusal fails that bound.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from experiments.dri2.stats import holm, mcnemar_exact
from experiments.dri3.world import REVERSIBLE, SETTLED
from experiments.dri9.rule import is_pivotal
from experiments.dri11.arms import ARMS, PRIMARY, SECONDARY, SIGNAL_ARMS, run_campaign
from experiments.dri11.world import Campaign, Decision, campaign_hash_row, iter_cell_campaigns

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
            if arm in SIGNAL_ARMS or arm == PRIMARY:
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

            def unneeded(arm: str) -> bool:
                return score_decision(decision, results[arm][index].terminal) == UNNEEDED_ABSTENTION

            p["reversibleTieredSilent"] += silent("tiered_rule")
            if critical:
                p["criticalTieredSilent"] += silent("tiered_rule")
            for arm in CONTENDERS:
                p[f"{arm}:silent"] += silent(arm)
                p[f"{arm}:unneeded"] += unneeded(arm)
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
                    "unneeded": p[f"{arm}:unneeded"],
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
        "schema": "minority-prophet.dri11-semantic-result.v1",
        "campaigns": campaigns,
        "campaignManifestSha256": manifest.hexdigest(),
        "scope": "criterion on reversible decisions; irreversible reported without a pass mark",
        "families": families,
    }


def evaluate_criterion(
    semantic: Mapping[str, Any], config: Mapping[str, Any], reproducible: bool
) -> dict[str, Any]:
    rule = config["success_criterion"]
    checks: dict[str, bool] = {}
    powered: dict[str, float] = {}
    underpowered: list[str] = []
    alpha = config["familywise_alpha"]

    for method in (PRIMARY, SECONDARY):
        for family in rule["dependence_families"]:
            for cell, row in semantic["families"][family].items():
                label = f"{method}:{family}:{cell}"
                critical = row["criticalTieredSilent"]
                comparison = row["comparisons"][method]
                if critical < rule["minimum_critical_silent_for_test"]:
                    underpowered.append(label)
                    continue
                powered[label] = comparison["p"]
                checks[f"{label}:preventsEnoughOfCritical"] = (
                    comparison["criticalPrevented"] >= rule["refusal_prevented_share"] * critical
                )

    primary_powered = [label for label in powered if label.startswith(f"{PRIMARY}:")]
    secondary_powered = [label for label in powered if label.startswith(f"{SECONDARY}:")]
    checks["hasPoweredDependenceComparison"] = bool(primary_powered)
    adjusted = holm(powered)
    for label, value in adjusted.items():
        method, family, cell = label.split(":", 2)
        comparison = semantic["families"][family][cell]["comparisons"][method]
        checks[f"{label}:significantlyFewerSilent"] = (
            value < alpha and comparison["tieredOnlySilent"] > comparison["armOnlySilent"]
        )

    for family, by_cell in semantic["families"].items():
        for cell, row in by_cell.items():
            refusal = row["comparisons"][PRIMARY]
            checks[f"{PRIMARY}:{family}:{cell}:costBound"] = (
                refusal["unneeded"] <= refusal["tieredOnlySilent"]
            )
            tiered = row["arms"]["tiered_rule"].get(f"{REVERSIBLE}:{CORRECT_SETTLEMENT}", 0)
            mine = row["arms"][PRIMARY].get(f"{REVERSIBLE}:{CORRECT_SETTLEMENT}", 0)
            checks[f"{PRIMARY}:{family}:{cell}:correctSettlementFloor"] = (
                mine >= rule["refusal_correct_settlement_floor"] * tiered
            )

            composite = row["comparisons"][SECONDARY]
            if family in rule["dependence_families"] and row["criticalTieredSilent"] >= rule["minimum_critical_silent_for_test"]:
                checks[f"{SECONDARY}:{family}:{cell}:beatsRefusalOnCost"] = (
                    composite["unneeded"] < refusal["unneeded"]
                    and composite["criticalPrevented"] >= refusal["criticalPrevented"]
                )
            if family in rule["collapse_families"]:
                false_m = row["arms"][SECONDARY].get("falseMerges", 0)
                true_m = row["arms"][SECONDARY].get("trueMerges", 0)
                checks[f"{SECONDARY}:{family}:{cell}:didNotCollapse"] = false_m <= true_m
                comp_correct = row["arms"][SECONDARY].get(f"{REVERSIBLE}:{CORRECT_SETTLEMENT}", 0)
                checks[f"{SECONDARY}:{family}:{cell}:correctSettlementFloor"] = (
                    comp_correct >= rule["instrument_correct_settlement_floor"] * tiered
                )

    checks["semanticResultReproducible"] = reproducible
    supported_primary = all(
        v for k, v in checks.items()
        if k == "semanticResultReproducible"
        or k == "hasPoweredDependenceComparison"
        or k.startswith(f"{PRIMARY}:")
    ) and bool(primary_powered)
    supported_secondary = all(
        v for k, v in checks.items() if k.startswith(f"{SECONDARY}:")
    ) and bool(secondary_powered)
    return {
        "tests": checks,
        "poweredComparisons": sorted(powered),
        "underpoweredComparisons": underpowered,
        "irreversibleReportedOnly": True,
        "supportedPrimary": supported_primary,
        "supportedSecondary": supported_secondary,
        "supported": supported_primary,
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
