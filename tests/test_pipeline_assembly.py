"""What the assembled pipeline reveals that no organ showed alone.

The composition finding: root resolution changes the CONCLUSION for presence
claims and never for absence claims. The absence rule short-circuits on the
existence of opposing evidence and never consults the root count, so collapsing
five laundered roots into one moves the margin and leaves the verdict alone.

That matters because KL-000 and KL-001 are absence experiments. The organ that
was built to stop laundered evidence winning does not change the answer on the
claim type this programme has studied most.
"""

import pytest

from knowledge_ledger.pipeline import ScopeSuppliedError, assemble, derive_scope

DOCS = {
    "SRC-0": {"isOriginal": True},
    **{f"C{i}": {"derivedFrom": "SRC-0"} for i in range(1, 6)},
    "A": {"isOriginal": True}, "B": {"isOriginal": True}, "ORPH": {},
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
    """The organ's actual payoff. Flips if resolution stops collapsing."""
    ev = _run(LAUNDERED + OPPOSE, "presence")["evaluation"]
    assert ev["unresolved"]["conclusion"] == "supported"
    assert ev["resolved"]["conclusion"] == "not_established"
    assert ev["conclusionChanged"] is True


@pytest.mark.parametrize("records", [LAUNDERED + OPPOSE, LAUNDERED,
                                     [{"id": f"C{i}", "side": "oppose", "rootId": f"S{i}"} for i in range(1, 6)],
                                     [{"id": "ORPH", "side": "support", "rootId": "X"}]])
def test_absence_claims_never_change_conclusion_and_that_is_the_finding(records):
    """Recorded rather than discovered later: for absence claims the conclusion
    is a function of whether opposing evidence EXISTS, not of how many roots
    there are. Root resolution therefore moves the margin and not the verdict.

    Flips if the absence rule ever starts consulting root counts -- at which
    point this test should be deleted and the finding rewritten, not patched."""
    ev = _run(records, "absence")["evaluation"]
    assert ev["conclusionChanged"] is False


def test_the_margin_does_move_even_when_the_verdict_does_not():
    """So the organ is not inert on absence claims -- it is invisible to the
    conclusion while still changing what the receipt reports."""
    ev = _run(LAUNDERED + OPPOSE, "absence")["evaluation"]
    assert ev["unresolved"]["supportingRoots"] == 5
    assert ev["resolved"]["supportingRoots"] == 1
    assert ev["conclusionChanged"] is False
