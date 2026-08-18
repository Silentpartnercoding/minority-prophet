"""CE-14 — universal claims, the counting aggregator, and the flip-budget gate.

These tests pin a DIVERGENCE that is currently unrepaired in `root_vote`, and a
presentation gate that is repaired. If someone fixes the aggregator, the first
test fails loudly and `formal/COUNTEREXAMPLES.md` must be updated with it. A
regression test that silently keeps passing through a repair would let the
ledger drift away from the code, which is the defect CLAIMS.md C6 records three
instances of.
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, pathlib.Path(__file__).resolve().parents[1].as_posix())

from audit.ce14_asymmetric_claims import counting_path, ledger_path  # noqa: E402
from knowledge_ledger.presentation import reversal_metrics  # noqa: E402
from knowledge_ledger.transaction import evaluate_transaction  # noqa: E402

FIXTURES = (pathlib.Path(__file__).resolve().parents[1]
            / "research/knowledge-ledger/experiments/KL-000/fixtures")


def test_ce14_the_two_verdict_paths_still_disagree():
    """The witness itself. Delete this only together with the ledger entry."""
    counted = counting_path()
    ledger = ledger_path()
    assert counted.verdict.value == "true"
    assert ledger["conclusion"] == "present"
    assert len(ledger["evidence"]["opposingRoots"]) == 1


def test_ce14_immunity_is_advertised_on_the_wrong_side():
    """`immunity_applicable` is the absence of a guarantee, not a correctness
    claim -- but it is True here, beside a verdict a counterexample refutes."""
    counted = counting_path()
    assert counted.immunity_applicable is True
    assert counted.attested_margin == counted.margin == 998


def test_ce14_copy_collapse_cannot_reach_an_absence_conclusion():
    """20 copies of one opposing root collapse to one root and change nothing.

    This is the scope statement, not a defect: the absence rule never reads the
    margin, so the repository's copy-discounting mechanism is inert here.
    """
    one = ledger_path(copies=1)
    twenty = ledger_path(copies=20)
    assert one["conclusion"] == twenty["conclusion"] == "present"
    assert one["evidence"]["repeatedRecordsCollapsed"] == 0
    assert twenty["evidence"]["repeatedRecordsCollapsed"] == 19
    assert (one["evidence"]["opposingRoots"]
            == twenty["evidence"]["opposingRoots"] == ["counterexample"])


def test_ce14_flip_budget_is_marked_inapplicable_on_absence_verdicts():
    metrics = reversal_metrics(ledger_path())
    assert metrics["budgetApplies"] is False
    assert metrics["decidedByRootCount"] == 1
    assert "CE-14" in metrics["note"]
    # The number is still returned. Suppressing a derivable value hides the
    # defect rather than correcting it.
    assert metrics["flipBudget"] == 998


def test_ce14_presence_claims_are_untouched_by_the_gate():
    """The margin does decide a presence claim, so its budget is its budget."""
    for rel in ("v1.2.0/c11-canonical-digest.json", "v1.2.0/c12-margin-sign.json"):
        doc = json.loads((FIXTURES / rel).read_text())
        receipt = evaluate_transaction(doc["input"])
        assert receipt["claim"]["type"] == "presence", rel
        metrics = reversal_metrics(receipt)
        assert metrics["budgetApplies"] is True, rel
        assert metrics["decidedByRootCount"] is None, rel
        assert "CE-14" not in metrics["note"], rel


def test_ce14_gate_covers_every_absence_conclusion_not_only_present():
    """Enumerated, not sampled: the absence rule has three reachable
    conclusions and the margin decides none of them."""
    seen = {}
    for coverage, opposing in (("searched", 0), ("not_searched", 0), ("searched", 1)):
        records = [{"rootId": f"conf-{i}", "side": "support"} for i in range(5)]
        records += [{"rootId": f"opp-{k}", "side": "oppose"} for k in range(opposing)]
        receipt = evaluate_transaction({
            "transactionId": "ce-14-enum",
            "claim": {"id": "u", "type": "absence"},
            "searchLedger": {"locations": [{"id": "s", "status": coverage}]},
            "evidenceLedger": {"records": records},
        })
        metrics = reversal_metrics(receipt)
        seen[receipt["conclusion"]] = metrics["budgetApplies"]
    assert seen == {
        "absent_within_declared_scope": False,
        "not_established": False,
        "present": False,
    }


# --- the vector file is a specification, so its structure is what can be pinned ---

VECTORS = json.loads(
    (pathlib.Path(__file__).resolve().parents[1]
     / "experiments/asymmetric-claims/false-candidate-vectors.json").read_text()
)


def test_vector_file_does_not_claim_to_be_a_measurement():
    """It states its own status. A file that quietly looked like a result is
    the failure mode CONTRIBUTING.md's lane rules exist to prevent."""
    assert VECTORS["status"] == "vectors-registered-no-implementation-under-test"
    assert "not a measurement" in VECTORS["statusNote"]


def test_only_evidence_layer_decidable_faults_are_scored():
    """Scope, pinned. A vector for a subsystem that does not exist cannot pass
    or fail, so it is not a test. The four numerical classes from the original
    RH spec are recorded as dropped, with their reason, rather than deleted."""
    assert sorted(v["faultClass"] for v in VECTORS["vectors"]) == ["FP5", "FP6", "FP7"]
    dropped = [c["faultClass"] for c in VECTORS["droppedClasses"]["classes"]]
    assert sorted(dropped) == ["FP1", "FP2", "FP3", "FP4"]
    assert VECTORS["droppedClasses"]["whatSurvivedThem"]


def test_no_vector_requires_recomputation_to_decide():
    """Every surviving vector is decidable from the report alone."""
    for vector in VECTORS["vectors"]:
        assert vector["observableToEvidenceLayer"], vector["id"]
        assert "detectableWithoutRecomputation" not in vector, vector["id"]


def test_only_fabrication_is_refused_before_verification():
    """The distinction that matters, and the one this test originally got wrong.

    Duplication is observable, but a duplicated candidate may be perfectly
    correct -- there is only one of it. Refusing on duplication alone discards a
    genuine lone counterexample, which is the failure this project exists to
    prevent. So observability does not imply refusal; only fabrication does.
    """
    for vector in VECTORS["vectors"]:
        expected = "REFUSE" if vector["faultKind"] == "fabrication" else "ESCALATE"
        assert vector["expected"]["beforeVerification"] == expected, vector["id"]


def test_duplication_is_never_refused_for_being_duplicated():
    for vector in VECTORS["vectors"]:
        if vector["faultKind"] == "duplication":
            assert vector["expected"]["beforeVerification"] != "REFUSE", vector["id"]
            assert vector["requiredReceiptProperty"]["distinctOpposingRoots"] == 1


def test_negative_controls_exist_and_admit():
    """Without an ADMIT case the file is satisfied by refusing everything."""
    controls = VECTORS["negativeControls"]
    assert controls, "a refuse-everything layer must be able to fail this suite"
    assert any(c["expected"]["afterVerification"] == "ADMIT" for c in controls)


def test_fp5_is_recorded_as_inert_on_the_conclusion():
    """The one place the vector file must agree with CE-14's measurement."""
    fp5 = next(v for v in VECTORS["vectors"] if v["faultClass"] == "FP5")
    assert fp5["inertOnTheConclusion"] is True
    assert fp5["requiredReceiptProperty"]["distinctOpposingRoots"] == 1
    tp2 = next(c for c in VECTORS["negativeControls"]
               if c["id"] == "TP2-three-independent-reproductions")
    assert tp2["requiredReceiptProperty"]["distinctOpposingRoots"] == 3


def test_pass_condition_states_no_threshold():
    condition = VECTORS["passCondition"]
    assert "No threshold, no percentage, no tolerance." in condition
