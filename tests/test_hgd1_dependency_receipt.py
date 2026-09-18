"""The published dependency-receipt shape, which nothing produced.

`research/knowledge-ledger/GATE-COVERAGE.json` cites
`experiments/hgd1/dependency-receipt.schema.json` as the artifact discharging
KL-006/KL-008/ADV-005 — shared dependency representable as interval-valued
shared weight. `run_hgd1.py` builds components as `{id, members, low, high}` and
shares not one field name with that schema. The coverage claim rested on a shape
nothing emitted.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from experiments.hgd1.dependency_receipt import (
    COMPONENT_KINDS,
    SCHEMA_ID,
    DependencyReceiptError,
    build_receipt,
    component_kind,
    receipt_errors,
    serialise_component,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "experiments" / "hgd1" / "dependency-receipt.schema.json"

ORIGIN = "sha256:" + "a" * 64
RECEIPT = "sha256:" + "c" * 64


def internal(component_id="station", low=0.4, high=0.6):
    """A component in the frozen runner's internal vocabulary."""
    return {"id": component_id, "members": ("a", "b"), "low": low, "high": high,
            "true": 0.5}


def test_the_runners_vocabulary_serialises_to_the_published_one():
    published = serialise_component(internal())
    assert published == {
        "componentId": "station", "kind": "station",
        "sharedWeightLower": 0.4, "sharedWeightUpper": 0.6,
    }


def test_ground_truth_weight_is_not_published():
    """`true` is the generator's ground truth, known only inside a simulation.
    Publishing it would put a value in an audit record that no real observer
    could supply."""
    assert "true" not in serialise_component(internal())


@pytest.mark.parametrize(
    "component_id,expected",
    [("station", "station"), ("station-a", "station"), ("station-b", "station"),
     ("calibration", "calibration"), ("model", "model"), ("instrument", "instrument"),
     ("weather-balloon", "other"), ("", "other")],
)
def test_kind_is_inferred_from_the_id(component_id, expected):
    """The runner never declared a kind, so every value is inferred. Anything
    unrecognised becomes `other` rather than raising: a coarse audit label is
    better declined than guessed."""
    assert component_kind(component_id) == expected


def test_every_inferred_kind_is_in_the_schema_enum():
    for component_id in ("station-a", "calibration", "model", "nonsense"):
        assert component_kind(component_id) in COMPONENT_KINDS


def test_a_built_receipt_validates():
    document = build_receipt(ORIGIN, [internal(), internal("model", 0.2, 0.4)],
                             receipt_digest=RECEIPT)
    assert receipt_errors(document) == []
    assert document["schema"] == SCHEMA_ID
    assert [c["componentId"] for c in document["components"]] == ["station", "model"]


def test_an_empty_component_list_is_valid():
    """HGD-1's own conformance vectors include cases with no shared components
    at all; a receipt asserting no shared dependence is a real receipt."""
    assert receipt_errors(build_receipt(ORIGIN, [], receipt_digest=RECEIPT)) == []


def test_inverted_interval_is_refused():
    with pytest.raises(DependencyReceiptError, match="lower <= upper"):
        serialise_component(internal(low=0.8, high=0.2))


def test_weight_outside_the_unit_interval_is_refused():
    with pytest.raises(DependencyReceiptError, match="0 <= lower <= upper <= 1"):
        serialise_component(internal(low=-0.1, high=0.5))


def test_malformed_digests_are_refused():
    with pytest.raises(DependencyReceiptError, match="originDigest"):
        build_receipt("a" * 64, [], receipt_digest=RECEIPT)
    with pytest.raises(DependencyReceiptError, match="receiptDigest"):
        build_receipt(ORIGIN, [], receipt_digest="c" * 64)


def test_unrecognised_support_status_is_refused():
    with pytest.raises(DependencyReceiptError, match="unrecognised support status"):
        build_receipt(ORIGIN, [], support_status="probably", receipt_digest=RECEIPT)


# --- the validator --------------------------------------------------------


def test_duplicate_component_ids_are_refused():
    """Not a schema rule, but two components sharing an id makes the receipt
    unreadable as an audit record: the weights could not be attributed."""
    document = build_receipt(ORIGIN, [internal(), internal()], receipt_digest=RECEIPT)
    assert any("duplicated" in error for error in receipt_errors(document))


def test_unpermitted_keys_are_refused():
    document = build_receipt(ORIGIN, [], receipt_digest=RECEIPT)
    document["confidence"] = 0.9
    assert any("unpermitted" in error for error in receipt_errors(document))


def test_a_boolean_is_not_a_weight():
    document = build_receipt(ORIGIN, [internal()], receipt_digest=RECEIPT)
    document["components"][0]["sharedWeightLower"] = True
    assert any("must be a number" in error for error in receipt_errors(document))


def test_non_object_is_refused():
    assert receipt_errors(["not", "a", "receipt"]) == ["receipt must be an object"]


# --- agreement with the published schema ---------------------------------


def test_serialiser_matches_the_published_schema():
    """The whole point. If these drift, the gate-coverage claim goes back to
    citing a shape nothing emits."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    component_schema = schema["properties"]["components"]["items"]

    published = serialise_component(internal())
    assert set(published) == set(component_schema["properties"])
    assert set(component_schema["required"]) <= set(published)
    assert component_schema["properties"]["kind"]["enum"] == list(COMPONENT_KINDS)

    document = build_receipt(ORIGIN, [internal()], receipt_digest=RECEIPT)
    assert set(document) == set(schema["properties"])
    assert set(schema["required"]) <= set(document)
    assert schema["properties"]["schema"]["const"] == SCHEMA_ID
