import unittest

from aggregation.semantic import evidence_root_vote, proposition_majority, semantic_coalition
from experiments.los_inspired_v01 import (
    conjunction_constraint,
    generate_corruption_world,
    generate_semantic_world,
    run_experiment,
)


class SemanticAggregationTests(unittest.TestCase):
    def test_copied_claims_collapse_to_one_root(self):
        world = generate_semantic_world(seed=7, index=0, regime="copied_false_majority")
        majority = proposition_majority(world.claims, conjunction_constraint)
        roots = evidence_root_vote(world.claims, conjunction_constraint)
        semantic = semantic_coalition(world.claims, conjunction_constraint)
        self.assertNotEqual(majority.assignment, world.truth)
        self.assertEqual(roots.assignment, world.truth)
        self.assertEqual(semantic.assignment, world.truth)
        self.assertEqual(semantic.roots_used, 4)

    def test_semantic_method_preserves_constraint_in_doctrinal_split(self):
        world = generate_semantic_world(seed=7, index=0, regime="doctrinal_split")
        majority = proposition_majority(world.claims, conjunction_constraint)
        semantic = semantic_coalition(world.claims, conjunction_constraint)
        self.assertFalse(majority.consistent)
        self.assertEqual(semantic.assignment, world.truth)
        self.assertTrue(semantic.consistent)

    def test_unsupported_minority_does_not_take_over(self):
        world = generate_semantic_world(seed=7, index=0, regime="unsupported_false_minority")
        self.assertEqual(
            semantic_coalition(world.claims, conjunction_constraint).assignment,
            world.truth,
        )

    def test_corrupted_lineage_exposes_failure_boundary(self):
        world = generate_semantic_world(seed=7, index=0, regime="corrupted_lineage")
        self.assertNotEqual(
            semantic_coalition(world.claims, conjunction_constraint).assignment,
            world.truth,
        )

    def test_corruption_generator_controls_forged_roots(self):
        clean = generate_corruption_world(seed=7, index=0, forged_roots=0)
        damaged = generate_corruption_world(seed=7, index=0, forged_roots=5)
        clean_roots = {claim.root_id for claim in clean.claims if claim.root_id}
        damaged_roots = {claim.root_id for claim in damaged.claims if claim.root_id}
        self.assertEqual(len(clean_roots), 4)
        self.assertEqual(len(damaged_roots), 9)

    def test_small_experiment_is_reproducible_except_timing(self):
        first = run_experiment(worlds_per_regime=5, seed=12)
        second = run_experiment(worlds_per_regime=5, seed=12)
        for report in (first, second):
            for row in report["results"]:
                row.pop("mean_compute_microseconds")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
