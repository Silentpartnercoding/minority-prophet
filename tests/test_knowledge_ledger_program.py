import json
import tempfile
import unittest
from pathlib import Path

from knowledge_ledger import evaluate_transaction, verify_content_digest


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "research" / "knowledge-ledger"


class KnowledgeLedgerProgramTests(unittest.TestCase):
    def test_every_kernel_is_seeded_with_required_fields(self):
        registry = json.loads((PROGRAM / "kernels.json").read_text())
        kernels = registry["kernels"]
        self.assertEqual([kernel["id"] for kernel in kernels], [f"KL-{index:03d}" for index in range(12)])
        for kernel in kernels:
            for field in ("realm", "question", "null", "target", "primaryEndpoint", "firstGate"):
                self.assertTrue(kernel[field])

    def test_incomplete_search_cannot_become_absence(self):
        payload = json.loads((PROGRAM / "first-transaction" / "input.json").read_text())
        result = evaluate_transaction(payload)
        self.assertEqual(result["conclusion"], "not_established")
        self.assertFalse(result["search"]["complete"])
        self.assertEqual(result["evidence"]["records"], 4)
        self.assertEqual(result["evidence"]["distinctRoots"], 2)
        self.assertEqual(result["evidence"]["repeatedRecordsCollapsed"], 2)
        self.assertTrue(verify_content_digest(result))

    def test_digest_rejects_mutated_receipt(self):
        payload = json.loads((PROGRAM / "first-transaction" / "input.json").read_text())
        result = evaluate_transaction(payload)
        result["conclusion"] = "absent_within_declared_scope"
        self.assertFalse(verify_content_digest(result))

    def test_complete_search_permits_only_bounded_absence(self):
        payload = json.loads((PROGRAM / "first-transaction" / "input.json").read_text())
        for location in payload["searchLedger"]["locations"]:
            location["status"] = "searched"
        result = evaluate_transaction(payload)
        self.assertEqual(result["conclusion"], "absent_within_declared_scope")
        self.assertIn("declared search space", result["limits"][1])

    def test_copy_multiplication_is_invariant(self):
        payload = json.loads((PROGRAM / "first-transaction" / "input.json").read_text())
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
        payload = json.loads((PROGRAM / "first-transaction" / "input.json").read_text())
        payload["evidenceLedger"]["records"].append(
            {"id": "contradiction", "rootId": "scanner-family-1", "side": "oppose"}
        )
        with self.assertRaises(ValueError):
            evaluate_transaction(payload)

    def test_materialized_kernel_seeds_are_explicitly_incomplete(self):
        for index in range(12):
            directory = PROGRAM / "kernels" / f"KL-{index:03d}"
            status = json.loads((directory / "STATUS.json").read_text())
            preregistration = json.loads((directory / "preregistration.json").read_text())
            self.assertEqual(status["state"], "seeded")
            self.assertEqual(preregistration["status"], "incomplete-seed")
            self.assertTrue(status["nextGate"])


if __name__ == "__main__":
    unittest.main()
