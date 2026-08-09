import unittest

from experiments.lir1.synthetic_fixture import build_fixture, hide_edges
from experiments.lir2.root_grouping import infer_roots, pair_score
from experiments.lir2.tune import THRESHOLDS
from experiments.lir2.score_confirmatory import BOOTSTRAP_SAMPLES, THRESHOLD


class LIR2Tests(unittest.TestCase):
    def test_threshold_grid_is_frozen(self):
        self.assertEqual(THRESHOLDS, (0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95))
        self.assertEqual(THRESHOLD, 0.75)
        self.assertEqual(BOOTSTRAP_SAMPLES, 10_000)

    def test_pair_score_is_symmetric(self):
        claims = build_fixture(1)
        left, right = claims[0].feature_view(), claims[1].feature_view()
        self.assertEqual(pair_score(left, right), pair_score(right, left))

    def test_exposed_edges_are_always_unioned(self):
        claims = hide_edges(build_fixture(1), 0.0)
        roots = infer_roots((row.feature_view() for row in claims), threshold=0.95)
        false_rows = [row for row in claims if not row.channel_metadata["asserted_value"]]
        self.assertEqual(len({roots[row.claim_id] for row in false_rows}), 1)


if __name__ == "__main__":
    unittest.main()
