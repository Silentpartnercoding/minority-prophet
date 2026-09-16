"""Integrity tests for the DRI-8 protocol.

Development salt only. Construction invariants; no arm comparisons.
"""

import json
import random
from itertools import combinations
from pathlib import Path

from experiments.dri3.world import CUTS
from experiments.dri8.arms import Learned, run_campaign
from experiments.dri8.scoring import evaluate, evaluate_criterion, margin_critical
from experiments.dri8.world import (
    FAMILIES,
    HIDDEN,
    RECORDED,
    cell_key,
    cells,
    degrade,
    generate_campaign,
    lookup_grouping,
    probe_result,
    reveals,
)

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "dri8" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]


def campaigns(family, count=4):
    return [generate_campaign(CONFIG, DEV, family, replicate) for replicate in range(count)]


def test_config_is_frozen_and_sized():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert tuple(CONFIG["families"]) == FAMILIES
    assert CONFIG["campaigns_per_family"] * CONFIG["decisions_per_campaign"] == 6000
    rule = CONFIG["success_criterion"]
    comparisons = len(rule["prevention_families"]) * len(CONFIG["missing_rates"]) * len(CONFIG["feedback_rates"])
    assert 2 * 0.5 ** rule["minimum_tiered_silent_for_test"] < 0.05 / comparisons
    assert rule["generous_probe_budget"] in CONFIG["probe_budgets"]


def test_the_hidden_component_is_recorded_nowhere():
    """The whole point: no cut, and no content fingerprint, links the pair."""
    for family in ("shared_upstream_pair", "shared_upstream_trio"):
        for campaign in campaigns(family):
            hidden = {s.source_id for s in campaign.sources if s.component_kind == HIDDEN}
            assert len(hidden) >= 2
            for decision in campaign.decisions:
                source_of = dict(decision.source_of)
                for cut in CUTS + ("content",):
                    groups = {}
                    for item in decision.evidence:
                        groups.setdefault(item.roots[cut], set()).add(source_of[item.observation_id])
                    assert not any(len(members & hidden) > 1 for members in groups.values()), cut


def test_the_lookup_never_reveals_the_hidden_component():
    """It is wrong the same way on every call, which is DRI-6's excluded case."""
    for campaign in campaigns("shared_upstream_pair"):
        hidden = sorted(s.source_id for s in campaign.sources if s.component_kind == HIDDEN)
        for decision in campaign.decisions:
            reported = dict(lookup_grouping(decision))
            observation = {source: obs for obs, source in decision.source_of}
            assert reported[observation[hidden[0]]] != reported[observation[hidden[1]]]


def test_the_recorded_pair_is_shared_and_degradation_splits_it():
    for campaign in campaigns("shared_upstream_pair"):
        recorded = sorted(s.source_id for s in campaign.sources if s.component_kind == RECORDED)
        assert len(recorded) == 2
        decision = campaign.decisions[0]
        observation = {source: obs for obs, source in decision.source_of}
        roots = {item.observation_id: item.roots["upstream_component"] for item in decision.evidence}
        assert roots[observation[recorded[0]]] == roots[observation[recorded[1]]]
        split = degrade(decision, 1.0, random.Random(0))
        split_roots = {item.observation_id: item.roots["upstream_component"] for item in split.evidence}
        assert split_roots[observation[recorded[0]]] != split_roots[observation[recorded[1]]]
        assert split.units == decision.units and split.reference == decision.reference


def test_probes_are_deterministic_symmetric_and_informative():
    campaign = campaigns("shared_upstream_pair", 1)[0]
    hidden = sorted(s.source_id for s in campaign.sources if s.component_kind == HIDDEN)
    alone = [s.source_id for s in campaign.sources if s.component is None]
    assert probe_result(CONFIG, DEV, campaign, *hidden, 0) == probe_result(CONFIG, DEV, campaign, *reversed(hidden), 0)
    shared_hits = sum(probe_result(CONFIG, DEV, campaign, hidden[0], hidden[1], i) for i in range(200))
    unrelated_hits = sum(probe_result(CONFIG, DEV, campaign, hidden[0], alone[0], i) for i in range(200))
    assert shared_hits > unrelated_hits


def test_feedback_is_deterministic_and_respects_its_rate():
    campaign = campaigns("shared_upstream_pair", 1)[0]
    assert reveals(CONFIG, DEV, campaign, 3, 1.0) is True
    assert reveals(CONFIG, DEV, campaign, 3, 0.0) is False
    assert reveals(CONFIG, DEV, campaign, 3, 0.25) == reveals(CONFIG, DEV, campaign, 3, 0.25)


def test_learned_merges_are_transitive():
    learned = Learned()
    learned.merge("a", "b")
    learned.merge("b", "c")
    assert learned.group_of("a") == {"a", "b", "c"}
    assert learned.label("c") == "learned:a+b+c"


def test_margin_critical_separates_the_dont_care_zone():
    """Both answers must occur, or the split is measuring nothing."""
    seen = set()
    for campaign in campaigns("shared_upstream_pair", 20):
        for decision in campaign.decisions:
            seen.add(margin_critical(decision, campaign))
    assert seen == {True, False}
    for campaign in campaigns("coincident_independents", 4):
        for decision in campaign.decisions:
            assert margin_critical(decision, campaign) is False


def test_arms_are_deterministic_and_probe_spends_within_budget():
    campaign = campaigns("shared_upstream_pair", 1)[0]
    first, learned = run_campaign("probe", campaign, CONFIG, DEV, 1.0, 10)
    again, _ = run_campaign("probe", campaign, CONFIG, DEV, 1.0, 10)
    assert [vars(o) for o in first] == [vars(o) for o in again]
    assert sum(o.probes for o in first) <= 10
    none_spent, _ = run_campaign("probe", campaign, CONFIG, DEV, 1.0, 0)
    assert sum(o.probes for o in none_spent) == 0
    baseline, empty = run_campaign("tiered_rule", campaign, CONFIG, DEV, 1.0, 10)
    assert empty.groups == [] and sum(o.probes for o in baseline) == 0


def test_criterion_logic_on_constructed_rows():
    def row(tiered_silent, method_silent, tiered_only, method_only, correct=1000, probe_correct=1000):
        comparison = {
            "silent": method_silent, "criticalSilent": method_silent,
            "tieredOnlySilent": tiered_only, "methodOnlySilent": method_only,
            "p": 2 * 0.5 ** max(tiered_only, method_only) if min(tiered_only, method_only) == 0 else 1.0,
        }
        return {
            "arms": {
                "tiered_rule": {"all:correct_settlement": correct},
                "probe": {"all:correct_settlement": probe_correct},
            },
            "tieredSilent": tiered_silent,
            "criticalTieredSilent": tiered_silent,
            "comparisons": {"track_record": dict(comparison), "probe": dict(comparison)},
        }

    def semantic(good):
        return {"families": {
            family: {cell_key(m, r, b): good for m, r, b in cells(CONFIG)} for family in CONFIG["families"]
        }}

    assert evaluate_criterion(semantic(row(40, 2, 38, 0)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(40, 40, 0, 0)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(40, 2, 38, 0, probe_correct=800)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(40, 2, 38, 0)), CONFIG, False)["supported"]
    harmful = semantic(row(40, 2, 38, 0))
    harmful["families"][CONFIG["success_criterion"]["no_harm_family"]] = {
        cell: row(5, 40, 0, 38) for cell in harmful["families"][CONFIG["success_criterion"]["no_harm_family"]]
    }
    assert not evaluate_criterion(harmful, CONFIG, True)["supported"]


def test_evaluation_runs_and_is_deterministic_on_development_campaigns():
    first = evaluate(CONFIG, DEV, 1)
    assert first == evaluate(CONFIG, DEV, 1)
    assert first["campaigns"] == len(FAMILIES) * len(cells(CONFIG))
    assert set(first["families"]) == set(FAMILIES)


def test_runner_pins_hold_and_refuse_changed_inputs(tmp_path):
    import shutil

    import pytest

    from experiments.dri8.run_confirmatory import PINNED, load_config, verify_pins

    verify_pins()
    assert load_config()["status"] == "preregistered-unexecuted"
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    reused = tmp_path / "experiments/dri8/world.py"
    reused.write_text(reused.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="dri8/world.py"):
        verify_pins(tmp_path)
