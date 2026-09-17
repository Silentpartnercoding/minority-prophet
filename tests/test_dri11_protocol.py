"""Integrity tests for the DRI-11 protocol. Development salt only."""

import json
from pathlib import Path

from experiments.dri3.world import CUTS, REVERSIBLE
from experiments.dri9.rule import lookup_grouping
from experiments.dri11.arms import ARMS, PRIMARY, run_campaign
from experiments.dri11.scoring import evaluate, evaluate_criterion
from experiments.dri11.world import (
    DEPENDENCE_FAMILIES,
    FAMILIES,
    generate_campaign,
    is_fragile_correct,
)

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "dri11" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]
CONF = CONFIG["confirmatory_salt"]


def campaigns(family, count=6, pickup=0.9, leak=0.02):
    return [generate_campaign(CONFIG, DEV, family, rep, pickup, leak) for rep in range(count)]


def test_config_names_their_methods_and_not_ours():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert CONFIG["success_criterion"]["primary"] == PRIMARY == "fragile_refusal"
    assert CONFIG["success_criterion"]["secondary"] == "composite"
    assert "unmarked_hidden_trio" in CONFIG["success_criterion"]["dependence_families"]
    assert "shared_shock" in CONFIG["success_criterion"]["collapse_families"]
    assert tuple(CONFIG["families"]) == FAMILIES
    assert CONF != DEV


def test_unmarked_trio_is_hidden_from_the_record():
    for campaign in campaigns("unmarked_hidden_trio", 4):
        focus = set(campaign.focus_group)
        assert len(focus) == 3
        for decision in campaign.decisions:
            source_of = dict(decision.source_of)
            for cut in CUTS + ("content",):
                groups = {}
                for item in decision.evidence:
                    groups.setdefault(item.roots[cut], set()).add(source_of[item.observation_id])
                assert not any(len(members & focus) > 1 for members in groups.values()), cut


def test_fragile_correct_reversible_decisions_are_mostly_fragile_and_already_right():
    hits = total = 0
    for campaign in campaigns("fragile_correct", 12, leak=0.02):
        for decision in campaign.decisions:
            if decision.decision_class != REVERSIBLE:
                continue
            total += 1
            hits += is_fragile_correct(decision)
    assert total >= 12
    assert hits / total >= 0.7


def test_shared_shock_is_not_an_identity_and_marks_both_when_it_fires():
    shocked = 0
    marked_together = 0
    both_wrong = 0
    for campaign in campaigns("shared_shock", 8, leak=0.02):
        assert campaign.shocked_pair
        left, right = campaign.shocked_pair
        assert all(s.component is None for s in campaign.sources)
        for decision in campaign.decisions:
            if not decision.shocked:
                continue
            shocked += 1
            source_of = dict(decision.source_of)
            holders = {source_of[obs] for obs, _ in decision.markers}
            marked_together += left in holders and right in holders
            values = {source_of[i.observation_id]: i.value for i in decision.evidence}
            both_wrong += values[left] != decision.truth and values[right] != decision.truth
    assert shocked >= 8
    assert marked_together == shocked
    assert both_wrong == shocked


def test_common_carrier_still_shares_no_error():
    for campaign in campaigns("common_carrier", 4):
        assert all(s.component is None for s in campaign.sources)
        assert campaign.marked_channel == "lib:shared"


def test_robust_correct_has_no_focus_to_inflate_critical():
    campaign = campaigns("robust_correct", 1)[0]
    assert campaign.focus_group == ()


def test_criterion_fails_closed_when_quiet_and_when_refusal_is_expensive():
    def comparison(prevented=0, unneeded=0, arm_only=0, p=1.0):
        return {
            "silent": 0, "unneeded": unneeded, "criticalSilent": 0,
            "criticalPrevented": prevented, "tieredOnlySilent": prevented,
            "armOnlySilent": arm_only, "p": p,
        }

    def row(critical=3, prevented=0, unneeded=0, correct=1000, method_correct=1000, false_m=0):
        comp = comparison(prevented, unneeded)
        return {
            "arms": {
                "tiered_rule": {f"{REVERSIBLE}:correct_settlement": correct},
                "fragile_refusal": {f"{REVERSIBLE}:correct_settlement": method_correct,
                                    "trueMerges": 0, "falseMerges": 0},
                "composite": {f"{REVERSIBLE}:correct_settlement": method_correct,
                              "trueMerges": 0, "falseMerges": false_m},
            },
            "reversibleTieredSilent": critical,
            "criticalTieredSilent": critical,
            "comparisons": {arm: dict(comp) for arm in
                            ("fragile_refusal", "composite", "bait", "ladder")},
        }

    from experiments.dri11.world import cell_key, cells

    def semantic(maker):
        return {"families": {f: {cell_key(p, leak): maker(f) for p, leak in cells(CONFIG)} for f in FAMILIES}}

    quiet = evaluate_criterion(semantic(lambda _: row(3, 0, 0)), CONFIG, True)
    assert quiet["supported"] is False
    assert quiet["tests"]["hasPoweredDependenceComparison"] is False

    expensive = evaluate_criterion(
        semantic(lambda fam: row(40, 10, unneeded=80) if fam == "fragile_correct" else row(40, 30, 0)),
        CONFIG,
        True,
    )
    assert any(k.endswith("costBound") and v is False for k, v in expensive["tests"].items())
    assert expensive["supportedPrimary"] is False


def test_everything_is_deterministic():
    for family in FAMILIES:
        campaign = generate_campaign(CONFIG, DEV, family, 1, 0.9, 0.02)
        assert campaign == generate_campaign(CONFIG, DEV, family, 1, 0.9, 0.02)
        for arm in ARMS:
            first, left = run_campaign(arm, campaign, CONFIG, DEV)
            again, right = run_campaign(arm, campaign, CONFIG, DEV)
            assert [vars(o) for o in first] == [vars(o) for o in again]
            assert sorted(map(sorted, left.groups)) == sorted(map(sorted, right.groups))


def test_evaluation_runs_on_one_development_campaign():
    first = evaluate(CONFIG, DEV, 1)
    assert first == evaluate(CONFIG, DEV, 1)
    assert set(first["families"]) == set(FAMILIES)


def test_runner_pins_hold_and_refuse_changed_inputs(tmp_path):
    import shutil

    import pytest

    from experiments.dri11.run_confirmatory import PINNED, load_config, verify_pins

    verify_pins()
    assert load_config()["success_criterion"]["primary"] == "fragile_refusal"
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    target = tmp_path / "experiments/dri11/world.py"
    target.write_text(target.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="dri11/world.py"):
        verify_pins(tmp_path)
