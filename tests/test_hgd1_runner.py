import unittest

from experiments.hgd1.run_hgd1 import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    SEEDS,
    WORLDS_PER_SEED,
    assess,
    component,
    receipt,
    synthetic_variant,
    synthetic_world,
)


class Hgd1RunnerTests(unittest.TestCase):
    def test_frozen_configuration(self):
        self.assertEqual(SEEDS, tuple(range(701, 721)))
        self.assertEqual(WORLDS_PER_SEED, 250)
        self.assertEqual(BOOTSTRAP_SEED, 20260809)
        self.assertEqual(BOOTSTRAP_RESAMPLES, 10_000)

    def test_extremes(self):
        duplicate = [receipt("r1", 1) for _ in range(8)]
        independent = [receipt(f"r{i}", i % 2) for i in range(8)]
        self.assertEqual(assess(duplicate, [], "interval")["massLower"], 1)
        self.assertEqual(assess(independent, [], "interval")["massUpper"], 8)

    def test_half_shared_interval(self):
        records = [receipt(f"r{i}", 1) for i in range(8)]
        components = [component("cal", [f"r{i}" for i in range(8)], 0.4, 0.6, 0.5)]
        result = assess(records, components, "interval")
        self.assertAlmostEqual(result["massLower"], 3.8)
        self.assertAlmostEqual(result["massUpper"], 5.2)

    def test_unknown_overlap_escalates(self):
        base = synthetic_world(__import__("random").Random(701), 701, 0)
        records, components, _ = synthetic_variant(base, "unknown_overlap")
        self.assertEqual(assess(records, components, "interval")["state"], "ESCALATE")


if __name__ == "__main__":
    unittest.main()
