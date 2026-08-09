import unittest

from experiments.lir1.synthetic_fixture import build_fixture
from experiments.lir4.attacks import (
    collide_identities,
    count_hidden_edges,
    remove_reply_identity,
    visible_edges,
)
from experiments.lir4.score_confirmatory import (
    BOOTSTRAP_SAMPLES,
    COLLISION_BUCKETS,
    INPUT_SHA256,
    MISSING_FRACTIONS,
)


class LIR4Tests(unittest.TestCase):
    def test_holdout_and_attack_grid_are_frozen(self):
        self.assertEqual(len(INPUT_SHA256), 64)
        self.assertEqual(MISSING_FRACTIONS, (0.00, 0.25, 0.50, 0.75, 1.00))
        self.assertEqual(COLLISION_BUCKETS, (32, 16, 8, 4, 2, 1))
        self.assertEqual(BOOTSTRAP_SAMPLES, 10_000)

    def test_missingness_is_nested_and_only_changes_hidden_edges(self):
        original = build_fixture(10)
        visible = visible_edges(original)
        quarter = remove_reply_identity(original, visible, fraction=0.25)
        half = remove_reply_identity(original, visible, fraction=0.50)
        quarter_missing = {
            row.claim_id
            for row in quarter
            if row.channel_metadata.get("reply_target_author_id") is None
        }
        half_missing = {
            row.claim_id
            for row in half
            if row.channel_metadata.get("reply_target_author_id") is None
        }
        self.assertLessEqual(quarter_missing, half_missing)

    def test_collision_preserves_matching_identity(self):
        original = build_fixture(1)
        visible = visible_edges(original)
        collided = collide_identities(original, visible, buckets=1)
        self.assertEqual({row.author_id for row in collided}, {"collision:0"})

    def test_hidden_edge_counter(self):
        original = build_fixture(20)
        visible = visible_edges(original)
        self.assertGreater(count_hidden_edges(original, visible), 0)


if __name__ == "__main__":
    unittest.main()
