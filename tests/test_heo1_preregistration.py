import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Heo1PreregistrationTests(unittest.TestCase):
    def test_protocol_freezes_causal_origin_experiment(self):
        protocol = (ROOT / "experiments" / "HEO-1-PREREGISTRATION.md").read_text()
        for required in (
            "seeds `501–520`", "`250` base worlds per seed",
            "seed `20260808`", "`10,000` resamples",
            "HEO-1a", "HEO-1f", "cannot discover an undisclosed common source",
        ):
            self.assertIn(required, protocol)

    def test_derivation_schema_is_closed_and_authority_free(self):
        schema = json.loads(
            (ROOT / "experiments" / "heo1" / "derivation-receipt.schema.json").read_text()
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertNotIn("authorization", schema["properties"])
        self.assertIn("model_transform", schema["properties"]["relationship"]["enum"])

    def test_vectors_distinguish_controller_from_origin_independence(self):
        packet = json.loads(
            (ROOT / "experiments" / "heo1" / "conformance-vectors.json").read_text()
        )
        vectors = {item["id"]: item for item in packet["vectors"]}
        self.assertEqual(vectors["one-origin-eight-controllers"]["expected"]["rootMass"], 1)
        self.assertEqual(vectors["eight-genuine-origins"]["expected"]["rootMass"], 8)
        self.assertEqual(vectors["unknown-origin"]["expected"]["state"], "ESCALATE")


if __name__ == "__main__":
    unittest.main()
