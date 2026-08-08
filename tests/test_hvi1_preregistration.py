import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Hvi1PreregistrationTests(unittest.TestCase):
    def test_protocol_freezes_confirmatory_configuration(self):
        protocol = (ROOT / "experiments" / "HVI-1-PREREGISTRATION.md").read_text()
        for required in (
            "seeds `401–420`",
            "`250` base worlds per seed",
            "seed `20260807`",
            "`10,000` resamples",
            "HVI-1a",
            "HVI-1f",
            "Unknown or conflicting controller provenance produces `ESCALATE`",
        ):
            self.assertIn(required, protocol)

    def test_schema_is_closed_and_does_not_grant_authority(self):
        schema = json.loads(
            (ROOT / "experiments" / "hvi1" / "independence-receipt.schema.json").read_text()
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["schema"]["const"],
                         "minority-prophet.independence-receipt.v1")
        self.assertNotIn("authorization", schema["properties"])

    def test_conformance_vectors_preserve_uncertainty_and_collapse_aliases(self):
        packet = json.loads(
            (ROOT / "experiments" / "hvi1" / "conformance-vectors.json").read_text()
        )
        vectors = {vector["id"]: vector for vector in packet["vectors"]}
        self.assertEqual(vectors["aliases-one-controller"]["expected"]["rootMass"], 1)
        self.assertEqual(vectors["self-verified"]["expected"]["rootMass"], 0)
        self.assertEqual(vectors["unknown-control"]["expected"]["decision"], "ESCALATE")


if __name__ == "__main__":
    unittest.main()
