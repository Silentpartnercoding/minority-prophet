"""Integrity tests for the AID-4 protocol. Development salt only.

These prove the world contains what the frozen draft asked for: that every
family produces its intended case, that `priced` settles identically to `ladder`
on every decision, and that the two constructions no previous world supplied —
wide margins with unattested witnesses, and settlements that rest on silence and
are nonetheless correct — actually exist in the generated campaigns.

Nothing here evaluates the confirmatory salt, and one test asserts it is passed
to nothing.
"""

import inspect
import json
from pathlib import Path

import pytest

from aggregation.independence_axes import DepthBasis, WitnessDepth, WitnessIdentity
from canon.proximity import ErrorClass
from experiments.aid4run.arms import (
    ARMS,
    BASELINE,
    CEILING,
    KNOWN_BAD,
    PRIMARY_B,
    PRIMARY_C,
    collapse_floor,
    exposure_figure,
    exposure_scalar,
    is_unattested,
    run_decision,
    settle,
)
from experiments.aid4run.scoring import (
    CORRECT_SETTLEMENT,
    FALSE_SETTLEMENT,
    ConfirmatorySaltRefused,
    evaluate,
    evaluate_criterion,
    score_decision,
)
from experiments.aid4run.world import (
    ABSTAIN,
    FAMILIES,
    SETTLED,
    SETTLED_FALSE,
    SETTLED_TRUE,
    ROLE_ATTESTABLE,
    ROLE_HIDDEN,
    ROLE_RESTATER,
    ROLE_UNATTESTABLE,
    campaign_hash_row,
    generate_campaign,
)

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "experiments" / "aid4run"
CONFIG = json.loads((PACKAGE / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]
RULE = CONFIG["success_criterion"]
FABRICATION = ErrorClass.FABRICATION


def campaigns(family, count=8, alpha=1.0):
    return [generate_campaign(CONFIG, DEV, family, rep, alpha) for rep in range(count)]


def decisions(family, count=8, alpha=1.0):
    return [d for c in campaigns(family, count, alpha) for d in c.decisions]


# --------------------------------------------------------------------------
# The protocol, and the salt
# --------------------------------------------------------------------------


def test_config_names_the_frozen_policies_and_the_frozen_criteria():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert RULE["primary_b"] == PRIMARY_B == "margin"
    assert RULE["primary_c"] == PRIMARY_C == "priced"
    assert RULE["baseline"] == BASELINE == "ladder"
    assert RULE["known_bad"] == KNOWN_BAD == "attested"
    assert RULE["ceiling"] == CEILING == "refuse_all_unrecorded"
    assert tuple(CONFIG["families"]) == FAMILIES
    assert CONFIG["development_salt"] != CONFIG["confirmatory_salt"]
    # The frozen numbers, exactly as the draft fixed them.
    assert RULE["prevention_share"] == 0.40
    assert RULE["refusal_prevention_tolerance"] == 0.10
    assert RULE["settlement_retention_share"] == 0.50
    assert RULE["exposure_auc_floor"] == 0.70
    assert RULE["exposure_variation_share"] == 0.20


def test_the_confirmatory_salt_is_reachable_only_through_one_runner():
    """Was `test_confirmatory_salt_is_passed_to_nothing` until a runner existed.

    The world's author deliberately shipped **no** runner, so that evaluating
    the confirmatory salt would require a separate, recorded act rather than a
    default anyone could trip over. The final assertion here was
    `not list(PACKAGE.glob("run_*.py"))`, and it held until the operator wrote
    `run_confirmatory.py` and turned that key.

    Retiring that clause is the point of the gate, not a loophole in it, and the
    guarantees that carry the provenance are unchanged and still asserted below:
    the salt value appears in no module, `evaluate` refuses it, and the opt-in
    still defaults off. What replaces the clause is the stronger statement —
    exactly one runner exists, and it is the thing that sets the flag.
    """
    salt = CONFIG["confirmatory_salt"]
    for path in sorted(PACKAGE.glob("*.py")):
        assert salt not in path.read_text(), f"{path} names the confirmatory salt"
    assert salt not in Path(__file__).read_text()
    with pytest.raises(ConfirmatorySaltRefused):
        evaluate(CONFIG, salt, 1)
    assert inspect.signature(evaluate).parameters["confirmatory"].default is False
    runners = sorted(p.name for p in PACKAGE.glob("run_*.py"))
    assert runners == ["run_confirmatory.py"], runners
    assert "confirmatory=True" in (PACKAGE / "run_confirmatory.py").read_text()


# --------------------------------------------------------------------------
# Each family produces its intended case
# --------------------------------------------------------------------------


def test_hidden_source_is_dr3_and_its_copies_attest_at_the_adoption_rate():
    """Nothing recorded connects the copies, and they can attest like anyone."""
    for campaign in campaigns("hidden_source", 4, alpha=1.0):
        focus = set(campaign.focus_group)
        assert len(focus) == 2
        copies = [s for s in campaign.sources if s.source_id in focus]
        assert all(s.component == "hidden:u" for s in copies)
        assert all(s.role == ROLE_HIDDEN and s.can_attest for s in copies)
        assert all(not s.ancestry and not s.markers for s in campaign.sources)
        for decision in campaign.decisions:
            realized = [w for w in decision.witnesses if w.source_id in focus]
            assert len({w.unit for w in realized}) == 1
            # At full adoption they are attested, so B's floor stops seeing them.
            assert all(w.adopted for w in realized)
            assert all(not is_unattested(w.witness) for w in realized)

    for campaign in campaigns("hidden_source", 4, alpha=0.0):
        for decision in campaign.decisions:
            assert all(is_unattested(w.witness) for w in decision.witnesses)


def test_hidden_source_prevention_decays_as_the_copies_start_attesting():
    """The AID-1 curve, on policy B: attestation hands back the independence."""
    prevented = {}
    for alpha in (0.0, 1.0):
        result = evaluate(CONFIG, DEV, 20)["families"]["hidden_source"][f"alpha={alpha}"]
        critical = result["criticalLadderSilent"]
        assert critical >= 12, "hidden_source must be powered to test prevention"
        prevented[alpha] = result["comparisons"][PRIMARY_B]["criticalPrevented"] / critical
    assert prevented[0.0] > 0.9, "with the copies silent, B's floor must collapse them"
    assert prevented[1.0] < 0.4, "with the copies attested, B must stop preventing"


def test_backed_hidden_source_is_attested_at_every_rate_and_b_never_collapses_it():
    for alpha in (0.0, 0.5, 1.0):
        for campaign in campaigns("backed_hidden_source", 3, alpha=alpha):
            focus = set(campaign.focus_group)
            assert len(focus) == 3
            for decision in campaign.decisions:
                copies = [w for w in decision.witnesses if w.source_id in focus]
                assert len({w.unit for w in copies}) == 1
                assert all(w.adopted for w in copies)
                assert all(w.witness.identity is WitnessIdentity.VERIFIED for w in copies)
                assert all(w.witness.depth_basis is DepthBasis.DEVICE_ATTESTED for w in copies)
                assert all(not is_unattested(w.witness) for w in copies)
                side = [w.witness for w in copies]
                assert collapse_floor(side, FABRICATION) == len(side)

    result = evaluate(CONFIG, DEV, 20)["families"]["backed_hidden_source"]
    for cell, row in result.items():
        assert row["criticalLadderSilent"] >= 12, f"{cell} must be powered"
        assert row["comparisons"][PRIMARY_B]["criticalPrevented"] == 0, (
            "a device attestation says nothing about shared origin; B must be blind here"
        )


def test_honest_unattestable_never_attests_and_is_pure_cost():
    for alpha in (0.0, 0.5, 1.0):
        for campaign in campaigns("honest_unattestable", 3, alpha=alpha):
            assert campaign.focus_group == ()
            assert all(s.role == ROLE_UNATTESTABLE for s in campaign.sources)
            for decision in campaign.decisions:
                assert all(not w.adopted for w in decision.witnesses)
                assert all(is_unattested(w.witness) for w in decision.witnesses)
                assert all(w.witness.admissible is WitnessDepth.TEXT for w in decision.witnesses)
                # The baseline is right, and B abstains anyway.
                baseline = run_decision(BASELINE, decision, CONFIG)
                assert baseline in SETTLED
                assert score_decision(decision, baseline) == CORRECT_SETTLEMENT
                assert run_decision(PRIMARY_B, decision, CONFIG) == ABSTAIN


def test_wide_margin_with_unattested_witnesses_lets_b_settle():
    """The construction no previous world supplied. Without it B is untestable."""
    settled = 0
    total = 0
    for campaign in campaigns("wide_margin_unattested", 6, alpha=1.0):
        assert campaign.focus_group == ()
        for decision in campaign.decisions:
            total += 1
            winners = [w for w in decision.witnesses if w.vote is decision.truth]
            losers = [w for w in decision.witnesses if w.vote is not decision.truth]
            assert len(winners) == 4 and len(losers) == 1
            # A wide margin that nonetheless carries unattested witnesses.
            assert any(is_unattested(w.witness) for w in winners)
            assert any(not is_unattested(w.witness) for w in winners)
            floor = collapse_floor([w.witness for w in winners], FABRICATION)
            assert floor >= decision.threshold
            terminal = run_decision(PRIMARY_B, decision, CONFIG)
            if terminal in SETTLED:
                settled += 1
                assert score_decision(decision, terminal) == CORRECT_SETTLEMENT
    assert settled == total, "at full adoption B must settle every wide-margin decision"


def test_settlements_that_rest_on_silence_and_are_correct_exist():
    """Without these, C's discrimination is trivially perfect and tests nothing."""
    shapes = set()
    silent_and_correct = 0
    for alpha in (0.0, 0.5):
        for campaign in campaigns("silent_but_correct", 8, alpha=alpha):
            roles = {s.role for s in campaign.sources}
            shapes.add(ROLE_HIDDEN in roles)
            for decision in campaign.decisions:
                baseline = run_decision(BASELINE, decision, CONFIG)
                assert baseline in SETTLED
                assert score_decision(decision, baseline) == CORRECT_SETTLEMENT
                if exposure_scalar(decision) >= 3:
                    silent_and_correct += 1
    assert shapes == {True, False}, "both shapes must occur"
    assert silent_and_correct > 0, "high-exposure correct settlements must exist"


def test_hidden_dependence_on_the_losing_side_does_not_make_the_settlement_wrong():
    """The sharpest case against C's figure: exposure high, settlement correct."""
    found = 0
    for campaign in campaigns("silent_but_correct", 8, alpha=0.0):
        if not campaign.focus_group:
            continue
        focus = set(campaign.focus_group)
        for decision in campaign.decisions:
            copies = [w for w in decision.witnesses if w.source_id in focus]
            winners = [w for w in decision.witnesses if w.vote is decision.truth]
            assert all(w.vote is not decision.truth for w in copies), "copies must lose"
            assert len({w.unit for w in copies}) == 1
            assert all(is_unattested(w.witness) for w in winners + copies)
            baseline = run_decision(BASELINE, decision, CONFIG)
            assert score_decision(decision, baseline) == CORRECT_SETTLEMENT
            assert exposure_scalar(decision) == len(decision.witnesses)
            found += 1
    assert found > 0


def test_minority_suppression_is_aid3s_forced_tie_unchanged():
    for campaign in campaigns("minority_suppression", 6, alpha=1.0):
        assert {s.role for s in campaign.sources} == {ROLE_ATTESTABLE, ROLE_UNATTESTABLE}
        for decision in campaign.decisions:
            assert decision.truth is True
            true_side = [w for w in decision.witnesses if w.vote]
            false_side = [w for w in decision.witnesses if not w.vote]
            assert len(true_side) == len(false_side) == 2
            assert all(w.role == ROLE_UNATTESTABLE for w in true_side)
            assert all(w.role == ROLE_ATTESTABLE for w in false_side)
            assert decision.reference == ABSTAIN
            assert run_decision(BASELINE, decision, CONFIG) == ABSTAIN
            assert run_decision(PRIMARY_B, decision, CONFIG) == ABSTAIN
            # The rejected policy still settles against the true claim.
            assert run_decision(KNOWN_BAD, decision, CONFIG) == SETTLED_FALSE


def test_minority_wins_is_the_asymmetric_case_criterion_four_cannot_see():
    """The minority is the winning side AND carries every unattested witness."""
    for campaign in campaigns("minority_wins", 6, alpha=1.0):
        for decision in campaign.decisions:
            assert decision.truth is True
            minority = [w for w in decision.witnesses if w.vote]
            majority = [w for w in decision.witnesses if not w.vote]
            assert len(minority) == 3 and len(majority) == 2
            assert all(is_unattested(w.witness) for w in minority)
            assert all(not is_unattested(w.witness) for w in majority)
            # The baseline settles for the true minority claim and is right.
            baseline = run_decision(BASELINE, decision, CONFIG)
            assert baseline == SETTLED_TRUE
            assert score_decision(decision, baseline) == CORRECT_SETTLEMENT
            # B gives that vindication up, while never settling against it.
            assert run_decision(PRIMARY_B, decision, CONFIG) == ABSTAIN

    row = evaluate(CONFIG, DEV, 6)["families"]["minority_wins"]["alpha=1.0"]
    ladder = row["arms"][BASELINE]
    margin = row["arms"][PRIMARY_B]
    assert margin["claimSurvives"] == ladder["claimSurvives"], "criterion 4 sees no loss"
    assert ladder["settlesForTruth"] == ladder["decisions"]
    assert margin.get("settlesForTruth", 0) == 0, "and every vindication is gone"


def test_mixed_populations_carries_all_four_kinds_and_both_outcome_classes():
    outcomes = set()
    for campaign in campaigns("mixed_populations", 6, alpha=0.5):
        roles = {s.role for s in campaign.sources}
        assert roles == {ROLE_HIDDEN, ROLE_ATTESTABLE, ROLE_UNATTESTABLE, ROLE_RESTATER}
        for decision in campaign.decisions:
            assert {w.role for w in decision.witnesses} == roles
            outcomes.add(score_decision(decision, run_decision(BASELINE, decision, CONFIG)))
    assert {CORRECT_SETTLEMENT, FALSE_SETTLEMENT} <= outcomes


def test_the_restater_keeps_the_exposure_axes_from_collapsing():
    decision = decisions("mixed_populations", 1, alpha=0.0)[0]
    figure = exposure_figure(decision)
    assert figure["witnesses"] == len(decision.witnesses)
    assert figure["ancestry_not_attested"] == len(decision.witnesses)
    # The restater is unattested and does not overclaim; everyone else does.
    assert figure["overclaimed_depth"] == len(decision.witnesses) - 1


# --------------------------------------------------------------------------
# Policy C changes nothing, structurally
# --------------------------------------------------------------------------


def test_priced_settles_identically_to_ladder_on_every_decision():
    for family in FAMILIES:
        for alpha in CONFIG["adoption_rates"]:
            for campaign in campaigns(family, 3, alpha=alpha):
                for decision in campaign.decisions:
                    assert run_decision(PRIMARY_C, decision, CONFIG) == run_decision(
                        BASELINE, decision, CONFIG
                    )


def test_priced_divergence_is_zero_in_every_cell_and_exposure_still_varies():
    result = evaluate(CONFIG, DEV, 8)
    varied = False
    for by_cell in result["families"].values():
        for row in by_cell.values():
            assert row["pricedDivergesFromLadder"] == 0
            if row["exposure"]["variationShare"]:
                varied = True
    assert varied, "a figure that never varies anywhere would not be worth scoring"


def test_exposure_cannot_reach_the_settlement():
    """`priced` delegates to the baseline rather than recomputing it."""
    source = inspect.getsource(settle)
    assert "return settle(BASELINE, decision, error)" in source


# --------------------------------------------------------------------------
# Determinism, and the criteria failing closed
# --------------------------------------------------------------------------


def test_same_config_and_salt_produce_byte_identical_campaigns():
    for family in FAMILIES:
        first = generate_campaign(CONFIG, DEV, family, 1, 0.5)
        second = generate_campaign(CONFIG, DEV, family, 1, 0.5)
        assert first == second
        assert campaign_hash_row("alpha=0.5", first) == campaign_hash_row("alpha=0.5", second)
        for arm in ARMS:
            assert [run_decision(arm, d, CONFIG) for d in first.decisions] == [
                run_decision(arm, d, CONFIG) for d in second.decisions
            ]


def test_evaluation_is_reproducible_on_development_campaigns():
    first = evaluate(CONFIG, DEV, 2)
    assert first == evaluate(CONFIG, DEV, 2)
    assert set(first["families"]) == set(FAMILIES)


def _comparison(prevented=0, unneeded=0, silent=0, p=1.0):
    return {
        "silent": silent,
        "unneeded": unneeded,
        "criticalSilent": 0,
        "criticalPrevented": prevented,
        "ladderOnlySilent": prevented,
        "armOnlySilent": 0,
        "p": p,
    }


def _row(critical=40, prevented=40, unneeded=0, auc=1.0, variation=1.0, diverges=0, survives=100):
    arms = {
        arm: {
            "correct_settlement": 500,
            "settlements": 500,
            "claimSurvives": survives,
            "settlesForTruth": 500,
            "decisions": 600,
        }
        for arm in ARMS
    }
    arms[CEILING]["correct_settlement"] = 0
    arms[CEILING]["settlements"] = 0
    return {
        "arms": arms,
        "ladderSilent": critical,
        "criticalLadderSilent": critical,
        "pricedDivergesFromLadder": diverges,
        "exposure": {
            "false": {"3": 100},
            "correct": {"1": 100},
            "settlements": 200,
            "auc": auc,
            "variationShare": variation,
            "aucOnShare": auc,
        },
        "comparisons": {
            arm: _comparison(prevented, unneeded, 0, 0.0) for arm in ARMS if arm != BASELINE
        },
    }


def _semantic(maker):
    cells = [f"alpha={a}" for a in CONFIG["adoption_rates"]]
    return {
        "families": {f: {cell: maker(f, cell) for cell in cells} for f in FAMILIES},
        "pooledExposureByCell": {cell: {"auc": 0.5} for cell in cells},
    }


def test_both_criteria_fail_closed_when_nothing_is_powered():
    quiet = _semantic(lambda *_: _row(critical=0, prevented=0))
    for by_cell in quiet["families"].values():
        for row in by_cell.values():
            row["exposure"]["false"] = {}
            row["exposure"]["correct"] = {}
            row["exposure"]["settlements"] = 0
    verdict = evaluate_criterion(quiet, CONFIG, True)
    assert verdict["policyB"]["tests"]["hasPoweredDependenceComparison"] is False
    assert verdict["policyC"]["tests"]["hasPoweredExposureCell"] is False
    assert verdict["policyB"]["supported"] is False
    assert verdict["policyC"]["supported"] is False
    assert verdict["supported"] is False


def test_a_clean_world_can_support_both_policies():
    """The criteria must be passable, or the world is measuring nothing."""
    verdict = evaluate_criterion(_semantic(lambda *_: _row()), CONFIG, True)
    assert verdict["policyB"]["supported"] is True
    assert verdict["policyC"]["supported"] is True


def test_criterion_four_fails_on_any_loss_of_the_true_claim():
    semantic = _semantic(lambda *_: _row())
    for cell in semantic["families"]["minority_suppression"]:
        semantic["families"]["minority_suppression"][cell]["arms"][PRIMARY_B]["claimSurvives"] = 99
    verdict = evaluate_criterion(semantic, CONFIG, True)
    assert any(
        key.endswith("doesNotSuppress") and value is False
        for key, value in verdict["policyB"]["tests"].items()
    )
    assert verdict["policyB"]["supported"] is False


def test_criterion_five_fails_when_b_degenerates_into_refusal():
    semantic = _semantic(lambda *_: _row())
    for family in RULE["baseline_right_families"]:
        for cell in semantic["families"][family]:
            semantic["families"][family][cell]["arms"][PRIMARY_B]["settlements"] = 249
    verdict = evaluate_criterion(semantic, CONFIG, True)
    assert any(
        key.endswith("notRefusalWithExtraSteps") and value is False
        for key, value in verdict["policyB"]["tests"].items()
    )


def test_policy_c_fails_on_a_coin_flip_on_a_constant_figure_and_on_divergence():
    flip = evaluate_criterion(_semantic(lambda *_: _row(auc=0.5)), CONFIG, True)
    assert any(
        key.endswith("discriminates") and value is False
        for key, value in flip["policyC"]["tests"].items()
    )

    constant = evaluate_criterion(_semantic(lambda *_: _row(variation=0.0)), CONFIG, True)
    assert any(
        key.endswith("exposureNotConstant") and value is False
        for key, value in constant["policyC"]["tests"].items()
    )

    diverged = evaluate_criterion(_semantic(lambda *_: _row(diverges=1)), CONFIG, True)
    assert any(
        key.endswith("identicalToLadder") and value is False
        for key, value in diverged["policyC"]["tests"].items()
    )
    assert diverged["policyC"]["supported"] is False
