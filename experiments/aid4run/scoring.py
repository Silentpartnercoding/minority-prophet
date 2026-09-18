"""AID-4 scoring. Both criterion sets copied verbatim from the frozen draft.

Policy B is scored on the draft's section 5, all five criteria, on reversible
decisions, powered cells only, Holm-corrected, failing closed when underpowered.
Policy C is scored on section 6 and on nothing else: it loses no settlements and
prevents no errors by construction, so prevention would be meaningless for it.

Nothing is renumbered, softened or added. Where the draft leaves a scope
unstated the scope is fixed here and in `PREREGISTRATION.md` section 6, before
any salt is read:

- Criterion 1 and criterion 3 are scored on the hidden-source cells, which are
  the cells where prevention is defined at all.
- Criterion 2 is self-scoping, exactly as worded: it is a pass mark in every
  family where the baseline makes at least one margin-critical silent false
  settlement, and a reported figure everywhere else.
- Criterion 4 is scored in both minority families.
- Criterion 5 is scored in the families where the baseline is already right and
  nothing is hidden.
- C's cells are (family, adoption rate), as everywhere else in this series, and
  a cell is powered for C only when the baseline produces both outcome classes
  in it. Pooling families would let the balance of the world set the AUC; the
  pooled figure is computed and reported, and it is not a pass mark.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from experiments.aid4run.arms import (
    ARMS,
    BASELINE,
    CEILING,
    PRIMARY_B,
    PRIMARY_C,
    exposure_scalar,
    exposure_share,
    is_pivotal,
    run_decision,
)
from experiments.aid4run.world import (
    SETTLED,
    SETTLED_FALSE,
    SETTLED_TRUE,
    Decision,
    campaign_hash_row,
    error_class,
    iter_cell_campaigns,
)
from experiments.dri2.stats import holm, mcnemar_exact

CORRECT_SETTLEMENT = "correct_settlement"
FALSE_SETTLEMENT = "false_settlement"
UNNEEDED_ABSTENTION = "unneeded_abstention"
REQUIRED_ABSTENTION = "required_abstention"


class ConfirmatorySaltRefused(RuntimeError):
    """Raised rather than evaluating the confirmatory salt during development.

    The confirmatory salt is passed to nothing until a registered run exists.
    `tests/test_aid4_protocol.py` asserts this refusal fires.
    """


def score_decision(decision: Decision, terminal: str) -> str:
    if terminal in SETTLED:
        return CORRECT_SETTLEMENT if terminal == decision.reference else FALSE_SETTLEMENT
    return UNNEEDED_ABSTENTION if decision.reference in SETTLED else REQUIRED_ABSTENTION


def claim_survives(decision: Decision, terminal: str) -> bool:
    """The true contrary claim is not settled against. Criterion 4's metric."""
    against = SETTLED_FALSE if decision.truth else SETTLED_TRUE
    return terminal != against


def settles_for_truth(decision: Decision, terminal: str) -> bool:
    """Reported, never a pass mark.

    Criterion 4 asks only whether a claim was settled *against*. In the
    `minority_wins` family the baseline settles *for* the minority's true claim
    and an abstaining arm does not, and criterion 4 as frozen cannot see the
    difference. This counter is what makes that visible in the record.
    """
    return terminal == (SETTLED_TRUE if decision.truth else SETTLED_FALSE)


def auc_from_histograms(positive: Mapping[str, int], negative: Mapping[str, int]) -> float | None:
    """P(exposure ranks a silent false settlement above a correct one).

    Ties score 0.5, which is what a figure that cannot separate two decisions
    has earned. Exact, computed over histograms rather than sampled.
    """
    n_pos = sum(positive.values())
    n_neg = sum(negative.values())
    if n_pos == 0 or n_neg == 0:
        return None
    total = 0.0
    for value_pos, count_pos in positive.items():
        for value_neg, count_neg in negative.items():
            if float(value_pos) > float(value_neg):
                total += count_pos * count_neg
            elif float(value_pos) == float(value_neg):
                total += 0.5 * count_pos * count_neg
    return total / (n_pos * n_neg)


def variation_share(histogram: Mapping[str, int]) -> float | None:
    """Share of settlements whose exposure differs from the modal value."""
    total = sum(histogram.values())
    if total == 0:
        return None
    modal = max(sorted(histogram.items()), key=lambda item: item[1])[1]
    return (total - modal) / total


def _merge(into: dict[str, int], other: Mapping[str, int]) -> None:
    for key, value in other.items():
        into[key] = into.get(key, 0) + value


def evaluate(
    config: Mapping[str, Any],
    salt: str,
    campaigns_per_family: int | None = None,
    *,
    confirmatory: bool = False,
) -> dict[str, Any]:
    """Semantic result over the generated campaigns. Development salt by default.

    `confirmatory=True` is the only way to evaluate the confirmatory salt and
    nothing in this repository passes it. There is deliberately no runner in
    this package: a confirmatory run needs a registration of its own.
    """
    if salt == config.get("confirmatory_salt") and not confirmatory:
        raise ConfirmatorySaltRefused(
            "the AID-4 confirmatory salt is frozen and unread; a confirmatory "
            "run must be registered and must pass confirmatory=True explicitly"
        )

    error = error_class(config)
    tallies: dict[tuple[str, str], dict[str, Counter]] = defaultdict(
        lambda: {arm: Counter() for arm in ARMS}
    )
    paired: dict[tuple[str, str], Counter] = defaultdict(Counter)
    exposure: dict[tuple[str, str], dict[str, dict[str, int]]] = defaultdict(
        lambda: {"false": {}, "correct": {}, "falseShare": {}, "correctShare": {}}
    )
    manifest = hashlib.sha256()
    campaigns = 0

    for cell, campaign in iter_cell_campaigns(config, salt, campaigns_per_family):
        campaigns += 1
        manifest.update(campaign_hash_row(cell, campaign))
        key = (campaign.family, cell)
        pivotal = tuple(is_pivotal(d, campaign.focus_group, error) for d in campaign.decisions)
        results: dict[str, list[str]] = {}
        for arm in ARMS:
            outcomes = [run_decision(arm, decision, config) for decision in campaign.decisions]
            results[arm] = outcomes
            counter = tallies[key][arm]
            for decision, terminal, critical in zip(
                campaign.decisions, outcomes, pivotal, strict=True
            ):
                result = score_decision(decision, terminal)
                counter["decisions"] += 1
                counter[result] += 1
                if terminal in SETTLED:
                    counter["settlements"] += 1
                if result == FALSE_SETTLEMENT:
                    counter["silentFalseSettlements"] += 1
                if decision.mixed:
                    counter["mixedDecisions"] += 1
                if claim_survives(decision, terminal):
                    counter["claimSurvives"] += 1
                if settles_for_truth(decision, terminal):
                    counter["settlesForTruth"] += 1
                if critical:
                    counter["criticalDecisions"] += 1

        p = paired[key]
        histograms = exposure[key]
        for index, decision in enumerate(campaign.decisions):
            critical = pivotal[index]

            def silent(arm: str, index: int = index, decision: Decision = decision) -> bool:
                return score_decision(decision, results[arm][index]) == FALSE_SETTLEMENT

            def unneeded(arm: str, index: int = index, decision: Decision = decision) -> bool:
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

            if results[PRIMARY_C][index] != results[BASELINE][index]:
                p["pricedDivergesFromLadder"] += 1

            # Policy C is scored on the baseline's settlements, which are also
            # C's own settlements — identical by construction, and checked.
            baseline_terminal = results[BASELINE][index]
            if baseline_terminal in SETTLED:
                outcome = score_decision(decision, baseline_terminal)
                bucket = "false" if outcome == FALSE_SETTLEMENT else "correct"
                value = str(exposure_scalar(decision))
                histograms[bucket][value] = histograms[bucket].get(value, 0) + 1
                share = str(exposure_share(decision))
                histograms[f"{bucket}Share"][share] = (
                    histograms[f"{bucket}Share"].get(share, 0) + 1
                )

    families: dict[str, dict[str, Any]] = {}
    pooled: dict[str, dict[str, dict[str, int]]] = {}
    for (family, cell), by_arm in sorted(tallies.items()):
        p = paired[(family, cell)]
        histograms = exposure[(family, cell)]
        combined: dict[str, int] = {}
        _merge(combined, histograms["false"])
        _merge(combined, histograms["correct"])
        pooled_cell = pooled.setdefault(cell, {"false": {}, "correct": {}})
        _merge(pooled_cell["false"], histograms["false"])
        _merge(pooled_cell["correct"], histograms["correct"])
        families.setdefault(family, {})[cell] = {
            "arms": {arm: dict(sorted(counter.items())) for arm, counter in by_arm.items()},
            "ladderSilent": p["ladderSilent"],
            "criticalLadderSilent": p["criticalLadderSilent"],
            "pricedDivergesFromLadder": p["pricedDivergesFromLadder"],
            "exposure": {
                "false": dict(sorted(histograms["false"].items(), key=lambda kv: float(kv[0]))),
                "correct": dict(
                    sorted(histograms["correct"].items(), key=lambda kv: float(kv[0]))
                ),
                "settlements": sum(combined.values()),
                "auc": auc_from_histograms(histograms["false"], histograms["correct"]),
                "variationShare": variation_share(combined),
                "aucOnShare": auc_from_histograms(
                    histograms["falseShare"], histograms["correctShare"]
                ),
            },
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
        "schema": "minority-prophet.aid4-semantic-result.v1",
        "campaigns": campaigns,
        "campaignManifestSha256": manifest.hexdigest(),
        "scope": "criterion on reversible decisions; adoption curve reported, not a pass mark",
        "families": families,
        "pooledExposureByCell": {
            cell: {
                "auc": auc_from_histograms(hist["false"], hist["correct"]),
                "false": dict(sorted(hist["false"].items(), key=lambda kv: float(kv[0]))),
                "correct": dict(sorted(hist["correct"].items(), key=lambda kv: float(kv[0]))),
            }
            for cell, hist in sorted(pooled.items())
        },
    }


def _prevention_share(comparison: Mapping[str, Any], critical: int) -> float | None:
    if critical <= 0:
        return None
    return comparison["criticalPrevented"] / critical


def evaluate_criterion(
    semantic: Mapping[str, Any], config: Mapping[str, Any], reproducible: bool
) -> dict[str, Any]:
    """The frozen criteria, applied. Section 5 for B, section 6 for C."""
    rule = config["success_criterion"]
    alpha = config["familywise_alpha"]
    method = PRIMARY_B
    checks_b: dict[str, bool] = {}
    checks_c: dict[str, bool] = {}
    reported: dict[str, Any] = {}
    powered: dict[str, float] = {}
    underpowered: list[str] = []
    powered_exposure: list[str] = []
    underpowered_exposure: list[str] = []

    # --- Criterion 1. Prevention, in every powered hidden-source cell. --------
    for family in rule["dependence_families"]:
        for cell, row in sorted(semantic["families"][family].items()):
            label = f"{method}:{family}:{cell}"
            critical = row["criticalLadderSilent"]
            comparison = row["comparisons"][method]
            if critical < rule["minimum_critical_silent_for_test"]:
                underpowered.append(label)
                continue
            powered[label] = comparison["p"]
            checks_b[f"{label}:preventsEnoughOfCritical"] = (
                comparison["criticalPrevented"] >= rule["prevention_share"] * critical
            )

    checks_b["hasPoweredDependenceComparison"] = bool(powered)
    for label, value in holm(powered).items():
        _, family, cell = label.split(":", 2)
        comparison = semantic["families"][family][cell]["comparisons"][method]
        checks_b[f"{label}:significantlyFewerSilent"] = (
            value < alpha and comparison["ladderOnlySilent"] > comparison["armOnlySilent"]
        )

    # --- Criterion 2. Cost bounded by benefit, where benefit is possible. -----
    for family, by_cell in sorted(semantic["families"].items()):
        for cell, row in sorted(by_cell.items()):
            comparison = row["comparisons"][method]
            label = f"{method}:{family}:{cell}"
            if row["criticalLadderSilent"] >= 1:
                checks_b[f"{label}:costBoundedByBenefit"] = (
                    comparison["unneeded"] <= comparison["ladderOnlySilent"]
                )
            else:
                reported[f"{label}:costWhereNoBenefitPossible"] = {
                    "correctSettlementsLost": comparison["unneeded"],
                    "silentFalsePrevented": comparison["ladderOnlySilent"],
                }

    # --- Criterion 3. It is not worse than refusing. --------------------------
    for family in rule["dependence_families"]:
        for cell, row in sorted(semantic["families"][family].items()):
            critical = row["criticalLadderSilent"]
            if critical < rule["minimum_critical_silent_for_test"]:
                continue
            label = f"{method}:{family}:{cell}"
            margin = row["comparisons"][method]
            refuse = row["comparisons"][CEILING]
            margin_correct = row["arms"][method].get(CORRECT_SETTLEMENT, 0)
            refuse_correct = row["arms"][CEILING].get(CORRECT_SETTLEMENT, 0)
            margin_share = _prevention_share(margin, critical) or 0.0
            refuse_share = _prevention_share(refuse, critical) or 0.0
            checks_b[f"{label}:betterThanRefusing"] = (
                margin_correct > refuse_correct
                and margin_share >= refuse_share - rule["refusal_prevention_tolerance"]
            )

    # --- Criterion 4. It does not suppress. -----------------------------------
    for family in rule["suppression_families"]:
        for cell, row in sorted(semantic["families"][family].items()):
            label = f"{method}:{family}:{cell}"
            baseline_survives = row["arms"][BASELINE].get("claimSurvives", 0)
            margin_survives = row["arms"][method].get("claimSurvives", 0)
            checks_b[f"{label}:doesNotSuppress"] = margin_survives >= baseline_survives
            reported[f"{label}:trueClaimVindicated"] = {
                arm: row["arms"][arm].get("settlesForTruth", 0) for arm in ARMS
            }

    # --- Criterion 5. It is not refusal with extra steps. ---------------------
    for family in rule["baseline_right_families"]:
        for cell, row in sorted(semantic["families"][family].items()):
            label = f"{method}:{family}:{cell}"
            baseline_settlements = row["arms"][BASELINE].get("settlements", 0)
            margin_settlements = row["arms"][method].get("settlements", 0)
            checks_b[f"{label}:notRefusalWithExtraSteps"] = margin_settlements >= (
                rule["settlement_retention_share"] * baseline_settlements
            )

    # --- Policy C, section 6. -------------------------------------------------
    for family, by_cell in sorted(semantic["families"].items()):
        for cell, row in sorted(by_cell.items()):
            label = f"{PRIMARY_C}:{family}:{cell}"
            figures = row["exposure"]
            n_false = sum(figures["false"].values())
            n_correct = sum(figures["correct"].values())
            minimum = rule["minimum_class_for_auc"]
            if n_false >= minimum and n_correct >= minimum:
                powered_exposure.append(label)
                checks_c[f"{label}:discriminates"] = (
                    figures["auc"] is not None and figures["auc"] >= rule["exposure_auc_floor"]
                )
            else:
                underpowered_exposure.append(label)
            if figures["settlements"] >= rule["minimum_settlements_for_constancy"]:
                checks_c[f"{label}:exposureNotConstant"] = (
                    figures["variationShare"] is not None
                    and figures["variationShare"] >= rule["exposure_variation_share"]
                )
            checks_c[f"{label}:identicalToLadder"] = row["pricedDivergesFromLadder"] == 0
            reported[f"{label}:aucOnShareDiagnostic"] = figures["aucOnShare"]

    checks_c["hasPoweredExposureCell"] = bool(powered_exposure)
    reported["pooledExposureAucByCell"] = {
        cell: value["auc"] for cell, value in semantic["pooledExposureByCell"].items()
    }

    checks_b["semanticResultReproducible"] = reproducible
    checks_c["semanticResultReproducible"] = reproducible

    supported_b = all(checks_b.values()) and bool(powered)
    supported_c = all(checks_c.values()) and bool(powered_exposure)
    return {
        "policyB": {
            "tests": checks_b,
            "poweredComparisons": sorted(powered),
            "underpoweredComparisons": sorted(underpowered),
            "supported": supported_b,
        },
        "policyC": {
            "tests": checks_c,
            "poweredExposureCells": sorted(powered_exposure),
            "underpoweredExposureCells": sorted(underpowered_exposure),
            "supported": supported_c,
        },
        "reported": reported,
        "adoptionCurveReportedOnly": True,
        "supported": supported_b and supported_c,
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
