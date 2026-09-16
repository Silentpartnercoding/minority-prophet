"""Closing root emptiness -- the second of the two failure classes.

`research/adversarial-weighting/two_failure_classes.py` prints two rows the
graph gets wrong: a fabricated root, and a fabricated root with nine honest
copies. Both are structurally perfect and worth zero. These tests take the
graph's own cases and show the dereference gate catching exactly those, and only
those.
"""

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from provenance.graph import EvidenceGraph, EvidenceNode  # noqa: E402
from provenance.root_dereference import (  # noqa: E402
    ABSENT, NO_REFERENCE, UNVERIFIABLE, VERIFIED, audit_roots, dereference_root,
)

REAL = {"doi": "10.1000/paper"}
FABRICATED = {"doi": "10.1000/never-happened"}
REGISTERED = {"10.1000/paper"}


def resolver(form, reference):
    return reference in REGISTERED


def node(nid, observer, evidence, parents=()):
    return EvidenceNode(node_id=nid, proposition_id="p", value=True,
                        observer_id=observer, source_id=observer, confidence=0.9,
                        evidence=evidence, copied_from=parents)


def _graph(nodes):
    g = EvidenceGraph(strict=True)
    for n in nodes:
        g.add(n)
    return list(g._nodes.values())


# ---- the two rows the graph gets wrong -------------------------------------

def test_a_fabricated_root_is_now_caught():
    """two_failure_classes row 4: graph says 1 root, truth is 0."""
    report = audit_roots(_graph([node("f", "liar", FABRICATED)]), resolver)
    assert report["states"][ABSENT] == 1
    assert report["hollowRoots"] == ["f"]


def test_a_fabricated_root_with_nine_honest_copies_is_caught():
    """two_failure_classes row 5, the one its author said to remember. The copies
    declare ancestry correctly, ancestry collapses them to one root, that one is
    the right number -- and it is hollow."""
    nodes = [node("f", "liar", FABRICATED)] + [
        node(f"c{i}", f"h{i}", FABRICATED, ("f",)) for i in range(9)]
    report = audit_roots(_graph(nodes), resolver)
    assert report["roots"] == 1, "ancestry already collapsed the copies"
    assert report["states"][ABSENT] == 1, "and the surviving root is hollow"
    assert report["hollowRate"] == 1.0


def test_a_real_root_still_passes():
    """The control. Flips if the gate refuses everything, which would make it
    useless in the opposite direction."""
    report = audit_roots(_graph([node("a", "alice", REAL)]), resolver)
    assert report["states"][VERIFIED] == 1
    assert report["hollowRoots"] == []


def test_real_and_fabricated_are_told_apart_in_one_graph():
    """The gate's outcome must actually vary within a single population."""
    report = audit_roots(_graph([node("a", "alice", REAL), node("f", "liar", FABRICATED)]), resolver)
    assert report["states"][VERIFIED] == 1 and report["states"][ABSENT] == 1
    assert report["distinctStatesObserved"] >= 2


# ---- the three-valued discipline -------------------------------------------

def test_no_resolver_yields_unverifiable_never_pass_or_fail():
    """Silently treating 'cannot check' as either answer is the DRI-7 defect."""
    result = dereference_root(REAL, None)
    assert result.state == UNVERIFIABLE
    assert result.hollow is False


def test_a_resolver_that_cannot_answer_is_not_evidence_of_absence():
    result = dereference_root(REAL, lambda form, ref: None)
    assert result.state == UNVERIFIABLE
    assert result.hollow is False


def test_hollow_rate_is_over_the_checkable_only():
    """An unverifiable root must not inflate or deflate the rate."""
    nodes = [node("a", "alice", REAL), node("f", "liar", FABRICATED)]
    report = audit_roots(_graph(nodes), lambda form, ref: None)
    assert report["checkable"] == 0
    assert report["hollowRate"] is None


def test_prose_is_no_reference_not_absent():
    """Kept distinct: a root naming nothing is already refused by
    UnattributedRootError, and reporting that as this gate's catch would claim
    the older gate's work."""
    assert dereference_root({"source": "trust me"}, resolver).state == NO_REFERENCE


def test_this_gate_does_nothing_about_count_inflation():
    """Stated as a test so the boundary is enforced, not just documented.
    Three undeclared copies of one real paper are three roots, all verified."""
    nodes = [node(f"u{i}", f"p{i}", REAL) for i in range(3)]
    report = audit_roots(_graph(nodes), resolver)
    assert report["roots"] == 3, "count inflation is ancestry's job, not this gate's"
    assert report["states"][VERIFIED] == 3
    assert report["hollowRoots"] == []
