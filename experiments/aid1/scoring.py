"""AID-1 scoring. Criteria copied from the spec that named the policy first.

Fail-closed when the hidden-source family is underpowered. Cost is scored at
α = 1.0 only, as the spec required. The adoption curve is reported and is
not a criterion.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from experiments.dri2.stats import holm, mcnemar_exact
from experiments.aid1.arms import ARMS, BASELINE, CEILING, PRIMARY, THEATRE, is_pivotal, run_decision
from experiments.aid1.world import (
    SETTLED,
    SETTLED_FALSE,
    SETTLED_TRUE,
    Decision,
    campaign_hash_row,
    iter_cell_campaigns,
)

CORRECT_SETTLEMENT = "correct_settlement"
FALSE_SETTLEMENT = "false_settlement"
UNNEEDED_ABSTENTION = "unneeded_abstention"
REQUIRED_ABSTENTION = "required_abstention"


def score_decision(decision: Decision, terminal: str) -> str:
    if terminal in SETTLED:
        return CORRECT_SETTLEMENT if terminal == decision.reference else FALSE_SETTLEMENT
    return UNNEEDED_ABSTENTION if decision.reference in SETTLED else REQUIRED_ABSTENTION


def claim_survives(decision: Decision, terminal: str) -> bool:
    """The true contrary claim is not settled against."""
    against = SETTLED_FALSE if decision.truth else SETTLED_TRUE
    return terminal != against


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
        results: dict[str, list[str]] = {}
        for arm in ARMS:
            outcomes = [run_decision(arm, decision, config) for decision in campaign.decisions]
            results[arm] = outcomes
            counter = tallies[key][arm]
            for decision, terminal, critical in zip(campaign.decisions, outcomes, pivotal, strict=True):
                result = score_decision(decision, terminal)
                counter["decisions"] += 1
                counter[result] += 1
                if result == FALSE_SETTLEMENT:
                    counter["silentFalseSettlements"] += 1
                if decision.mixed:
                    counter["mixedDecisions"] += 1
                if claim_survives(decision, terminal):
                    counter["claimSurvives"] += 1
                if critical:
                    counter["criticalDecisions"] += 1

        p = paired[key]
        for index, decision in enumerate(campaign.decisions):
            critical = pivotal[index]

            def silent(arm: str) -> bool:
                return score_decision(decision, results[arm][index]) == FALSE_SETTLEMENT

            def unneeded(arm: str) -> bool:
                return score_decision(decision, results[arm][index]) == UNNEEDED_ABSTENTION

            p["ladderSilent"] += silent(BASELINE)
            if critical:
                p["criticalLadderSilent"] += silent(BASELINE)
            for arm in ARMS:
                if arm == BASELINE:
                    continue
                p[f"{arm}:silent"] += silent(arm)
                p[f"{arm}:unneeded"] += unneeded(arm)
                p[f"{arm}:ladderOnlySilent"] += silent(BASELINE) and not silent(arm)
                p[f"{arm}:armOnlySilent"] += silent(arm) and not silent(BASELINE)
                if critical:
                    p[f"{arm}:criticalSilent"] += silent(arm)
                    p[f"{arm}:criticalPrevented"] += silent(BASELINE) and not silent(arm)

    families: dict[str, dict[str, Any]] = {}
    for (family, cell), by_arm in sorted(tallies.items()):
        p = paired[(family, cell)]
        families.setdefault(family, {})[cell] = {
            "arms": {arm: dict(sorted(counter.items())) for arm, counter in by_arm.items()},
            "ladderSilent": p["ladderSilent"],
            "criticalLadderSilent": p["criticalLadderSilent"],
            "comparisons": {
                arm: {
                    "silent": p[f"{arm}:silent"],
                    "unneeded": p[f"{arm}:unneeded"],
                    "criticalSilent": p[f"{arm}:criticalSilent"],
                    "criticalPrevented": p[f"{arm}:criticalPrevented"],
                    "ladderOnlySilent": p[f"{arm}:ladderOnlySilent"],
                    "armOnlySilent": p[f"{arm}:armOnlySilent"],
                    "p": mcnemar_exact(p[f"{arm}:ladderOnlySilent"], p[f"{arm}:armOnlySilent"]),
                }
                for arm in ARMS
                if arm != BASELINE
            },
        }
    return {
        "schema": "minority-prophet.aid1-semantic-result.v1",
        "campaigns": campaigns,
        "campaignManifestSha256": manifest.hexdigest(),
        "scope": "criterion on reversible decisions; adoption curve reported, not a pass mark",
        "families": families,
    }


def _alpha_cell(cell: str) -> float:
    return float(cell.split("=", 1)[1])


def evaluate_criterion(
    semantic: Mapping[str, Any], config: Mapping[str, Any], reproducible: bool
) -> dict[str, Any]:
    rule = config["success_criterion"]
    checks: dict[str, bool] = {}
    powered: dict[str, float] = {}
    underpowered: list[str] = []
    alpha = config["familywise_alpha"]
    cost_alpha = rule["cost_adoption_rate"]
    method = PRIMARY

    for family in rule["dependence_families"]:
        for cell, row in semantic["families"][family].items():
            label = f"{method}:{family}:{cell}"
            critical = row["criticalLadderSilent"]
            comparison = row["comparisons"][method]
            if critical < rule["minimum_critical_silent_for_test"]:
                underpowered.append(label)
                continue
            powered[label] = comparison["p"]
            checks[f"{label}:preventsEnoughOfCritical"] = (
                comparison["criticalPrevented"] >= rule["prevention_share"] * critical
            )

    checks["hasPoweredDependenceComparison"] = bool(powered)
    adjusted = holm(powered)
    for label, value in adjusted.items():
        _, family, cell = label.split(":", 2)
        comparison = semantic["families"][family][cell]["comparisons"][method]
        checks[f"{label}:significantlyFewerSilent"] = (
            value < alpha and comparison["ladderOnlySilent"] > comparison["armOnlySilent"]
        )

    for family, by_cell in semantic["families"].items():
        for cell, row in by_cell.items():
            if _alpha_cell(cell) != cost_alpha:
                continue
            comparison = row["comparisons"][method]
            checks[f"{method}:{family}:{cell}:costBound"] = (
                comparison["unneeded"] <= comparison["ladderOnlySilent"]
            )

    for family in rule["theatre_families"]:
        for cell, row in semantic["families"][family].items():
            declared = row["comparisons"][THEATRE]
            attested = row["comparisons"][method]
            checks[f"{THEATRE}:{family}:{cell}:materiallyWorseThanAttested"] = (
                declared["silent"] > attested["silent"]
            )

    for family, by_cell in semantic["families"].items():
        for cell, row in by_cell.items():
            if family not in rule["dependence_families"]:
                continue
            if row["criticalLadderSilent"] < rule["minimum_critical_silent_for_test"]:
                continue
            attested = row["comparisons"][method]
            refuse = row["comparisons"][CEILING]
            attested_correct = row["arms"][method].get(CORRECT_SETTLEMENT, 0)
            refuse_correct = row["arms"][CEILING].get(CORRECT_SETTLEMENT, 0)
            checks[f"{method}:{family}:{cell}:cheaperThanRefuseAll"] = (
                attested_correct > refuse_correct
                and attested["criticalPrevented"] >= refuse["criticalPrevented"]
            )

    for family in rule["suppression_families"]:
        for cell, row in semantic["families"][family].items():
            ladder_survives = row["arms"][BASELINE].get("claimSurvives", 0)
            attested_survives = row["arms"][method].get("claimSurvives", 0)
            checks[f"{method}:{family}:{cell}:doesNotSuppress"] = attested_survives == ladder_survives

    checks["semanticResultReproducible"] = reproducible
    supported = all(checks.values()) and bool(powered)
    return {
        "tests": checks,
        "poweredComparisons": sorted(powered),
        "underpoweredComparisons": underpowered,
        "adoptionCurveReportedOnly": True,
        "supported": supported,
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
