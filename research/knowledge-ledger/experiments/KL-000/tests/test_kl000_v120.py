"""Protocol v1.2.0 permanent tests: R5.1 (receipt object) and R5.2 (margin sign).

Both repairs register serialisation-level facts the evaluator already
exhibits; these tests pin them so a drift breaks a test instead of silently
reopening findings G1/G2. The v1.0.0 and v1.1.0 suites are unchanged.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = EXPERIMENT.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXPERIMENT / "src"))

from knowledge_ledger.transaction import (  # noqa: E402
    canonical_bytes,
    evaluate_transaction,
)

PREREG_V120 = json.loads((EXPERIMENT / "preregistration-v1.2.0.json").read_text())
PREREG_V110 = json.loads((EXPERIMENT / "preregistration-v1.1.0.json").read_text())
PREREG_V100 = json.loads((EXPERIMENT / "preregistration.json").read_text())
RECEIPT_OBJECT = PREREG_V120["receiptObject"]


def world(records, locations, ctype="presence"):
    proposition = (
        "A target-class defect exists in the declared components."
        if ctype == "presence"
        else "No target-class defect exists in the declared components."
    )
    return {
        "transactionId": "kl000-v120-test",
        "claim": {"type": ctype, "proposition": proposition},
        "evidenceLedger": {"records": records},
        "searchLedger": {"locations": locations},
    }


def rec(i, root, side):
    return {"id": f"rec-{i}", "rootId": root, "side": side}


SEARCHED = [{"id": "loc-1", "status": "searched"}]
UNSEARCHED = [{"id": "loc-1", "status": "not_searched"}]

SAMPLE_WORLDS = [
    world([], SEARCHED, "absence"),
    world([], UNSEARCHED, "absence"),
    world([rec(1, "r1", "oppose")], SEARCHED, "absence"),
    world([rec(1, "r1", "support")], SEARCHED),
    world([rec(1, "r1", "support"), rec(2, "r2", "oppose")], SEARCHED),
    world([rec(1, "r1", "support"), rec(2, "r2", "oppose"), rec(3, "r3", "oppose")], UNSEARCHED),
    world([rec(1, "r2", "support"), rec(2, "r1", "support"), rec(3, "r1", "support")], SEARCHED),
]


# --- R5.1: the receipt object ------------------------------------------------

def test_r51_member_list_is_closed_and_exact():
    registered = RECEIPT_OBJECT["memberList"]
    assert len(registered) == 9
    for w in SAMPLE_WORLDS:
        receipt = evaluate_transaction(w)
        assert sorted(receipt.keys()) == sorted(registered)
        assert "receiptVersion" not in receipt


def test_r51_schema_and_limits_are_the_registered_constants():
    receipt = evaluate_transaction(SAMPLE_WORLDS[0])
    assert receipt["schema"] == RECEIPT_OBJECT["members"]["schema"]["value"]
    assert receipt["limits"] == RECEIPT_OBJECT["members"]["limits"]["value"]


def test_r51_reason_strings_cover_all_four_branches_exactly():
    branches = RECEIPT_OBJECT["members"]["reason"]["branches"]
    cases = {
        "absenceWithOpposingRoot": world([rec(1, "r1", "oppose")], UNSEARCHED, "absence"),
        "absenceCompleteNoOpposing": world([], SEARCHED, "absence"),
        "absenceOtherwise": world([], UNSEARCHED, "absence"),
        "presenceAlways": world([rec(1, "r1", "support")], SEARCHED),
    }
    for branch, w in cases.items():
        assert evaluate_transaction(w)["reason"] == branches[branch], branch


def test_r51_root_lists_are_sorted_ascending():
    receipt = evaluate_transaction(
        world([rec(1, "r3", "support"), rec(2, "r1", "support"), rec(3, "r2", "oppose")], SEARCHED)
    )
    ev = receipt["evidence"]
    assert ev["supportingRoots"] == sorted(ev["supportingRoots"])
    assert ev["opposingRoots"] == sorted(ev["opposingRoots"])
    assert ev["supportingRoots"] == ["r1", "r3"]


def test_r51_conversions_to_reverse_formula_including_empty_ledger():
    for w in SAMPLE_WORLDS:
        ev = evaluate_transaction(w)["evidence"]
        margin = ev["margin"]
        expected = margin // 2 + 1 if margin > 0 else 1
        assert ev["conversionsToReverse"] == expected
    # The registered (and contested -- F4, objection preserved) empty-ledger value:
    assert evaluate_transaction(world([], SEARCHED, "absence"))["evidence"]["conversionsToReverse"] == 1


def test_r51_digest_covers_all_nine_unsigned_members():
    receipt = evaluate_transaction(SAMPLE_WORLDS[4])
    unsigned = {k: v for k, v in receipt.items() if k != "contentDigest"}
    assert sorted(unsigned.keys()) == sorted(m for m in RECEIPT_OBJECT["memberList"] if m != "contentDigest")
    assert receipt["contentDigest"] == "sha256:" + hashlib.sha256(canonical_bytes(unsigned)).hexdigest()


# --- R5.2: margin sign -------------------------------------------------------

def test_r52_margin_is_absolute_on_a_strict_minority():
    ev = evaluate_transaction(
        world([rec(1, "r1", "support"), rec(2, "r2", "oppose"), rec(3, "r3", "oppose")], SEARCHED)
    )["evidence"]
    assert ev["margin"] == 1  # signed reading would give -1
    assert ev["margin"] >= 0


def test_r52_margin_never_negative_across_samples():
    for w in SAMPLE_WORLDS:
        ev = evaluate_transaction(w)["evidence"]
        assert ev["margin"] >= 0
        assert ev["margin"] == abs(len(ev["supportingRoots"]) - len(ev["opposingRoots"]))


# --- the two v1.2.0 fixtures -------------------------------------------------

def _fixture(name):
    return json.loads((EXPERIMENT / "fixtures" / "v1.2.0" / name).read_text())


def test_c11_v120_digest_unchanged_from_v110_pin():
    doc = _fixture("c11-canonical-digest.json")
    v110 = json.loads((EXPERIMENT / "fixtures" / "v1.1.0" / "c11-canonical-digest.json").read_text())
    assert doc["input"] == v110["input"]
    assert doc["expected"]["contentDigest"] == v110["expected"]["contentDigest"]
    receipt = evaluate_transaction(doc["input"])
    assert receipt["contentDigest"] == doc["expected"]["contentDigest"]
    unsigned = {k: v for k, v in receipt.items() if k != "contentDigest"}
    form = canonical_bytes(unsigned).decode("utf-8")
    assert form == doc["expected"]["canonicalUnsignedForm"]
    assert len(form.encode("utf-8")) == 703


def test_c12_pins_the_margin_sign_end_to_end():
    doc = _fixture("c12-margin-sign.json")
    receipt = evaluate_transaction(doc["input"])
    assert receipt["conclusion"] == "not_established"
    assert receipt["evidence"]["margin"] == 1
    assert receipt["evidence"]["opposingRoots"] == ["r2", "r3"]
    assert receipt["contentDigest"] == doc["expected"]["contentDigest"]
    unsigned = {k: v for k, v in receipt.items() if k != "contentDigest"}
    assert canonical_bytes(unsigned).decode("utf-8") == doc["expected"]["canonicalUnsignedForm"]


# --- registration integrity --------------------------------------------------

def test_v120_registration_freezes_the_same_experiment():
    assert PREREG_V120["evaluatorUnderTest"]["sha256"] == PREREG_V100["evaluatorUnderTest"]["sha256"]
    assert PREREG_V120["population"]["exhaustive"] == PREREG_V100["population"]["exhaustive"]
    assert PREREG_V120["population"]["randomized"] == PREREG_V100["population"]["randomized"]
    assert (
        PREREG_V120["frozenSeedsOrSplits"]["randomizedSeed"]
        == PREREG_V100["frozenSeedsOrSplits"]["randomizedSeed"]
    )


def test_v120_controls_are_v100_plus_repinned_c11_plus_c12():
    v100 = [c["fixture"] for c in PREREG_V100["controls"]]
    v120 = [c["fixture"] for c in PREREG_V120["controls"]]
    assert v120[: len(v100)] == v100
    assert v120[len(v100):] == [
        "fixtures/v1.2.0/c11-canonical-digest.json",
        "fixtures/v1.2.0/c12-margin-sign.json",
    ]
