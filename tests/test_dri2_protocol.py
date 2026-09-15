"""Integrity tests for the frozen DRI-2 generator, arms, scoring and statistics.

These use the development salt only and assert construction invariants. They do
not compare contestant arms, so no confirmatory or comparative outcome is seen
before the protocol is frozen.
"""

import dataclasses
import json
from collections import defaultdict
from pathlib import Path

import pytest

from experiments.dri2.arms import COMPARISON_ARMS, VisibleDecision, act
from experiments.dri2.scoring import (
    CORRECT,
    FALL,
    INCORRECT_STALL,
    REQUIRED_HANDOVER,
    run_arm,
    score_junction,
)
from experiments.dri2.stats import holm, mcnemar_exact, wilcoxon_signed_rank, wilson_interval
from experiments.dri2.world import (
    CUTS,
    GATHER,
    HAND_OVER,
    PATH_TYPES,
    SETTLE,
    classify,
    generate_world,
    settlements_at_cuts,
)

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "dri2" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]


def _partition(decision, key):
    groups = defaultdict(set)
    for item in decision.evidence:
        groups[key(item)].add(item.observation_id)
    return {frozenset(group) for group in groups.values()}


def _unit_partition(decision):
    unit_of = dict(decision.units)
    return _partition(decision, lambda item: unit_of[item.observation_id])


def test_config_is_frozen_and_sized_for_significance():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert CONFIG["wrong_time_escalation_cost_ms"] == 2 * CONFIG["probe_cost_ms"]
    assert set(CONFIG["success_criterion"]["faster_than"]) == {"determined_or_escalate", "weakest_link"}
    assert CONFIG["worlds_per_path_type"] * len(CONFIG["path_types"]) >= 3155
    assert CONFIG["development_salt"] != CONFIG["confirmatory_salt"]


def test_statistics_match_known_values():
    assert mcnemar_exact(10, 2) == pytest.approx(0.03857, abs=1e-5)
    assert mcnemar_exact(0, 0) == 1.0
    low, high = wilson_interval(50, 100)
    assert (low, high) == (pytest.approx(0.4038, abs=1e-3), pytest.approx(0.5962, abs=1e-3))
    assert holm({"a": 0.01, "b": 0.04, "c": 0.03}) == {
        "a": pytest.approx(0.03),
        "c": pytest.approx(0.06),
        "b": pytest.approx(0.06),
    }
    assert wilcoxon_signed_rank([1, 2, 3, 4, 5])["p"] == pytest.approx(0.0591, abs=1e-3)
    assert wilcoxon_signed_rank([0, 0])["p"] == 1.0


@pytest.mark.parametrize("family", CONFIG["families"])
@pytest.mark.parametrize("path_type", PATH_TYPES)
def test_worlds_are_deterministic_and_match_their_path_type(family, path_type):
    for replicate in range(3):
        world = generate_world(CONFIG, DEV, family, path_type, replicate)
        assert world == generate_world(CONFIG, DEV, family, path_type, replicate)
        junctions = [d.junction for d in world.decisions]
        if path_type == "no_handover":
            assert HAND_OVER not in junctions and world.probe_available
        elif path_type == "one_handover":
            assert junctions.count(HAND_OVER) == 1 and world.probe_available
        else:
            assert not world.probe_available and GATHER not in junctions


def test_topology_per_family():
    for replicate in range(5):
        single = generate_world(CONFIG, DEV, "single_domain", "no_handover", replicate)
        for d in single.decisions:
            from experiments.dri2.world import DOMAIN_CUT

            relevant = DOMAIN_CUT[d.domains[0]]
            assert _partition(d, lambda item: item.roots[relevant]) == _unit_partition(d)
        joint = generate_world(CONFIG, DEV, "joint_domain", "no_handover", replicate)
        for d in joint.decisions:
            assert all(_partition(d, lambda item, c=c: item.roots[c]) != _unit_partition(d) for c in CUTS)
        origin = generate_world(CONFIG, DEV, "separate_control_shared_origin", "no_handover", replicate)
        for d in origin.decisions:
            assert _partition(d, lambda item: item.roots["evidence_origin"]) == _unit_partition(d)
            assert _partition(d, lambda item: item.roots["controller"]) != _unit_partition(d)
        independent = generate_world(CONFIG, DEV, "genuinely_independent", "no_handover", replicate)
        for d in independent.decisions:
            assert all(_partition(d, lambda item, c=c: item.roots[c]) == _unit_partition(d) for c in CUTS)


def test_junction_classification_follows_its_rule():
    for family in CONFIG["families"]:
        for path_type in PATH_TYPES:
            world = generate_world(CONFIG, DEV, family, path_type, 0)
            for d in world.decisions:
                cuts = settlements_at_cuts(d.evidence, d.threshold)
                assert dict(d.cut_settlements) == cuts
                assert d.junction == classify(d.reference, cuts, d.probe_available)


def test_contestants_cannot_see_hidden_facts():
    fields = {f.name for f in dataclasses.fields(VisibleDecision)}
    assert fields == {"decision_id", "threshold", "evidence"}


def test_junction_scoring_table():
    assert score_junction(HAND_OVER, "unsettled", "escalate", False) == REQUIRED_HANDOVER
    assert score_junction(HAND_OVER, "unsettled", "settled_true", True) == FALL
    assert score_junction(SETTLE, "settled_true", "escalate", False) == INCORRECT_STALL
    assert score_junction(SETTLE, "settled_true", "settled_true", False) == CORRECT
    assert score_junction(SETTLE, "settled_true", "settled_false", False) == FALL
    assert score_junction(GATHER, "settled_true", "settled_true", False) == FALL
    assert score_junction(GATHER, "settled_true", "settled_true", True) == CORRECT
    assert score_junction(GATHER, "settled_true", "escalate", True) == INCORRECT_STALL


def test_oracle_reference_never_falls_by_construction():
    for family in CONFIG["families"]:
        for path_type in PATH_TYPES:
            world = generate_world(CONFIG, DEV, family, path_type, 1)
            record = run_arm("oracle_reference", world, CONFIG)
            assert record.crossed and record.clean
            assert record.human_calls == record.required_calls


def test_every_contestant_arm_runs_and_probes_are_charged():
    world = generate_world(CONFIG, DEV, "joint_domain", "no_handover", 2)
    for arm in COMPARISON_ARMS + ("method_under_test",):
        record = run_arm(arm, world, CONFIG)
        assert record.virtual_ms >= len(record.junction_results) * CONFIG["action_cost_ms"]
        assert record.virtual_ms >= record.probes * CONFIG["probe_cost_ms"]
    for d in world.decisions:
        terminal, calls = act("agent_headcount", d)
        assert calls == 0


def _fake_semantic(crossing_row, timing_row):
    arms = COMPARISON_ARMS
    family = {"tests": {"crossing": {a: dict(crossing_row) for a in arms},
                        "timeToCrossing": {a: dict(timing_row) for a in arms}}}
    return {"families": {f: family for f in CONFIG["families"]}}


def test_criterion_logic_on_constructed_rows():
    from experiments.dri2.scoring import evaluate_criterion

    winning = _fake_semantic(
        {"holmP": 0.001, "difference": 0.1, "difference95": [0.05, 0.15]},
        {"holmP": 0.001, "wilcoxon_z": -5.0},
    )
    assert evaluate_criterion(winning, CONFIG, True)["supported"]
    assert not evaluate_criterion(winning, CONFIG, False)["supported"]
    worse = _fake_semantic(
        {"holmP": 0.001, "difference": -0.1, "difference95": [-0.15, -0.05]},
        {"holmP": 0.001, "wilcoxon_z": -5.0},
    )
    assert not evaluate_criterion(worse, CONFIG, True)["supported"]
    slower = _fake_semantic(
        {"holmP": 0.001, "difference": 0.1, "difference95": [0.05, 0.15]},
        {"holmP": 0.001, "wilcoxon_z": 5.0},
    )
    assert not evaluate_criterion(slower, CONFIG, True)["supported"]
