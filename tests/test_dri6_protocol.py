"""Integrity tests for the DRI-6 protocol.

Development salt only. Construction invariants; no arm comparisons.
"""

import json
import random
from collections import Counter
from pathlib import Path

from experiments.dri3.arms import ABSTAIN, VisibleDecision
from experiments.dri3.scoring import zero_event_upper_bound
from experiments.dri3.world import CUTS, IRREVERSIBLE
from experiments.dri4.world import base_world
from experiments.dri6.arms import checked_look, confirmed_look
from experiments.dri6.scoring import evaluate, evaluate_criterion
from experiments.dri6.world import FAMILIES, ImperfectLook, cell_key, cells, reported_units
from provenance.decision_relative import DecisionEvidence

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "dri6" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]


def test_config_is_frozen_and_sized_for_the_bound():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert tuple(CONFIG["families"]) == FAMILIES
    assert CONFIG["worlds_per_family"] * CONFIG["decisions_per_world"] == 6000
    assert zero_event_upper_bound(6000) < CONFIG["success_criterion"]["maximum_rate_bound"]
    comparisons = len(CONFIG["families"]) * (len(cells(CONFIG)) - 1)
    assert 2 * 0.5 ** CONFIG["success_criterion"]["minimum_tiered_silent_for_test"] < 0.05 / comparisons
    assert cells(CONFIG)[0] == (0.0, 0.0)


def _decisions(replicate=0):
    for family in FAMILIES:
        yield from base_world(CONFIG, DEV, family, replicate).decisions


def test_truthful_and_extreme_error_rates_report_what_they_say():
    for d in _decisions():
        assert reported_units(d, 0, 0, random.Random(1)) == d.units
        assert len({unit for _, unit in reported_units(d, 0, 1.0, random.Random(1))}) == 1
        sizes = Counter(unit for _, unit in d.units)
        split = reported_units(d, 1.0, 0, random.Random(1))
        assert len({unit for _, unit in split}) == sum(size if size > 1 else 1 for size in sizes.values())


def test_calls_are_common_across_arms_and_fresh_across_calls():
    fresh = 0
    for d in (*_decisions(0), *_decisions(1)):
        if not d.lookup_available:
            look = ImperfectLook(d, DEV, 0.5, 0.5)
            assert look() is None and look.calls == 1
            continue
        a, b = ImperfectLook(d, DEV, 0.5, 0.5), ImperfectLook(d, DEV, 0.5, 0.5)
        first = a()
        assert first == b()
        fresh += a() != first
    assert fresh > 0


def _witness(value_pattern=(True, True, False)):
    evidence = tuple(
        DecisionEvidence(
            observation_id=f"o{i}", proposition_id="w", value=value,
            roots={cut: f"{cut}:o{i}" for cut in CUTS}, basis={cut: "attested" for cut in CUTS},
        )
        for i, value in enumerate(value_pattern)
    )
    return VisibleDecision("w", 1, IRREVERSIBLE, evidence)


def test_check_rejects_invented_dependence_and_confirmation_rejects_disagreement():
    view = _witness()
    merged = (("o0", "a"), ("o1", "a"), ("o2", "c"))
    distinct = (("o0", "a"), ("o1", "b"), ("o2", "c"))

    class Scripted:
        def __init__(self, *reports):
            self.reports, self.calls = list(reports), 0

        def __call__(self):
            self.calls += 1
            return self.reports.pop(0)

    assert checked_look(view, Scripted(merged)) == (ABSTAIN, False)
    assert checked_look(view, Scripted(distinct)) == ("settled_true", False)
    assert confirmed_look(view, Scripted(distinct, distinct)) == ("settled_true", False)
    look = Scripted(distinct, merged)
    assert confirmed_look(view, look) == (ABSTAIN, False) and look.calls == 2
    assert confirmed_look(view, Scripted(None)) == (ABSTAIN, False)


def test_criterion_logic_on_constructed_rows():
    def row(tiered_silent, confirmed_silent, tiered_only, method_only):
        comparison = {
            "silent": confirmed_silent, "tieredOnlySilent": tiered_only, "methodOnlySilent": method_only,
            "p": 2 * 0.5 ** tiered_only if method_only == 0 else 1.0,
        }
        return {
            "arms": {"confirmed_tiered_rule": {"all:decisions": 6000}},
            "tieredSilent": tiered_silent,
            "comparisons": {"checked_tiered_rule": dict(comparison), "confirmed_tiered_rule": dict(comparison)},
        }

    def semantic(truthful, erring):
        return {"families": {
            family: {cell_key(s, m): truthful if (s, m) == (0.0, 0.0) else erring for s, m in cells(CONFIG)}
            for family in CONFIG["families"]
        }}

    good = semantic(row(0, 0, 0, 0), row(40, 2, 38, 0))
    assert evaluate_criterion(good, CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(1, 1, 0, 0), row(40, 2, 38, 0)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(0, 0, 0, 0), row(40, 40, 0, 0)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(0, 0, 0, 0), row(40, 3, 38, 1)), CONFIG, True)["supported"]
    assert not evaluate_criterion(good, CONFIG, False)["supported"]
    quiet = evaluate_criterion(semantic(row(0, 0, 0, 0), row(3, 0, 3, 0)), CONFIG, True)
    assert quiet["supported"] and quiet["underpoweredComparisons"]


def test_evaluation_runs_and_is_deterministic_on_development_worlds():
    first = evaluate(CONFIG, DEV, 1)
    assert first == evaluate(CONFIG, DEV, 1)
    assert first["worlds"] == len(FAMILIES)
    assert all(len(by_cell) == len(cells(CONFIG)) for by_cell in first["families"].values())


def test_runner_pins_hold_and_refuse_changed_inputs(tmp_path):
    import shutil

    import pytest

    from experiments.dri6.run_confirmatory import PINNED, load_config, verify_pins

    verify_pins()
    assert load_config()["status"] == "preregistered-unexecuted"
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    reused = tmp_path / "experiments/dri5/world.py"
    reused.write_text(reused.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="dri5/world.py"):
        verify_pins(tmp_path)
