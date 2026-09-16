"""How firmly an absence claim was refuted — without touching I5.

KL-000 pins I5 hard: a non-empty opposingRoots concludes `present`, at any
coverage level, and two independent implementations agreed across 110,840
receipts. These tests exist partly to prove this layer leaves that alone.
"""

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from knowledge_ledger.transaction_v2 import evaluate_transaction_v2  # noqa: E402
from provenance.counterexample_strength import (  # noqa: E402
    ACTIONABLE, ESCALATE_THIN, NOT_APPLICABLE, assess, required_roots, strength_note,
)
from provenance.decision_relative import DecisionContext  # noqa: E402

ONE = {"conclusion": "present", "evidence": {"opposingRoots": ["A"]}}
NINE = {"conclusion": "present", "evidence": {"opposingRoots": list("ABCDEFGHI")}}
CLEAN = {"conclusion": "absent_within_declared_scope", "evidence": {"opposingRoots": []}}


SAFE_TO_DEFER = {"minimum_winning_roots": 2, "deferring_is_safe": True,
                 "consequence": "accusation", "reversibility": "low"}


def test_the_default_changes_nothing():
    """Adopting this module must be a no-op until a decision opts in."""
    assert assess(ONE)["decision"] == ACTIONABLE
    assert required_roots(None) == (1, None)


def test_a_bar_above_one_is_REFUSED_unless_deferring_was_declared_safe():
    """The correction. Raising the counterexample bar means a single genuine
    finding does not get acted on — and for a safety absence claim that is the
    hole staying open, not caution. Flips if the guard is ever removed."""
    threshold, refusal = required_roots({"minimum_winning_roots": 2, "consequence": "safety"})
    assert threshold == 1
    assert refusal and "deferring_is_safe" in refusal
    assert assess(ONE, {"minimum_winning_roots": 2, "consequence": "safety"})["decision"] == ACTIONABLE


def test_a_decision_that_declares_deferral_safe_may_raise_the_bar():
    assert required_roots(SAFE_TO_DEFER) == (2, None)
    assert assess(ONE, SAFE_TO_DEFER)["decision"] == ESCALATE_THIN
    assert assess(NINE, SAFE_TO_DEFER)["decision"] == ACTIONABLE


def test_the_refusal_is_recorded_on_the_assessment_not_silent():
    """A guard that quietly overrides a declared number is its own defect."""
    out = assess(ONE, {"minimum_winning_roots": 5, "consequence": "safety"})
    assert "thresholdRefused" in out
    assert out["declaredMinimum"] == 1


def test_it_reads_a_real_DecisionContext_object_too():
    ctx = DecisionContext(
        decision_id="d", proposition_id="p", failure_domain="f",
        independence_cut="machine", minimum_winning_roots=3,
        consequence="irreversible", reversibility="none",
        cut_selection_basis="declared", candidate_cuts=("machine",))
    # A DecisionContext has no deferring_is_safe field, so the guard holds.
    assert required_roots(ctx) == (1, None) or required_roots(ctx)[0] == 1
    assert assess(ONE, ctx)["decision"] == ACTIONABLE


def test_the_escalation_carries_why_acting_is_expensive():
    """The consequence and reversibility travel with the decision, so a reader
    sees WHY corroboration was required rather than only that it was."""
    out = assess(ONE, SAFE_TO_DEFER)
    assert out["consequence"] == "accusation"
    assert out["reversibility"] == "low"


def test_escalation_says_what_would_lift_it():
    """An abstention that does not say what would lift it is just a refusal."""
    out = assess(ONE, {"minimum_winning_roots": 3, "deferring_is_safe": True})
    assert out["wouldLiftIf"]
    assert "2 more" in out["wouldLiftIf"]


def test_it_never_touches_the_verdict():
    """I5 is a hard invariant of a passed experiment. This layer reports on a
    conclusion; it must never be mistaken for a second opinion about one."""
    for ctx in ({"minimum_winning_roots": 1},
                {"minimum_winning_roots": 5, "deferring_is_safe": True}):
        out = assess(ONE, ctx)
        assert out["conclusion"] == "present"
        assert out["verdictUnchanged"] is True


def test_i5_still_holds_in_the_evaluator_itself():
    """The invariant, checked against the real evaluator rather than asserted:
    one opposing root concludes `present` even with coverage incomplete."""
    payload = {
        "transactionId": "t",
        "claim": {"type": "absence", "statement": "s"},
        "searchLedger": {"locations": [{"id": "l1", "status": "not_searched"}]},
        "evidenceLedger": {"records": [{"id": "A", "side": "oppose", "rootId": "A"}]},
    }
    result = evaluate_transaction_v2(payload)
    assert result["conclusion"] == "present"
    assert len(result["evidence"]["opposingRoots"]) == 1


def test_it_declines_to_speak_when_nothing_was_refuted():
    """Reporting on a verdict it does not govern would make the field look
    exercised when nothing was assessed."""
    assert assess(CLEAN)["decision"] == NOT_APPLICABLE


def test_all_three_decisions_are_reachable():
    got = {assess(r, c)["decision"] for r, c in (
        (ONE, {"minimum_winning_roots": 1}),
        (ONE, SAFE_TO_DEFER),
        (CLEAN, {"minimum_winning_roots": 1}))}
    assert got == {ACTIONABLE, ESCALATE_THIN, NOT_APPLICABLE}


def test_a_threshold_below_one_is_refused():
    with pytest.raises(ValueError):
        required_roots({"minimum_winning_roots": 0})


def test_the_note_distinguishes_one_root_from_nine():
    """Adds information without moving a line: the difference is invisible in
    the conclusion, and a reader who cannot see it cannot weigh it."""
    assert "single independent root" in strength_note(ONE)
    assert "9 independent roots" in strength_note(NINE)
    assert strength_note(CLEAN) == ""
