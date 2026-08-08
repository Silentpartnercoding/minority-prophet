import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Hgd1PreregistrationTests(unittest.TestCase):
    def test_protocol_freezes_synthetic_and_observational_tracks(self):
        protocol = (ROOT / "experiments" / "HGD-1-PREREGISTRATION.md").read_text()
        for required in (
            "seeds `701–720`",
            "`250` base worlds per seed",
            "seed `20260809`",
            "`10,000` world-clustered resamples",
            "daily_88101_2025.zip",
            "HGD-1a",
            "HGD-1g",
            "cannot discover an undisclosed common cause",
            "field is three raw sensor streams",
        ):
            self.assertIn(required, protocol)

    def test_dependency_schema_is_closed_and_authority_free(self):
        schema = json.loads(
            (ROOT / "experiments" / "hgd1" / "dependency-receipt.schema.json").read_text()
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertNotIn("authorization", schema["properties"])
        component = schema["properties"]["components"]["items"]
        self.assertFalse(component["additionalProperties"])
        self.assertEqual(component["properties"]["sharedWeightLower"]["minimum"], 0)
        self.assertEqual(component["properties"]["sharedWeightUpper"]["maximum"], 1)

    def test_vectors_preserve_extremes_and_uncertainty(self):
        packet = json.loads(
            (ROOT / "experiments" / "hgd1" / "conformance-vectors.json").read_text()
        )
        vectors = {item["id"]: item for item in packet["vectors"]}
        self.assertEqual(vectors["one-origin-eight-records"]["expected"]["massUpper"], 1)
        self.assertEqual(vectors["eight-independent-origins"]["expected"]["massLower"], 8)
        self.assertEqual(vectors["eight-half-shared"]["expected"], {
            "state": "ASSESS", "massLower": 3.8, "massUpper": 5.2
        })
        self.assertEqual(vectors["unknown-component"]["expected"]["state"], "ESCALATE")

    def test_source_manifest_preserves_frozen_archive_and_limit(self):
        manifest = json.loads(
            (ROOT / "experiments" / "hgd1" / "source-manifest.json").read_text()
        )
        self.assertEqual(
            manifest["archiveSha256"],
            "cc8cb80bcc0317705202d12a472918438b8bee60316f54777d6f748c58ac2661",
        )
        self.assertEqual(manifest["valueInspectionBeganAfterPublicCommit"], "350de0b")
        self.assertTrue(any("no per-row qualifier" in item for item in manifest["limitations"]))


if __name__ == "__main__":
    unittest.main()
