"""SCH-005 — the receipt can now carry doubt, and v0.1 is untouched.

RESEARCH-DIRECTION.md has always specified that the evidence ledger records
unattributed evidence, uncertainty, declared shared dependencies and the reason
for abstention. v0.1 emits none of them, and the omission has a shape: everything
it emits expresses confidence, everything absent expresses doubt.

That blocks KL-011, whose claim is that protected fields survive crossing
systems. A receipt that cannot carry doubt could pass while establishing only
that confident claims survive.

v0.1 is pinned by SHA-256 in four KL-000 preregistrations, so it cannot be
edited. These tests check that it was not.
"""
import hashlib
import json
import pathlib
import unittest

from knowledge_ledger.transaction import evaluate_transaction, verify_content_digest
from knowledge_ledger.transaction_v2 import SCHEMA, evaluate_transaction_v2

REPO = pathlib.Path(__file__).resolve().parents[1]
KL000 = REPO / "research/knowledge-ledger/experiments/KL-000"


def payload(records, statuses=("searched",), claim_type="absence"):
    return {
        "schema": "minority-prophet.knowledge-transaction.v0.1",
        "transactionId": "t-1",
        "claim": {"type": claim_type, "statement": "x"},
        "searchLedger": {"locations": [
            {"id": f"l{i}", "status": s} for i, s in enumerate(statuses)]},
        "evidenceLedger": {"records": records},
    }


class V01IsUntouched(unittest.TestCase):
    def test_the_pinned_evaluator_hash_still_matches_every_registration(self):
        digest = hashlib.sha256(
            (REPO / "knowledge_ledger/transaction.py").read_bytes()).hexdigest()
        pinned = set()
        for path in KL000.glob("preregistration*.json"):
            doc = json.loads(path.read_text())
            if "evaluatorUnderTest" in doc:
                pinned.add(doc["evaluatorUnderTest"]["sha256"])
        self.assertTrue(pinned, "no registration pins the evaluator")
        self.assertEqual(pinned, {digest},
                         "v0.1 was modified; four registrations pin its hash")


class V02CarriesUncertainty(unittest.TestCase):
    def test_the_spec_fields_v01_omitted_are_present(self):
        r = evaluate_transaction_v2(payload([{"recordId": "a", "rootId": "r1",
                                              "side": "oppose"}]))
        self.assertIn("flipBudget", r["evidence"])
        self.assertIn("unattributedRecords", r["evidence"])
        self.assertIn("declaredSharedDependencies", r["evidence"])
        self.assertIn("uncertainty", r)
        self.assertIn("abstentionReason", r["uncertainty"])

    def test_unattributed_evidence_is_counted_not_dropped(self):
        """The difference between 'we found nothing' and 'we could not attribute
        what we found'."""
        r = evaluate_transaction_v2(payload([
            {"recordId": "a", "side": "oppose"},            # no rootId
            {"recordId": "b", "side": "oppose"},
        ]))
        self.assertEqual(r["evidence"]["unattributedRecords"], 2)
        self.assertEqual(r["evidence"]["distinctRoots"], 0)
        self.assertEqual(r["conclusion"], "absent_within_declared_scope",
                         "unattributed records join no side and move no margin")

    def test_abstention_reason_is_none_when_the_conclusion_is_decisive(self):
        """A field that is always populated distinguishes nothing."""
        decisive = evaluate_transaction_v2(payload([{"recordId": "a", "rootId": "r1",
                                                     "side": "oppose"}]))
        self.assertIsNone(decisive["uncertainty"]["abstentionReason"])
        abstained = evaluate_transaction_v2(payload([], statuses=("not_searched",)))
        self.assertEqual(abstained["uncertainty"]["abstentionReason"],
                         "incomplete_coverage")

    def test_shared_dependencies_break_side_separation(self):
        r = evaluate_transaction_v2(payload([
            {"recordId": "a", "rootId": "r1", "side": "oppose",
             "sharedDependencies": ["vendor-x"]},
        ]))
        self.assertEqual(r["evidence"]["declaredSharedDependencies"], ["vendor-x"])
        self.assertFalse(r["uncertainty"]["sideSeparationDeclared"])

    def test_both_attack_prices_are_reported(self):
        """Quoting either alone misstates the other (CE-03)."""
        r = evaluate_transaction_v2(payload(
            [{"recordId": f"s{i}", "rootId": f"s{i}", "side": "support"} for i in range(4)]
            + [{"recordId": "o", "rootId": "o1", "side": "oppose"}],
            claim_type="presence"))
        self.assertEqual(r["evidence"]["margin"], 3)
        self.assertEqual(r["evidence"]["flipBudget"], 3)
        self.assertEqual(r["evidence"]["conversionsToReverse"], 2)


class A2IsRegistered(unittest.TestCase):
    """Owner decision: presence does not require complete coverage.

    This is what v0.1 already does. The decision removes an ambiguity that let
    two conforming implementations diverge on 17.3% of receipts; it changes no
    behaviour, and these tests pin that agreement.
    """

    def test_presence_survives_incomplete_coverage(self):
        r = evaluate_transaction_v2(payload(
            [{"recordId": "a", "rootId": "r1", "side": "oppose"}],
            statuses=("searched", "not_searched")))
        self.assertEqual(r["conclusion"], "present")
        self.assertIsNone(r["uncertainty"]["abstentionReason"])
        self.assertEqual(r["uncertainty"]["unsearchedLocations"], 1,
                         "the doubt is reported even though the verdict stands")

    def test_absence_still_requires_complete_coverage(self):
        r = evaluate_transaction_v2(payload([], statuses=("searched", "not_searched")))
        self.assertEqual(r["conclusion"], "not_established")

    def test_v01_and_v02_agree_on_the_conclusion_for_every_shared_input(self):
        """The decision must not have changed a verdict anywhere."""
        cases = [
            ([], ("searched",)), ([], ("not_searched",)),
            ([{"recordId": "a", "rootId": "r1", "side": "oppose"}], ("searched",)),
            ([{"recordId": "a", "rootId": "r1", "side": "oppose"}], ("not_searched",)),
            ([{"recordId": "a", "rootId": "r1", "side": "support"}], ("searched",)),
        ]
        for records, statuses in cases:
            with self.subTest(records=len(records), statuses=statuses):
                self.assertEqual(
                    evaluate_transaction(payload(records, statuses))["conclusion"],
                    evaluate_transaction_v2(payload(records, statuses))["conclusion"])

    def test_v02_receipts_are_self_verifying(self):
        r = evaluate_transaction_v2(payload([{"recordId": "a", "rootId": "r1",
                                              "side": "oppose"}]))
        self.assertEqual(r["schema"], SCHEMA)
        self.assertTrue(verify_content_digest(r))


if __name__ == "__main__":
    unittest.main()
