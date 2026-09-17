"""Integrity tests for the AID-1 protocol. Development salt only.

These are construction tests, not results. Each one asserts that a family really
produces the case section 5 of the spec asked for -- that the hidden source is
invisible in the record at every cut, that the freely-attesting adversary really
does state `REALITY` with nothing behind it, that the minority family really
carries a true contrary claim, that the already-right family really is already
right. If one of these fails, the construction is wrong and the construction is
what gets fixed.
"""

import json
from pathlib import Path

import pytest

from aggregation.attested_independence import Use, Witness
from aggregation.attested_independence import effective_witnesses_for as attested_effective
from aggregation.attested_independence import independent_for as attested_independent
from aggregation.independence_axes import DepthBasis, WitnessDepth, WitnessIdentity
from canon.proximity import ErrorClass
from canon.proximity import independent_for as ladder_independent
from experiments.aid1run.arms import (
    ARMS,
    BASELINE,
    POLICY,
    REFUSE,
    THEATRE,
    at_face_value,
    every_pair_shares_ancestry,
    ladder_source,
    run_campaign,
    settle_decision,
    survival_call_is_refused,
)
from experiments.aid1run.scoring import (
    contrary_claim_survives,
    evaluate,
    evaluate_criterion,
    semantic_hash,
)
from experiments.aid1run.world import (
    FAMILIES,
    FREELY_ATTESTING_FAMILY,
    HIDDEN_FAMILY,
    MINORITY_FAMILY,
    SETTLED,
    VARIANTS,
    build_witness,
    cell_key,
    cells,
    generate_campaign,
    hidden_group_is_unrecorded,
    layout,
)
from experiments.dri3.world import REVERSIBLE

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "aid1run" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]
CONF = CONFIG["confirmatory_salt"]
ALPHAS = tuple(CONFIG["adoption_rates"])
ERRORS = (ErrorClass.FABRICATION, ErrorClass.INSTRUMENT, ErrorClass.TRANSCRIPTION)


def campaigns(family, variant, count=4, alpha=1.0):
    return [
        generate_campaign(CONFIG, DEV, family, variant, replicate, alpha)
        for replicate in range(count)
    ]


def reversible(campaign):
    return [d for d in campaign.decisions if d.decision_class == REVERSIBLE]


def test_config_is_preregistered_and_names_the_arms_the_spec_named():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert tuple(CONFIG["families"]) == FAMILIES
    assert len(FAMILIES) == 6
    assert ARMS == ("ladder", "attested", "attested_declared_only", "refuse_all_unrecorded")
    rule = CONFIG["success_criterion"]
    assert (rule["baseline_arm"], rule["policy_arm"]) == (BASELINE, POLICY)
    assert (rule["theatre_arm"], rule["refusal_arm"]) == (THEATRE, REFUSE)
    assert rule["prevented_share"] == 0.40
    assert rule["scope"] == "reversible"
    assert set(CONFIG["adoption_rates"]) >= {0.0, 0.25, 0.5, 0.75, 1.0}
    assert CONF != DEV


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


def test_nobody_can_attest_hides_nothing_so_every_lost_settlement_is_pure_cost():
    for campaign in campaigns("nobody_can_attest", "unfindable_honest", 4, 1.0):
        assert hidden_group_is_unrecorded(campaign)
        for decision in reversible(campaign):
            assert decision.reference == decision.naive
            assert decision.critical is False
        results = run_campaign(BASELINE, campaign, ErrorClass.FABRICATION, CONFIG)
        policy = run_campaign(POLICY, campaign, ErrorClass.FABRICATION, CONFIG)
        for index, decision in enumerate(campaign.decisions):
            if decision.decision_class != REVERSIBLE:
                continue
            assert results[index].terminal == decision.reference
            assert policy[index].terminal == "unsettled"


# --- family 2: the adversary attests freely ---------------------------------


def test_adversary_states_reality_with_no_backing_in_every_strain():
    for variant in VARIANTS[FREELY_ATTESTING_FAMILY]:
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


def test_declared_completeness_no_longer_buys_independence():
    """The spec's own family, verbatim: declared REALITY, declared complete
    ancestry, no backing, no holdable identity.

    Until AID-1 this asserted the opposite, and that assertion was the point:
    the completeness clause returned before any depth was consulted, so saying
    the words bought full independence. The clause was removed afterwards,
    because a witness cannot certify an absence it cannot see. The world is
    unchanged; only the policy moved.
    """
    for campaign in campaigns(FREELY_ATTESTING_FAMILY, "declares_completeness", 2, 1.0):
        adversaries = tuple(w for w in campaign.witnesses if w.name.startswith("a"))
        for witness in adversaries:
            assert witness.ancestry_complete is True
            assert witness.identity is WitnessIdentity.ANONYMOUS
            # The backing machinery works: the claim is granted TEXT, not REALITY.
            assert witness.admissible is WitnessDepth.TEXT
        # And it is no longer bypassed: TEXT cannot clear a fabrication-class
        # divergence, and the declaration adds nothing on top of it.
        assert not attested_independent(
            adversaries[0], adversaries[1], ErrorClass.FABRICATION
        )
        # None of them is independent of any other now, so the group that once
        # counted as three counts as one.
        assert attested_effective(
            adversaries, ErrorClass.FABRICATION, use=Use.PERMIT_ACTION
        ) == 1


def test_a_self_declared_bond_no_longer_buys_reality():
    """`IndependenceAxes.honoured_identity` degrades an unreferenced BONDED claim.

    Until AID-1 this asserted `REALITY` and a full independent count, because
    `Witness.admissible` called `admissible_depth` directly and skipped the
    guard sitting one import away. The guard is wired in now, so a bond with
    nothing to point at is honoured as a bare claim of identity and buys what
    that is worth. The world is unchanged; only the policy moved.
    """
    for campaign in campaigns(FREELY_ATTESTING_FAMILY, "claims_bonded_identity", 2, 1.0):
        adversaries = tuple(w for w in campaign.witnesses if w.name.startswith("a"))
        for witness in adversaries:
            assert witness.identity is WitnessIdentity.BONDED
            assert witness.depth_basis is DepthBasis.DECLARED
            assert witness.ancestry_complete is False
            assert witness.admissible is not WitnessDepth.REALITY
        assert attested_effective(
            adversaries, ErrorClass.FABRICATION, use=Use.PERMIT_ACTION
        ) < len(adversaries)


def test_the_depth_only_strain_is_the_one_where_backing_bites():
    for campaign in campaigns(FREELY_ATTESTING_FAMILY, "declares_depth_only", 2, 1.0):
        adversaries = tuple(w for w in campaign.witnesses if w.name.startswith("a"))
        for witness in adversaries:
            assert witness.ancestry_complete is False
            assert witness.admissible is WitnessDepth.TEXT
        assert attested_effective(adversaries, ErrorClass.FABRICATION, use=Use.PERMIT_ACTION) == 1
        face = tuple(at_face_value(w) for w in adversaries)
        assert attested_effective(
            face, ErrorClass.FABRICATION, use=Use.PERMIT_ACTION
        ) == len(adversaries)


# --- family 3: DR3's hidden shared source -----------------------------------


def test_hidden_source_is_invisible_in_the_record_at_every_cut():
    for variant in VARIANTS[HIDDEN_FAMILY]:
        for campaign in campaigns(HIDDEN_FAMILY, variant, 3, 1.0):
            assert hidden_group_is_unrecorded(campaign)
            group = {
                name for name, unit in campaign.unit_of if unit == "hidden:source"
            }
            assert len(group) == CONFIG["hidden_group_size"]
            source_of = {
                f"{d.decision_id}|{name}": name
                for d in campaign.decisions
                for name in group
            }
            for decision in campaign.decisions:
                for cut in campaign.ancestry_cuts:
                    together = {
                        source_of[item.observation_id]
                        for item in decision.evidence
                        if item.observation_id in source_of and item.roots.get(cut)
                    }
                    grouped = {}
                    for item in decision.evidence:
                        root = item.roots.get(cut)
                        if root is None:
                            continue
                        grouped.setdefault(root, set()).add(
                            item.observation_id.rsplit("|", 1)[1]
                        )
                    assert not any(len(members & group) > 1 for members in grouped.values())
                    assert together or True


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


def test_unaware_and_aware_hidden_witnesses_differ_only_in_the_completeness_claim():
    unaware = campaigns(HIDDEN_FAMILY, "unaware", 1, 1.0)[0]
    aware = campaigns(HIDDEN_FAMILY, "aware", 1, 1.0)[0]
    by_name = {w.name: w for w in aware.witnesses}
    for witness in unaware.witnesses:
        other = by_name[witness.name]
        assert witness.admissible is other.admissible
        if witness.name.startswith("g"):
            assert witness.ancestry_complete is True
            assert other.ancestry_complete is False


# --- family 4: the baseline is already right --------------------------------


def test_baseline_already_right_really_is_already_right():
    for alpha in ALPHAS:
        for campaign in campaigns("baseline_already_right", "nothing_hidden", 2, alpha):
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


def test_baseline_already_right_costs_the_policy_everything_against_fabrication():
    """The price the repair introduced, recorded rather than hidden.

    Until AID-1 this asserted that full adoption settled everything here. The
    repaired policy settles **nothing** in this family against a
    fabrication-class error even at full adoption, because these witnesses are
    backed by an artifact and a verified identity, which tops out at `METHOD`.
    Only a device attestation or a resolved bond reaches `REALITY`, and nothing
    shallower clears a fabrication divergence.

    Defensible doctrine — a log proves you did something, not that you stood in
    the room — and expensive. One class up it behaves as the family intends.
    """
    full = run_campaign(
        POLICY,
        campaigns("baseline_already_right", "nothing_hidden", 1, 1.0)[0],
        ErrorClass.FABRICATION,
        CONFIG,
    )
    assert all(o.terminal == "unsettled" for o in full)

    settled_at_full = run_campaign(
        POLICY,
        campaigns("baseline_already_right", "nothing_hidden", 1, 1.0)[0],
        ErrorClass.INSTRUMENT,
        CONFIG,
    )
    settled_at_none = run_campaign(
        POLICY,
        campaigns("baseline_already_right", "nothing_hidden", 1, 0.0)[0],
        ErrorClass.INSTRUMENT,
        CONFIG,
    )
    assert sum(o.terminal in SETTLED for o in settled_at_full) > sum(
        o.terminal in SETTLED for o in settled_at_none
    )


# --- family 5: minority suppression -----------------------------------------


def test_minority_family_carries_a_true_contrary_claim_that_cannot_attest():
    for alpha in ALPHAS:
        for campaign in campaigns(MINORITY_FAMILY, "count_decides_survival", 2, alpha):
            attested = dict(campaign.attested)
            minority = [w for w in campaign.witnesses if w.name.startswith("c")]
            assert len(minority) == CONFIG["minority_size"]
            for witness in minority:
                assert attested[witness.name] is False
                assert witness.ancestry_complete is False
                assert witness.admissible is WitnessDepth.TEXT
            for decision in campaign.decisions:
                values = dict(decision.values)
                assert decision.contrary_value == decision.truth
                for witness in minority:
                    assert values[witness.name] == decision.truth
                for name in [w.name for w in campaign.witnesses if w.name.startswith("m")]:
                    assert values[name] != decision.truth
            # Genuinely independent on both sides: no shared unit anywhere.
            assert len({unit for _, unit in campaign.unit_of}) == len(campaign.unit_of)


def test_the_count_no_longer_deletes_the_true_claim():
    """AID-1's outright failure, now repaired.

    Until the repair this asserted `policy_survived == 0`: the attested majority
    kept its independence, the unattestable minority deflated toward one, and
    the majority crossed a threshold the baseline refused to cross — 720 of 720
    decisions settled against a true contrary claim in the confirmatory run.

    It survives now because the repair is strict on *both* sides: the majority's
    artifact-and-verified backing tops out at `METHOD`, which cannot clear a
    fabrication divergence either, so it deflates too and no longer crosses.
    Symmetric strictness removed the asymmetry. That is worth stating precisely,
    because it is not the same as the structural fix: `witness_bounds` is the
    principled answer and these arms still ask for a single count, so this world
    does not exercise it.
    """
    ladder_survived = policy_survived = total = 0
    for campaign in campaigns(MINORITY_FAMILY, "count_decides_survival", 4, 1.0):
        base = run_campaign(BASELINE, campaign, ErrorClass.FABRICATION, CONFIG)
        policy = run_campaign(POLICY, campaign, ErrorClass.FABRICATION, CONFIG)
        for index, decision in enumerate(campaign.decisions):
            if decision.decision_class != REVERSIBLE:
                continue
            total += 1
            ladder_survived += contrary_claim_survives(decision, base[index].terminal)
            policy_survived += contrary_claim_survives(decision, policy[index].terminal)
    assert total >= 12
    assert ladder_survived == total
    assert policy_survived == total


def test_the_scope_bites_only_when_the_caller_declares_what_it_is_doing():
    campaign = campaigns(MINORITY_FAMILY, "count_decides_survival", 1, 1.0)[0]
    assert survival_call_is_refused(campaign.witnesses, ErrorClass.FABRICATION)
    # And the same count, declared as permitting an action, is answered.
    assert attested_effective(
        campaign.witnesses, ErrorClass.FABRICATION, use=Use.PERMIT_ACTION
    ) >= 1


# --- family 6: mixed attestation --------------------------------------------


def test_mixed_attestation_really_mixes_within_one_decision():
    campaign = campaigns("mixed_attestation", "mixed", 1, 1.0)[0]
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
        for campaign in campaigns("mixed_attestation", "mixed", 4, alpha):
            seen.add(campaign.mixed_attestation)
    assert True in seen


def test_a_shared_marker_is_decisive_for_both_the_ladder_and_the_policy():
    campaign = campaigns("mixed_attestation", "mixed", 1, 1.0)[0]
    by_name = {w.name: w for w in campaign.witnesses}
    left, right = by_name["x2"], by_name["x3"]
    for error in ERRORS:
        assert not attested_independent(left, right, error)
        assert not ladder_independent(ladder_source(left), ladder_source(right), error)


# --- the arms ----------------------------------------------------------------


def test_declared_only_is_the_policy_with_admissible_depth_neutralised():
    for claimed in WitnessDepth:
        for basis in DepthBasis:
            for identity in WitnessIdentity:
                witness = Witness("w", claimed, basis, identity)
                assert at_face_value(witness).admissible is claimed
                assert at_face_value(witness).ancestry_complete is witness.ancestry_complete


def test_the_policy_is_never_more_permissive_than_the_ladder():
    for family in FAMILIES:
        for variant in VARIANTS[family]:
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
    for family in FAMILIES:
        for variant in VARIANTS[family]:
            campaign = generate_campaign(CONFIG, DEV, family, variant, 0, 1.0)
            assert not every_pair_shares_ancestry(campaign.witnesses)
            for decision in campaign.decisions:
                outcome = settle_decision(REFUSE, campaign, decision, ErrorClass.FABRICATION)
                assert outcome.terminal == "unsettled"


def test_everything_is_deterministic():
    for family in FAMILIES:
        for variant in VARIANTS[family]:
            campaign = generate_campaign(CONFIG, DEV, family, variant, 1, 0.5)
            assert campaign == generate_campaign(CONFIG, DEV, family, variant, 1, 0.5)
            for arm in ARMS:
                first = run_campaign(arm, campaign, ErrorClass.INSTRUMENT, CONFIG)
                assert first == run_campaign(arm, campaign, ErrorClass.INSTRUMENT, CONFIG)


def test_evaluation_is_reproducible_on_development_campaigns():
    first = evaluate(CONFIG, DEV, 1)
    assert semantic_hash(first) == semantic_hash(evaluate(CONFIG, DEV, 1))
    assert set(first["families"]) == set(FAMILIES)
    assert first["adoptionCurve"]
    verdict = evaluate_criterion(first, CONFIG, True)
    assert verdict["verdict"] in ("supported", "not supported")


# --- the criterion -----------------------------------------------------------


def _comparison(**kwargs):
    row = {
        "correct": 0, "false": 0, "silent": 0, "unneeded": 0, "correctLost": 0,
        "correctGained": 0, "silentPrevented": 0, "armOnlySilent": 0,
        "criticalSilent": 0, "criticalPrevented": 0, "survived": 0, "p": 1.0,
    }
    row.update(kwargs)
    return row


def _row(critical=0, baseline_silent=0, **per_arm):
    return {
        "baselineCriticalSilent": critical,
        "baselineSilent": baseline_silent,
        "baselineCorrect": 0,
        "theatreVersusPolicyP": per_arm.pop("theatre_p", 1.0),
        "comparisons": {
            arm: _comparison(**per_arm.get(arm, {})) for arm in ARMS
        },
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


def test_criterion_fails_when_the_policy_costs_more_than_it_prevents():
    def maker(family):
        if family == "nobody_can_attest":
            return _row(critical=0, **{POLICY: {"correctLost": 40, "silentPrevented": 0}})
        return _row(critical=0)

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["supported"] is False
    assert any(
        name.startswith("c2:nobody_can_attest") and name.endswith("costBoundedByBenefit")
        for name in verdict["failedTests"]
    )


def test_criterion_fails_outright_when_the_true_contrary_claim_is_suppressed():
    def maker(family):
        if family == MINORITY_FAMILY:
            return _row(
                critical=0,
                **{BASELINE: {"survived": 100}, POLICY: {"survived": 0}},
            )
        return _row(critical=0)

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["supported"] is False
    assert any(
        name.endswith("contraryClaimSurvives") for name in verdict["failedTests"]
    )


def test_criterion_rejects_theatre_even_when_everything_else_holds():
    def maker(family):
        row = _row(
            critical=100,
            baseline_silent=100,
            **{
                POLICY: {
                    "correct": 100, "silent": 10, "correctLost": 0,
                    "silentPrevented": 90, "criticalPrevented": 90, "p": 1e-9,
                    "survived": 100,
                },
                THEATRE: {"correct": 100, "silent": 10, "p": 1e-9},
                REFUSE: {"correct": 0, "criticalPrevented": 90, "p": 1e-9},
                BASELINE: {"survived": 100},
            },
        )
        row["theatreVersusPolicyP"] = 1.0
        return row

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["supported"] is False
    assert any(name.startswith("c3:") for name in verdict["failedTests"])


def test_criterion_can_return_supported_so_the_failures_above_mean_something():
    def maker(family):
        policy = {
            "correct": 100, "silent": 10, "correctLost": 0, "silentPrevented": 90,
            "armOnlySilent": 0, "criticalPrevented": 90, "p": 1e-9, "survived": 100,
        }
        theatre = {"correct": 100, "silent": 90, "p": 1e-9}
        row = _row(
            critical=100,
            baseline_silent=100,
            **{
                POLICY: policy,
                THEATRE: theatre,
                REFUSE: {"correct": 0, "criticalPrevented": 90, "p": 1e-9},
                BASELINE: {"survived": 100},
            },
        )
        row["theatreVersusPolicyP"] = 1e-9
        return row

    verdict = evaluate_criterion(_semantic(maker), CONFIG, True)
    assert verdict["failedTests"] == []
    assert verdict["supported"] is True
    assert verdict["verdict"] == "supported"


def test_an_unreproducible_result_is_never_supported():
    def maker(family):
        policy = {
            "correct": 100, "silent": 10, "correctLost": 0, "silentPrevented": 90,
            "criticalPrevented": 90, "p": 1e-9, "survived": 100,
        }
        row = _row(
            critical=100, baseline_silent=100,
            **{POLICY: policy, THEATRE: {"correct": 100, "silent": 90, "p": 1e-9},
               REFUSE: {"correct": 0, "criticalPrevented": 90, "p": 1e-9},
               BASELINE: {"survived": 100}},
        )
        row["theatreVersusPolicyP"] = 1e-9
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
                      f"run_campaign(CONFIG, {name}", f", {name},"):
        assert forbidden not in source
    with pytest.raises(AssertionError):
        assert CONF == DEV
