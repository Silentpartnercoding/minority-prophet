"""Integrity tests for the DRI-10 protocol.

Development salt only. Construction invariants; no arm comparisons on
prevention. The confirmatory salt is not imported.
"""

import json
from pathlib import Path

from experiments.dri3.world import CUTS, IRREVERSIBLE, REVERSIBLE
from experiments.dri10.arms import ARMS, METHOD, run_campaign
from experiments.dri10.scoring import evaluate, evaluate_criterion
from experiments.dri10.world import (
    FAMILIES,
    HARM_FAMILIES,
    HIDDEN_FAMILIES,
    cell_key,
    cells,
    generate_campaign,
)
from experiments.dri9.rule import lookup_grouping

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "dri10" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]
CONF = CONFIG["confirmatory_salt"]


def campaigns(family, count=6, pickup=0.9, leak=0.02):
    return [generate_campaign(CONFIG, DEV, family, rep, pickup, leak) for rep in range(count)]


def test_config_is_frozen_and_names_bait():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert tuple(CONFIG["families"]) == FAMILIES
    assert CONFIG["success_criterion"]["method_under_test"] == METHOD == "bait"
    assert CONFIG["success_criterion"]["floor_family"] == "marked_hidden_pair"
    assert CONFIG["success_criterion"]["mechanism_contrast_family"] == "unmarked_hidden_pair"
    assert tuple(CONFIG["success_criterion"]["harm_families"]) == HARM_FAMILIES
    assert CONF != DEV
    assert CONF not in (DEV,)


def test_every_family_emits_markers_including_the_old_decoy():
    """The DRI-9 decoy hole: leaky_independents must not plant zero markers."""
    for family in FAMILIES:
        n_markers = 0
        for campaign in campaigns(family, 8, pickup=0.9, leak=0.20):
            assert campaign.marked_channel
            n_markers += sum(len(d.markers) for d in campaign.decisions)
        assert n_markers > 0, family


def test_leaky_independents_emit_markers_at_the_low_leak_too():
    n_markers = sum(
        len(d.markers)
        for campaign in campaigns("leaky_independents", 12, pickup=0.5, leak=0.02)
        for d in campaign.decisions
    )
    assert n_markers > 0


def test_marked_hidden_carries_more_than_unmarked_hidden_on_the_focus_group():
    """The mark is a knob. If both families mark the hidden pair the same, the
    world collapsed back into DRI-9."""
    marked_hits = unmarked_hits = focus_obs = 0
    for rep in range(20):
        marked = generate_campaign(CONFIG, DEV, "marked_hidden_pair", rep, 0.9, 0.02)
        unmarked = generate_campaign(CONFIG, DEV, "unmarked_hidden_pair", rep, 0.9, 0.02)
        for campaign, bucket in ((marked, "marked"), (unmarked, "unmarked")):
            focus = set(campaign.focus_group)
            for decision in campaign.decisions:
                source_of = dict(decision.source_of)
                held = {source_of[obs] for obs, _ in decision.markers}
                hits = len(held & focus)
                if bucket == "marked":
                    marked_hits += hits
                else:
                    unmarked_hits += hits
                focus_obs += len(focus)
    assert marked_hits > unmarked_hits * 3
    assert unmarked_hits < marked_hits


def test_common_carrier_shares_a_mark_and_not_an_error_component():
    for campaign in campaigns("common_carrier", 8):
        focus = [s for s in campaign.sources if s.source_id in campaign.focus_group]
        assert len(focus) == 3
        assert all(s.component is None for s in focus)
        assert all(s.carrier == "lib:shared" for s in focus)
        assert campaign.marked_channel == "lib:shared"
        # They must not fault together as a hidden component: no component at all.
        assert {s.component for s in campaign.sources} == {None}


def test_unmarked_hidden_still_hides_the_component_from_the_record():
    for campaign in campaigns("unmarked_hidden_pair", 4):
        focus = set(campaign.focus_group)
        assert len(focus) == 2
        for decision in campaign.decisions:
            source_of = dict(decision.source_of)
            for cut in CUTS + ("content",):
                groups = {}
                for item in decision.evidence:
                    groups.setdefault(item.roots[cut], set()).add(source_of[item.observation_id])
                assert not any(len(members & focus) > 1 for members in groups.values()), cut
            reported = dict(lookup_grouping(decision))
            observation = {source: obs for obs, source in decision.source_of}
            left, right = sorted(focus)
            assert reported[observation[left]] != reported[observation[right]]


def test_criterion_is_fail_closed_when_every_floor_cell_is_underpowered():
    def row(critical=3, prevented=0, arm_only=0, correct=1000, method_correct=1000, false_m=0):
        comparison = {
            "silent": 0, "criticalSilent": 0, "criticalPrevented": prevented,
            "tieredOnlySilent": prevented, "armOnlySilent": arm_only,
            "p": 1.0,
        }
        return {
            "arms": {
                "tiered_rule": {f"{REVERSIBLE}:correct_settlement": correct},
                METHOD: {
                    f"{REVERSIBLE}:correct_settlement": method_correct,
                    f"{REVERSIBLE}:interventions": 0,
                    "trueMerges": 0, "falseMerges": false_m,
                },
            },
            "reversibleTieredSilent": critical,
            "criticalTieredSilent": critical,
            "comparisons": {arm: dict(comparison) for arm in
                            ("fragile_refusal", "bait", "reflection", "ablation", "ladder")},
        }

    def semantic(floor_row, other_row=None):
        other = other_row or floor_row
        families = {}
        for family in CONFIG["families"]:
            families[family] = {
                cell_key(p, leak): (floor_row if family == "marked_hidden_pair" else other)
                for p, leak in cells(CONFIG)
            }
        return {"families": families}

    quiet = evaluate_criterion(semantic(row(3, 0, 0)), CONFIG, True)
    assert quiet["underpoweredComparisons"]
    assert quiet["supported"] is False
    assert quiet["tests"]["hasPoweredFloorComparison"] is False

    # Library collapse at 500 campaigns * 0.1 = 50 allowed.
    collapsed = evaluate_criterion(semantic(row(40, 30, 0), row(0, 0, 0, false_m=200)), CONFIG, True)
    assert collapsed["supported"] is False
    assert any("didNotCollapseTheLibrary" in k and v is False for k, v in collapsed["tests"].items())


def test_only_ablation_spends_and_everything_is_deterministic():
    for family in FAMILIES:
        campaign = generate_campaign(CONFIG, DEV, family, 1, 0.9, 0.02)
        assert campaign == generate_campaign(CONFIG, DEV, family, 1, 0.9, 0.02)
        for arm in ARMS:
            first, left = run_campaign(arm, campaign, CONFIG, DEV)
            again, right = run_campaign(arm, campaign, CONFIG, DEV)
            assert [vars(o) for o in first] == [vars(o) for o in again]
            assert sorted(map(sorted, left.groups)) == sorted(map(sorted, right.groups))
            spent = sum(o.interventions for o in first)
            assert spent <= CONFIG["ablation_budget"]
            if arm != "ablation":
                assert spent == 0


def test_decision_classes_alternate():
    campaign = campaigns("marked_hidden_pair", 1)[0]
    classes = [d.decision_class for d in campaign.decisions]
    assert classes[0] == IRREVERSIBLE and classes[1] == REVERSIBLE


def test_evaluation_runs_on_one_development_campaign_and_does_not_touch_confirmatory():
    first = evaluate(CONFIG, DEV, 1)
    assert first == evaluate(CONFIG, DEV, 1)
    assert first["campaigns"] == len(FAMILIES) * len(cells(CONFIG))
    assert set(first["families"]) == set(FAMILIES)


def test_runner_pins_hold_and_refuse_changed_inputs(tmp_path):
    import shutil

    import pytest

    from experiments.dri10.run_confirmatory import PINNED, load_config, verify_pins

    verify_pins()
    assert load_config()["status"] == "preregistered-unexecuted"
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    reused = tmp_path / "experiments/dri10/world.py"
    reused.write_text(reused.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="dri10/world.py"):
        verify_pins(tmp_path)
