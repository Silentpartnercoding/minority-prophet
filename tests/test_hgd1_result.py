import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "hgd1-v1"


class Hgd1ResultTests(unittest.TestCase):
    def test_receipt_binds_all_outputs(self):
        receipt = json.loads((RESULTS / "receipt.json").read_text())
        for name, metadata in receipt["outputs"].items():
            actual = hashlib.sha256((RESULTS / name).read_bytes()).hexdigest()
            self.assertEqual(actual, metadata["sha256"])
        self.assertTrue(receipt["scientific_output_byte_identical"])
        self.assertEqual(receipt["verdict"], "rejected")

    def test_result_preserves_failed_primary_claim(self):
        result = json.loads((RESULTS / "result.json").read_text())
        self.assertFalse(result["hypotheses"]["HGD-1g"])
        self.assertFalse(result["hypotheses"]["primary_claim"])
        self.assertEqual(result["observational_structure"]["confirmatory_cases"], 50_978)


if __name__ == "__main__":
    unittest.main()
