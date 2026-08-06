"""Deterministic regression fixtures for every valid counterexample.

Each test pins ONE witness. If a future change to the core, to
`provenance/graph.py`, or to `aggregation/semantic.py` makes a witness stop
witnessing, the corresponding test fails LOUDLY rather than the finding being
quietly lost.

These tests assert that the counterexamples still hold. They are NOT tests that
the system is correct. A green run here means "the known holes are still where
we left them", which is the point: negative results must not decay.

Run:  python -m pytest audit/test_counterexamples.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))

from core_models import (  # noqa: E402
    dag_S,
    dag_roots_of,
    dag_side_consistent,
    dag_verdict,
    forest_S,
    forest_margin,
    forest_side_consistent,
    forest_verdict,
    verdict_of,
)


# --------------------------------------------------------------------------
# CE-01 — "adding copied claims cannot change the verdict" needs its hypothesis
# --------------------------------------------------------------------------


def test_ce01_recorded_copy_is_harmless():
    """The PROVED form of T2: the copy records its parent. Verdict survives."""
    before = ((-1, -1, -1), (1, 1, 0))
    after = ((-1, -1, -1, 2, 2), (1, 1, 0, 0, 0))
    assert forest_side_consistent(*after)
    assert forest_verdict(*before) == 1
    assert forest_verdict(*after) == 1


def test_ce01_unrecorded_copy_reverses_the_verdict():
    """The PLAIN-ENGLISH form of T2 is false: unrecorded copies are roots."""
    before = ((-1, -1, -1), (1, 1, 0))
    after = ((-1, -1, -1, -1, -1), (1, 1, 0, 0, 0))
    assert forest_verdict(*before) == 1
    assert forest_verdict(*after) == 0, (
        "two copies entered without provenance must still reverse the verdict; "
        "if this fails the aggregator changed and CE-01 needs re-derivation"
    )


# --------------------------------------------------------------------------
# CE-02 / CE-03 — a side conversion is worth 2 units of margin, not 1
# --------------------------------------------------------------------------


def test_ce02_one_conversion_changes_a_margin_two_verdict():
    p = (-1, -1, -1, -1)
    base = (1, 1, 1, 0)
    converted = (0, 1, 1, 0)
    assert forest_margin(p, base) == 2
    assert forest_verdict(p, base) == 1
    assert forest_verdict(p, converted) is None, (
        "T5's corollary predicts no change for k=1 < margin=2; it changes"
    )
    # the conversion is worth 2 units of T4 flow
    p0 = len(forest_S(p, converted, 0)) - len(forest_S(p, base, 0))
    p1 = len(forest_S(p, converted, 1)) - len(forest_S(p, base, 1))
    assert p0 - p1 == 2


def test_ce03_reversal_costs_margin_not_margin_plus_one():
    p = (-1, -1, -1, -1)
    base = (1, 1, 1, 0)
    two_conversions = (0, 0, 1, 0)
    assert forest_margin(p, base) == 2
    assert forest_verdict(p, two_conversions) == 0, (
        "T4' predicts reversal needs margin+1 = 3 units; 2 conversions suffice"
    )


@pytest.mark.parametrize("m", range(1, 9))
def test_conversion_budget_is_about_half_the_doctrine(m):
    """Reversal by conversion costs floor(m/2)+1, not m+1."""
    n1, n0 = m + 1, 1
    need = next(f for f in range(n1 + 1) if verdict_of(n1 - f, n0 + f) == 0)
    assert need == m // 2 + 1
    assert need <= m + 1
    if m >= 2:
        assert need < m + 1, "doctrine over-states the attacker's cost"


@pytest.mark.parametrize("m", [1, 3, 5, 7])
def test_odd_margin_cannot_be_driven_to_abstention_by_conversions(m):
    """Parity invariant (proved in Lean as `no_abstention_of_odd_margin`)."""
    n1, n0 = m + 1, 1
    reachable = {verdict_of(n1 - f, n0 + f) for f in range(n1 + 1)}
    assert None not in reachable


# --------------------------------------------------------------------------
# CE-04 / CE-05 — one real-world "error" is not one edge edit
# --------------------------------------------------------------------------


def test_ce04_one_deleted_record_orphans_a_whole_subtree():
    fanout = 5
    p = tuple([-1] + [0] * fanout + [-1, -1, -1, -1])
    a = tuple([0] * (1 + fanout) + [1, 1, 1, 1])
    assert forest_side_consistent(p, a)
    assert forest_margin(p, a) == 3
    assert forest_verdict(p, a) == 1
    p_del = tuple([-1] * (1 + fanout) + [-1, -1, -1, -1])
    assert forest_verdict(p_del, a) == 0, (
        "deleting ONE claim record reversed a margin-3 verdict; "
        "'immunity to any single ops error at flip_budget>=2' is false"
    )


def test_ce05_one_key_compromise_mints_many_roots():
    base_p, base_a = (-1, -1, -1), (1, 1, 1)
    assert forest_verdict(base_p, base_a) == 1
    assert forest_margin(base_p, base_a) == 3
    p = tuple([-1] * 7)
    a = tuple([1, 1, 1] + [0] * 4)
    assert forest_verdict(p, a) == 0, (
        "one compromised root-signing key that mints 4 roots reverses a "
        "margin-3 verdict; roots-per-key must be bounded by attestation"
    )


# --------------------------------------------------------------------------
# CE-06 / CE-07 — assumption boundaries
# --------------------------------------------------------------------------


def test_ce06_without_side_consistency_a_root_serves_both_sides():
    p, a = (-1, 0), (0, 1)
    assert not forest_side_consistent(p, a)
    assert forest_S(p, a, 0) & forest_S(p, a, 1) == frozenset({0})


def test_ce07_side_consistency_forbids_synthesis_in_the_dag():
    """A claim derived from BOTH sides is inexpressible in the forest model and
    rejected by side-consistency in the DAG model."""
    ps = (frozenset(), frozenset(), frozenset({0, 1}))
    a = (1, 0, 1)
    assert not dag_side_consistent(ps, a)
    assert dag_roots_of(ps, 2) == frozenset({0, 1})
    assert dag_S(ps, a, 0) & dag_S(ps, a, 1) == frozenset({1})


# --------------------------------------------------------------------------
# CE-08 — root identity is an unstated parameter
# --------------------------------------------------------------------------


def test_ce08_identity_merge_changes_the_verdict():
    a = [1, 1, 0]
    distinct = ["r1", "r2", "r3"]
    merged = ["r1", "r1", "r3"]

    def tally(ids):
        return verdict_of(
            len({i for i, v in zip(ids, a) if v == 1}),
            len({i for i, v in zip(ids, a) if v == 0}),
        )

    assert tally(distinct) == 1
    assert tally(merged) is None


# --------------------------------------------------------------------------
# CE-09 .. CE-12 — implementation invariants (not theorems)
#
# These four were REPAIRED on 2026-08-05. The tests below now pin the FIXED
# behaviour, and each records what the defect was so the negative result is not
# erased. CE-11 and CE-12 additionally pin the UNFIXED behaviour of
# aggregation.semantic.evidence_root_vote, which is retained byte-identical
# because results/los-inspired-v0.1.manifest.json binds its sha256.
# --------------------------------------------------------------------------


def _node(nid, value, parents=(), proposition="p"):
    from provenance.graph import EvidenceNode

    return EvidenceNode(
        node_id=nid,
        proposition_id=proposition,
        value=value,
        observer_id="o",
        source_id="s",
        confidence=1.0,
        evidence={},
        copied_from=tuple(parents),
    )


def test_ce09_cross_side_edge_is_now_rejected():
    """WAS: EvidenceGraph.add accepted a claim derived from an opposite-valued
    parent, so R2 -- the hypothesis every theorem consumes -- had no
    enforcement point anywhere in the codebase."""
    from provenance.graph import EvidenceGraph, SideConsistencyError

    g = EvidenceGraph()
    g.add(_node("r", True))
    with pytest.raises(SideConsistencyError):
        g.add(_node("c", False, ("r",)))


def test_ce09_permissive_mode_records_rather_than_hides():
    """Non-strict ingest must still fail LOUDLY: the violation is recorded and
    immunity_applicable goes False. Silence is the thing being fixed."""
    from provenance.graph import EvidenceGraph

    g = EvidenceGraph(strict=False)
    g.add(_node("r", True))
    g.add(_node("c", False, ("r",)))
    assert len(g.violations) == 1
    assert g.violations[0].kind == "side_inconsistent_edge"
    assert g.immunity_applicable is False


def test_ce10_cross_proposition_edge_is_now_rejected():
    """WAS: a claim about proposition p could record a parent about a different
    proposition, leaving subject substitution unconstrained at the data layer."""
    from provenance.graph import EvidenceGraph, PropositionMismatchError

    g = EvidenceGraph()
    g.add(_node("r", True))
    with pytest.raises(PropositionMismatchError):
        g.add(_node("c", True, ("r",), proposition="DIFFERENT"))


def test_cycles_cannot_hang_the_root_walk():
    """roots() was unmemoised and had no cycle guard. add() makes cycles
    unreachable, but from_dict() is a second ingest path."""
    from provenance.graph import CycleError, EvidenceGraph

    payload = {
        "nodes": [
            dict(node_id="a", proposition_id="p", value=True, observer_id="o",
                 source_id="s", confidence=1.0, evidence={}, copied_from=("b",),
                 transformations=(), signature=None, timestamp="t"),
            dict(node_id="b", proposition_id="p", value=True, observer_id="o",
                 source_id="s", confidence=1.0, evidence={}, copied_from=("a",),
                 transformations=(), signature=None, timestamp="t"),
        ]
    }
    with pytest.raises(CycleError):
        EvidenceGraph.from_dict(payload)


class _MC:
    def __init__(self, value, root_id):
        self.value = value
        self.root_id = root_id
        self.assignment = (value,)
        self.confidence = 1.0
        self.competence = 1.0


def test_ce11_legacy_evidence_root_vote_is_still_order_dependent():
    """UNFIXED BY DESIGN. semantic.evidence_root_vote resolves duplicate root
    IDs first-writer-wins. Its bytes are bound by a canonical manifest, so it
    cannot be corrected in place without falsifying a canonical record."""
    from aggregation.semantic import evidence_root_vote

    a, b, c = _MC(True, "R"), _MC(False, "R"), _MC(False, "B")
    forward = evidence_root_vote([a, b, c], lambda x: True)
    reverse = evidence_root_vote([b, a, c], lambda x: True)
    assert forward.assignment != reverse.assignment


def test_ce11_root_vote_is_order_independent_and_fails_closed():
    """FIXED: aggregation.root_vote collects a SET of assertions per root, so a
    conflicting root is detected regardless of input order and the verdict is
    withheld rather than silently resolved."""
    from aggregation.root_vote import Verdict, verdict

    a, b, c = _MC(True, "R"), _MC(False, "R"), _MC(False, "B")
    forward = verdict([a, b, c])
    reverse = verdict([b, a, c])
    assert forward.verdict == reverse.verdict == Verdict.ABSTAIN
    assert forward.conflicting_roots == reverse.conflicting_roots == frozenset({"R"})
    assert forward.immunity_applicable is False


def test_ce12_unattributed_claims_are_reported_not_silently_dropped():
    """WAS: claims with root_id=None vanished. Now they are counted, and under
    the default policy they force abstention when they could change the answer."""
    from aggregation.root_vote import Verdict, verdict

    claims = [_MC(True, "r1"), _MC(True, "r2"), _MC(False, "r3"),
              _MC(False, None), _MC(False, None)]
    result = verdict(claims)
    assert result.unattributed == 2
    assert result.margin == 1
    assert result.verdict is Verdict.ABSTAIN, "2 unattributed >= flip budget 1"
    assert any("unattributed" in n for n in result.notes)


def test_ce12_the_two_rejected_readings_are_still_available_and_named():
    """The repository previously held BOTH rejected answers in different
    modules with no decision recorded. They are now explicit policies."""
    from aggregation.root_vote import Verdict, verdict

    claims = [_MC(True, "r1"), _MC(True, "r2"), _MC(False, "r3"),
              _MC(False, None), _MC(False, None)]
    assert verdict(claims, unattributed_policy="ignore").verdict is Verdict.TRUE
    assert verdict(claims, unattributed_policy="treat_as_root").verdict is Verdict.FALSE


def test_root_vote_reports_both_attack_units():
    """CE-02/CE-03: flip_budget alone overstates the attacker's cost ~2x."""
    from aggregation.root_vote import tolerated_root_errors, verdict

    claims = [_MC(True, f"t{i}") for i in range(5)] + [_MC(False, "f0")]
    result = verdict(claims)
    assert result.margin == 4 and result.flip_budget == 4
    assert result.conversions_to_reverse == 3        # floor(4/2)+1, not 5
    assert result.abstention_reachable_by_conversion is True
    assert tolerated_root_errors(result) == 3

    odd = verdict([_MC(True, f"t{i}") for i in range(4)] + [_MC(False, "f0")])
    assert odd.margin == 3
    assert odd.abstention_reachable_by_conversion is False   # parity, T6


# --------------------------------------------------------------------------
# Positive regressions: the theorems that DO hold, in the DAG model
# --------------------------------------------------------------------------


def test_t1_holds_in_the_dag_model_on_a_representative_pair():
    ps = (frozenset(), frozenset(), frozenset({0}), frozenset({0, 2}))
    qs = (frozenset(), frozenset(), frozenset({0}), frozenset({2}))
    a = (1, 0, 1, 1)
    assert dag_side_consistent(ps, a) and dag_side_consistent(qs, a)
    assert dag_verdict(ps, a) == dag_verdict(qs, a)


def test_t2_holds_in_the_dag_model_when_the_copy_edge_is_recorded():
    ps = (frozenset(), frozenset(), frozenset({0}))
    a = (1, 0, 1)
    before = dag_verdict(ps, a)
    ps2 = tuple(list(ps) + [frozenset({1})])
    a2 = tuple(list(a) + [a[1]])
    assert dag_side_consistent(ps2, a2)
    assert dag_verdict(ps2, a2) == before
