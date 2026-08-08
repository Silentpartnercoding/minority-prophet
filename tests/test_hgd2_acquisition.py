import hashlib
import json
import unittest
from pathlib import Path

from experiments.hgd2.acquire_software_evidence import BAD_ROOT, GOOD_ROOT, selected_pairs

ROOT = Path(__file__).resolve().parents[1]


class Hgd2AcquisitionTests(unittest.TestCase):
    @unittest.skipUnless(GOOD_ROOT.exists() and BAD_ROOT.exists(), "frozen source archives not local")
    def test_reciprocal_candidate_pairs_and_pair_safe_split(self):
        pairs, development = selected_pairs()
        self.assertGreater(len(pairs), 20)
        for good, bad in pairs:
            self.assertEqual(good["state"], "good")
            self.assertEqual(bad["state"], "bad")
            self.assertEqual(good["cwe"], bad["cwe"])
            self.assertEqual(good["case"] in development, bad["case"] in development)
        self.assertEqual(sum(good["case"] not in development for good, _ in pairs), 20)

    def test_committed_detector_packet_is_bound_and_balanced(self):
        path = ROOT / "experiments" / "hgd2" / "software-detector-records.json"
        packet = json.loads(path.read_text())
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            "096a3a04adb7b4eac2b53fb1b6df5243247b1a5f8b5291a63f83a9711b7c694c",
        )
        confirmatory = [r for r in packet["records"] if r["split"] == "confirmatory"]
        self.assertEqual(len(confirmatory), 36)
        self.assertEqual(sum(r["truth"] == 0 for r in confirmatory), 18)
        self.assertEqual(sum(r["truth"] == 1 for r in confirmatory), 18)


if __name__ == "__main__":
    unittest.main()
