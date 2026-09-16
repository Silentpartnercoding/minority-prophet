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


def test_the_default_changes_nothing():
    """Adopting this module must be a no-op until a decision opts in. Flips if
    the default ever rises above one."""
    assert assess(ONE)["decision"] == ACTIONABLE
    assert required_roots(None) == 1


def test_the_threshold_comes_from_the_decision_context_not_a_second_dial():
    """minimum_winning_roots already exists, is required by the schema, and is
    decision-scoped. Inventing a parallel threshold would create two numbers
    that can disagree."""
    ctx = {"minimum_winning_roots": 2, "consequence": "accusation", "reversibility": "low"}
    assert required_roots(ctx) == 2
    assert assess(ONE, ctx)["decision"] == ESCALATE_THIN
    assert assess(NINE, ctx)["decision"] == ACTIONABLE


def test_it_reads_a_real_DecisionContext_object_too():
    ctx = DecisionContext(
        decision_id="d", proposition_id="p", failure_domain="f",
        independence_cut="machine", minimum_winning_roots=3,
        consequence="irreversible", reversibility="none",
        cut_selection_basis="declared", candidate_cuts=("machine",))
    assert required_roots(ctx) == 3
    assert assess(ONE, ctx)["decision"] == ESCALATE_THIN


def test_the_escalation_carries_why_acting_is_expensive():
    """The consequence and reversibility travel with the decision, so a reader
    sees WHY corroboration was required rather than only that it was."""
    ctx = {"minimum_winning_roots": 2, "consequence": "accusation", "reversibility": "low"}
    out = assess(ONE, ctx)
    assert out["consequence"] == "accusation"
    assert out["reversibility"] == "low"


def test_escalation_says_what_would_lift_it():
    """An abstention that does not say what would lift it is just a refusal."""
    out = assess(ONE, {"minimum_winning_roots": 3})
    assert out["wouldLiftIf"]
    assert "2 more" in out["wouldLiftIf"]


def test_it_never_touches_the_verdict():
    """I5 is a hard invariant of a passed experiment. This layer reports on a
    conclusion; it must never be mistaken for a second opinion about one."""
    for ctx in ({"minimum_winning_roots": 1}, {"minimum_winning_roots": 5}):
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
        (ONE, {"minimum_winning_roots": 2}),
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
