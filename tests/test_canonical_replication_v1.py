import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "experiments/replications/v1/run.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("canonical_replication_v1", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CanonicalReplicationV1Tests(unittest.TestCase):
    def test_frozen_sources_exist(self):
        module = load_runner()
        self.assertTrue(module.HANDOFF.is_file())
        self.assertTrue(module.ONESHOT.is_file())
        self.assertTrue(module.EXP008.is_file())

    def test_portability_transform_is_narrow(self):
        module = load_runner()
        source = b'x = "/home/claude/file"\nseed = 7\n'
        with tempfile.TemporaryDirectory() as directory:
            transformed = module.portable(source, Path(directory))
        self.assertNotIn(b"/home/claude", transformed)
        self.assertTrue(transformed.endswith(b"seed = 7\n"))

    def test_canonical_json_is_stable(self):
        module = load_runner()
        left = module.canonical_json({"b": 2, "a": 1})
        right = module.canonical_json({"a": 1, "b": 2})
        self.assertEqual(left, right)
        self.assertEqual(left, b'{"a":1,"b":2}\n')
        self.assertEqual(hashlib.sha256(left).hexdigest(), hashlib.sha256(right).hexdigest())

    def test_committed_result_receipt_binds_outputs(self):
        result_dir = ROOT / "results/canonical-replications-v1/run-a"
        if not result_dir.exists():
            self.skipTest("results are added only after the preregistered run")
        receipt = json.loads((result_dir / "receipt.json").read_text())
        for name, metadata in receipt["outputs"].items():
            artifact = result_dir / name
            self.assertTrue(artifact.is_file(), name)
            self.assertEqual(len(artifact.read_bytes()), metadata["bytes"], name)
            self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), metadata["sha256"], name)
        self.assertEqual(
            hashlib.sha256((result_dir / "environment.json").read_bytes()).hexdigest(),
            receipt["environment_sha256"],
        )
