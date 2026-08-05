import unittest

from aggregation import majority_vote, weighted_vote
from benchmark import evaluate, generate_world, generate_worlds


class BenchmarkTests(unittest.TestCase):
    def test_generation_is_deterministic(self):
        self.assertEqual(generate_world(seed=7), generate_world(seed=7))

    def test_default_world_is_minority_truth(self):
        world = generate_world(seed=7)
        self.assertTrue(world.minority_truth)
        self.assertEqual(sum(claim.independent for claim in world.claims), 3)
        self.assertEqual(sum(claim.copied_from is not None for claim in world.claims), 95)

    def test_majority_follows_copied_falsehood(self):
        world = generate_world(seed=7, independent_accuracy=1.0)
        self.assertEqual(majority_vote(world.claims).belief, not world.truth)

    def test_weighted_result_is_probabilistic(self):
        world = generate_world(seed=7)
        result = weighted_vote(world.claims)
        self.assertGreaterEqual(result.probability_true, 0)
        self.assertLessEqual(result.probability_true, 1)

    def test_evaluation_reports_required_metrics(self):
        reports = evaluate(generate_worlds(count=10, seed=4))
        self.assertEqual({item["method"] for item in reports}, {"majority", "weighted"})
        self.assertIn("minority_truth_recovery", reports[0])
        self.assertIn("brier_score", reports[0])

    def test_invalid_world_configuration_fails(self):
        with self.assertRaises(ValueError):
            generate_world(seed=1, independent_truth_count=0)


if __name__ == "__main__":
    unittest.main()
