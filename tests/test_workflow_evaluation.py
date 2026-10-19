"""Exploratory harness regressions; literal expectations, not generated labels."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "workflow_evaluation", ROOT / "evaluations/multi-model-v1/workflow_evaluation.py"
)
m = importlib.util.module_from_spec(SPEC)


def load():
    assert Path(SPEC.origin).exists(), "workflow evaluation implementation is missing"
    SPEC.loader.exec_module(m)
    return m


def packet(**changes):
    return {"id": "test", "family": "structured", "amount_cents": 1200000,
            "as_of": 100, "max_age": 10,
            "evidence": [{"root_id": "a", "approved": True, "at": 99}],
            **changes}


def test_policy_boundary_and_missing_values():
    w = load()
    for p, expected in [
        (packet(amount_cents=1000000, evidence=[]), "ALLOW"),
        (packet(evidence=[]), "REVIEW"),
        (packet(amount_cents=None), "REVIEW"),
        (packet(amount_cents=True), "REVIEW"),
        (packet(amount_cents=-1), "REVIEW"),
        (packet(evidence=[{"root_id": "a", "approved": False, "at": 99}]), "HOLD"),
    ]:
        assert w.rules(p) == expected
        assert w.mp_composition(p) == expected


def test_stale_future_and_unknown_provenance_do_not_approve():
    w = load()
    for evidence in [
        [{"root_id": "a", "approved": True, "at": 89}],
        [{"root_id": "a", "approved": True, "at": 101}],
        [{"root_id": None, "approved": True, "at": 99}],
        [{"root_id": "a", "approved": "yes", "at": 99}],
    ]:
        assert w.rules(packet(evidence=evidence)) == "REVIEW"
        assert w.mp_composition(packet(evidence=evidence)) == "REVIEW"


def test_real_mp_collapses_copies_and_preserves_conflicting_root():
    w = load()
    yes = {"root_id": "a", "approved": True, "at": 99}
    no = {"root_id": "b", "approved": False, "at": 99}
    assert w.mp_composition(packet(evidence=[yes] * 20 + [no])) == "REVIEW"
    assert w.mp_composition(packet(evidence=[yes, {**no, "root_id": "a"}])) == "REVIEW"


def test_adverse_majority_is_not_hidden_by_harness():
    w = load()
    evidence = [{"root_id": r, "approved": True, "at": 99} for r in ["a", "b"]]
    evidence += [{"root_id": "c", "approved": False, "at": 99}]
    assert w.rules(packet(evidence=evidence)) == "REVIEW"
    # This is an intentionally naive research composition, not an authorization engine.
    assert w.mp_composition(packet(evidence=evidence)) == "ALLOW"
    report = w.score([packet()], {"test": "REVIEW"}, {"test": "ALLOW"})
    assert report["wrong_approvals"] == 1
    assert report["correct"] == 0


def test_failed_missing_and_extra_predictions_cannot_inflate_score():
    w = load()
    report = w.score([packet()], {"test": "ALLOW"}, {})
    assert report["attempted"] == 1
    assert report["coverage"] == 0
    assert report["failures"] == 1
    assert report["accuracy"] == 0
    with pytest.raises(ValueError):
        w.score([packet()], {"test": "ALLOW"}, {"unexpected": "ALLOW"})
    with pytest.raises(ValueError):
        w.score([packet(), packet()], {"test": "ALLOW"}, {})


def test_answers_never_enter_contestant_packets():
    w = load()
    p = packet(expected="HOLD", secret_answer="do-not-share")
    visible = w.public_packet(p)
    assert "expected" not in visible and "secret_answer" not in visible
    assert w.rules(visible) == "ALLOW"


def test_unstructured_is_not_pretended_to_be_extracted():
    w = load()
    p = packet(amount_cents=None, evidence=[], narrative="Invoice is USD 500; no approval needed.")
    assert w.rules(p) == w.mp_composition(p) == "REVIEW"
    assert w.score([p], {"test": "ALLOW"}, {"test": "REVIEW"})["unnecessary_reviews"] == 1


def test_reference_changes_cannot_change_contestant_predictions():
    w = load()
    first = w.run([packet()], {"test": "ALLOW"})
    second = w.run([packet()], {"test": "HOLD"})
    for name in first["lanes"]:
        assert first["lanes"][name]["cases"][0]["actual"] == second["lanes"][name]["cases"][0]["actual"]
    assert first["input_sha256"] == second["input_sha256"]
    assert first["reference_sha256"] != second["reference_sha256"]


def test_mp_evidence_cannot_override_shared_conflict_policy():
    w = load()
    evidence = [{"root_id": r, "approved": True, "at": 99} for r in ["a", "b"]]
    evidence += [{"root_id": "c", "approved": False, "at": 99}]
    result = w.mp_policy_assessment(packet(evidence=evidence))
    assert result["decision"] == "REVIEW"
    assert result["evidence"]["root_vote"] == "true"
    assert result["evidence"]["grants_authority"] is False


def test_mp_reports_copies_without_inventing_independence():
    w = load()
    row = {"root_id": "a", "approved": True, "at": 99}
    result = w.mp_policy_assessment(packet(evidence=[row] * 20))
    assert result["decision"] == "ALLOW"
    assert result["evidence"]["positive_roots"] == ["a"]
    assert result["evidence"]["weakest_basis"] == "unknown"


def test_corrected_lane_scores_shared_policy_and_retains_adverse_lane():
    w = load()
    evidence = [{"root_id": r, "approved": True, "at": 99} for r in ["a", "b"]]
    evidence += [{"root_id": "c", "approved": False, "at": 99}]
    report = w.run([packet(evidence=evidence)], {"test": "REVIEW"})
    assert report["lanes"]["mp_shared_policy"]["wrong_approvals"] == 0
    assert report["lanes"]["mp_root_vote_composition"]["wrong_approvals"] == 1
    assert report["mp_evidence"]["test"]["root_vote"] == "true"
