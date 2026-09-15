"""Integrity tests for the frozen DRI-3 protocol.

Development salt only. These assert construction invariants and never compare
arms, so no comparative outcome is seen before the protocol is frozen.
"""

import dataclasses
import json
from collections import Counter, defaultdict
from pathlib import Path

import pytest

from experiments.dri3.arms import VisibleDecision, act
from experiments.dri3.scoring import (
    CORRECT_SETTLEMENT,
    FALSE_SETTLEMENT,
    REQUIRED_ABSTENTION,
    UNNEEDED_ABSTENTION,
    evaluate,
    evaluate_criterion,
    score_decision,
    zero_event_upper_bound,
)
from experiments.dri3.world import (
    CONDITIONS,
    CUTS,
    IRREVERSIBLE,
    RECORDED_FAMILIES,
    REVERSIBLE,
    SETTLED,
    generate_world,
)
from provenance.dependence_robustness import assess_dependence_robustness

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "dri3" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]


def _partition(decision, key):
    groups = defaultdict(set)
    for item in decision.evidence:
        groups[key(item)].add(item.observation_id)
    return {frozenset(group) for group in groups.values()}


def _units(decision):
    unit_of = dict(decision.units)
    return _partition(decision, lambda item: unit_of[item.observation_id])


def test_config_is_frozen_and_sized_for_the_bound():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert CONFIG["development_salt"] != CONFIG["confirmatory_salt"]
    decisions = CONFIG["worlds_per_family"] * CONFIG["decisions_per_world"]
    irreversible = decisions // 2
    bound = CONFIG["success_criterion"]["maximum_rate_bound"]
    assert zero_event_upper_bound(irreversible) < bound
    assert zero_event_upper_bound(decisions) < bound
    assert CONFIG["families"][-1] == CONFIG["expected_failure_family"]
    assert tuple(CONFIG["recorded_families"]) == RECORDED_FAMILIES


@pytest.mark.parametrize("family", CONFIG["families"])
def test_worlds_are_deterministic_and_balanced(family):
    classes, conditions = Counter(), Counter()
    for replicate in range(8):
        world = generate_world(CONFIG, DEV, family, replicate)
        assert world == generate_world(CONFIG, DEV, family, replicate)
        conditions[world.condition] += 1
        for d in world.decisions:
            classes[d.decision_class] += 1
            assert d.lookup_available == (world.condition == CONDITIONS[0])
    assert classes[IRREVERSIBLE] == classes[REVERSIBLE] == 12
    assert conditions[CONDITIONS[0]] == conditions[CONDITIONS[1]] == 4


def test_topology_per_family():
    for replicate in range(20):
        for d in generate_world(CONFIG, DEV, "single_domain", replicate).decisions:
            assert _partition(d, lambda i, c=d.copy_cut: i.roots[c]) == _units(d)
        for d in generate_world(CONFIG, DEV, "joint_domain", replicate).decisions:
            assert all(_partition(d, lambda i, c=c: i.roots[c]) != _units(d) for c in CUTS)
        for d in generate_world(CONFIG, DEV, "separate_control_shared_origin", replicate).decisions:
            assert _partition(d, lambda i: i.roots["evidence_origin"]) == _units(d)
        for d in generate_world(CONFIG, DEV, "three_stacked", replicate).decisions:
            assert all(_partition(d, lambda i, c=c: i.roots[c]) != _units(d) for c in CUTS)
        for d in generate_world(CONFIG, DEV, "decoy_shared_identity", replicate).decisions:
            assert _partition(d, lambda i, c=d.copy_cut: i.roots[c]) == _units(d)
            assert _partition(d, lambda i: i.roots["upstream_component"]) != _units(d)
        for d in generate_world(CONFIG, DEV, "unrecorded_dependence", replicate).decisions:
            assert all(_partition(d, lambda i, c=c: i.roots[c]) != _units(d) for c in CUTS)


def test_side_asymmetric_pairs_are_recorded_at_different_cuts():
    for replicate in range(20):
        for d in generate_world(CONFIG, DEV, "side_asymmetric", replicate).decisions:
            unit_of = dict(d.units)
            for item in d.evidence:
                if unit_of[item.observation_id] == "u_true_pair":
                    assert item.value and item.roots["evidence_origin"].endswith("shared_true")
                if unit_of[item.observation_id] == "u_false_pair":
                    assert not item.value and item.roots["controller"].endswith("shared_false")


def test_recorded_families_keep_the_true_grouping_among_the_readings():
    for family in RECORDED_FAMILIES:
        for replicate in range(20):
            for d in generate_world(CONFIG, DEV, family, replicate).decisions:
                reachable = assess_dependence_robustness(d.evidence, d.threshold, CUTS).reachable_settlements
                assert d.reference in reachable, (family, d.decision_id)


def test_contestants_see_only_visible_fields():
    assert {f.name for f in dataclasses.fields(VisibleDecision)} == {
        "decision_id", "threshold", "decision_class", "evidence"
    }


def test_decision_scoring_table():
    world = generate_world(CONFIG, DEV, "single_domain", 0)
    d = world.decisions[0]
    settled = d.reference if d.reference in SETTLED else "settled_true"
    other = "settled_false" if settled == "settled_true" else "settled_true"
    if d.reference in SETTLED:
        assert score_decision(d, settled) == CORRECT_SETTLEMENT
        assert score_decision(d, other) == FALSE_SETTLEMENT
        assert score_decision(d, "abstain") == UNNEEDED_ABSTENTION
    unsettled = dataclasses.replace(d, reference="unsettled")
    assert score_decision(unsettled, "abstain") == REQUIRED_ABSTENTION
    assert score_decision(unsettled, "settled_true") == FALSE_SETTLEMENT
    blind = dataclasses.replace(d, lookup_available=False, record_settles_reference=False)
    if d.reference in SETTLED:
        assert score_decision(blind, "abstain") == REQUIRED_ABSTENTION


def test_arm_contracts_by_construction():
    """Structural guarantees of the rules, not outcome comparisons."""
    for family in CONFIG["families"]:
        for replicate in range(8):
            for d in generate_world(CONFIG, DEV, family, replicate).decisions:
                terminal, stamped, looks = act("oracle_reference", d)
                assert score_decision(d, terminal) != FALSE_SETTLEMENT and looks == 0
                robust = assess_dependence_robustness(d.evidence, d.threshold, CUTS)
                for arm in ("robustness_everywhere", "tiered_rule"):
                    terminal, stamped, looks = act(arm, d)
                    if arm == "robustness_everywhere" or d.decision_class == IRREVERSIBLE:
                        assert not stamped
                        if terminal in SETTLED and looks == 0:
                            assert robust.robust and robust.settlement == terminal
                    if stamped:
                        assert terminal in SETTLED and looks == 0 and not robust.robust
                assert act("always_look", d)[2] == 1


def test_criterion_logic_on_constructed_rows():
    def semantic(silent, irreversible_false, agreement_only, tiered_only):
        arms = {"tiered_rule": {
            "all:decisions": 6000, "high_irreversible:decisions": 3000,
            "all:silentFalseSettlements": silent, "high_irreversible:false_settlement": irreversible_false}}
        comparison = {"agreementSilent": agreement_only, "agreementOnlySilent": agreement_only,
                      "tieredOnlySilent": tiered_only, "p": 2 * 0.5 ** max(agreement_only, 1) if tiered_only == 0 else 1.0}
        return {"families": {f: {"arms": arms, "silentComparison": comparison} for f in CONFIG["families"]}}

    assert evaluate_criterion(semantic(0, 0, 20, 0), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(1, 0, 20, 0), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(0, 1, 20, 0), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(0, 0, 20, 0), CONFIG, False)["supported"]
    underpowered = evaluate_criterion(semantic(0, 0, 3, 0), CONFIG, True)
    assert underpowered["supported"] and len(underpowered["underpoweredComparisons"]) == 3


def test_evaluation_runs_and_is_deterministic_on_development_worlds():
    first = evaluate(CONFIG, DEV, 4)
    second = evaluate(CONFIG, DEV, 4)
    assert first == second
    assert first["worlds"] == 4 * len(CONFIG["families"])
    assert set(first["families"]) == set(CONFIG["families"])


def test_runner_pins_hold_and_refuse_changed_inputs(tmp_path):
    import shutil

    from experiments.dri3.run_confirmatory import PINNED, load_config, verify_pins

    verify_pins()
    assert load_config()["status"] == "preregistered-unexecuted"
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    engine = tmp_path / "provenance/dependence_robustness.py"
    engine.write_text(engine.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="dependence_robustness"):
        verify_pins(tmp_path)
