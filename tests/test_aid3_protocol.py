"""Integrity tests for the AID-1 confirmatory protocol. Development salt only."""

import json
from pathlib import Path

from aggregation.attested_independence import independent_for
from aggregation.independence_axes import DepthBasis, WitnessDepth, WitnessIdentity
from canon.proximity import ErrorClass
from experiments.aid3run.arms import ARMS, PRIMARY, declared_only_independent_for, run_decision
from experiments.aid3run.scoring import evaluate, evaluate_criterion
from experiments.aid3run.world import (
    DEPENDENCE_FAMILIES,
    FAMILIES,
    SETTLED_FALSE,
    SETTLED_TRUE,
    generate_campaign,
)

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "aid3run" / "CONFIRMATORY-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]


def campaigns(family, count=6, alpha=1.0):
    return [generate_campaign(CONFIG, DEV, family, rep, alpha) for rep in range(count)]


def test_config_names_their_policy_and_not_a_new_detector():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert CONFIG["success_criterion"]["primary"] == PRIMARY == "attested"
    assert CONFIG["success_criterion"]["theatre"] == "attested_declared_only"
    assert CONFIG["success_criterion"]["dependence_families"] == ["hidden_source"]
    assert CONFIG["success_criterion"]["suppression_families"] == ["minority_suppression"]
    assert tuple(CONFIG["families"]) == FAMILIES
    assert CONFIG["development_salt"] != CONFIG["confirmatory_salt"]


def test_honest_unattestable_cannot_tick_the_box():
    for campaign in campaigns("honest_unattestable", 4, alpha=1.0):
        assert campaign.focus_group == ()
        assert all(not s.can_attest and s.component is None for s in campaign.sources)
        for decision in campaign.decisions:
            assert all(not w.adopted for w in decision.witnesses)
            assert all(w.witness.admissible is WitnessDepth.TEXT for w in decision.witnesses)


def test_hidden_source_is_unrecorded_and_can_fill_the_same_form():
    for campaign in campaigns("hidden_source", 4, alpha=1.0):
        focus = set(campaign.focus_group)
        assert len(focus) == 2
        hidden = [s for s in campaign.sources if s.source_id in focus]
        assert all(s.component == "hidden:u" for s in hidden)
        assert all(s.can_attest and not s.always_attest for s in hidden)
        assert all(s.depth_basis is DepthBasis.DECLARED for s in hidden)
        assert all(s.identity is WitnessIdentity.ANONYMOUS for s in hidden)
        assert all(not s.ancestry for s in campaign.sources)
        for decision in campaign.decisions:
            copies = [w for w in decision.witnesses if w.source_id in focus]
            assert len(copies) == 2
            assert copies[0].unit == copies[1].unit
            assert all(w.adopted for w in copies)


def test_adversary_ticks_complete_even_when_nobody_else_does():
    for campaign in campaigns("adversary_attests", 4, alpha=0.0):
        focus = set(campaign.focus_group)
        for decision in campaign.decisions:
            copies = [w for w in decision.witnesses if w.source_id in focus]
            others = [w for w in decision.witnesses if w.source_id not in focus]
            assert all(w.adopted and w.witness.ancestry_complete for w in copies)
            assert all(not w.adopted for w in others)


def test_complete_box_on_empty_record_no_longer_grants_independence():
    """The hole this world was built to put on the prevention floor, now shut.

    **This assertion is inverted from the reviewer's original, and the
    inversion is the measurement.** As written by the adversarial review it
    asserted that two unbacked witnesses ticking `ancestry_complete` on an
    empty ancestry record are granted independence against fabrication — the
    policy's completeness short-circuit, which the reviewer's own
    preregistration section 10 identified at lines 148-149 and noted was pinned
    elsewhere as intended behaviour.

    That short-circuit was removed in the repair merged as #216, because a
    witness cannot certify an absence it cannot see. The reviewer's world was
    authored against the pre-repair policy; running it against the repaired one
    is the point of AID-3, and this test failing in its original form is the
    repair landing rather than the world breaking.

    The theatre arm keeps the old control flow inline, so it still takes the
    short-circuit. That contrast is now sharper than when the world was
    written, and it is what criterion 3 scores.
    """
    campaign = campaigns("adversary_attests", 1, alpha=0.0)[0]
    decision = campaign.decisions[0]
    focus = set(campaign.focus_group)
    left, right = [w.witness for w in decision.witnesses if w.source_id in focus]
    assert not independent_for(left, right, ErrorClass.FABRICATION)
    assert declared_only_independent_for(left, right, ErrorClass.FABRICATION)


def test_robust_correct_has_no_focus_and_real_backing():
    campaign = campaigns("robust_correct", 1)[0]
    assert campaign.focus_group == ()
    assert all(s.can_attest and s.component is None for s in campaign.sources)
    assert all(s.depth_basis is DepthBasis.DEVICE_ATTESTED for s in campaign.sources)


def test_minority_family_is_a_forced_tie_the_policy_can_break():
    for campaign in campaigns("minority_suppression", 8, alpha=1.0):
        assert set(s.role for s in campaign.sources) == {"attestable", "unattestable"}
        for decision in campaign.decisions:
            assert decision.truth is True
            true_side = [w for w in decision.witnesses if w.vote]
            false_side = [w for w in decision.witnesses if not w.vote]
            assert len(true_side) == len(false_side) == 2
            assert all(w.role == "unattestable" for w in true_side)
            assert all(w.role == "attestable" for w in false_side)
            assert decision.reference not in (SETTLED_TRUE, SETTLED_FALSE)
            assert run_decision("ladder", decision, CONFIG) not in (SETTLED_TRUE, SETTLED_FALSE)
            assert run_decision("attested", decision, CONFIG) == SETTLED_FALSE


def test_mixed_family_always_has_all_three_kinds():
    for campaign in campaigns("mixed_attestation", 4, alpha=1.0):
        roles = {s.role for s in campaign.sources}
        assert roles == {"hidden", "attestable", "unattestable"}
        for decision in campaign.decisions:
            assert {w.role for w in decision.witnesses} == roles
            assert decision.mixed is True


def test_criterion_fails_closed_when_quiet_equal_or_suppressing():
    cells = [f"alpha={a}" for a in CONFIG["adoption_rates"]]

    def comparison(prevented=0, unneeded=0, silent=0, p=1.0):
        return {
            "silent": silent,
            "unneeded": unneeded,
            "criticalSilent": 0,
            "criticalPrevented": prevented,
            "ladderOnlySilent": prevented,
            "armOnlySilent": 0,
            "p": p,
        }

    def row(critical=3, prevented=0, unneeded=0, silent=0, survives=10, theatre_silent=0):
        return {
            "arms": {
                "ladder": {"correct_settlement": 1000, "claimSurvives": survives},
                "attested": {"correct_settlement": 1000, "claimSurvives": survives},
                "attested_declared_only": {"correct_settlement": 1000, "claimSurvives": survives},
                "refuse_all_unrecorded": {"correct_settlement": 0, "claimSurvives": survives},
            },
            "ladderSilent": critical,
            "criticalLadderSilent": critical,
            "comparisons": {
                "attested": comparison(prevented, unneeded, silent),
                "attested_declared_only": comparison(0, 0, theatre_silent),
                "refuse_all_unrecorded": comparison(prevented, 1000, 0),
            },
        }

    def semantic(maker):
        return {"families": {family: {cell: maker(family, cell) for cell in cells} for family in FAMILIES}}

    quiet = evaluate_criterion(semantic(lambda *_: row(3, 0, 0)), CONFIG, True)
    assert quiet["supported"] is False
    assert quiet["tests"]["hasPoweredDependenceComparison"] is False

    theatre = evaluate_criterion(
        semantic(lambda fam, cell: row(40, 20, 0, theatre_silent=0 if fam == "adversary_attests" else 5)),
        CONFIG,
        True,
    )
    assert any(k.endswith("materiallyWorseThanAttested") and v is False for k, v in theatre["tests"].items())
    assert theatre["supported"] is False

    suppression_semantic = semantic(lambda fam, cell: row(40, 20, 0, theatre_silent=8))
    for cell in cells:
        suppression_semantic["families"]["minority_suppression"][cell]["arms"]["attested"]["claimSurvives"] = 0
    suppression = evaluate_criterion(suppression_semantic, CONFIG, True)
    assert any(k.endswith("doesNotSuppress") and v is False for k, v in suppression["tests"].items())
    assert suppression["supported"] is False


def test_everything_is_deterministic():
    for family in FAMILIES:
        first = generate_campaign(CONFIG, DEV, family, 1, 0.5)
        assert first == generate_campaign(CONFIG, DEV, family, 1, 0.5)
        for arm in ARMS:
            outcomes = [run_decision(arm, d, CONFIG) for d in first.decisions]
            again = [run_decision(arm, d, CONFIG) for d in first.decisions]
            assert outcomes == again


def test_evaluation_runs_on_one_development_campaign():
    first = evaluate(CONFIG, DEV, 1)
    assert first == evaluate(CONFIG, DEV, 1)
    assert set(first["families"]) == set(FAMILIES)
    assert set(DEPENDENCE_FAMILIES) <= set(first["families"])


def test_runner_pins_hold_and_refuse_changed_inputs(tmp_path):
    import shutil

    import pytest

    from experiments.aid3run.run_confirmatory import PINNED, load_config, verify_pins

    verify_pins()
    assert load_config()["success_criterion"]["primary"] == "attested"
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    target = tmp_path / "experiments/aid3run/world.py"
    target.write_text(target.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="aid3run/world.py"):
        verify_pins(tmp_path)
