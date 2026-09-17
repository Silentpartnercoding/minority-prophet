"""DRI-8 scoring and criterion.

Decision outcomes follow DRI-3: correct settlement, false settlement (flagged
when stamped "not robust", silent otherwise), unneeded abstention, required
abstention. A lookup is always available here, so abstaining on a decision whose
true grouping settles is unneeded.

Two things are new.

**The margin split.** A decision is *margin-critical* when merging the true
hidden group would change the settlement the record reaches. Everywhere else the
hidden dependence is real and cannot move the outcome, which is the don't-care
zone a flip budget describes. Prevention is reported on both, because preventing
errors that could not happen is not prevention.

**Merges.** What each learning arm came to believe, split into true merges
(sources that really do share a component) and false ones. A false merge removes
a root from its own side and is how learning can make things worse.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from experiments.dri2.stats import holm, mcnemar_exact
from experiments.dri3.world import IRREVERSIBLE, SETTLED
from experiments.dri8.arms import ARMS, LEARNING_CUTS, Learned, _settle, _with_learned, run_campaign
from experiments.dri8.world import (
    HIDDEN,
    Campaign,
    Decision,
    campaign_hash_row,
    iter_cell_campaigns,
    parse_cell,
)

CORRECT_SETTLEMENT = "correct_settlement"
FALSE_SETTLEMENT = "false_settlement"
UNNEEDED_ABSTENTION = "unneeded_abstention"
REQUIRED_ABSTENTION = "required_abstention"
METHODS = ("track_record", "probe")


def score_decision(decision: Decision, terminal: str) -> str:
    if terminal in SETTLED:
        return CORRECT_SETTLEMENT if terminal == decision.reference else FALSE_SETTLEMENT
    return UNNEEDED_ABSTENTION if decision.reference in SETTLED else REQUIRED_ABSTENTION


def margin_critical(decision: Decision, campaign: Campaign) -> bool:
    """Whether merging the WHOLE true hidden group would change the settlement.

    The trio family shares one component across three sources, so merging only
    two of them tests the wrong counterfactual.
    """
    hidden = sorted(s.source_id for s in campaign.sources if s.component_kind == HIDDEN)
    if len(hidden) < 2:
        return False
    base_terminal, base_stamped, _ = _settle(decision, _with_learned(decision, Learned()), LEARNING_CUTS)
    merged = Learned()
    for other in hidden[1:]:
        merged.merge(hidden[0], other)
    terminal, stamped, _ = _settle(decision, _with_learned(decision, merged), LEARNING_CUTS)
    # Stamping a settlement "not robust" is the protection on offer, so a change
    # from silent to flagged counts as the merge mattering.
    return (terminal, stamped) != (base_terminal, base_stamped)


def _merge_counts(learned: Learned, campaign: Campaign) -> tuple[int, int]:
    component = {s.source_id: s.component for s in campaign.sources}
    true_merges = false_merges = 0
    for group in learned.groups:
        members = sorted(group)
        for index, left in enumerate(members):
            for right in members[index + 1:]:
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
        _, feedback, budget = parse_cell(cell)
        key = (campaign.family, cell)
        # Depends on the decision and the campaign, never on the arm, so it is
        # computed once here rather than per arm inside the loops below.
        critical = tuple(margin_critical(decision, campaign) for decision in campaign.decisions)
        results: dict[str, list] = {}
        for arm in ARMS:
            outcomes, learned = run_campaign(arm, campaign, config, salt, feedback, budget)
            results[arm] = outcomes
            counter = tallies[key][arm]
            if arm in METHODS:
                true_merges, false_merges = _merge_counts(learned, campaign)
                counter["trueMerges"] += true_merges
                counter["falseMerges"] += false_merges
            for decision, outcome, is_critical in zip(campaign.decisions, outcomes, critical, strict=True):
                result = score_decision(decision, outcome.terminal)
                scopes = ("all", decision.decision_class, "critical" if is_critical else "slack")
                for scope in scopes:
                    counter[f"{scope}:decisions"] += 1
                    counter[f"{scope}:{result}"] += 1
                    counter[f"{scope}:looks"] += outcome.looks
                    counter[f"{scope}:probes"] += outcome.probes
                    if result == FALSE_SETTLEMENT:
                        counter[f"{scope}:{'flagged' if outcome.stamped else 'silent'}FalseSettlements"] += 1

        pair = paired[key]
        for index, decision in enumerate(campaign.decisions):
            is_critical = critical[index]

            def silent(arm: str) -> bool:
                outcome = results[arm][index]
                return score_decision(decision, outcome.terminal) == FALSE_SETTLEMENT and not outcome.stamped

            pair["tieredSilent"] += silent("tiered_rule")
            if is_critical:
                pair["criticalTieredSilent"] += silent("tiered_rule")
            for method in METHODS:
                pair[f"{method}:silent"] += silent(method)
                pair[f"{method}:tieredOnlySilent"] += silent("tiered_rule") and not silent(method)
                pair[f"{method}:methodOnlySilent"] += silent(method) and not silent("tiered_rule")
                if is_critical:
                    pair[f"{method}:criticalSilent"] += silent(method)

    families: dict[str, dict[str, Any]] = {}
    for (family, cell), by_arm in sorted(tallies.items()):
        p = paired[(family, cell)]
        comparisons = {
            method: {
                "silent": p[f"{method}:silent"],
                "criticalSilent": p[f"{method}:criticalSilent"],
                "tieredOnlySilent": p[f"{method}:tieredOnlySilent"],
                "methodOnlySilent": p[f"{method}:methodOnlySilent"],
                "p": mcnemar_exact(p[f"{method}:tieredOnlySilent"], p[f"{method}:methodOnlySilent"]),
            }
            for method in METHODS
        }
        families.setdefault(family, {})[cell] = {
            "arms": {arm: dict(sorted(counter.items())) for arm, counter in by_arm.items()},
            "tieredSilent": p["tieredSilent"],
            "criticalTieredSilent": p["criticalTieredSilent"],
            "comparisons": comparisons,
        }
    return {
        "schema": "minority-prophet.dri8-semantic-result.v1",
        "campaigns": campaigns,
        "campaignManifestSha256": manifest.hexdigest(),
        "families": families,
    }


def evaluate_criterion(
    semantic: Mapping[str, Any], config: Mapping[str, Any], reproducible: bool
) -> dict[str, Any]:
    rule = config["success_criterion"]
    checks: dict[str, bool] = {}
    powered: dict[str, float] = {}
    underpowered: list[str] = []

    for family in rule["prevention_families"]:
        for cell, row in semantic["families"][family].items():
            _, _, budget = parse_cell(cell)
            if budget != rule["generous_probe_budget"]:
                continue
            label = f"{family}:{cell}"
            if row["tieredSilent"] >= rule["minimum_tiered_silent_for_test"]:
                powered[label] = row["comparisons"]["probe"]["p"]
            else:
                underpowered.append(label)
    adjusted = holm(powered)
    for label, value in adjusted.items():
        family, cell = label.split(":", 1)
        comparison = semantic["families"][family][cell]["comparisons"]["probe"]
        checks[f"{label}:probeFewerSilentThanTiered"] = (
            value < config["familywise_alpha"]
            and comparison["tieredOnlySilent"] > comparison["methodOnlySilent"]
        )

    harm_family = rule["no_harm_family"]
    for cell, row in semantic["families"][harm_family].items():
        for method in METHODS:
            comparison = row["comparisons"][method]
            worse = (
                comparison["methodOnlySilent"] > comparison["tieredOnlySilent"]
                and comparison["p"] < config["familywise_alpha"]
            )
            checks[f"{harm_family}:{cell}:{method}:noSignificantHarm"] = not worse

    floor = rule["correct_settlement_floor"]
    for family, by_cell in semantic["families"].items():
        for cell, row in by_cell.items():
            tiered = row["arms"]["tiered_rule"].get(f"all:{CORRECT_SETTLEMENT}", 0)
            probe = row["arms"]["probe"].get(f"all:{CORRECT_SETTLEMENT}", 0)
            checks[f"{family}:{cell}:probeCorrectSettlementFloor"] = probe >= floor * tiered

    checks["semanticResultReproducible"] = reproducible
    return {
        "tests": checks,
        "poweredComparisons": sorted(powered),
        "underpoweredComparisons": underpowered,
        "supported": all(checks.values()),
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
