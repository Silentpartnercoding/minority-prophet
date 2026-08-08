import unittest

from experiments.exp009_hybrid import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    MARGIN_THRESHOLD,
    SEEDS,
    WORLDS_PER_SEED,
    selective,
)


class Exp009HybridTests(unittest.TestCase):
    def test_confirmatory_configuration_is_frozen(self):
        self.assertEqual(SEEDS, tuple(range(301, 321)))
        self.assertEqual(WORLDS_PER_SEED, 200)
        self.assertEqual(BOOTSTRAP_SEED, 20260806)
        self.assertEqual(BOOTSTRAP_RESAMPLES, 10_000)
        self.assertEqual(MARGIN_THRESHOLD, 3)

    def test_selective_challenger_only_overrides_at_frozen_margin(self):
        majority = [0] * 8
        roots = [1, 1, 1, 0, 0, 0, 0, 0]
        margins = [3, 2, 9, 9, 9, 9, 9, 9]
        ties = [False, False, True, False, False, False, False, False]
        self.assertEqual(selective(majority, roots, margins, ties), [1, 0, 0, 0, 0, 0, 0, 0])


if __name__ == "__main__":
    unittest.main()
