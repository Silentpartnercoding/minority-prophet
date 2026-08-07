import json
import unittest
from pathlib import Path

from knowledge_ledger import evaluate_transaction, verify_content_digest
from scripts.run_knowledge_transaction import render_transmission


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "research" / "knowledge-ledger"
REFERENCE_INPUT = PROGRAM / "interoperability" / "reference-input.json"


class KnowledgeLedgerProgramTests(unittest.TestCase):
    def test_every_experiment_is_seeded_with_required_fields(self):
        registry = json.loads((PROGRAM / "EXPERIMENT-REGISTRY.json").read_text())
        experiments = registry["experiments"]
        self.assertEqual(
            [experiment["id"] for experiment in experiments],
            [f"KL-{index:03d}" for index in range(12)],
        )
        for experiment in experiments:
            for field in ("realm", "question", "null", "target", "primaryEndpoint", "firstGate"):
                self.assertTrue(experiment[field])

    def load_reference_input(self):
        return json.loads(REFERENCE_INPUT.read_text())

    def test_incomplete_search_cannot_become_absence(self):
        result = evaluate_transaction(self.load_reference_input())
        self.assertEqual(result["conclusion"], "not_established")
        self.assertFalse(result["search"]["complete"])
        self.assertEqual(result["evidence"]["records"], 4)
        self.assertEqual(result["evidence"]["distinctRoots"], 2)
        self.assertEqual(result["evidence"]["repeatedRecordsCollapsed"], 2)
        self.assertTrue(verify_content_digest(result))

    def test_digest_rejects_mutated_receipt(self):
        result = evaluate_transaction(self.load_reference_input())
        result["conclusion"] = "absent_within_declared_scope"
        self.assertFalse(verify_content_digest(result))

    def test_human_transmission_preserves_claim_limits(self):
        result = evaluate_transaction(self.load_reference_input())
        transmission = render_transmission(result)
        self.assertIn("Not established", transmission)
        self.assertIn(result["contentDigest"], transmission)
        self.assertIn("JSON receipt is authoritative", transmission)
        self.assertNotIn("proved absent", transmission.lower())

    def test_complete_search_permits_only_bounded_absence(self):
        payload = self.load_reference_input()
        for location in payload["searchLedger"]["locations"]:
            location["status"] = "searched"
        result = evaluate_transaction(payload)
        self.assertEqual(result["conclusion"], "absent_within_declared_scope")
        self.assertIn("declared search space", result["limits"][1])

    def test_copy_multiplication_is_invariant(self):
        payload = self.load_reference_input()
        baseline = evaluate_transaction(payload)
        payload["evidenceLedger"]["records"].extend(
            {"id": f"copy-{index}", "rootId": "scanner-family-1", "side": "support"}
            for index in range(1000)
        )
        multiplied = evaluate_transaction(payload)
        self.assertEqual(multiplied["evidence"]["distinctRoots"], baseline["evidence"]["distinctRoots"])
        self.assertEqual(multiplied["evidence"]["margin"], baseline["evidence"]["margin"])
        self.assertEqual(multiplied["conclusion"], baseline["conclusion"])

    def test_one_root_cannot_cross_sides(self):
        payload = self.load_reference_input()
        payload["evidenceLedger"]["records"].append(
            {"id": "contradiction", "rootId": "scanner-family-1", "side": "oppose"}
        )
        with self.assertRaises(ValueError):
            evaluate_transaction(payload)

    def test_materialized_experiment_seeds_are_explicitly_incomplete(self):
        for index in range(12):
            directory = PROGRAM / "experiments" / f"KL-{index:03d}"
            status = json.loads((directory / "STATUS.json").read_text())
            preregistration = json.loads((directory / "preregistration.json").read_text())
            self.assertEqual(status["state"], "seeded")
            self.assertEqual(preregistration["status"], "incomplete-seed")
            self.assertTrue(status["nextGate"])


if __name__ == "__main__":
    unittest.main()
