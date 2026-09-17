"""Integrity tests for the AID-2 protocol. Development salt only.

These are construction tests, not results. Each one asserts that a family really
produces the case section 5 of the spec asked for, and that the primary arm
really consults the range rather than a point estimate -- which is the one thing
AID-1 could not do and the only reason this experiment exists.

If one of these fails, the construction is wrong and the construction is what
gets fixed. No criterion moves.
"""

import itertools
import json
from pathlib import Path

import pytest

from aggregation.attested_independence import Use, Witness, witness_bounds
from aggregation.attested_independence import effective_witnesses_for as attested_effective
from aggregation.attested_independence import independent_for as attested_independent
from aggregation.independence_axes import (
    DepthBasis,
    WitnessBounds,
    WitnessDepth,
    WitnessIdentity,
)
from canon.proximity import ErrorClass
from canon.proximity import independent_for as ladder_independent
from experiments.aid2run.arms import (
    ARMS,
    BASELINE,
    POINT,
    PRIMARY,
    REFUSE,
    THEATRE,
    at_face_value,
    bounds_for,
    every_pair_shares_ancestry,
    ladder_source,
    range_settlements,
    run_campaign,
    settle_decision,
    sides,
    survival_call_is_refused,
)
from experiments.aid2run.scoring import (
    contrary_claim_survives,
    evaluate,
    evaluate_criterion,
    semantic_hash,
)
from experiments.aid2run.world import (
    ALREADY_RIGHT_FAMILY,
    FAMILIES,
    FREELY_ATTESTING_FAMILY,
    HIDDEN_FAMILY,
    MINORITY_FAMILY,
    MIXED_FAMILY,
    SETTLED,
    VARIANTS,
    build_witness,
    cell_key,
    cells,
    generate_campaign,
    hidden_group_is_unrecorded,
    layout,
    recorded_kinship_is_a_decoy,
)
from experiments.dri3.world import REVERSIBLE
from provenance.dependence_robustness import settle_counts

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "aid2run" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]
CONF = CONFIG["confirmatory_salt"]
ALPHAS = tuple(CONFIG["adoption_rates"])
ERRORS = (ErrorClass.FABRICATION, ErrorClass.INSTRUMENT, ErrorClass.TRANSCRIPTION)
UNSETTLED = "unsettled"


def campaigns(family, variant, count=4, alpha=1.0):
    return [
        generate_campaign(CONFIG, DEV, family, variant, replicate, alpha)
        for replicate in range(count)
    ]


def reversible(campaign):
    return [d for d in campaign.decisions if d.decision_class == REVERSIBLE]


def every_variant():
    for family in FAMILIES:
        for variant in VARIANTS[family]:
            yield family, variant


def test_config_is_preregistered_and_names_the_arms_the_spec_named():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert tuple(CONFIG["families"]) == FAMILIES
    assert len(FAMILIES) == 6
    assert ARMS == (
        "ladder",
        "attested_bounds",
        "attested_point",
        "attested_declared_only",
        "refuse_all_unrecorded",
    )
    rule = CONFIG["success_criterion"]
    assert (rule["baseline_arm"], rule["primary_arm"]) == (BASELINE, PRIMARY)
    assert (rule["point_arm"], rule["theatre_arm"]) == (POINT, THEATRE)
    assert rule["refusal_arm"] == REFUSE
    assert rule["prevented_share"] == 0.40
    assert rule["already_right_settle_share"] == 0.50
    assert rule["refusal_prevention_slack"] == 0.10
    assert rule["scope"] == "reversible"
    assert set(CONFIG["adoption_rates"]) >= {0.0, 0.25, 0.5, 0.75, 1.0}
    assert set(CONFIG["error_classes"]) == {"FABRICATION", "INSTRUMENT", "TRANSCRIPTION"}
    assert CONF != DEV


# --- the primary arm really consults the range ------------------------------


def test_the_primary_arm_settles_by_both_ends_of_witness_bounds():
    """Recomputed from the policy's own `witness_bounds`, decision by decision.

    This is the test that would fail if the primary were quietly reimplemented
    as a point estimate, or as one end of the range.
    """
    seen_ends_differ = False
    for family, variant in every_variant():
        for alpha in (0.0, 0.5, 1.0):
            campaign = campaigns(family, variant, 1, alpha)[0]
            for error in ERRORS:
                for decision in campaign.decisions:
                    true_side, false_side = sides(campaign, decision)
                    lower_true = witness_bounds(true_side, error)
                    lower_false = witness_bounds(false_side, error)
                    lower = settle_counts(
                        lower_true.lower, lower_false.lower, decision.threshold
                    )
                    upper = settle_counts(
                        lower_true.upper, lower_false.upper, decision.threshold
                    )
                    expected = lower if lower == upper else UNSETTLED
                    outcome = settle_decision(PRIMARY, campaign, decision, error)
                    assert outcome.terminal == expected
                    assert outcome.true_bounds == (lower_true.lower, lower_true.upper)
                    assert outcome.false_bounds == (lower_false.lower, lower_false.upper)
                    seen_ends_differ |= lower != upper
    # A rule that never sees its two ends disagree is not being tested at all.
    assert seen_ends_differ


def test_the_range_is_load_bearing_and_not_the_point_estimate():
    """The primary and the point arm must actually part company somewhere.

    The concrete case is AID-1's suppression: at the instrument class and full
    adoption the single count deletes the true minority claim in every decision,
    and the range refuses instead. That difference is the whole thesis of the
    repair, so it is pinned rather than left to a sweep.
    """
    point_suppressed = bounds_refused = total = 0
    for campaign in campaigns(MINORITY_FAMILY, "count_decides_survival", 4, 1.0):
        point = run_campaign(POINT, campaign, ErrorClass.INSTRUMENT, CONFIG)
        primary = run_campaign(PRIMARY, campaign, ErrorClass.INSTRUMENT, CONFIG)
        for index, decision in enumerate(campaign.decisions):
            if decision.decision_class != REVERSIBLE:
                continue
            total += 1
            point_suppressed += not contrary_claim_survives(decision, point[index].terminal)
            bounds_refused += primary[index].terminal == UNSETTLED
    assert total >= 12
    assert point_suppressed == total
    assert bounds_refused == total


def test_the_primary_is_not_simply_refusing_whenever_the_range_is_wide():
    """Wide range and refusal are different events, and both must occur.

    If they were the same event the arm would be `refuse_all_unrecorded` wearing
    a range, and criterion 6 would be measuring nothing.
    """
    wide_and_settled = wide_and_refused = 0
    for family, variant in every_variant():
        campaign = campaigns(family, variant, 2, 1.0)[0]
        for error in ERRORS:
            for decision in campaign.decisions:
                outcome = settle_decision(PRIMARY, campaign, decision, error)
                if not outcome.range_is_wide:
                    continue
                if outcome.terminal in SETTLED:
                    wide_and_settled += 1
                else:
                    wide_and_refused += 1
    assert wide_and_settled > 0
    assert wide_and_refused > 0


def test_range_settlements_matches_brute_force_over_the_whole_box():
    """The diagnostic is exact, so the interior-disagreement count means something."""
    for t_low, t_high, f_low, f_high, threshold in itertools.product(
        range(0, 4), range(0, 4), range(0, 4), range(0, 4), (2, 3)
    ):
        if t_low > t_high or f_low > f_high:
            continue
        true_bounds = WitnessBounds(t_low, t_high)
        false_bounds = WitnessBounds(f_low, f_high)
        brute = {
            settle_counts(t, f, threshold)
            for t in range(t_low, t_high + 1)
            for f in range(f_low, f_high + 1)
        }
        assert range_settlements(true_bounds, false_bounds, threshold) == frozenset(brute)


def test_the_lower_bound_never_exceeds_the_upper_anywhere_in_the_world():
    for family, variant in every_variant():
        for alpha in ALPHAS:
            campaign = generate_campaign(CONFIG, DEV, family, variant, 0, alpha)
            for error in ERRORS:
                for side in sides(campaign, campaign.decisions[0]):
                    bounds = witness_bounds(side, error)
                    assert bounds.lower <= bounds.upper


# --- family 1: nobody can attest -------------------------------------------


def test_nobody_can_attest_is_out_of_reach_of_every_adoption_rate():
    """Honest, deep, and unprovable at every alpha, including 1.0."""
    for alpha in ALPHAS:
        for campaign in campaigns("nobody_can_attest", "unfindable_honest", 2, alpha):
            assert all(not attested for _, attested in campaign.attested)
            for witness in campaign.witnesses:
                assert witness.claimed is WitnessDepth.REALITY
                assert witness.depth_basis is DepthBasis.DECLARED
                assert witness.identity is WitnessIdentity.ANONYMOUS
                assert witness.admissible is WitnessDepth.TEXT
                assert witness.ancestry_complete is False


def test_nobody_can_attest_hides_nothing_so_every_refusal_is_pure_cost():
    """The family that decides what the range costs where it can buy nothing.

    Nothing is hidden, so no decision here is margin-critical and the policy can
    prevent no error at all. Against fabrication the range is wide at both ends
    and the primary refuses every settlement the baseline gets right.
    """
    for campaign in campaigns("nobody_can_attest", "unfindable_honest", 4, 1.0):
        assert hidden_group_is_unrecorded(campaign)
        for decision in reversible(campaign):
            assert decision.reference == decision.naive
            assert decision.critical is False
        base = run_campaign(BASELINE, campaign, ErrorClass.FABRICATION, CONFIG)
        primary = run_campaign(PRIMARY, campaign, ErrorClass.FABRICATION, CONFIG)
        for index, decision in enumerate(campaign.decisions):
            if decision.decision_class != REVERSIBLE:
                continue
            assert base[index].terminal == decision.reference
            assert primary[index].terminal == UNSETTLED
            assert primary[index].ends_disagreed is True


def test_the_cost_of_the_range_is_error_class_specific_and_not_uniform():
    """At the bottom class every admissible depth clears divergence, so the two
    ends coincide and the primary settles everything. A world in which the
    primary refused in every cell could not tell degeneration from strictness."""
    campaign = campaigns("nobody_can_attest", "unfindable_honest", 1, 1.0)[0]
    transcription = run_campaign(PRIMARY, campaign, ErrorClass.TRANSCRIPTION, CONFIG)
    assert all(o.terminal in SETTLED for o in transcription)
    assert all(not o.range_is_wide for o in transcription)


# --- family 2: the adversary attests freely ---------------------------------


def test_adversary_states_reality_with_no_backing_in_the_declared_strains():
    for variant in ("declares_completeness", "declares_depth_only", "claims_bonded_identity"):
        for campaign in campaigns(FREELY_ATTESTING_FAMILY, variant, 2, 1.0):
            units = dict(campaign.unit_of)
            adversaries = [w for w in campaign.witnesses if w.name.startswith("a")]
            assert len(adversaries) == CONFIG["adversary_group_size"]
            assert {units[w.name] for w in adversaries} == {"hidden:fabricator"}
            for witness in adversaries:
                assert witness.claimed is WitnessDepth.REALITY
                # No artifact, no device: nothing was produced, only stated.
                assert witness.depth_basis is DepthBasis.DECLARED
                assert not witness.markers


def test_declared_completeness_still_buys_nothing_after_the_repair():
    """`ancestry_complete` is recorded and not honoured. Kept from AID-1 because
    a world that drops the case a repair claims to have fixed cannot show it."""
    for campaign in campaigns(FREELY_ATTESTING_FAMILY, "declares_completeness", 2, 1.0):
        adversaries = tuple(w for w in campaign.witnesses if w.name.startswith("a"))
        for witness in adversaries:
            assert witness.ancestry_complete is True
            assert witness.identity is WitnessIdentity.ANONYMOUS
            assert witness.admissible is WitnessDepth.TEXT
        assert not attested_independent(
            adversaries[0], adversaries[1], ErrorClass.FABRICATION
        )
        assert witness_bounds(adversaries, ErrorClass.FABRICATION).lower == 1


def test_a_self_declared_bond_is_honoured_as_a_bare_claim_of_identity():
    """`honoured_identity` degrades an unreferenced BONDED claim to NAMED, whose
    stake is worth `PROCEDURAL` backing, whose floor is `RAW`."""
    for campaign in campaigns(FREELY_ATTESTING_FAMILY, "claims_bonded_identity", 2, 1.0):
        adversaries = tuple(w for w in campaign.witnesses if w.name.startswith("a"))
        for witness in adversaries:
            assert witness.identity is WitnessIdentity.BONDED
            assert witness.depth_basis is DepthBasis.DECLARED
            assert witness.stake_reference is None
            assert witness.admissible is WitnessDepth.RAW
        assert witness_bounds(adversaries, ErrorClass.FABRICATION).lower == 1


def test_the_depth_only_strain_is_the_one_where_backing_bites():
    for campaign in campaigns(FREELY_ATTESTING_FAMILY, "declares_depth_only", 2, 1.0):
        adversaries = tuple(w for w in campaign.witnesses if w.name.startswith("a"))
        for witness in adversaries:
            assert witness.ancestry_complete is False
            assert witness.admissible is WitnessDepth.TEXT
        assert witness_bounds(adversaries, ErrorClass.FABRICATION).lower == 1
        face = tuple(at_face_value(w) for w in adversaries)
        assert witness_bounds(face, ErrorClass.FABRICATION).lower == len(adversaries)


def test_a_device_attested_fabricator_is_counted_in_full_at_both_ends():
    """The strain aimed at the range, and the defect it exhibits.

    Three copies of one fabricator, each carrying a device attestation, are
    admissible at `REALITY`; the record connects none of them. `independent_for`
    asks only that both witnesses clear the error class and that their recorded
    ancestries are disjoint, so the **lower** bound -- the one the policy
    describes as counting only independence that was *earned* -- counts them as
    three. The range is not merely wide here, it is pinned on a falsehood: both
    ends agree, so the rule settles, and settles wrongly in every decision.
    """
    for campaign in campaigns(FREELY_ATTESTING_FAMILY, "device_attested_fabricator", 4, 1.0):
        by_name = {w.name: w for w in campaign.witnesses}
        adversaries = tuple(by_name[n] for n in sorted(by_name) if n.startswith("a"))
        honest = tuple(by_name[n] for n in sorted(by_name) if n.startswith("h"))
        assert hidden_group_is_unrecorded(campaign)
        for witness in adversaries:
            assert witness.admissible is WitnessDepth.REALITY
        for witness in honest:
            assert witness.admissible is WitnessDepth.TEXT
        # Earned-only and cannot-rule-it-out agree, on three sources that are one.
        adversary_bounds = witness_bounds(adversaries, ErrorClass.FABRICATION)
        assert adversary_bounds == WitnessBounds(len(adversaries), len(adversaries))
        # The honest pair filed through one recorded intermediary and cannot
        # attest, so they collapse to one at both ends instead.
        honest_bounds = witness_bounds(honest, ErrorClass.FABRICATION)
        assert honest_bounds == WitnessBounds(1, 1)

        primary = run_campaign(PRIMARY, campaign, ErrorClass.FABRICATION, CONFIG)
        for index, decision in enumerate(campaign.decisions):
            if decision.decision_class != REVERSIBLE:
                continue
            assert primary[index].terminal in SETTLED
            assert primary[index].terminal != decision.reference
            assert primary[index].range_is_wide is False


# --- family 3: DR3's hidden shared source -----------------------------------


def test_hidden_source_is_invisible_in_the_record_at_every_cut():
    for variant in VARIANTS[HIDDEN_FAMILY]:
        for campaign in campaigns(HIDDEN_FAMILY, variant, 3, 1.0):
            assert hidden_group_is_unrecorded(campaign)
            group = {name for name, unit in campaign.unit_of if unit == "hidden:source"}
            assert len(group) == CONFIG["hidden_group_size"]
            for decision in campaign.decisions:
                for cut in campaign.ancestry_cuts:
                    grouped: dict[str, set[str]] = {}
                    for item in decision.evidence:
                        root = item.roots.get(cut)
                        if root is None:
                            continue
                        grouped.setdefault(root, set()).add(
                            item.observation_id.rsplit("|", 1)[1]
                        )
                    assert not any(len(members & group) > 1 for members in grouped.values())


def test_hidden_source_false_settlements_are_silent_and_margin_critical():
    silent = critical = 0
    for variant in VARIANTS[HIDDEN_FAMILY]:
        for campaign in campaigns(HIDDEN_FAMILY, variant, 6, 1.0):
            outcomes = run_campaign(BASELINE, campaign, ErrorClass.FABRICATION, CONFIG)
            for index, decision in enumerate(campaign.decisions):
                if decision.decision_class != REVERSIBLE:
                    continue
                terminal = outcomes[index].terminal
                if terminal in SETTLED and terminal != decision.reference:
                    # Nothing recorded connects the group, so the record alone
                    # settles exactly the way the baseline does: no flag.
                    assert decision.robust_settlement == terminal
                    silent += 1
                    critical += decision.critical
    assert silent >= 12
    assert critical == silent


def test_aware_and_unaware_are_now_the_same_case_to_the_policy():
    """The repair's own claim, pinned. `ancestry_complete` differs between these
    two variants and nothing the policy computes may differ because of it."""
    unaware = campaigns(HIDDEN_FAMILY, "unaware", 1, 1.0)[0]
    aware = campaigns(HIDDEN_FAMILY, "aware", 1, 1.0)[0]
    by_name = {w.name: w for w in aware.witnesses}
    for witness in unaware.witnesses:
        other = by_name[witness.name]
        assert witness.admissible is other.admissible
        if witness.name.startswith("g"):
            assert witness.ancestry_complete is True
            assert other.ancestry_complete is False
        for error in ERRORS:
            for partner in unaware.witnesses:
                if partner.name == witness.name:
                    continue
                assert attested_independent(witness, partner, error) is attested_independent(
                    by_name[witness.name], by_name[partner.name], error
                )


def test_device_attested_echoes_invert_who_the_policy_protects():
    """The hidden group carries the backing and the honest independents do not.

    Every echo is admissible at `REALITY` and nothing in the record connects
    them, so both ends of the range count four sources where there is one. The
    honest independents cannot attest, so the lower bound deflates them. The
    range agrees, and it agrees with the echoes.
    """
    for campaign in campaigns(HIDDEN_FAMILY, "device_attested_echoes", 3, 1.0):
        by_name = {w.name: w for w in campaign.witnesses}
        echoes = tuple(by_name[n] for n in sorted(by_name) if n.startswith("g"))
        independents = tuple(by_name[n] for n in sorted(by_name) if n.startswith("i"))
        for witness in echoes:
            assert witness.admissible is WitnessDepth.REALITY
        for witness in independents:
            assert witness.admissible is WitnessDepth.TEXT
        assert witness_bounds(echoes, ErrorClass.FABRICATION) == WitnessBounds(
            len(echoes), len(echoes)
        )
        assert witness_bounds(independents, ErrorClass.FABRICATION).lower == 1
        # The group is genuinely one source, and the record still shows nothing.
        assert hidden_group_is_unrecorded(campaign)
        assert len({unit for name, unit in campaign.unit_of if name.startswith("g")}) == 1


# --- family 4: the baseline is already right --------------------------------


def test_baseline_already_right_really_is_already_right():
    for alpha in ALPHAS:
        for campaign in campaigns(ALREADY_RIGHT_FAMILY, "nothing_hidden", 2, alpha):
            assert hidden_group_is_unrecorded(campaign)
            for error in ERRORS:
                outcomes = run_campaign(BASELINE, campaign, error, CONFIG)
                for index, decision in enumerate(campaign.decisions):
                    if decision.decision_class != REVERSIBLE:
                        continue
                    assert decision.reference in SETTLED
                    assert decision.reference == decision.naive
                    assert decision.critical is False
                    assert outcomes[index].terminal == decision.reference


def test_the_family_criterion_six_is_scored_on_can_be_settled_and_can_be_refused():
    """Criterion 6's target, and the proof that it is a test rather than a trap.

    At full adoption these witnesses are backed by an artifact and a verified
    identity, which tops out at `METHOD`. Against a fabrication-class error the
    lower bound therefore earns nothing while the upper bound counts everyone,
    the ends disagree, and the primary refuses every decision the baseline gets
    right. One error class up the same population settles completely. The
    criterion can be passed and can be failed by the same world, which is what
    makes it measure the degeneration rather than the construction.
    """
    campaign = campaigns(ALREADY_RIGHT_FAMILY, "nothing_hidden", 1, 1.0)[0]
    for witness in campaign.witnesses:
        assert witness.admissible is WitnessDepth.METHOD

    fabrication = run_campaign(PRIMARY, campaign, ErrorClass.FABRICATION, CONFIG)
    assert all(o.terminal == UNSETTLED for o in fabrication)
    assert all(o.ends_disagreed for o in fabrication)

    instrument = run_campaign(PRIMARY, campaign, ErrorClass.INSTRUMENT, CONFIG)
    assert all(o.terminal in SETTLED for o in instrument)
    base = run_campaign(BASELINE, campaign, ErrorClass.INSTRUMENT, CONFIG)
    assert [o.terminal for o in instrument] == [o.terminal for o in base]


# --- family 5: minority suppression -----------------------------------------


def test_minority_family_carries_a_true_contrary_claim_that_cannot_attest():
    for variant in VARIANTS[MINORITY_FAMILY]:
        for alpha in ALPHAS:
            for campaign in campaigns(MINORITY_FAMILY, variant, 2, alpha):
                attested = dict(campaign.attested)
                minority = [w for w in campaign.witnesses if w.name.startswith("c")]
                assert len(minority) == CONFIG["minority_size"]
                for witness in minority:
                    assert attested[witness.name] is False
                    assert witness.admissible is WitnessDepth.TEXT
                for decision in campaign.decisions:
                    values = dict(decision.values)
                    assert decision.contrary_value == decision.truth
                    for witness in minority:
                        assert values[witness.name] == decision.truth
                    for name in [
                        w.name for w in campaign.witnesses if w.name.startswith("m")
                    ]:
                        assert values[name] != decision.truth
                # Genuinely independent on both sides: no shared unit anywhere.
                assert len({unit for _, unit in campaign.unit_of}) == len(campaign.unit_of)


def test_the_range_prevents_the_suppression_the_single_count_caused():
    """AID-1's outright failure, and the repair's central claim, in one place."""
    for campaign in campaigns(MINORITY_FAMILY, "count_decides_survival", 3, 1.0):
        for error in ERRORS:
            base = run_campaign(BASELINE, campaign, error, CONFIG)
            primary = run_campaign(PRIMARY, campaign, error, CONFIG)
            for index, decision in enumerate(campaign.decisions):
                if decision.decision_class != REVERSIBLE:
                    continue
                assert contrary_claim_survives(decision, base[index].terminal)
                assert contrary_claim_survives(decision, primary[index].terminal)


def test_recorded_kinship_is_a_decoy_that_deletes_the_true_claim_at_both_ends():
    """The construction that fails criterion 5, and why it is not rigged.

    All six witnesses went to the world alone: no two share a causal unit, so
    the minority really is three independent sources carrying the true value.
    The record merely shows the three of them citing one registry, and they
    cannot attest. `_ladder_view` runs the ladder at *admissible* depth rather
    than at the claimed depth, so the policy's discount is applied at the upper
    end too -- the end that is supposed to count independence wherever the
    record cannot rule it out. Recorded kinship then defeats the minority at
    both ends at once, the range agrees, and the rule settles against a true
    claim that the baseline preserves.

    The baseline survives this because the ladder reads the claimed `REALITY`
    and shared ancestry cannot beat a divergence of zero. So does the theatre
    arm, and so does refusal. The primary is the only arm that suppresses.
    """
    for campaign in campaigns(MINORITY_FAMILY, "recorded_kinship_decoy", 4, 1.0):
        assert recorded_kinship_is_a_decoy(campaign)
        by_name = {w.name: w for w in campaign.witnesses}
        minority = tuple(by_name[n] for n in sorted(by_name) if n.startswith("c"))
        majority = tuple(by_name[n] for n in sorted(by_name) if n.startswith("m"))
        # Recorded kinship among the minority, and none of it is real.
        for left, right in itertools.combinations(minority, 2):
            assert left.ancestry & right.ancestry
        units = dict(campaign.unit_of)
        assert len({units[w.name] for w in minority}) == len(minority)
        # Collapsed at both ends; the majority counted in full at both ends.
        assert witness_bounds(minority, ErrorClass.FABRICATION) == WitnessBounds(1, 1)
        assert witness_bounds(majority, ErrorClass.FABRICATION) == WitnessBounds(
            len(majority), len(majority)
        )

        base = run_campaign(BASELINE, campaign, ErrorClass.FABRICATION, CONFIG)
        primary = run_campaign(PRIMARY, campaign, ErrorClass.FABRICATION, CONFIG)
        theatre = run_campaign(THEATRE, campaign, ErrorClass.FABRICATION, CONFIG)
        refuse = run_campaign(REFUSE, campaign, ErrorClass.FABRICATION, CONFIG)
        for index, decision in enumerate(campaign.decisions):
            if decision.decision_class != REVERSIBLE:
                continue
            assert contrary_claim_survives(decision, base[index].terminal)
            assert contrary_claim_survives(decision, theatre[index].terminal)
            assert contrary_claim_survives(decision, refuse[index].terminal)
            assert not contrary_claim_survives(decision, primary[index].terminal)


def test_the_scope_guard_still_exists_and_is_still_powerless():
    campaign = campaigns(MINORITY_FAMILY, "count_decides_survival", 1, 1.0)[0]
    assert survival_call_is_refused(campaign.witnesses, ErrorClass.FABRICATION)
    # And the same count, declared as permitting an action, is answered.
    assert attested_effective(
        campaign.witnesses, ErrorClass.FABRICATION, use=Use.PERMIT_ACTION
    ) >= 1


# --- family 6: mixed attestation --------------------------------------------


def test_mixed_attestation_really_mixes_within_one_decision():
    campaign = campaigns(MIXED_FAMILY, "mixed", 1, 1.0)[0]
    by_name = {w.name: w for w in campaign.witnesses}
    assert by_name["x5"].admissible is WitnessDepth.UNSTATED
    assert by_name["x5"].has_depth is False
    assert by_name["x6"].admissible is WitnessDepth.REALITY
    assert by_name["x4"].admissible is WitnessDepth.TEXT
    assert by_name["x0"].admissible is WitnessDepth.METHOD
    assert by_name["x2"].ancestry & by_name["x3"].ancestry
    assert by_name["x2"].markers & by_name["x3"].markers
    seen = set()
    for alpha in (0.25, 0.5, 0.75):
        for campaign in campaigns(MIXED_FAMILY, "mixed", 4, alpha):
            seen.add(campaign.mixed_attestation)
    assert True in seen


def test_a_shared_marker_is_decisive_for_both_the_ladder_and_the_policy():
    campaign = campaigns(MIXED_FAMILY, "mixed", 1, 1.0)[0]
    by_name = {w.name: w for w in campaign.witnesses}
    left, right = by_name["x2"], by_name["x3"]
    for error in ERRORS:
        assert not attested_independent(left, right, error)
        assert not ladder_independent(ladder_source(left), ladder_source(right), error)


def test_both_ends_can_agree_on_a_settlement_the_range_does_not_determine():
    """The defect in the rule *as the specification words it*.

    The rule reads the two diagonal corners of the count box, (lower, lower) and
    (upper, upper). The box is bounded by the other two corners, and
    `settle_counts` is monotone, so a settlement can hold at both read corners
    and fail in between. Here the true side ranges over 1..3 and the false side
    over 2..4: both read corners settle false, and (3, 2) settles true. The rule
    settles anyway, and settles wrongly, in every decision of the variant.

    This is reported, never corrected. Closing the gap would be repairing the
    instrument under test from inside its own world.
    """
    found = 0
    for campaign in campaigns(MIXED_FAMILY, "interior_disagreement", 4, 1.0):
        by_name = {w.name: w for w in campaign.witnesses}
        for name in ("e0", "e1", "h0"):
            assert by_name[name].admissible is WitnessDepth.REALITY
        for name in ("n0", "n1", "h1", "h2"):
            assert by_name[name].admissible is WitnessDepth.TEXT
        # The two device-attested echoes are one source and are counted as two.
        assert len({unit for name, unit in campaign.unit_of if name.startswith("e")}) == 1

        primary = run_campaign(PRIMARY, campaign, ErrorClass.FABRICATION, CONFIG)
        for index, decision in enumerate(campaign.decisions):
            if decision.decision_class != REVERSIBLE:
                continue
            outcome = primary[index]
            # Which side carries which value flips with `truth`, because the
            # sides are split by reported value and not by honesty. The shape of
            # the two ranges does not flip: one side is pinned between one and
            # three, the other between two and four.
            assert {outcome.true_bounds, outcome.false_bounds} == {(1, 3), (2, 4)}
            assert outcome.lower_terminal == outcome.upper_terminal
            assert outcome.terminal in SETTLED
            assert len(outcome.reachable) > 1
            assert outcome.ends_agree_interior_does_not is True
            assert outcome.terminal != decision.reference
            found += 1
    assert found >= 12


# --- the arms ----------------------------------------------------------------


def test_declared_only_is_the_primary_with_admissible_depth_neutralised():
    """Differs from the primary in backing alone, so criterion 3 cannot confound
    "the backing does nothing" with "the range does nothing"."""
    for claimed in WitnessDepth:
        for basis in DepthBasis:
            for identity in WitnessIdentity:
                witness = Witness("w", claimed, basis, identity)
                assert at_face_value(witness).admissible is claimed
                assert at_face_value(witness).ancestry_complete is witness.ancestry_complete
    # And it reaches its answer through the range, exactly as the primary does.
    campaign = campaigns(FREELY_ATTESTING_FAMILY, "declares_depth_only", 1, 1.0)[0]
    for decision in campaign.decisions:
        outcome = settle_decision(THEATRE, campaign, decision, ErrorClass.FABRICATION)
        assert outcome.consulted_a_range is True
        true_side, false_side = sides(campaign, decision)
        for side, reported in (
            (true_side, outcome.true_bounds),
            (false_side, outcome.false_bounds),
        ):
            expected = bounds_for(THEATRE, side, ErrorClass.FABRICATION, 2_000_000)
            assert reported == (expected.lower, expected.upper)


def test_the_policy_is_never_more_permissive_than_the_ladder():
    for family, variant in every_variant():
        for alpha in ALPHAS:
            campaign = generate_campaign(CONFIG, DEV, family, variant, 0, alpha)
            for error in ERRORS:
                for left in campaign.witnesses:
                    for right in campaign.witnesses:
                        if left.name >= right.name:
                            continue
                        if attested_independent(left, right, error):
                            assert ladder_independent(
                                ladder_source(left), ladder_source(right), error
                            )


def test_refuse_all_unrecorded_refuses_whenever_a_pair_lacks_recorded_ancestry():
    for family, variant in every_variant():
        campaign = generate_campaign(CONFIG, DEV, family, variant, 0, 1.0)
        assert not every_pair_shares_ancestry(campaign.witnesses)
        for decision in campaign.decisions:
            outcome = settle_decision(REFUSE, campaign, decision, ErrorClass.FABRICATION)
            assert outcome.terminal == UNSETTLED


def test_every_family_and_variant_is_reachable_and_distinct():
    assert set(VARIANTS) == set(FAMILIES)
    built = {
        (family, variant): layout(CONFIG, family, variant)
        for family, variant in every_variant()
    }
    assert len(built) == sum(len(VARIANTS[f]) for f in FAMILIES)
    for family in FAMILIES:
        # Every distinguishing field, including the ones that separate the two
        # hidden variants and the three declared adversary strains. No variant
        # of a family may be a duplicate of another under another name.
        shapes = {
            tuple(
                (s.wid, s.unit, s.role, s.claimed, s.attestation, s.attestable,
                 s.ancestry, s.markers, s.complete_when_attested,
                 s.complete_override, s.identity_override)
                for s in built[(family, variant)]
            )
            for variant in VARIANTS[family]
        }
        assert len(shapes) == len(VARIANTS[family])


def test_everything_is_deterministic_and_byte_identical():
    for family, variant in every_variant():
        campaign = generate_campaign(CONFIG, DEV, family, variant, 1, 0.5)
        assert campaign == generate_campaign(CONFIG, DEV, family, variant, 1, 0.5)
        for arm in ARMS:
            first = run_campaign(arm, campaign, ErrorClass.INSTRUMENT, CONFIG)
            assert first == run_campaign(arm, campaign, ErrorClass.INSTRUMENT, CONFIG)
    first = evaluate(CONFIG, DEV, 1)
    second = evaluate(CONFIG, DEV, 1)
    assert first["campaignManifestSha256"] == second["campaignManifestSha256"]
    assert semantic_hash(first) == semantic_hash(second)


def test_evaluation_is_reproducible_on_development_campaigns():
    first = evaluate(CONFIG, DEV, 1)
    assert set(first["families"]) == set(FAMILIES)
    assert first["adoptionCurve"]
    for family in FAMILIES:
        assert set(first["variants"][family]) == set(VARIANTS[family])
    verdict = evaluate_criterion(first, CONFIG, True)
    assert verdict["verdict"] in ("supported", "not supported")
    # The reported-not-criteria list of section 6 must actually be emitted.
    sample = next(iter(next(iter(first["families"].values())).values()))
    assert "endsDisagreedShare" in sample["range"]
    assert "primaryMinusPointCorrect" in sample["range"]


# --- the criteria ------------------------------------------------------------


def _comparison(**kwargs):
    row = {
        "correct": 0, "settled": 0, "false": 0, "silent": 0, "unneeded": 0,
        "correctLost": 0, "correctGained": 0, "silentPrevented": 0,
        "armOnlySilent": 0, "criticalSilent": 0, "criticalPrevented": 0,
        "survived": 0, "p": 1.0,
    }
    row.update(kwargs)
    return row


def _row(critical=0, baseline_silent=0, baseline_settled=0, arms_can_differ=True, **per_arm):
    return {
        "baselineCriticalSilent": critical,
        "baselineSilent": baseline_silent,
        "baselineCorrect": 0,
        "baselineSettled": baseline_settled,
        "armsCanDiffer": arms_can_differ,
        "theatreVersusPrimaryP": per_arm.pop("theatre_p", 1.0),
        "comparisons": {arm: _comparison(**per_arm.get(arm, {})) for arm in ARMS},
    }


def _semantic(maker):
    return {
        "families": {
            family: {cell_key(alpha, error): maker(family) for alpha, error in cells(CONFIG)}
            for family in FAMILIES
        }
    }


def test_criterion_fails_closed_when_no_cell_is_powered():
    quiet = evaluate_criterion(_semantic(lambda _: _row(critical=0)), CONFIG, True)
    assert quiet["supported"] is False
    assert quiet["verdict"] == "not supported"
    assert quiet["tests"]["hasPoweredHiddenSourceCell"] is False
    assert quiet["tests"]["hasPoweredFreelyAttestingCell"] is False
    assert len(quiet["underpoweredCells"]) == len(FAMILIES) * len(cells(CONFIG))


def test_criterion_two_is_reported_without_a_pass_mark_where_benefit_is_impossible():
    """The repair section 7 of the spec made, pinned so it cannot quietly revert."""
    def maker(family):
        if family == "nobody_can_attest":
            return _row(critical=0, **{PRIMARY: {"correctLost": 40, "silentPrevented": 0}})
        return _row(critical=0)

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert not any(name.startswith("c2:nobody_can_attest") for name in verdict["tests"])
    reported = [
        name for name in verdict["reportedNotScored"]
        if name.startswith("c2:nobody_can_attest")
    ]
    assert reported
    assert verdict["reportedNotScored"][reported[0]]["isNotAPassMark"] is True


def test_criterion_two_still_bites_where_benefit_was_possible():
    def maker(family):
        if family == HIDDEN_FAMILY:
            return _row(critical=30, **{PRIMARY: {"correctLost": 40, "silentPrevented": 1}})
        return _row(critical=0)

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["supported"] is False
    assert any(
        name.startswith(f"c2:{HIDDEN_FAMILY}") and name.endswith("costBoundedByBenefit")
        for name in verdict["failedTests"]
    )


def test_criterion_fails_outright_when_the_true_contrary_claim_is_suppressed():
    def maker(family):
        if family == MINORITY_FAMILY:
            return _row(critical=0, **{BASELINE: {"survived": 100}, PRIMARY: {"survived": 0}})
        return _row(critical=0)

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["supported"] is False
    assert any(name.endswith("contraryClaimSurvives") for name in verdict["failedTests"])


def test_criterion_six_fails_a_rule_that_refuses_whenever_the_range_is_wide():
    """The kill criterion for degeneration. A primary that settles nothing in
    `baseline_already_right` at full adoption fails here, and should."""
    def maker(family):
        if family == ALREADY_RIGHT_FAMILY:
            return _row(critical=0, baseline_settled=100, **{PRIMARY: {"settled": 0}})
        return _row(critical=0)

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["supported"] is False
    failed = [name for name in verdict["failedTests"] if name.startswith("c6:")]
    assert failed
    assert all("alpha=1.0" in name for name in failed)
    assert len(failed) == len(CONFIG["error_classes"])


def test_criterion_four_fails_a_primary_that_prevents_far_less_than_refusing():
    def maker(family):
        return _row(
            critical=100,
            **{
                PRIMARY: {"correct": 10, "criticalPrevented": 10},
                REFUSE: {"correct": 0, "criticalPrevented": 100},
            },
        )

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["supported"] is False
    assert any(name.startswith("c4:") for name in verdict["failedTests"])


def test_criterion_three_is_skipped_where_no_arm_can_differ():
    def maker(family):
        return _row(critical=100, baseline_silent=100, arms_can_differ=False)

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert not any(name.startswith("c3:") for name in verdict["tests"])
    assert any(
        name.startswith(f"c3:{FREELY_ATTESTING_FAMILY}") and name.endswith("armsCannotDiffer")
        for name in verdict["reportedNotScored"]
    )


def test_criterion_rejects_theatre_even_when_everything_else_holds():
    def maker(family):
        row = _row(
            critical=100,
            baseline_silent=100,
            baseline_settled=100,
            **{
                PRIMARY: {
                    "correct": 100, "settled": 100, "silent": 10, "correctLost": 0,
                    "silentPrevented": 90, "criticalPrevented": 90, "p": 1e-9,
                    "survived": 100,
                },
                THEATRE: {"correct": 100, "silent": 10, "p": 1e-9},
                REFUSE: {"correct": 0, "criticalPrevented": 90, "p": 1e-9},
                BASELINE: {"survived": 100},
            },
        )
        row["theatreVersusPrimaryP"] = 1.0
        return row

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["supported"] is False
    assert any(name.startswith("c3:") for name in verdict["failedTests"])


def test_criterion_can_return_supported_so_the_failures_above_mean_something():
    def maker(family):
        row = _row(
            critical=100,
            baseline_silent=100,
            baseline_settled=100,
            **{
                PRIMARY: {
                    "correct": 100, "settled": 100, "silent": 10, "correctLost": 0,
                    "silentPrevented": 90, "armOnlySilent": 0, "criticalPrevented": 90,
                    "p": 1e-9, "survived": 100,
                },
                THEATRE: {"correct": 100, "silent": 90, "p": 1e-9},
                REFUSE: {"correct": 0, "criticalPrevented": 90, "p": 1e-9},
                BASELINE: {"survived": 100},
            },
        )
        row["theatreVersusPrimaryP"] = 1e-9
        return row

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["failedTests"] == []
    assert verdict["supported"] is True
    assert verdict["verdict"] == "supported"


def test_an_unreproducible_result_is_never_supported():
    def maker(family):
        row = _row(
            critical=100, baseline_silent=100, baseline_settled=100,
            **{
                PRIMARY: {
                    "correct": 100, "settled": 100, "silent": 10, "correctLost": 0,
                    "silentPrevented": 90, "criticalPrevented": 90, "p": 1e-9,
                    "survived": 100,
                },
                THEATRE: {"correct": 100, "silent": 90, "p": 1e-9},
                REFUSE: {"correct": 0, "criticalPrevented": 90, "p": 1e-9},
                BASELINE: {"survived": 100},
            },
        )
        row["theatreVersusPrimaryP"] = 1e-9
        return row

    verdict = evaluate_criterion(_semantic(maker), CONFIG, False)
    assert verdict["supported"] is False


def test_the_confirmatory_salt_is_named_but_never_used_here():
    source = Path(__file__).read_text()
    assert 'CONF = CONFIG["confirmatory_salt"]' in source
    assert CONF != DEV
    # Named so that it can be checked as distinct, and passed to nothing. The
    # needles are assembled at run time so that they do not match themselves.
    name = "CO" + "NF"
    for forbidden in (f"generate_campaign(CONFIG, {name}", f"evaluate(CONFIG, {name}",
                      f"run_campaign(CONFIG, {name}", f"campaigns(CONFIG, {name}",
                      f", {name},", f"({name})", f"({name},"):
        assert forbidden not in source
    with pytest.raises(AssertionError):
        assert CONF == DEV
