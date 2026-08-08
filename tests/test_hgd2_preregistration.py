import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Hgd2PreregistrationTests(unittest.TestCase):
    def test_protocol_freezes_two_domains_and_base_rate_aware_endpoints(self):
        protocol = (ROOT / "experiments" / "HGD-2-PREREGISTRATION.md").read_text()
        for required in (
            "not rewrite HGD-1",
            "shift `0`",
            "`-20`, `-10`",
            "NIST SARD test suite 101",
            "19b7059d067c093d078c6b34d1ec669ccd648aa5b8507ca3fb49d58324bb802b",
            "compiler frontend",
            "Flawfinder",
            "lexical rules",
            "false_negative",
            "false_positive",
            "stale_replay",
            "seed is `20260810`",
            "`10,000` resamples",
            "HGD-2a",
            "HGD-2g",
            "Structural-feasibility amendment",
            "paired union of suites 100 and 101",
            "423f20e8ead850bf64cd93cd4a73dc1161d7b5bb6036328e16fc32e27d09f0d1",
            "Pair-split feasibility correction",
            "20 confirmatory pairs",
        ):
            self.assertIn(required, protocol)

    def test_protocol_forbids_abstention_only_win(self):
        protocol = (ROOT / "experiments" / "HGD-2-PREREGISTRATION.md").read_text()
        self.assertIn("untouched controls prevent abstention-only success", protocol)
        self.assertIn("answers at least 50%", protocol)

    def test_source_commitment_precedes_content_inspection(self):
        manifest = json.loads(
            (ROOT / "experiments" / "hgd2" / "source-manifest.json").read_text()
        )
        sard = manifest["sources"]["nistSard101"]
        self.assertEqual(
            sard["sha256"],
            "19b7059d067c093d078c6b34d1ec669ccd648aa5b8507ca3fb49d58324bb802b",
        )
        self.assertIn("detector execution", manifest["inspectionBoundary"]["notPerformedBeforeThisCommit"])


if __name__ == "__main__":
    unittest.main()
