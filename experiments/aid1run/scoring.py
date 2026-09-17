"""AID-1 scoring. Criteria 1-5 are copied from AID-1-DESIGN-DRAFT.md section 6.

The criteria were frozen before this world existed and are not renumbered,
softened, or added to here. Two things in section 6 are not numbers and had to
be operationalised; both are named in `PREREGISTRATION.md` section 8:

* "materially worse" (criterion 3) is a significant McNemar difference in silent
  false settlements plus an excess of at least `theatre_margin` of the
  baseline's silent false settlements in that family;
* "survives at the same rate" (criterion 5) is read as "no loss": the policy's
  surviving count may not fall below the baseline's in any cell.

The preamble of section 6 is also binding: reversible decisions only, powered
cells only, Holm-corrected across arms, fail closed when underpowered.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from aggregation.attested_independence import unattested_exposure
from experiments.aid1run.arms import ARMS, BASELINE, POLICY, REFUSE, THEATRE, run_campaign
from experiments.aid1run.world import (
    Decision,
    campaign_hash_row,
    iter_cell_campaigns,
)
from experiments.dri2.stats import holm, mcnemar_exact
from experiments.dri3.world import REVERSIBLE, SETTLED

CORRECT_SETTLEMENT = "correct_settlement"
FALSE_SETTLEMENT = "false_settlement"
UNNEEDED_ABSTENTION = "unneeded_abstention"
REQUIRED_ABSTENTION = "required_abstention"


def score_decision(decision: Decision, terminal: str) -> str:
    """DRI-3 outcomes, unchanged: correct, false, unneeded, required."""
    if terminal in SETTLED:
        return CORRECT_SETTLEMENT if terminal == decision.reference else FALSE_SETTLEMENT
    return UNNEEDED_ABSTENTION if decision.reference in SETTLED else REQUIRED_ABSTENTION


def is_silent_false(decision: Decision, terminal: str) -> bool:
    """A false settlement the record itself does not contradict.

    `assess_dependence_robustness` over the recorded ancestry says what the
    record alone robustly settles. Where it settles the same way, nothing in the
    record marks the error, and the settlement is silent. Where the record shows
    possible dependence, the settlement is flagged and somebody could have
    looked.
    """
    return (
        terminal in SETTLED
        and terminal != decision.reference
        and decision.robust_settlement == terminal
    )


def contrary_claim_survives(decision: Decision, terminal: str) -> bool:
    """The minority's true claim survives unless the decision settles against it."""
    if decision.contrary_value is None:
        raise ValueError(f"{decision.decision_id} carries no contrary claim")
    if terminal not in SETTLED:
        return True
    return (terminal == "settled_true") == decision.contrary_value


def _tally(counter: Counter, decision: Decision, terminal: str) -> None:
    result = score_decision(decision, terminal)
    scopes = ["all", decision.decision_class]
    if decision.decision_class == REVERSIBLE:
        scopes.append("reversible:critical" if decision.critical else "reversible:slack")
    for scope in scopes:
        counter[f"{scope}:decisions"] += 1
        counter[f"{scope}:{result}"] += 1
        if result == FALSE_SETTLEMENT:
            silent = is_silent_false(decision, terminal)
            counter[f"{scope}:{'silent' if silent else 'flagged'}FalseSettlements"] += 1


def _pair_up(paired: Counter, decision: Decision, terminals: Mapping[str, str]) -> None:
    """Paired arm-versus-baseline counts, on reversible decisions only."""
    base = terminals[BASELINE]
    base_correct = score_decision(decision, base) == CORRECT_SETTLEMENT
    base_silent = is_silent_false(decision, base)
    paired["baselineCorrect"] += base_correct
    paired["baselineSilent"] += base_silent
    paired["decisions"] += 1
    if decision.critical:
        paired["criticalDecisions"] += 1
        paired["baselineCriticalSilent"] += base_silent
    for arm in ARMS:
        terminal = terminals[arm]
        result = score_decision(decision, terminal)
        correct = result == CORRECT_SETTLEMENT
        silent = is_silent_false(decision, terminal)
        paired[f"{arm}:correct"] += correct
        paired[f"{arm}:unneeded"] += result == UNNEEDED_ABSTENTION
        paired[f"{arm}:false"] += result == FALSE_SETTLEMENT
        paired[f"{arm}:silent"] += silent
        paired[f"{arm}:correctLost"] += base_correct and not correct
        paired[f"{arm}:correctGained"] += correct and not base_correct
        paired[f"{arm}:silentPrevented"] += base_silent and not silent
        paired[f"{arm}:armOnlySilent"] += silent and not base_silent
        if decision.critical:
            paired[f"{arm}:criticalSilent"] += silent
            paired[f"{arm}:criticalPrevented"] += base_silent and not silent
    policy_silent = is_silent_false(decision, terminals[POLICY])
    theatre_silent = is_silent_false(decision, terminals[THEATRE])
    paired["theatreOnlySilent"] += theatre_silent and not policy_silent
    paired["policyOnlySilent"] += policy_silent and not theatre_silent
    if decision.contrary_value is not None:
        for arm in ARMS:
            paired[f"{arm}:survived"] += contrary_claim_survives(decision, terminals[arm])
        paired["survivalDecisions"] += 1


def _comparison(paired: Counter, arm: str) -> dict[str, Any]:
    return {
        "correct": paired[f"{arm}:correct"],
        "false": paired[f"{arm}:false"],
        "silent": paired[f"{arm}:silent"],
        "unneeded": paired[f"{arm}:unneeded"],
        "correctLost": paired[f"{arm}:correctLost"],
        "correctGained": paired[f"{arm}:correctGained"],
        "silentPrevented": paired[f"{arm}:silentPrevented"],
        "armOnlySilent": paired[f"{arm}:armOnlySilent"],
        "criticalSilent": paired[f"{arm}:criticalSilent"],
        "criticalPrevented": paired[f"{arm}:criticalPrevented"],
        "survived": paired[f"{arm}:survived"],
        "p": mcnemar_exact(paired[f"{arm}:silentPrevented"], paired[f"{arm}:armOnlySilent"]),
    }


def evaluate(
    config: Mapping[str, Any], salt: str, campaigns_per_variant: int | None = None
) -> dict[str, Any]:
    """The semantic result: every family, every cell, every arm."""
    tallies: dict[tuple[str, str], dict[str, Counter]] = defaultdict(
        lambda: {arm: Counter() for arm in ARMS}
    )
    paired: dict[tuple[str, str], Counter] = defaultdict(Counter)
    variant_paired: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    descriptive: dict[tuple[str, str], Counter] = defaultdict(Counter)
    manifest = hashlib.sha256()
    campaigns = 0

    for cell, error, campaign in iter_cell_campaigns(config, salt, campaigns_per_variant):
        campaigns += 1
        manifest.update(campaign_hash_row(cell, error, campaign))
        key = (campaign.family, cell)
        results = {arm: run_campaign(arm, campaign, error, config) for arm in ARMS}

        exposure = unattested_exposure(campaign.witnesses)
        row = descriptive[key]
        row["campaigns"] += 1
        row["mixedAttestationCampaigns"] += campaign.mixed_attestation
        for name, value in exposure.items():
            row[f"exposure:{name}"] += value

        for index, decision in enumerate(campaign.decisions):
            terminals = {arm: results[arm][index].terminal for arm in ARMS}
            for arm in ARMS:
                _tally(tallies[key][arm], decision, terminals[arm])
            row["decisions"] += 1
            row["mixedAttestationDecisions"] += campaign.mixed_attestation
            if decision.decision_class == REVERSIBLE:
                _pair_up(paired[key], decision, terminals)
                _pair_up(variant_paired[(campaign.family, campaign.variant, cell)],
                         decision, terminals)

    families: dict[str, dict[str, Any]] = {}
    for (family, cell), by_arm in sorted(tallies.items()):
        counts = paired[(family, cell)]
        row = descriptive[(family, cell)]
        families.setdefault(family, {})[cell] = {
            "arms": {arm: dict(sorted(counter.items())) for arm, counter in by_arm.items()},
            "reversibleDecisions": counts["decisions"],
            "criticalDecisions": counts["criticalDecisions"],
            "baselineCorrect": counts["baselineCorrect"],
            "baselineSilent": counts["baselineSilent"],
            "baselineCriticalSilent": counts["baselineCriticalSilent"],
            "survivalDecisions": counts["survivalDecisions"],
            "theatreOnlySilent": counts["theatreOnlySilent"],
            "policyOnlySilent": counts["policyOnlySilent"],
            "theatreVersusPolicyP": mcnemar_exact(
                counts["theatreOnlySilent"], counts["policyOnlySilent"]
            ),
            "comparisons": {arm: _comparison(counts, arm) for arm in ARMS},
            "descriptive": dict(sorted(row.items())),
        }

    variants: dict[str, dict[str, Any]] = {}
    for (family, variant, cell), counts in sorted(variant_paired.items()):
        variants.setdefault(family, {}).setdefault(variant, {})[cell] = {
            "baselineSilent": counts["baselineSilent"],
            "baselineCriticalSilent": counts["baselineCriticalSilent"],
            "theatreOnlySilent": counts["theatreOnlySilent"],
            "policyOnlySilent": counts["policyOnlySilent"],
            "comparisons": {arm: _comparison(counts, arm) for arm in ARMS},
        }

    return {
        "schema": "minority-prophet.aid1-semantic-result.v1",
        "campaigns": campaigns,
        "campaignManifestSha256": manifest.hexdigest(),
        "scope": (
            "criteria on reversible decisions, per the owner's standing scope "
            "decision; irreversible decisions are tallied without a pass mark"
        ),
        "families": families,
        "variants": variants,
        "adoptionCurve": adoption_curve(families),
    }


def adoption_curve(families: Mapping[str, Any]) -> dict[str, Any]:
    """Reported, never a criterion. Cost and prevention at each adoption rate.

    Section 6 says naming a preferred `alpha` after seeing this curve would be
    the selection error this programme made twice. It is emitted so the question
    can be answered, and it decides nothing.
    """
    curve: dict[str, Any] = {}
    for family, by_cell in families.items():
        for cell, row in by_cell.items():
            alpha = cell.split("|")[0].split("=")[1]
            error = cell.split("=")[-1]
            policy = row["comparisons"][POLICY]
            curve.setdefault(family, {}).setdefault(alpha, {})[error] = {
                "correctLost": policy["correctLost"],
                "correctGained": policy["correctGained"],
                "silentPrevented": policy["silentPrevented"],
                "unneeded": policy["unneeded"],
                "baselineCorrect": row["baselineCorrect"],
                "baselineSilent": row["baselineSilent"],
                "mixedAttestationDecisions": row["descriptive"].get(
                    "mixedAttestationDecisions", 0
                ),
                "decisions": row["descriptive"].get("decisions", 0),
            }
    return curve


def evaluate_criterion(
    semantic: Mapping[str, Any], config: Mapping[str, Any], reproducible: bool
) -> dict[str, Any]:
    """Criteria 1-5, verbatim from section 6. Returns a verdict that can be
    "not supported", and is "not supported" whenever anything is missing."""
    rule = config["success_criterion"]
    level = config["familywise_alpha"]
    minimum = rule["minimum_critical_silent_for_test"]
    checks: dict[str, bool] = {}
    powered: list[tuple[str, str]] = []
    underpowered: list[str] = []
    pvalues: dict[str, float] = {}

    for family, by_cell in sorted(semantic["families"].items()):
        for cell, row in sorted(by_cell.items()):
            if row["baselineCriticalSilent"] >= minimum:
                powered.append((family, cell))
                for arm in (POLICY, THEATRE, REFUSE):
                    pvalues[f"{arm}:{family}:{cell}"] = row["comparisons"][arm]["p"]
                if family == rule["freely_attesting_family"]:
                    pvalues[f"theatre-vs-policy:{family}:{cell}"] = row["theatreVersusPolicyP"]
            else:
                underpowered.append(f"{family}:{cell}")

    adjusted = holm(pvalues)
    hidden = rule["hidden_source_family"]
    freely = rule["freely_attesting_family"]
    minority = rule["minority_family"]

    hidden_powered = [cell for family, cell in powered if family == hidden]
    freely_powered = [cell for family, cell in powered if family == freely]
    checks["hasPoweredHiddenSourceCell"] = bool(hidden_powered)
    checks["hasPoweredFreelyAttestingCell"] = bool(freely_powered)

    # 1. It prevents what it exists to prevent.
    for cell in hidden_powered:
        row = semantic["families"][hidden][cell]
        policy = row["comparisons"][POLICY]
        floor = rule["prevented_share"] * row["baselineCriticalSilent"]
        checks[f"c1:{hidden}:{cell}:preventsFortyPercentOfCritical"] = (
            policy["criticalPrevented"] >= floor
        )
        checks[f"c1:{hidden}:{cell}:significantlyFewerSilent"] = (
            adjusted[f"{POLICY}:{hidden}:{cell}"] < level
            and policy["silentPrevented"] > policy["armOnlySilent"]
        )

    # 2. Cost is bounded by benefit, at alpha = 1.0, in every family and cell.
    bound_alpha = f"alpha={rule['cost_bound_alpha']}"
    for family, by_cell in sorted(semantic["families"].items()):
        for cell, row in sorted(by_cell.items()):
            if not cell.startswith(bound_alpha + "|"):
                continue
            policy = row["comparisons"][POLICY]
            checks[f"c2:{family}:{cell}:costBoundedByBenefit"] = (
                policy["correctLost"] <= policy["silentPrevented"]
            )

    # 3. It is not theatre.
    for cell in freely_powered:
        row = semantic["families"][freely][cell]
        policy = row["comparisons"][POLICY]
        theatre = row["comparisons"][THEATRE]
        excess = theatre["silent"] - policy["silent"]
        checks[f"c3:{freely}:{cell}:theatreDoesWorse"] = (
            excess > 0
            and adjusted[f"theatre-vs-policy:{freely}:{cell}"] < level
            and excess >= rule["theatre_margin"] * row["baselineSilent"]
        )

    # 4. It is cheaper than refusing.
    for family, cell in powered:
        row = semantic["families"][family][cell]
        policy = row["comparisons"][POLICY]
        refuse = row["comparisons"][REFUSE]
        checks[f"c4:{family}:{cell}:cheaperThanRefusing"] = (
            policy["correct"] > refuse["correct"]
            and policy["criticalPrevented"] >= refuse["criticalPrevented"]
        )

    # 5. It does not suppress.
    for cell, row in sorted(semantic["families"].get(minority, {}).items()):
        policy = row["comparisons"][POLICY]
        baseline = row["comparisons"][BASELINE]
        checks[f"c5:{minority}:{cell}:contraryClaimSurvives"] = (
            policy["survived"] >= baseline["survived"]
        )

    checks["semanticResultReproducible"] = reproducible
    supported = (
        all(checks.values())
        and bool(hidden_powered)
        and bool(freely_powered)
        and reproducible
    )
    failed = sorted(name for name, value in checks.items() if not value)
    return {
        "criteria": {
            "1": "It prevents what it exists to prevent.",
            "2": "Cost is bounded by benefit.",
            "3": "It is not theatre.",
            "4": "It is cheaper than refusing.",
            "5": "It does not suppress.",
        },
        "tests": dict(sorted(checks.items())),
        "failedTests": failed,
        "poweredCells": [f"{family}:{cell}" for family, cell in powered],
        "underpoweredCells": underpowered,
        "holmAdjusted": dict(sorted(adjusted.items())),
        "irreversibleReportedOnly": True,
        "supported": supported,
        "verdict": "supported" if supported else "not supported",
    }


def semantic_hash(result: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


__all__ = [
    "CORRECT_SETTLEMENT",
    "FALSE_SETTLEMENT",
    "REQUIRED_ABSTENTION",
    "UNNEEDED_ABSTENTION",
    "adoption_curve",
    "contrary_claim_survives",
    "evaluate",
    "evaluate_criterion",
    "is_silent_false",
    "score_decision",
    "semantic_hash",
]
