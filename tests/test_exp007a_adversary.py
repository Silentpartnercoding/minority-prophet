import hashlib
import json
import unittest
from pathlib import Path

from experiments.exp007a_adversary import evaluate, make_world, optimize


class Exp007AAdversaryTests(unittest.TestCase):
    def test_world_is_deterministic(self):
        import random

        params = (0.2, 0.4, 0.6, 0.8)
        self.assertEqual(make_world(random.Random(9), params),
                         make_world(random.Random(9), params))

    def test_evaluation_is_deterministic(self):
        params = (0.2, 0.4, 0.6, 0.8)
        self.assertEqual(evaluate(params, 11, 5), evaluate(params, 11, 5))

    def test_optimizer_honors_exact_budget(self):
        selected, history = optimize(worlds=2)
        self.assertEqual(len(history), 45)
        self.assertEqual(len({tuple(row["params"]) for row in history}), 45)
        self.assertTrue(all(0.0 <= value <= 1.0 for value in selected))

    def test_committed_result_is_bound_and_complete(self):
        root = Path(__file__).resolve().parents[1]
        result_path = root / "results/exp007a-v1/result.json"
        if not result_path.exists():
            self.skipTest("result is added only after preregistered execution")
        data = result_path.read_bytes()
        record = json.loads(data)
        verification = json.loads((result_path.parent / "verification.json").read_text())
        self.assertEqual(hashlib.sha256(data).hexdigest(), verification["output_sha256"])
        self.assertEqual(len(record["training_evaluations"]), 45)
        self.assertEqual(record["provenance"]["protocol_commit"], verification["protocol_commit"])
        self.assertEqual(record["overall_verdict"], "supported")
