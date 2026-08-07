"""Protocol v1.1.0 permanent tests: the four repairs R1-R4.

Every repair documents behaviour the evaluator already had, or resolves an
ambiguity in its favour. These tests pin that behaviour so losing it breaks a
test instead of silently reopening the specification gap. The v1.0.0 suites
(test_kl000_invariants.py, test_kl000_adversarial.py) are unchanged.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = EXPERIMENT.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXPERIMENT / "src"))

from knowledge_ledger.transaction import (  # noqa: E402
    canonical_bytes,
    evaluate_transaction,
)
from kl000_invariants import check_world  # noqa: E402

PREREG_V110 = json.loads((EXPERIMENT / "preregistration-v1.1.0.json").read_text())
PREREG_V100 = json.loads((EXPERIMENT / "preregistration.json").read_text())


def world(records, locations, ctype="presence"):
    proposition = (
        "A target-class defect exists in the declared components."
        if ctype == "presence"
        else "No target-class defect exists in the declared components."
    )
    return {
        "transactionId": "kl000-v110-test",
        "claim": {"type": ctype, "proposition": proposition},
        "evidenceLedger": {"records": records},
        "searchLedger": {"locations": locations},
    }


def rec(i, root, side):
    return {"id": f"rec-{i}", "rootId": root, "side": side}


SEARCHED = [{"id": "loc-1", "status": "searched"}]


# --- R1: tie rule ----------------------------------------------------------

def test_r1_tie_is_not_established():
    receipt = evaluate_transaction(
        world([rec(1, "r1", "support"), rec(2, "r2", "oppose")], SEARCHED)
    )
    assert receipt["conclusion"] == "not_established"


def test_r1_strict_minority_is_not_established():
    receipt = evaluate_transaction(
        world(
            [rec(1, "r1", "support"), rec(2, "r2", "oppose"), rec(3, "r3", "oppose")],
            SEARCHED,
        )
    )
    assert receipt["conclusion"] == "not_established"


def test_r1_strict_majority_is_supported():
    receipt = evaluate_transaction(world([rec(1, "r1", "support")], SEARCHED))
    assert receipt["conclusion"] == "supported"


def test_r1_presence_never_concludes_present_or_absent():
    """The registered conclusion function: presence -> {supported, not_established}."""
    for records in ([], [rec(1, "r1", "oppose")], [rec(1, "r1", "support")]):
        receipt = evaluate_transaction(world(records, SEARCHED))
        assert receipt["conclusion"] in {"supported", "not_established"}


# --- R2: non-empty declared scope ------------------------------------------

def test_r2_empty_declared_scope_refuses():
    with pytest.raises(ValueError, match="must not be empty"):
        evaluate_transaction(world([], [], ctype="absence"))


def test_r2_checker_accepts_the_refusal_and_flags_acceptance():
    empty_scope = world([], [], ctype="absence")
    # The real evaluator refuses; the checker records no violation for that.
    assert check_world(evaluate_transaction, empty_scope) == []

    # A literal-v1.0.0 evaluator that emits vacuous absence is flagged, and the
    # flag lands on I8, where the declared > 0 conjunct now lives.
    def vacuous_evaluator(payload):
        receipt = evaluate_transaction(
            world([], SEARCHED, ctype="absence")
        )
        return receipt

    violations = check_world(vacuous_evaluator, empty_scope)
    assert [v.invariant for v in violations] == ["I8"]


# --- R3 / I11: location identifier uniqueness ------------------------------

def test_r3_duplicate_location_ids_refuse():
    with pytest.raises(ValueError, match="unique"):
        evaluate_transaction(
            world(
                [],
                [{"id": "loc-1", "status": "searched"},
                 {"id": "loc-1", "status": "searched"}],
                ctype="absence",
            )
        )


def test_r3_checker_accepts_the_refusal_and_flags_acceptance_as_i11():
    padded = world(
        [],
        [{"id": "loc-1", "status": "searched"},
         {"id": "loc-1", "status": "searched"}],
        ctype="absence",
    )
    assert check_world(evaluate_transaction, padded) == []

    # A permissive evaluator that counts entries rather than locations is the
    # attack I11 exists to catch.
    def permissive_evaluator(payload):
        deduped = json.loads(json.dumps(payload))
        deduped["searchLedger"]["locations"] = [{"id": "loc-1", "status": "searched"}]
        receipt = evaluate_transaction(deduped)
        return receipt

    violations = check_world(permissive_evaluator, padded)
    assert [v.invariant for v in violations] == ["I11"]


# --- R4: canonical form and digest scope ------------------------------------

def test_r4_canonical_form_exact_bytes():
    """Pins each canonicalisation rule at byte level, per the v1.1.0 definition."""
    value = {
        "b": 1,
        "a": "é \" \\ \n \x1f —",
        "nested": {"z": True, "y": [2, 1]},
    }
    assert canonical_bytes(value) == (
        b'{"a":"\xc3\xa9 \\" \\\\ \\n \\u001f \xe2\x80\x94",'
        b'"b":1,"nested":{"y":[2,1],"z":true}}'
    )


def test_r4_digest_covers_everything_except_top_level_content_digest():
    receipt = evaluate_transaction(world([rec(1, "r1", "support")], SEARCHED))
    unsigned = {k: v for k, v in receipt.items() if k != "contentDigest"}
    expected = "sha256:" + hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
    assert receipt["contentDigest"] == expected


def test_r4_c11_fixture_digest_is_reproduced():
    doc = json.loads(
        (EXPERIMENT / "fixtures" / "v1.1.0" / "c11-canonical-digest.json").read_text()
    )
    receipt = evaluate_transaction(doc["input"])
    assert receipt["conclusion"] == doc["expected"]["conclusion"] == "not_established"
    assert receipt["contentDigest"] == doc["expected"]["contentDigest"]
    unsigned = {k: v for k, v in receipt.items() if k != "contentDigest"}
    assert len(canonical_bytes(unsigned)) == 703


# --- registration integrity --------------------------------------------------

def test_v110_registration_freezes_the_same_experiment():
    """v1.1.0 is documentation: same evaluator, same bounds, same seed."""
    assert (
        PREREG_V110["evaluatorUnderTest"]["sha256"]
        == PREREG_V100["evaluatorUnderTest"]["sha256"]
    )
    # The prose description notes the version relationship; the registered
    # bounds themselves must be identical.
    assert PREREG_V110["population"]["exhaustive"] == PREREG_V100["population"]["exhaustive"]
    assert PREREG_V110["population"]["randomized"] == PREREG_V100["population"]["randomized"]
    assert (
        PREREG_V110["frozenSeedsOrSplits"]["randomizedSeed"]
        == PREREG_V100["frozenSeedsOrSplits"]["randomizedSeed"]
    )


def test_v110_evaluator_hash_matches_the_file_on_disk():
    digest = hashlib.sha256(
        (REPO / "knowledge_ledger" / "transaction.py").read_bytes()
    ).hexdigest()
    assert digest == PREREG_V110["evaluatorUnderTest"]["sha256"]


def test_v110_controls_are_v100_controls_plus_c11():
    v100 = [c["fixture"] for c in PREREG_V100["controls"]]
    v110 = [c["fixture"] for c in PREREG_V110["controls"]]
    assert v110[: len(v100)] == v100
    assert v110[len(v100):] == ["fixtures/v1.1.0/c11-canonical-digest.json"]
