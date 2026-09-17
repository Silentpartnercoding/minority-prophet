"""DRI-9 scoring and criterion.

Outcomes follow DRI-3: correct settlement; false settlement, flagged when stamped
and silent otherwise; unneeded abstention; required abstention.

**Scoped to reversible decisions, by owner decision on 2026-09-16.** In this
world the irreversible path settles only when the record is robust and otherwise
looks, and the lookup is blind to what an arm believes — so belief cannot move it
at all. Measured on the development world: believing the focus group changed 0 of
360 irreversible decisions in every family, against 233 and 279 reversible ones
in the hidden families. A criterion spanning both would dilute the effect with
decisions no instrument could touch. Irreversible decisions are tallied and
reported; they carry no pass mark. What belief should have to clear before it is
allowed to act on an irreversible decision is a separate question, deliberately
left open.

**The margin split** uses `rule.is_pivotal` against the focus group — the same
function the arms decide with, so the situations counted as critical and the rule
being tested cannot drift apart, which is what went wrong in DRI-8.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from experiments.dri2.stats import holm, mcnemar_exact
from experiments.dri3.world import REVERSIBLE, SETTLED
from experiments.dri9.arms import ARMS, METHOD, SIGNAL_ARMS, run_campaign
from experiments.dri9.rule import is_pivotal
from experiments.dri9.world import Campaign, Decision, campaign_hash_row, iter_cell_campaigns

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
        "schema": "minority-prophet.dri9-semantic-result.v1",
        "campaigns": campaigns,
        "campaignManifestSha256": manifest.hexdigest(),
        "scope": "criterion on reversible decisions; irreversible reported without a pass mark",
        "families": families,
    }


def evaluate_criterion(
    semantic: Mapping[str, Any], config: Mapping[str, Any], reproducible: bool
) -> dict[str, Any]:
    rule = config["success_criterion"]
    method = rule["method_under_test"]
    checks: dict[str, bool] = {}
    powered: dict[str, float] = {}
    underpowered: list[str] = []

    for family in rule["hidden_families"]:
        for cell, row in semantic["families"][family].items():
            label = f"{family}:{cell}"
            critical = row["criticalTieredSilent"]
            comparison = row["comparisons"][method]
            if critical < rule["minimum_critical_silent_for_test"]:
                underpowered.append(label)
                continue
            powered[label] = comparison["p"]
            checks[f"{label}:preventsEnoughOfCritical"] = (
                comparison["criticalPrevented"] >= rule["minimum_prevented_share_of_critical"] * critical
            )
    adjusted = holm(powered)
    for label, value in adjusted.items():
        family, cell = label.split(":", 1)
        comparison = semantic["families"][family][cell]["comparisons"][method]
        checks[f"{label}:significantlyFewerSilent"] = (
            value < config["familywise_alpha"] and comparison["tieredOnlySilent"] > comparison["armOnlySilent"]
        )

    harm = rule["no_harm_family"]
    for cell, row in semantic["families"][harm].items():
        for arm, comparison in row["comparisons"].items():
            worse = (
                comparison["armOnlySilent"] > comparison["tieredOnlySilent"]
                and comparison["p"] < config["familywise_alpha"]
            )
            checks[f"{harm}:{cell}:{arm}:noSignificantHarm"] = not worse
        checks[f"{harm}:{cell}:{method}:falseMergesNotAboveTrue"] = (
            row["arms"][method].get("falseMerges", 0) <= row["arms"][method].get("trueMerges", 0)
        )

    for family, by_cell in semantic["families"].items():
        for cell, row in by_cell.items():
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
