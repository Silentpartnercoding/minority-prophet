"""The gate that checks a criterion rather than an artifact.

Every other integrity check in this repository examines something produced: a
digest, a link, a registration, a coverage claim. None of them could see that
HGD-1g demanded a 5-point error reduction from a 4.349-point baseline, and was
therefore unsatisfiable by any possible result at the moment it was frozen.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from scripts.check_criterion_reachability import (
    REQUIRED_KEYS,
    SCHEMA,
    SUPPORTED_FORMS,
    RegistryError,
    assess,
    resolve,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "research/criterion-reachability/CRITERIA.json"
RESULT = ROOT / "results/hgd1-v1/result.json"


@pytest.fixture
def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


@pytest.fixture
def hgd1g(registry):
    return next(e for e in registry["criteria"] if e["id"] == "HGD-1g")


# --- the finding itself ---------------------------------------------------


def test_hgd1g_was_unreachable_as_scored(hgd1g):
    """The finding, asserted against the frozen result rather than restated.

    The threshold was 5 percentage points. The pooled head-count error never
    exceeded 4.349 points at any shift, and an error rate cannot fall below
    zero, so no possible result could have cleared the bar.
    """
    assessment = assess(hgd1g, ROOT)
    assert assessment["reachable"] is False
    assert assessment["bestCeiling"] == pytest.approx(0.043489, abs=1e-6)
    assert assessment["threshold"] == 0.05
    assert assessment["shortfall"] == pytest.approx(0.006511, abs=1e-6)


def test_the_run_nearly_reached_the_arithmetic_maximum(hgd1g):
    """4.227 of a possible 4.349 points. The method was not the problem."""
    assessment = assess(hgd1g, ROOT)
    attained = assessment["bestAchieved"] / assessment["bestCeiling"]
    assert attained > 0.97


def test_every_shift_was_individually_unreachable(hgd1g):
    """Not a near miss at one shift: the bar exceeded the ceiling everywhere."""
    assessment = assess(hgd1g, ROOT)
    assert len(assessment["ceilingByCell"]) == 3
    for ceiling in assessment["ceilingByCell"].values():
        assert ceiling < 0.05


def test_the_unreachable_criterion_is_acknowledged_in_writing(hgd1g):
    """An unreachable criterion is permitted in the registry only when the
    finding recording it exists. The frozen result is never edited to match."""
    acknowledgement = ROOT / hgd1g["acknowledged"]
    assert acknowledgement.is_file()


# --- the checker's own discipline ----------------------------------------


def test_unsupported_forms_are_refused_not_guessed(hgd1g):
    """HGD-2's criteria are ratios. A checker that invented a verdict for a
    shape it does not model would repeat, in a costlier place, the defect this
    gate exists to document."""
    entry = {**hgd1g, "form": "relative-risk"}
    with pytest.raises(RegistryError, match="will not guess"):
        assess(entry, ROOT)


def test_supported_forms_are_declared_explicitly():
    assert SUPPORTED_FORMS == ("absolute-difference",)


def test_a_missing_key_is_an_error_not_a_default(hgd1g):
    entry = {k: v for k, v in hgd1g.items() if k != "subtrahendFloor"}
    with pytest.raises(RegistryError, match="subtrahendFloor"):
        assess(entry, ROOT)


def test_a_stale_path_is_an_error_not_a_pass(hgd1g):
    """A registry naming a path the result does not contain is stale. Skipping
    it would report the criterion reachable because its operands were missing —
    failing toward silence, which is the direction that hides defects."""
    entry = {**hgd1g, "minuend": "observational.pooled.*.head.nonexistent_metric"}
    with pytest.raises(RegistryError, match="missing segment"):
        assess(entry, ROOT)


def test_mismatched_cells_are_refused(hgd1g):
    entry = {**hgd1g, "subtrahend": "synthetic.*.interval.false_confident_error"}
    with pytest.raises(RegistryError, match="different cells"):
        assess(entry, ROOT)


def test_a_reachable_criterion_passes(hgd1g):
    """Sanity in the other direction: lower the threshold under the ceiling and
    the same criterion is reachable. The checker is not simply always failing."""
    entry = {**hgd1g, "threshold": 0.04}
    assessment = assess(entry, ROOT)
    assert assessment["reachable"] is True
    assert assessment["shortfall"] is None


def test_every_quantifier_is_modelled(hgd1g):
    """`every` takes the weakest cell rather than the strongest."""
    entry = {**hgd1g, "quantifier": "every"}
    assessment = assess(entry, ROOT)
    assert assessment["bestCeiling"] == pytest.approx(0.002197, abs=1e-6)


# --- the registry ---------------------------------------------------------


def test_registry_declares_its_schema(registry):
    assert registry["schema"] == SCHEMA


def test_every_entry_carries_every_required_key(registry):
    for entry in registry["criteria"]:
        missing = [key for key in REQUIRED_KEYS if key not in entry]
        assert not missing, f"{entry.get('id')} missing {missing}"


def test_every_entry_quotes_a_protocol_that_exists(registry):
    """The quoted text is hand-checked against the protocol; this only asserts
    the protocol is still there to check against."""
    for entry in registry["criteria"]:
        assert (ROOT / entry["protocol"]).is_file()
        assert (ROOT / entry["result"]).is_file()


def test_the_floor_is_declared_rather_than_inferred(registry):
    """A metric's floor is a property of the metric. Inferring it from observed
    values would make the ceiling depend on the data, which is exactly what a
    reachability argument must not do."""
    for entry in registry["criteria"]:
        assert isinstance(entry["subtrahendFloor"], (int, float))
        assert entry["floorBasis"].strip()


def test_resolve_iterates_wildcards_in_sorted_order():
    document = {"a": {"x": {"v": 2.0}, "b": {"v": 1.0}}}
    assert resolve(document, "a.*.v") == {"b": 1.0, "x": 2.0}


def test_resolve_refuses_a_boolean_as_a_number():
    with pytest.raises(RegistryError, match="not a number"):
        resolve({"a": True}, "a")
