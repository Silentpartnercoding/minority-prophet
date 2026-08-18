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
from dataclasses import dataclass

import pytest

sys.path.insert(0, pathlib.Path(__file__).resolve().parents[1].as_posix())

from audit.ce14_asymmetric_claims import counting_path, ledger_path  # noqa: E402
from knowledge_ledger.presentation import reversal_metrics  # noqa: E402
from knowledge_ledger.transaction import evaluate_transaction  # noqa: E402

@dataclass
class _Claim:
    value: bool
    root_id: str | None
    independence_basis: str | None = None


def _universal_claims():
    """999 confirmations and one attested counterexample -- the CE-14 witness."""
    for i in range(999):
        yield _Claim(True, f"conf-{i}", "attested")
    yield _Claim(False, "counterexample", "attested")


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


# --- CE-14 repair A: the counting aggregator refuses universal claims --------

def test_universal_claims_are_refused_by_the_counting_aggregator():
    from aggregation.root_vote import UniversalClaimError, verdict

    claims = list(_universal_claims())
    with pytest.raises(UniversalClaimError) as raised:
        verdict(claims, claim_shape="universal")
    message = str(raised.value)
    assert "CE-14" in message
    assert "evaluate_transaction_v2" in message, "the refusal must name the tool that works"


def test_the_refusal_happens_before_any_counting():
    """A guard that runs after the work is a report, not a fence. Conflicting
    roots would otherwise be raised first and mask the refusal."""
    from aggregation.root_vote import UniversalClaimError, verdict

    conflicting = [_Claim(True, "r"), _Claim(False, "r")]
    with pytest.raises(UniversalClaimError):
        verdict(conflicting, claim_shape="universal")


def test_symmetric_claims_are_unchanged_by_the_fence():
    """Every existing caller asks a symmetric question and must be unaffected."""
    from aggregation.root_vote import verdict

    claims = list(_universal_claims())
    assert verdict(claims).verdict.value == "true"
    assert verdict(claims, claim_shape="symmetric").verdict.value == "true"
    assert verdict(claims).margin == verdict(claims, claim_shape="symmetric").margin


def test_the_fence_is_a_declaration_not_a_detector():
    """Pinned because it is the honest limit of repair A, and a later reader
    must not mistake it for classification. The identical claim iterable that
    raises when declared universal returns a verdict when declared symmetric --
    nothing in the claims themselves says which question is being asked."""
    from aggregation.root_vote import UniversalClaimError, verdict

    claims = list(_universal_claims())
    with pytest.raises(UniversalClaimError):
        verdict(claims, claim_shape="universal")
    assert verdict(claims, claim_shape="symmetric").verdict.value == "true"


def test_existential_claims_are_refused_in_the_mirror_direction():
    from aggregation.root_vote import AsymmetricClaimError, verdict

    with pytest.raises(AsymmetricClaimError) as raised:
        verdict(list(_universal_claims()), claim_shape="existential")
    assert "absence of evidence" in str(raised.value)


def test_the_ledger_presence_branch_counts_pinned_as_an_open_question():
    """Measured, not asserted. One verified find against 999 unsuccessful
    searches returns not_established. Whether that is wrong depends on what
    'oppose' means for a presence claim -- positive evidence of absence, or an
    unsuccessful search. The evaluator does not distinguish them, and that
    ambiguity is the finding. Pinned so a later semantic decision is a visible
    change, not a silent one.
    """
    from knowledge_ledger.transaction_v2 import evaluate_transaction_v2

    def presence(supporting, opposing):
        records = [{"rootId": f"s{i}", "side": "support"} for i in range(supporting)]
        records += [{"rootId": f"o{i}", "side": "oppose"} for i in range(opposing)]
        return evaluate_transaction_v2({
            "transactionId": "mirror",
            "claim": {"id": "c", "type": "presence"},
            "searchLedger": {"locations": [{"id": "L", "status": "searched"}]},
            "evidenceLedger": {"records": records},
        })["conclusion"]

    assert presence(1, 0) == "supported"
    assert presence(1, 2) == "not_established"
    assert presence(1, 999) == "not_established"


# --- CE-14 repair B: the compiled rule, implemented ------------------------

def test_universal_one_decisive_root_settles_it_whatever_the_other_side():
    """AC1, in Python. 999 confirmations do not outweigh one counterexample."""
    from aggregation.root_vote import AsymmetricOutcome, asymmetric_verdict

    result = asymmetric_verdict(list(_universal_claims()), claim_shape="universal")
    assert result.outcome is AsymmetricOutcome.REFUTED
    assert result.decisive_roots == frozenset({"counterexample"})
    assert result.ignored_root_count == 999
    assert result.roots_to_reverse == 1


def test_the_outcome_does_not_read_the_other_side():
    """AC2, in Python: vary the confirming side arbitrarily, outcome is fixed."""
    from aggregation.root_vote import asymmetric_verdict

    outcomes = set()
    for confirmations in (0, 1, 50, 999):
        claims = [_Claim(True, f"conf-{i}", "attested") for i in range(confirmations)]
        claims.append(_Claim(False, "counterexample", "attested"))
        outcomes.add(asymmetric_verdict(claims, claim_shape="universal").outcome)
    assert len(outcomes) == 1


def test_no_margin_or_flip_budget_is_reported_for_an_asymmetric_claim():
    """AC2's consequence. Reporting a margin here is the CE-14 misreading; the
    field does not exist rather than existing and being ignored."""
    from aggregation.root_vote import AsymmetricVerdict, asymmetric_verdict

    result = asymmetric_verdict(list(_universal_claims()), claim_shape="universal")
    fields = set(AsymmetricVerdict.__dataclass_fields__)
    assert not fields & {"margin", "flip_budget", "conversions_to_reverse"}
    assert not hasattr(result, "margin")


def test_not_refuted_is_never_presented_as_proof():
    """The RH lesson, enforced: no counterexample found is not a proof, because
    this function has no search-coverage input at all."""
    from aggregation.root_vote import AsymmetricOutcome, asymmetric_verdict

    result = asymmetric_verdict([_Claim(True, "conf", "attested")],
                                claim_shape="universal")
    assert result.outcome is AsymmetricOutcome.NOT_REFUTED
    assert any("NOT a proof" in note for note in result.notes)
    assert result.roots_to_reverse == 1


def test_existential_mirror_one_find_beats_any_number_of_empty_searches():
    from aggregation.root_vote import AsymmetricOutcome, asymmetric_verdict

    claims = [_Claim(True, "find", "attested")]
    claims += [_Claim(False, f"searched-{i}", "attested") for i in range(999)]
    result = asymmetric_verdict(claims, claim_shape="existential")
    assert result.outcome is AsymmetricOutcome.ESTABLISHED
    assert result.decisive_roots == frozenset({"find"})
    assert result.ignored_root_count == 999


def test_preconditions_fail_closed_and_say_no_theorem_covers_them():
    """Side separation and attribution are hypotheses of the compiled rule.
    Where they fail the implementation must not invent an answer."""
    from aggregation.root_vote import AsymmetricOutcome, asymmetric_verdict

    conflicting = asymmetric_verdict([_Claim(True, "r"), _Claim(False, "r")],
                                     claim_shape="universal")
    assert conflicting.outcome is AsymmetricOutcome.INDETERMINATE
    assert any("R2" in note for note in conflicting.notes)

    # An unattributed claim could BE the decisive root, so a negative outcome
    # must be withheld -- but it cannot undo one that already exists.
    withheld = asymmetric_verdict([_Claim(True, "conf", "attested"), _Claim(False, None)],
                                  claim_shape="universal")
    assert withheld.outcome is AsymmetricOutcome.INDETERMINATE

    already = asymmetric_verdict([_Claim(False, "ce", "attested"), _Claim(True, None)],
                                 claim_shape="universal")
    assert already.outcome is AsymmetricOutcome.REFUTED


def test_symmetric_shape_is_rejected_by_the_asymmetric_function():
    """The fence points both ways; neither function silently answers the
    other's question."""
    from aggregation.root_vote import asymmetric_verdict

    with pytest.raises(ValueError, match="root_vote.verdict"):
        asymmetric_verdict([], claim_shape="symmetric")


# --- Python must agree with the compiled Lean on the pinned worlds ---------

def test_python_agrees_with_lean_on_the_ce14_worlds():
    """AC4 and AC5 are proved about two explicit flat worlds. The same worlds,
    encoded here, must produce the same answers -- otherwise the compiled rule
    and the shipped code have drifted apart and the ledger's lean_theorem
    reference is misleading.

        AC4  flatWorld [true, true, true, false]  -> F=one,  universalF=refuted
        AC5  flatWorld [true, false, false, false] -> F=zero, existentialF=established
    """
    from aggregation.root_vote import AsymmetricOutcome, Verdict, asymmetric_verdict, verdict

    ce14 = [_Claim(v, f"root-{i}") for i, v in enumerate([True, True, True, False])]
    assert verdict(ce14).verdict is Verdict.TRUE
    assert verdict(ce14).margin == 2
    assert asymmetric_verdict(ce14, claim_shape="universal").outcome \
        is AsymmetricOutcome.REFUTED

    mirror = [_Claim(v, f"root-{i}") for i, v in enumerate([True, False, False, False])]
    assert verdict(mirror).verdict is Verdict.FALSE
    assert verdict(mirror).margin == -2
    assert asymmetric_verdict(mirror, claim_shape="existential").outcome \
        is AsymmetricOutcome.ESTABLISHED
