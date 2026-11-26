import hashlib
import json
import random
import unittest
from pathlib import Path

from experiments.exp010_root_identifiability import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    CASE_FAMILIES,
    CONFIRMATORY_SEEDS,
    METHODS,
    PAIRS_PER_SEED,
    attach_provenance,
    build_parser,
    canonical_json,
    estimate_roots,
    exact_all_success_lower,
    exact_zero_error_upper,
    generate_pair,
    project,
    run_experiment,
    score_roots,
    score_verdicts,
)


class PairedWorldGeneratorTests(unittest.TestCase):
    def test_all_ten_frozen_case_families_are_present(self):
        self.assertEqual(len(CASE_FAMILIES), 10)
        self.assertEqual(len(set(CASE_FAMILIES)), 10)

    def test_generation_is_deterministic(self):
        first = generate_pair(random.Random(7), CASE_FAMILIES[0])
        second = generate_pair(random.Random(7), CASE_FAMILIES[0])

        self.assertEqual(first, second)

    def test_every_family_changes_the_hidden_root_relation(self):
        for family in CASE_FAMILIES:
            with self.subTest(family=family):
                left, right = generate_pair(random.Random(11), family)
                self.assertNotEqual(left.true_root_by_claim, right.true_root_by_claim)
                self.assertNotEqual(
                    left.true_root_by_claim[1], right.true_root_by_claim[1]
                )

    def test_every_family_is_indistinguishable_through_l3(self):
        for family in CASE_FAMILIES:
            with self.subTest(family=family):
                left, right = generate_pair(random.Random(13), family)
                for level in range(4):
                    self.assertEqual(project(left, level), project(right, level))

    def test_honest_receipts_distinguish_first_nine_families(self):
        for family in CASE_FAMILIES[:-1]:
            with self.subTest(family=family):
                left, right = generate_pair(random.Random(17), family)
                self.assertNotEqual(project(left, 4), project(right, 4))
                self.assertTrue(left.provider_honest)
                self.assertTrue(right.provider_honest)

    def test_compromised_provider_pair_remains_identical_at_l4(self):
        left, right = generate_pair(random.Random(19), CASE_FAMILIES[-1])

        self.assertEqual(project(left, 4), project(right, 4))
        self.assertFalse(left.provider_honest)
        self.assertFalse(right.provider_honest)

    def test_world_shape_matches_draft_constraints(self):
        for family in CASE_FAMILIES:
            with self.subTest(family=family):
                for world in generate_pair(random.Random(23), family):
                    self.assertEqual(len(world.claims), 24)
                    self.assertEqual(len(world.claims[0].assertion), 8)
                    root_count = len(set(world.true_root_by_claim.values()))
                    self.assertGreaterEqual(root_count, 4)
                    self.assertLessEqual(root_count, 8)

    def test_projection_rejects_unknown_level(self):
        world, _ = generate_pair(random.Random(29), CASE_FAMILIES[0])

        with self.assertRaises(ValueError):
            project(world, 5)


class EstimatorAndMetricTests(unittest.TestCase):
    def test_method_inventory_is_frozen(self):
        self.assertEqual(
            METHODS,
            (
                "all_claims",
                "actor_key",
                "declared_lineage",
                "registry_policy",
                "source_receipt",
                "oracle",
            ),
        )

    def test_oracle_scores_perfectly(self):
        world, _ = generate_pair(random.Random(31), CASE_FAMILIES[0])
        estimate = estimate_roots(world, "oracle", level=5)
        metrics = score_roots(world, estimate)

        self.assertEqual(metrics.root_precision, 1.0)
        self.assertEqual(metrics.root_recall, 1.0)
        self.assertEqual(metrics.root_f1, 1.0)
        self.assertEqual(metrics.pairwise_f1, 1.0)
        self.assertEqual(metrics.root_inflation, 0)
        self.assertEqual(metrics.root_deflation, 0)
        self.assertEqual(metrics.symmetric_difference, 0)

    def test_all_claims_reports_root_inflation_and_pairwise_false_negatives(self):
        _, copied = generate_pair(random.Random(37), CASE_FAMILIES[2])
        metrics = score_roots(copied, estimate_roots(copied, "all_claims", level=0))

        self.assertGreater(metrics.root_inflation, 0)
        self.assertEqual(metrics.root_deflation, 0)
        self.assertLess(metrics.pairwise_recall, 1.0)
        self.assertGreater(metrics.symmetric_difference, 0)

    def test_actor_keys_do_not_prove_independence(self):
        _, copied = generate_pair(random.Random(41), "sybil_control_boundary")
        estimate = estimate_roots(copied, "actor_key", level=1)

        self.assertNotEqual(estimate.root_by_claim, copied.true_root_by_claim)
        self.assertGreater(score_roots(copied, estimate).root_inflation, 0)

    def test_same_actor_does_not_prove_common_root(self):
        independent, _ = generate_pair(
            random.Random(43), "same_actor_distinct_acquisitions"
        )
        estimate = estimate_roots(independent, "actor_key", level=1)

        self.assertNotEqual(estimate.root_by_claim, independent.true_root_by_claim)
        self.assertGreater(score_roots(independent, estimate).root_deflation, 0)

    def test_source_receipts_recover_all_honest_world_partitions(self):
        for family in CASE_FAMILIES[:-1]:
            for world in generate_pair(random.Random(47), family):
                with self.subTest(family=family, roots=len(set(world.true_root_by_claim.values()))):
                    estimate = estimate_roots(world, "source_receipt", level=4)
                    self.assertEqual(estimate.root_by_claim, world.true_root_by_claim)
                    self.assertEqual(score_roots(world, estimate).symmetric_difference, 0)

    def test_source_receipts_fail_under_compromised_provider(self):
        _, copied = generate_pair(
            random.Random(53), "compromised_provider_receipt"
        )
        estimate = estimate_roots(copied, "source_receipt", level=4)

        self.assertNotEqual(estimate.root_by_claim, copied.true_root_by_claim)
        self.assertGreater(score_roots(copied, estimate).symmetric_difference, 0)

    def test_source_receipt_method_abstains_below_l4(self):
        world, _ = generate_pair(random.Random(59), CASE_FAMILIES[0])
        estimate = estimate_roots(world, "source_receipt", level=3)

        self.assertEqual(len(estimate.abstained_claims), len(world.claims))
        self.assertEqual(score_roots(world, estimate).abstention_rate, 1.0)

    def test_verdict_metrics_report_oracle_margin_k_and_agreement(self):
        world, _ = generate_pair(random.Random(61), CASE_FAMILIES[0])
        estimate = estimate_roots(world, "oracle", level=5)
        verdicts = score_verdicts(world, estimate)

        self.assertEqual(verdicts.applicable, 8)
        self.assertEqual(verdicts.agree, 8)
        self.assertEqual(verdicts.false_reversals, 0)
        self.assertEqual(verdicts.root_error_k, 0)
        self.assertEqual(len(verdicts.oracle_margins), 8)


class ProtocolConsistencyTests(unittest.TestCase):
    def test_protocol_freezes_configuration_and_boundaries(self):
        protocol = (
            Path(__file__).resolve().parents[1]
            / "experiments/EXP010-ROOT-IDENTIFIABILITY-PREREGISTRATION.md"
        ).read_text()

        for required in (
            "Status: preregistered",
            "`401–420`",
            "`4,000` world pairs",
            "`10,000`",
            "`20261029`",
            "H10-1",
            "H10-2",
            "H10-3",
            "H10-4",
            "H10-5",
            "1 - 0.05^(1/n)",
            "`k < m`",
            "compromised provider",
            "minority-prophet.exp010-result.v1",
        ):
            with self.subTest(required=required):
                self.assertIn(required, protocol)

        for family_number in range(1, 11):
            self.assertIn(f"{family_number}.", protocol)


class FrozenRunnerTests(unittest.TestCase):
    def test_frozen_configuration_matches_protocol(self):
        self.assertEqual(CONFIRMATORY_SEEDS, tuple(range(401, 421)))
        self.assertEqual(PAIRS_PER_SEED, 200)
        self.assertEqual(BOOTSTRAP_SEED, 20261029)
        self.assertEqual(BOOTSTRAP_RESAMPLES, 10_000)

    def test_cli_has_no_confirmatory_overrides(self):
        destinations = {action.dest for action in build_parser()._actions}
        self.assertEqual(
            destinations,
            {
                "help",
                "implementation_commit",
                "output",
                "protocol_commit",
                "timing_output",
            },
        )

    def test_exact_zero_and_all_success_bounds(self):
        self.assertAlmostEqual(exact_zero_error_upper(100), 1 - 0.05 ** 0.01)
        self.assertAlmostEqual(exact_all_success_lower(100), 0.05 ** 0.01)

    def test_small_development_run_is_deterministic_and_supports_boundaries(self):
        first = run_experiment(seeds=(1,), pairs_per_seed=10, resamples=40)
        second = run_experiment(seeds=(1,), pairs_per_seed=10, resamples=40)

        self.assertEqual(first, second)
        # The tiny development sample cannot satisfy the preregistered exact
        # confidence bounds, but it must exercise both construction claims.
        self.assertEqual(first["hypotheses"]["H10-1"], "supported")
        self.assertEqual(first["hypotheses"]["H10-4"], "supported")
        self.assertEqual(first["hypotheses"]["H10-5"], "supported")
        self.assertEqual(first["construction"]["l0_l3_projection_violations"], 0)
        self.assertEqual(first["construction"]["compromised_l4_witnesses"], 1)
        self.assertEqual(first["bootstrap"]["resampling_unit"], "world_pair")

    def test_scientific_provenance_is_canonical_and_excludes_runtime(self):
        result = attach_provenance(
            {"overall_verdict": "supported"},
            protocol_commit="a" * 40,
            implementation_commit="b" * 40,
            runner_source=b"runner",
        )
        encoded = canonical_json(result)

        self.assertIn(b"minority-prophet.exp010-result.v1", encoded)
        self.assertNotIn(b"duration", encoded)
        self.assertNotIn(b"platform", encoded)

    def test_committed_result_is_bound_complete_and_confirmatory(self):
        root = Path(__file__).resolve().parents[1]
        review_packet = root / "experiments/exp010-review"
        result_path = review_packet / "result.json"
        verification = json.loads((review_packet / "verification.json").read_text())
        result_bytes = result_path.read_bytes()
        result = json.loads(result_bytes)

        self.assertTrue(verification["all_scientific_files_match"])
        self.assertEqual(len(verification["known_protocol_deviations"]), 2)
        self.assertIn("bootstrap", verification["known_protocol_deviations"][0])
        self.assertIn("exact-binomial", verification["known_protocol_deviations"][1])
        self.assertEqual(
            hashlib.sha256(result_bytes).hexdigest(),
            verification["scientific_output_sha256"],
        )
        self.assertEqual(result["configuration"]["seeds"], list(CONFIRMATORY_SEEDS))
        self.assertEqual(result["configuration"]["pairs_per_seed"], PAIRS_PER_SEED)
        self.assertEqual(result["overall_verdict"], "supported")
        self.assertEqual(set(result["hypotheses"].values()), {"supported"})
        self.assertEqual(result["construction"]["l0_l3_projection_violations"], 0)
        self.assertEqual(result["construction"]["compromised_l4_witnesses"], 400)

        for name, expected in (
            ("diagnostics-run-a.json", verification["run_a_diagnostics_sha256"]),
            ("diagnostics-run-b.json", verification["run_b_diagnostics_sha256"]),
        ):
            self.assertEqual(
                hashlib.sha256((result_path.parent / name).read_bytes()).hexdigest(),
                expected,
            )


if __name__ == "__main__":
    unittest.main()
