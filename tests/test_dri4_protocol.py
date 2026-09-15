"""Integrity tests for the frozen DRI-4 protocol.

Development salt only. Construction invariants; no arm comparisons.
"""

import json
import random
from collections import defaultdict
from pathlib import Path

from experiments.dri3.world import CUTS, SETTLED
from experiments.dri4.scoring import evaluate, evaluate_criterion
from experiments.dri4.world import (
    FAMILIES,
    TRAP_FAMILY,
    base_world,
    cells,
    degrade,
    degraded_world,
)
from experiments.dri3.scoring import zero_event_upper_bound
from provenance.dependence_robustness import assess_dependence_robustness

ROOT = Path(__file__).parents[1]
CONFIG = json.loads((ROOT / "experiments" / "dri4" / "EXECUTION-CONFIG.json").read_text())
DEV = CONFIG["development_salt"]


def test_config_is_frozen_and_sized_for_the_bound():
    assert CONFIG["status"] == "preregistered-unexecuted"
    assert tuple(CONFIG["families"]) == FAMILIES
    decisions = CONFIG["worlds_per_family"] * CONFIG["decisions_per_world"]
    assert zero_event_upper_bound(decisions) < CONFIG["success_criterion"]["maximum_rate_bound"]
    assert len(cells(CONFIG)) == len(CONFIG["missing_rates"]) * len(CONFIG["spurious_rates"])


def test_trap_family_always_sets_the_trap():
    for replicate in range(30):
        for d in base_world(CONFIG, DEV, TRAP_FAMILY, replicate).decisions:
            values = set(dict(d.cut_settlements).values())
            assert len(values) == 1 and next(iter(values)) in SETTLED
            assert d.reference not in SETTLED


def test_undegraded_cell_is_the_base_world_and_worlds_are_deterministic():
    for family in FAMILIES:
        base = base_world(CONFIG, DEV, family, 3)
        assert degraded_world(CONFIG, DEV, base, 0, 0) == base
        assert degraded_world(CONFIG, DEV, base, 0.25, 0.1) == degraded_world(CONFIG, DEV, base, 0.25, 0.1)
        assert base_world(CONFIG, DEV, family, 3) == base


def _groups(decision):
    unit_of = dict(decision.units)
    for cut in CUTS:
        groups = defaultdict(list)
        for item in decision.evidence:
            groups[item.roots[cut]].append(unit_of[item.observation_id])
        yield from groups.values()


def test_full_missing_removes_every_true_shared_identity_and_nothing_else_changes():
    rng = random.Random(1)
    for family in FAMILIES:
        for replicate in range(6):
            for d in base_world(CONFIG, DEV, family, replicate).decisions:
                degraded = degrade(d, 1.0, 0.0, rng)
                assert degraded.reference == d.reference and degraded.units == d.units
                assert degraded.truth == d.truth and degraded.lookup_available == d.lookup_available
                for members in _groups(degraded):
                    assert len(members) < 2 or len(set(members)) > 1


def test_spurious_only_keeps_the_true_grouping_admissible():
    """With nothing missing the proven guarantee's precondition holds, so the true
    settlement is always among the reachable settlements."""
    rng = random.Random(2)
    for family in FAMILIES:
        for replicate in range(6):
            for d in base_world(CONFIG, DEV, family, replicate).decisions:
                degraded = degrade(d, 0.0, 1.0, rng)
                reachable = assess_dependence_robustness(degraded.evidence, degraded.threshold, CUTS).reachable_settlements
                assert degraded.reference in reachable


def test_criterion_logic_on_constructed_rows():
    def row(tiered_silent, agreement_silent, agreement_only, tiered_only):
        return {
            "arms": {"tiered_rule": {"all:decisions": 6000, "high_irreversible:decisions": 3000}},
            "silentComparison": {
                "tieredSilent": tiered_silent, "agreementSilent": agreement_silent,
                "agreementOnlySilent": agreement_only, "tieredOnlySilent": tiered_only,
                "p": 2 * 0.5 ** agreement_only if tiered_only == 0 else 1.0,
            },
        }

    def semantic(zero_cell, degraded):
        out = {}
        for family in CONFIG["families"]:
            out[family] = {}
            for m, s in cells(CONFIG):
                out[family][f"m={m}|s={s}"] = zero_cell if m == 0 else degraded
        return {"families": out}

    good = semantic(row(0, 5, 5, 0), row(3, 40, 37, 0))
    assert evaluate_criterion(good, CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(1, 5, 4, 0), row(3, 40, 37, 0)), CONFIG, True)["supported"]
    assert not evaluate_criterion(semantic(row(0, 5, 5, 0), row(41, 40, 1, 2)), CONFIG, True)["supported"]
    assert not evaluate_criterion(good, CONFIG, False)["supported"]
    quiet = evaluate_criterion(semantic(row(0, 0, 0, 0), row(0, 3, 3, 0)), CONFIG, True)
    assert quiet["supported"] and quiet["underpoweredComparisons"]


def test_evaluation_runs_and_is_deterministic_on_development_worlds():
    first = evaluate(CONFIG, DEV, 2)
    assert first == evaluate(CONFIG, DEV, 2)
    assert first["worlds"] == 2 * len(FAMILIES) * len(cells(CONFIG))
    assert set(first["families"]) == set(FAMILIES)
