import random, unittest
from experiments.heo1.run_heo1 import (SEEDS, WORLDS_PER_SEED, BOOTSTRAP_SEED,
    BOOTSTRAP_RESAMPLES, base_world, materialize, decide, hidden_roots)

class Heo1RunnerTests(unittest.TestCase):
    def setUp(self): self.base = base_world(random.Random(501), 501, 0)
    def test_frozen_configuration(self):
        self.assertEqual(SEEDS, tuple(range(501, 521))); self.assertEqual(WORLDS_PER_SEED, 250)
        self.assertEqual(BOOTSTRAP_SEED, 20260808); self.assertEqual(BOOTSTRAP_RESAMPLES, 10_000)
    def test_transforms_keep_one_adverse_origin(self):
        expected = decide(materialize(self.base, "single_origin"), "evidence_origin")["mass"]
        for variant in ("byte_copy_8", "paraphrase_8", "translation_8", "summary_8", "model_transform_8", "mixed_transform_32"):
            self.assertEqual(decide(materialize(self.base, variant), "evidence_origin")["mass"], expected)
    def test_uncertain_and_forged_origins_escalate(self):
        for variant in ("unknown_origin_8", "forged_parent_8"):
            self.assertEqual(decide(materialize(self.base, variant), "evidence_origin")["state"], "ESCALATE")
    def test_genuine_origins_remain_distinct(self):
        records = materialize(self.base, "genuine_origins_8")
        self.assertEqual(hidden_roots(records), 14)
        self.assertEqual(decide(records, "evidence_origin")["mass"], 14)

if __name__ == "__main__": unittest.main()
