"""Integrity tests for the DRI-5 protocol.

Development salt only. Construction invariants; no arm comparisons.
"""

import json
import random
from collections import defaultdict
from pathlib import Path

from experiments.dri3.scoring import zero_event_upper_bound
from experiments.dri3.world import CUTS, settlement_over_units
from experiments.dri4.world import base_world, degraded_world
from experiments.dri5.scoring import evaluate, evaluate_criterion
from experiments.dri5.world import (
    ALL_CUTS,
    CONTENT_CUT,
    FAMILIES,
    add_content,
    cells,
    content_draws,
    iter_cell_worlds,
    parse_cell,
    root_and_copy,
    true_grouping_admissible,
)
from provenance.decision_relative import DecisionEvidence

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "dri5" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]


def test_config_is_frozen_and_sized_for_the_bound():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert tuple(CONFIG["families"]) == FAMILIES
    assert CONFIG["worlds_per_family"] * CONFIG["decisions_per_world"] == 6000
    assert zero_event_upper_bound(6000) < CONFIG["success_criterion"]["maximum_rate_bound"]
    comparisons = len(CONFIG["families"]) * len(CONFIG["success_criterion"]["significance_missing_rates"]) * 4
    assert 2 * 0.5 ** CONFIG["success_criterion"]["minimum_tiered_silent_for_test"] < 0.05 / comparisons


def _decisions(family, replicate=0):
    base = base_world(CONFIG, DEV, family, replicate)
    rng = random.Random(replicate)
    return [(d, content_draws(d, rng)) for d in base.decisions]


def _fingerprints(decision):
    return {item.observation_id: item.roots[CONTENT_CUT] for item in decision.evidence}


def test_clean_content_marks_exactly_the_copies_of_each_root():
    for family in FAMILIES:
        for decision, draws in _decisions(family):
            prints = _fingerprints(add_content(decision, draws, 0.0, 0.0))
            by_root = defaultdict(set)
            for observation, fingerprint in prints.items():
                by_root[root_and_copy(observation)[0]].add(fingerprint)
            assert all(len(group) == 1 for group in by_root.values())
            assert len({next(iter(group)) for group in by_root.values()}) == len(by_root)


def test_fingerprints_never_cross_sides_and_rates_are_nested():
    for family in FAMILIES:
        for decision, draws in _decisions(family, 1):
            for p, q in ((0.5, 0.2), (1.0, 1.0)):
                shown = add_content(decision, draws, p, q)
                sides = defaultdict(set)
                for item in shown.evidence:
                    sides[item.roots[CONTENT_CUT]].add(item.value)
                assert all(len(values) == 1 for values in sides.values())
            half = _fingerprints(add_content(decision, draws, 0.5, 0.0))
            full = _fingerprints(add_content(decision, draws, 1.0, 0.0))
            reworded_half = {o for o, f in half.items() if f == f"{CONTENT_CUT}:{o}"}
            reworded_full = {o for o, f in full.items() if f == f"{CONTENT_CUT}:{o}"}
            assert reworded_half <= reworded_full


def test_content_is_identical_across_missing_rates_and_never_breaks_admissibility():
    by_cell = {}
    for cell, world in iter_cell_worlds(CONFIG, DEV, 3):
        m, p, q = parse_cell(cell)
        for d in world.decisions:
            lineage = true_grouping_admissible(d.evidence, d.units, CUTS)
            assert lineage <= true_grouping_admissible(d.evidence, d.units, ALL_CUTS)
            if m == 0:
                assert lineage
            by_cell[(world.family, world.replicate, d.decision_id, p, q, m)] = {
                item.observation_id: item.roots[CONTENT_CUT] for item in d.evidence
            }
    for (family, replicate, decision, p, q, m), prints in by_cell.items():
        assert prints == by_cell[(family, replicate, decision, p, q, 0.0)]


def test_degradation_and_content_leave_truth_grouping_and_lookup_unchanged():
    for family in FAMILIES:
        base = base_world(CONFIG, DEV, family, 2)
        degraded = degraded_world(CONFIG, DEV, base, 0.5, 0.0)
        rng = random.Random(3)
        for before, after in zip(base.decisions, degraded.decisions, strict=True):
            shown = add_content(after, content_draws(after, rng), 0.5, 0.2)
            assert (shown.truth, shown.reference, shown.units, shown.lookup_available) == (
                before.truth, before.reference, before.units, before.lookup_available
            )


def test_record_alone_cannot_separate_the_dr3_witness():
    """The Python counterpart of ledger DR3: one record, two groupings, two settlements."""
    evidence = tuple(
        DecisionEvidence(
            observation_id=f"o{i}", proposition_id="w", value=value,
            roots={cut: f"{cut}:o{i}" for cut in CUTS}, basis={cut: "attested" for cut in CUTS},
        )
        for i, value in enumerate((True, True, False))
    )
    distinct = (("o0", "a"), ("o1", "b"), ("o2", "c"))
    merged = (("o0", "a"), ("o1", "a"), ("o2", "c"))
    assert true_grouping_admissible(evidence, distinct, CUTS)
    assert not true_grouping_admissible(evidence, merged, CUTS)
    assert settlement_over_units(evidence, distinct, 1) == "settled_true"
    assert settlement_over_units(evidence, merged, 1) != "settled_true"


def test_criterion_logic_on_constructed_rows():
    def row(content_silent, tiered_silent, tiered_only, content_only, where_admissible=0):
        return {
            "arms": {
                "tiered_rule": {"all:decisions": 6000},
                "content_tiered_rule": {"all:decisions": 6000},
            },
            "silentComparison": {
                "contentSilent": content_silent, "tieredSilent": tiered_silent,
                "tieredOnlySilent": tiered_only, "contentOnlySilent": content_only,
                "contentSilentWhereAdmissible": where_admissible,
                "p": 2 * 0.5 ** tiered_only if content_only == 0 else 1.0,
            },
        }

    def semantic(zero_cell, degraded):
        return {"families": {
            family: {f"m={m}|p={p}|q={q}": zero_cell if m == 0 else degraded for m, p, q in cells(CONFIG)}
            for family in CONFIG["families"]
        }}

    good = semantic(row(0, 0, 0, 0), row(5, 40, 35, 0))
    assert evaluate_criterion(good, CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(1, 1, 0, 0), row(5, 40, 35, 0)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(0, 0, 0, 0), row(40, 40, 0, 0)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(0, 0, 0, 0), row(6, 40, 35, 1)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(0, 0, 0, 0), row(5, 40, 35, 0, 1)), CONFIG, True)["supported"]
    assert not evaluate_criterion(good, CONFIG, False)["supported"]
    quiet = evaluate_criterion(semantic(row(0, 0, 0, 0), row(3, 3, 0, 0)), CONFIG, True)
    assert quiet["supported"] and quiet["underpoweredComparisons"]


def test_evaluation_runs_and_is_deterministic_on_development_worlds():
    first = evaluate(CONFIG, DEV, 1)
    assert first == evaluate(CONFIG, DEV, 1)
    assert first["worlds"] == len(FAMILIES) * len(cells(CONFIG))
    assert set(first["families"]) == set(FAMILIES)


def test_runner_pins_hold_and_refuse_changed_inputs(tmp_path):
    import shutil

    import pytest

    from experiments.dri5.run_confirmatory import PINNED, load_config, verify_pins

    verify_pins()
    assert load_config()["status"] == "preregistered-unexecuted"
    for name in PINNED:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    reused = tmp_path / "experiments/dri4/world.py"
    reused.write_text(reused.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="dri4/world.py"):
        verify_pins(tmp_path)
