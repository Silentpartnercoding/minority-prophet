import json
from pathlib import Path

import pytest

from provenance.decision_relative import (
    DecisionContext,
    DecisionContextError,
    DecisionEvidence,
    assess_decision,
)

FIXTURES = Path(__file__).parents[1] / "benchmark" / "decision-relative-independence-v0.1.json"


def _evidence(raw):
    return tuple(
        DecisionEvidence(
            observation_id=item["observation_id"],
            proposition_id=item["proposition_id"],
            value=item["value"],
            roots=item["roots"],
            basis={cut: "attested" for cut in item["roots"]},
        )
        for item in raw
    )


def _context(raw, proposition_id):
    return DecisionContext(
        decision_id=raw["decision_id"],
        proposition_id=proposition_id,
        failure_domain=raw["failure_domain"],
        independence_cut=raw["independence_cut"],
        minimum_winning_roots=raw["minimum_winning_roots"],
        consequence="fixture",
        reversibility="fixture",
        candidate_cuts=tuple(raw.get("candidate_cuts", ())),
    )


def test_constructed_fixtures_pin_decision_relative_settlement():
    payload = json.loads(FIXTURES.read_text())
    assert payload["status"] == "constructed-falsification-fixtures"
    assert payload["fixture_assumptions"]["root_identity"] == "attested constructed ground truth"
    for case in payload["cases"]:
        evidence = _evidence(case["evidence"])
        proposition_id = evidence[0].proposition_id
        for raw_context in case["contexts"]:
            result = assess_decision(evidence, _context(raw_context, proposition_id))
            assert result.selected.settlement == raw_context["expected_settlement"], case["id"]
            assert list(result.material_alternative_cuts) == raw_context["expected_material_cuts"]


def test_same_evidence_can_settle_one_question_without_settling_another():
    evidence = _evidence(json.loads(FIXTURES.read_text())["cases"][0]["evidence"])
    machine = assess_decision(
        evidence,
        DecisionContext(
            "compatibility",
            "route-works",
            "machine-specific",
            "machine",
            3,
            candidate_cuts=("controller",),
        ),
    )
    controller = assess_decision(
        evidence,
        DecisionContext(
            "consensus",
            "route-works",
            "shared-control",
            "controller",
            2,
            candidate_cuts=("machine",),
        ),
    )
    assert machine.selected.settlement == "settled_true"
    assert controller.selected.settlement == "unsettled"
    assert machine.selected.root_verdict.support_true == frozenset({"m1", "m4", "osmo"})
    assert controller.selected.root_verdict.support_true == frozenset({"owner-j"})


def test_independent_minority_is_not_erased_by_agent_headcount():
    case = json.loads(FIXTURES.read_text())["cases"][1]
    result = assess_decision(
        _evidence(case["evidence"]),
        DecisionContext(
            "source-sensitive",
            "claim-p",
            "copying",
            "evidence_origin",
            2,
            candidate_cuts=("agent",),
        ),
    )
    assert result.selected.root_verdict.support_true == frozenset({"independent-sensor"})
    assert result.selected.root_verdict.support_false == frozenset({"social-root"})
    assert result.selected.settlement == "unsettled"
    assert result.alternatives["agent"].settlement == "settled_false"


def test_missing_selected_root_fails_closed_when_it_could_change_outcome():
    evidence = (
        DecisionEvidence("known", "p", True, {"controller": "c1"}, {"controller": "attested"}),
        DecisionEvidence("unknown", "p", False, {"controller": None}),
    )
    result = assess_decision(
        evidence,
        DecisionContext("d", "p", "shared-control", "controller", 1),
    )
    assert result.selected.settlement == "unsettled"
    assert result.selected.root_verdict.unattributed == 1


def test_count_change_is_not_material_until_it_changes_settlement():
    evidence = (
        DecisionEvidence("a", "p", True, {"machine": "m1", "controller": "c1"}),
        DecisionEvidence("b", "p", True, {"machine": "m2", "controller": "c1"}),
    )
    result = assess_decision(
        evidence,
        DecisionContext("d", "p", "availability", "machine", 1, candidate_cuts=("controller",)),
    )
    assert not result.cut_is_material
    assert result.count_sensitive_cuts == ("controller",)


def test_proposition_mismatch_and_duplicate_observations_are_refused():
    context = DecisionContext("d", "p", "source-copying", "source", 1)
    with pytest.raises(DecisionContextError, match="does not match"):
        assess_decision((DecisionEvidence("x", "other", True, {"source": "s"}),), context)
    with pytest.raises(DecisionContextError, match="duplicate"):
        assess_decision(
            (
                DecisionEvidence("x", "p", True, {"source": "s1"}),
                DecisionEvidence("x", "p", True, {"source": "s2"}),
            ),
            context,
        )


def test_evaluator_does_not_mutate_full_multi_resolution_record():
    roots = {"agent": "a1", "machine": "m1", "controller": "c1", "source": "s1"}
    item = DecisionEvidence("x", "p", True, roots)
    before = dict(item.roots)
    assess_decision(
        (item,),
        DecisionContext("d", "p", "source-copying", "source", 1, candidate_cuts=("agent",)),
    )
    assert dict(item.roots) == before
    with pytest.raises(TypeError):
        item.roots["source"] = "rewritten"


def test_decision_context_schema_requires_cut_selection_provenance():
    schema = json.loads(
        (Path(__file__).parents[1] / "provenance" / "decision-context.schema.json").read_text()
    )
    assert "cut_selection_basis" in schema["required"]
    assert schema["properties"]["cut_selection_basis"]["enum"] == [
        "preregistered",
        "rules-engine",
        "model-selected",
        "human-reviewed",
        "declared",
        "unknown",
    ]
    with pytest.raises(ValueError, match="cut_selection_basis"):
        DecisionContext("d", "p", "source", "source", 1, cut_selection_basis="magic")
