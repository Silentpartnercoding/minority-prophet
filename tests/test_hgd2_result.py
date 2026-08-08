import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "hgd2-v1"


class Hgd2ResultTests(unittest.TestCase):
    def test_receipt_binds_reproduced_outputs(self):
        receipt = json.loads((RESULTS / "receipt.json").read_text())
        for name, metadata in receipt["outputs"].items():
            actual = hashlib.sha256((RESULTS / name).read_bytes()).hexdigest()
            self.assertEqual(actual, metadata["sha256"])
        self.assertTrue(receipt["scientific_output_byte_identical"])
        self.assertEqual(receipt["verdict"], "rejected")

    def test_result_preserves_passes_and_failures(self):
        result = json.loads((RESULTS / "result.json").read_text())
        expected = {
            "HGD-2a": True, "HGD-2b": True, "HGD-2c": True,
            "HGD-2d": False, "HGD-2e": False, "HGD-2f": True,
            "HGD-2g": True, "primary_claim": False,
        }
        self.assertEqual(result["hypotheses"], expected)
        self.assertEqual(result["software"]["structure"]["confirmatory_records"], 36)


if __name__ == "__main__":
    unittest.main()
