import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CanonicalRecordTests(unittest.TestCase):
    def test_every_canonical_manifest_binds_every_declared_artifact(self):
        manifests = sorted((ROOT / "results").glob("*.manifest.json"))
        self.assertGreaterEqual(len(manifests), 2)
        for manifest_path in manifests:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "canonical-derived-record")
            for artifact in manifest["artifacts"]:
                content = (ROOT / artifact["path"]).read_bytes()
                self.assertEqual(
                    hashlib.sha256(content).hexdigest(),
                    artifact["sha256"],
                    f"hash drift in {manifest_path.name}: {artifact['path']}",
                )

    def test_exp002_does_not_overclaim_mutable_source_replay(self):
        manifest_path = ROOT / "results" / "resolved-weather-v0.1.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertFalse(manifest["sourceBoundary"]["byteIdenticalSourceReplayClaimed"])

    def test_exp009_receipt_binds_preserved_outputs(self):
        receipt = json.loads(
            (ROOT / "results" / "exp009-v1" / "receipt.json").read_text()
        )
        self.assertTrue(receipt["scientific_output_byte_identical"])
        self.assertEqual(receipt["verdict"], "supported")
        for name, artifact in receipt["outputs"].items():
            content = (ROOT / "results" / "exp009-v1" / name).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), artifact["sha256"])

    def test_hvi1_receipt_binds_preserved_outputs(self):
        receipt = json.loads(
            (ROOT / "results" / "hvi1-v1" / "receipt.json").read_text()
        )
        result = json.loads(
            (ROOT / "results" / "hvi1-v1" / "result.json").read_text()
        )
        self.assertTrue(receipt["scientific_output_byte_identical"])
        self.assertTrue(result["hypotheses"]["primary_claim"])
        self.assertEqual(receipt["verdict"], "supported")
        for name, artifact in receipt["outputs"].items():
            content = (ROOT / "results" / "hvi1-v1" / name).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), artifact["sha256"])


if __name__ == "__main__":
    unittest.main()
