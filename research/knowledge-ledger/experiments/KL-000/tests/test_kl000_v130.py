"""Protocol v1.3.0 permanent tests: I12, decision enforcement.

The committed gate: the two owner decisions (R1 tie rule, R5.2 absolute
margin) must be enforced by an invariant with power against their inversion,
not by pinned fixtures. Full-enumeration counts are the confirmatory run's
job; these tests pin the mechanism at unit scale.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = EXPERIMENT.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXPERIMENT / "src"))

from knowledge_ledger.transaction import evaluate_transaction  # noqa: E402
from kl000_decision_ablations import (  # noqa: E402
    ablation_r1_inverted,
    ablation_r52_signed,
)
from kl000_invariants import check_world  # noqa: E402

PREREG_V130 = json.loads((EXPERIMENT / "preregistration-v1.3.0.json").read_text())
PREREG_V120 = json.loads((EXPERIMENT / "preregistration-v1.2.0.json").read_text())


def world(records, locations, ctype="presence"):
    proposition = (
        "A target-class defect exists in the declared components."
        if ctype == "presence"
        else "No target-class defect exists in the declared components."
    )
    return {
        "transactionId": "kl000-v130-test",
        "claim": {"type": ctype, "proposition": proposition},
        "evidenceLedger": {"records": records},
        "searchLedger": {"locations": locations},
    }


def rec(i, root, side):
    return {"id": f"rec-{i}", "rootId": root, "side": side}


SEARCHED = [{"id": "loc-1", "status": "searched"}]
UNSEARCHED = [{"id": "loc-1", "status": "not_searched"}]

TIE = world([rec(1, "r1", "support"), rec(2, "r2", "oppose")], SEARCHED)
MINORITY = world(
    [rec(1, "r1", "support"), rec(2, "r2", "oppose"), rec(3, "r3", "oppose")], SEARCHED
)
MAJORITY = world([rec(1, "r1", "support")], SEARCHED)


# --- B5 records zero I12 violations ------------------------------------------

def test_i12_clears_the_reference_on_every_conclusion_branch():
    for w in (
        TIE,
        MINORITY,
        MAJORITY,
        world([], SEARCHED, "absence"),
        world([], UNSEARCHED, "absence"),
        world([rec(1, "r1", "oppose")], UNSEARCHED, "absence"),
        world([rec(1, "r1", "support"), rec(2, "r1", "support")], SEARCHED),
    ):
        assert check_world(evaluate_transaction, w) == []


# --- I12 catches each inversion, one violation per world, no fixture ---------

def test_i12_catches_the_r1_inversion_on_a_tie_and_a_minority():
    for w in (TIE, MINORITY):
        violations = check_world(ablation_r1_inverted, w)
        assert [v.invariant for v in violations] == ["I12"]
        assert "conclusion" in violations[0].detail
        assert "margin" not in violations[0].detail
    # majority worlds are unchanged by the inversion and must stay clean
    assert check_world(ablation_r1_inverted, MAJORITY) == []


def test_i12_catches_the_r52_inversion_exactly_where_margin_signs_differ():
    violations = check_world(ablation_r52_signed, MINORITY)
    assert [v.invariant for v in violations] == ["I12"]
    assert "margin" in violations[0].detail
    assert "conclusion" not in violations[0].detail
    # ties (margin 0) and majorities (positive either way) are sign-agnostic
    assert check_world(ablation_r52_signed, TIE) == []
    assert check_world(ablation_r52_signed, MAJORITY) == []


def test_i12_emits_at_most_one_violation_per_world_even_when_both_fail():
    def both_inverted(payload):
        return ablation_r52_signed_after_r1(payload)

    def ablation_r52_signed_after_r1(payload):
        receipt = ablation_r1_inverted(payload)
        return ablation_r52_signed_from_receipt(receipt)

    def ablation_r52_signed_from_receipt(receipt):
        import hashlib
        from knowledge_ledger.transaction import canonical_bytes
        evidence = receipt["evidence"]
        signed = len(evidence["supportingRoots"]) - len(evidence["opposingRoots"])
        if signed != evidence["margin"]:
            receipt = dict(receipt)
            receipt["evidence"] = dict(evidence)
            receipt["evidence"]["margin"] = signed
            unsigned = {k: v for k, v in receipt.items() if k != "contentDigest"}
            receipt["contentDigest"] = (
                "sha256:" + hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
            )
        return receipt

    violations = check_world(both_inverted, MINORITY)
    i12 = [v for v in violations if v.invariant == "I12"]
    assert len(i12) == 1
    assert "conclusion" in i12[0].detail and "margin" in i12[0].detail


def test_the_ablations_change_nothing_else_the_checker_sees():
    """On worlds each inversion touches, I12 is the ONLY invariant that fires --
    the unit-scale form of the registered 0-other-violations condition."""
    for ablation, w in ((ablation_r1_inverted, TIE), (ablation_r52_signed, MINORITY)):
        assert {v.invariant for v in check_world(ablation, w)} == {"I12"}


# --- registration integrity --------------------------------------------------

def test_v130_registration_is_v120_plus_i12_only():
    assert PREREG_V130["evaluatorUnderTest"]["sha256"] == PREREG_V120["evaluatorUnderTest"]["sha256"]
    assert PREREG_V130["population"]["exhaustive"] == PREREG_V120["population"]["exhaustive"]
    assert PREREG_V130["population"]["randomized"] == PREREG_V120["population"]["randomized"]
    v120_ids = [i["id"] for i in PREREG_V120["invariants"]]
    v130_ids = [i["id"] for i in PREREG_V130["invariants"]]
    assert v130_ids == v120_ids + ["I12"]
    assert [c["fixture"] for c in PREREG_V130["controls"]] == [
        c["fixture"] for c in PREREG_V120["controls"]
    ]


def test_v130_registered_ablation_surfaces_match_the_prior_measurements():
    expected = PREREG_V130["expectedIdenticalToRun1"]["ablations"]
    assert expected["ABL-R1"] == {"i12Violations": 22440, "otherViolations": 0}
    assert expected["ABL-R52"] == {"i12Violations": 38760, "otherViolations": 0}


def test_v130_pinned_digests_are_carried_unchanged():
    exp = PREREG_V130["expectedIdenticalToRun1"]
    v120 = PREREG_V120["expectedIdenticalToRun1"]
    assert exp["c11ContentDigest"] == v120["c11ContentDigest"]
    assert exp["c12ContentDigest"] == v120["c12ContentDigest"]
