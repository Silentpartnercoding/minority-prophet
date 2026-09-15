"""DRI-3 scoring, cost scorecard and criterion. DRAFT, NOT FROZEN.

Decision outcomes:

- **correct settlement:** settles the way the true grouping does.
- **false settlement:** any other settlement, including settling where the true
  grouping does not settle. It is **flagged** when the arm stamped it "not robust",
  and **silent** otherwise.
- **unneeded abstention:** abstains although the decision was decidable from what
  was available. The true grouping settles, and either a lookup was available or
  the record alone robustly settles it that way.
- **required abstention:** abstains where nothing available could settle it.

Decisions are independent, so a false settlement does not end a world. Every
decision is scored.

World outcomes: **falsely settled** (any false settlement), **complete** (no false
settlement and no unneeded abstention), **incomplete** (no false settlement but at
least one unneeded abstention).
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from typing import Any

from experiments.dri2.stats import holm, mcnemar_exact
from experiments.dri3.arms import ALL_ARMS, act
from experiments.dri3.world import IRREVERSIBLE, REVERSIBLE, SETTLED, Decision, iter_worlds, world_hash_row

CORRECT_SETTLEMENT = "correct_settlement"
FALSE_SETTLEMENT = "false_settlement"
UNNEEDED_ABSTENTION = "unneeded_abstention"
REQUIRED_ABSTENTION = "required_abstention"


def score_decision(decision: Decision, terminal: str) -> str:
    if terminal in SETTLED:
        return CORRECT_SETTLEMENT if terminal == decision.reference else FALSE_SETTLEMENT
    decidable = decision.reference in SETTLED and (
        decision.lookup_available or decision.record_settles_reference
    )
    return UNNEEDED_ABSTENTION if decidable else REQUIRED_ABSTENTION


def zero_event_upper_bound(trials: int, confidence: float = 0.95) -> float | None:
    """Exact one-sided upper bound on a rate when zero events occur in ``trials``."""
    return 1 - (1 - confidence) ** (1 / trials) if trials else None


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 9) if denominator else None


def evaluate(
    config: Mapping[str, Any], salt: str, worlds_per_family: int | None = None
) -> dict[str, Any]:
    tallies: dict[str, dict[str, Counter]] = {
        family: {arm: Counter() for arm in ALL_ARMS} for family in config["families"]
    }
    paired: dict[str, Counter] = {family: Counter() for family in config["families"]}
    manifest = hashlib.sha256()
    worlds = 0
    look_ms, action_ms = config["look_cost_ms"], config["action_cost_ms"]
    for world in iter_worlds(config, salt, worlds_per_family):
        worlds += 1
        manifest.update(world_hash_row(world))
        world_outcomes: dict[str, list[str]] = {arm: [] for arm in ALL_ARMS}
        for decision in world.decisions:
            results = {}
            for arm in ALL_ARMS:
                terminal, stamped, looks = act(arm, decision)
                outcome = score_decision(decision, terminal)
                results[arm] = (outcome, stamped, looks, terminal)
                world_outcomes[arm].append(outcome)
                t = tallies[world.family][arm]
                for scope in ("all", world.condition, decision.decision_class):
                    t[f"{scope}:decisions"] += 1
                    t[f"{scope}:{outcome}"] += 1
                    t[f"{scope}:looks"] += looks
                    t[f"{scope}:virtualMs"] += looks * look_ms + action_ms
                    if terminal in SETTLED and stamped:
                        t[f"{scope}:stampedSettlements"] += 1
                    if outcome == FALSE_SETTLEMENT:
                        t[f"{scope}:{'flagged' if stamped else 'silent'}FalseSettlements"] += 1
            p = paired[world.family]
            agreement_silent = results["agreement_rule"][0] == FALSE_SETTLEMENT and not results["agreement_rule"][1]
            tiered_silent = results["tiered_rule"][0] == FALSE_SETTLEMENT and not results["tiered_rule"][1]
            p["agreementSilent"] += agreement_silent
            p["agreementOnlySilent"] += agreement_silent and not tiered_silent
            p["tieredOnlySilent"] += tiered_silent and not agreement_silent
            if decision.decision_class == REVERSIBLE:
                robust, agreement = results["robustness_everywhere"], results["agreement_rule"]
                p["reversibleExtraLooks"] += max(robust[2] - agreement[2], 0)
                p["reversiblePrevented"] += agreement[0] == FALSE_SETTLEMENT and robust[0] != FALSE_SETTLEMENT
                p["reversibleExtraAbstentions"] += (
                    agreement[0] == CORRECT_SETTLEMENT and robust[0] in (UNNEEDED_ABSTENTION, REQUIRED_ABSTENTION)
                )
        for arm, outcomes in world_outcomes.items():
            t = tallies[world.family][arm]
            if FALSE_SETTLEMENT in outcomes:
                t["worlds:falselySettled"] += 1
            elif UNNEEDED_ABSTENTION in outcomes:
                t["worlds:incomplete"] += 1
            else:
                t["worlds:complete"] += 1

    ceiling = config["reversible_extra_looks_per_prevented_ceiling"]
    families: dict[str, Any] = {}
    overall = Counter()
    for family, by_arm in tallies.items():
        p = paired[family]
        if family in config["recorded_families"]:
            for key in ("reversibleExtraLooks", "reversiblePrevented", "reversibleExtraAbstentions"):
                overall[key] += p[key]
        families[family] = {
            "arms": {arm: dict(sorted(counter.items())) for arm, counter in by_arm.items()},
            "silentComparison": {
                "agreementSilent": p["agreementSilent"],
                "agreementOnlySilent": p["agreementOnlySilent"],
                "tieredOnlySilent": p["tieredOnlySilent"],
                "p": mcnemar_exact(p["agreementOnlySilent"], p["tieredOnlySilent"]),
            },
            "reversibleScorecard": _scorecard(p, ceiling),
        }
    return {
        "schema": "minority-prophet.dri3-semantic-result.v0-draft",
        "worlds": worlds,
        "worldManifestSha256": manifest.hexdigest(),
        "families": families,
        "reversibleScorecardRecordedFamilies": _scorecard(overall, ceiling),
    }


def _scorecard(counts: Mapping[str, int], ceiling: int) -> dict[str, Any]:
    prevented = counts["reversiblePrevented"]
    ratio = counts["reversibleExtraLooks"] / prevented if prevented else None
    return {
        "extraLooks": counts["reversibleExtraLooks"],
        "preventedFalseSettlements": prevented,
        "extraAbstentionsOnCorrectAgreement": counts["reversibleExtraAbstentions"],
        "extraLooksPerPrevented": ratio,
        "ceiling": ceiling,
        "policy": (
            "force looks on reversible decisions"
            if ratio is not None and ratio <= ceiling
            else "stamp non-robust reversible settlements"
        ),
    }


def evaluate_criterion(
    semantic: Mapping[str, Any], config: Mapping[str, Any], reproducible: bool
) -> dict[str, Any]:
    rule = config["success_criterion"]
    bound = rule["maximum_rate_bound"]
    checks: dict[str, bool] = {}
    for family in rule["recorded_families"]:
        tiered = semantic["families"][family]["arms"]["tiered_rule"]
        decisions = tiered.get("all:decisions", 0)
        irreversible = tiered.get(f"{IRREVERSIBLE}:decisions", 0)
        checks[f"{family}:noSilentFalseSettlement"] = tiered.get("all:silentFalseSettlements", 0) == 0
        checks[f"{family}:silentRateBoundBelow"] = (zero_event_upper_bound(decisions) or 1) < bound
        checks[f"{family}:noIrreversibleFalseSettlement"] = tiered.get(f"{IRREVERSIBLE}:{FALSE_SETTLEMENT}", 0) == 0
        checks[f"{family}:irreversibleRateBoundBelow"] = (zero_event_upper_bound(irreversible) or 1) < bound
    powered = {
        family: semantic["families"][family]["silentComparison"]["p"]
        for family in rule["fewer_silent_than_agreement_in"]
        if semantic["families"][family]["silentComparison"]["agreementSilent"]
        >= rule["minimum_agreement_silent_for_test"]
    }
    adjusted = holm(powered)
    underpowered = []
    for family in rule["fewer_silent_than_agreement_in"]:
        row = semantic["families"][family]["silentComparison"]
        if family in adjusted:
            checks[f"{family}:fewerSilentThanAgreement"] = (
                adjusted[family] < config["familywise_alpha"]
                and row["agreementOnlySilent"] > row["tieredOnlySilent"]
            )
        else:
            underpowered.append(family)
    checks["semanticResultReproducible"] = reproducible
    return {"tests": checks, "underpoweredComparisons": underpowered, "supported": all(checks.values())}


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
