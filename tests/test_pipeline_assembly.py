"""What the assembled pipeline reveals that no organ showed alone.

CORRECTED. An earlier version of this file asserted that root resolution never
changes an absence conclusion. That was false, and it was false in the way this
repository exists to catch: the four shapes it tested all happened to keep at
least one genuine opposing root, so the outcome could not vary, and the constant
was reported as a property. The original error is kept in the git history rather
than tidied away.

The true finding is a boundary, not an absence:

    An absence conclusion turns on whether ANY opposing root SURVIVES
    resolution, never on how many. Resolution therefore changes the verdict
    exactly when it takes the opposing side from some to none, and changes only
    the margin otherwise.

That asymmetry is correct rather than a defect. One genuine counterexample
refutes a universal absence claim; five do not refute it harder. What the root
rule adds is that a counterexample nobody can attribute is no longer a
counterexample.
"""

import pytest

from knowledge_ledger.pipeline import ScopeSuppliedError, assemble, derive_scope

DOCS = {
    "SRC-0": {"isOriginal": True},
    **{f"C{i}": {"derivedFrom": "SRC-0"} for i in range(1, 6)},
    "A": {"isOriginal": True}, "B": {"isOriginal": True},
    "ORPH": {}, "CYC1": {"derivedFrom": "CYC2"}, "CYC2": {"derivedFrom": "CYC1"},
}
LAUNDERED = [{"id": f"C{i}", "side": "support", "rootId": f"S{i}"} for i in range(1, 6)]
OPPOSE = [{"id": "A", "side": "oppose", "rootId": "A"}, {"id": "B", "side": "oppose", "rootId": "B"}]


def _run(records, claim_type="absence"):
    payload = {"transactionId": "t", "claim": {"type": claim_type, "statement": "s"},
               "searchLedger": {"locations": [{"id": "loc-1", "status": "searched"}]},
               "evidenceLedger": {"records": records}}
    return assemble(payload, DOCS)["stages"]


def test_every_organ_runs_in_one_path():
    stages = _run(LAUNDERED + OPPOSE)
    assert stages["scope"]["derived"] is True
    assert stages["roots"]["collapsed"] == 4
    assert "unresolved" in stages["evaluation"] and "resolved" in stages["evaluation"]


def test_the_pipeline_refuses_a_supplied_scope():
    with pytest.raises(ScopeSuppliedError):
        derive_scope([{"id": "loc-1", "status": "searched"}], scope=["anything"])


def test_presence_claim_the_laundered_majority_stops_winning():
    ev = _run(LAUNDERED + OPPOSE, "presence")["evaluation"]
    assert ev["unresolved"]["conclusion"] == "supported"
    assert ev["resolved"]["conclusion"] == "not_established"
    assert ev["conclusionChanged"] is True


# ---- the boundary, tested from BOTH sides ----------------------------------

@pytest.mark.parametrize("records,expected_after", [
    # opposing evidence that cannot be attributed stops refuting the absence
    ([{"id": "ORPH", "side": "oppose", "rootId": "X"}], "absent_within_declared_scope"),
    ([{"id": "CYC1", "side": "oppose", "rootId": "Y"}], "absent_within_declared_scope"),
    ([{"id": "ORPH", "side": "oppose", "rootId": "X"},
      {"id": "A", "side": "support", "rootId": "A"}], "absent_within_declared_scope"),
])
def test_absence_flips_when_resolution_removes_every_opposing_root(records, expected_after):
    """The side of the boundary the original test set missed entirely."""
    ev = _run(records, "absence")["evaluation"]
    assert ev["unresolved"]["conclusion"] == "present"
    assert ev["resolved"]["conclusion"] == expected_after
    assert ev["conclusionChanged"] is True


@pytest.mark.parametrize("records", [
    LAUNDERED + OPPOSE,                                                    # a real opposing root survives
    [{"id": f"C{i}", "side": "oppose", "rootId": f"S{i}"} for i in range(1, 6)],   # laundered, but SRC-0 is real
    [{"id": f"C{i}", "side": "oppose", "rootId": f"S{i}"} for i in range(1, 3)]
        + [{"id": "ORPH", "side": "oppose", "rootId": "X"}],               # one survives, one refused
])
def test_absence_holds_while_any_opposing_root_survives(records):
    """The other side. Collapsing five opposing roots to one leaves the verdict
    alone, because one genuine counterexample already refutes an absence claim
    and five do not refute it harder."""
    ev = _run(records, "absence")["evaluation"]
    assert ev["resolved"]["opposingRoots"] >= 1
    assert ev["conclusionChanged"] is False


def test_the_rule_is_existence_not_count():
    """States the finding as a property rather than leaving it to the reader:
    the absence verdict is a function of whether any opposing root survives."""
    survives = _run(LAUNDERED + OPPOSE, "absence")["evaluation"]
    none_survive = _run([{"id": "ORPH", "side": "oppose", "rootId": "X"}], "absence")["evaluation"]
    assert survives["resolved"]["opposingRoots"] > 0 and not survives["conclusionChanged"]
    assert none_survive["resolved"]["opposingRoots"] == 0 and none_survive["conclusionChanged"]


def test_the_margin_moves_even_when_the_verdict_does_not():
    ev = _run(LAUNDERED + OPPOSE, "absence")["evaluation"]
    assert ev["unresolved"]["supportingRoots"] == 5
    assert ev["resolved"]["supportingRoots"] == 1
    assert ev["conclusionChanged"] is False
