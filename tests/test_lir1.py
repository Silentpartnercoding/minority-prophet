import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.lir1.infer import infer_parents, roots_from_parents
from experiments.lir1.metrics import (
    aggregation_accuracy,
    parent_metrics,
    root_count_metrics,
    root_pair_metrics,
)
from experiments.lir1.model import ClaimInstance, read_jsonl, write_jsonl
from experiments.lir1.pheme import flatten_tree, truth_label
from experiments.lir1.synthetic_fixture import build_fixture, hide_edges
from experiments.lir1.tune_pheme import THRESHOLDS, select_threshold
from experiments.lir1.run_pheme_confirmatory import f1_from_counts, percentile


class LIR1Tests(unittest.TestCase):
    def test_confirmatory_metric_helpers_are_deterministic(self):
        self.assertEqual(f1_from_counts(3, 1, 1), 0.75)
        self.assertEqual(percentile([0.0, 0.25, 0.5, 0.75, 1.0], 0.5), 0.5)

    def test_pheme_threshold_grid_and_tie_rule_are_frozen(self):
        self.assertEqual(
            THRESHOLDS,
            (0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85),
        )
        self.assertEqual(
            select_threshold([
                {"threshold": 0.4, "parentF1": 0.7},
                {"threshold": 0.6, "parentF1": 0.7},
                {"threshold": 0.8, "parentF1": 0.6},
            ]),
            0.6,
        )

    def test_pheme_tree_flattening_preserves_direct_parents(self):
        tree = {"root": {"a": {"b": []}, "c": {}}}
        self.assertEqual(
            list(flatten_tree(tree)),
            [
                ("root", None, "root"),
                ("a", "root", "root"),
                ("b", "a", "root"),
                ("c", "root", "root"),
            ],
        )

    def test_pheme_truth_mapping_does_not_force_unverified(self):
        self.assertEqual(truth_label({"true": "1"}), "true")
        self.assertEqual(truth_label({"true": 0}), "false")
        self.assertEqual(truth_label({"misinformation": 1}), "unresolved")

    def test_mechanics_manifest_binds_every_file(self):
        root = Path(__file__).resolve().parents[1]
        for manifest_path in (
            "results/lir1-mechanics-v0.1/manifest.json",
            "results/lir1-pheme-development-v0.1/manifest.json",
        ):
            manifest = json.loads((root / manifest_path).read_text())
            for relative, expected in manifest["files"].items():
                self.assertEqual(hashlib.sha256((root / relative).read_bytes()).hexdigest(), expected)

    def test_feature_view_excludes_every_label_field(self):
        claim = build_fixture(1)[0]
        view = claim.feature_view()
        self.assertFalse({"content_truth", "independence_label", "true_root_id", "label_basis", "label_scope", "split"} & view.keys())

    def test_proxy_cannot_assert_true_root(self):
        claim = build_fixture(1)[0]
        invalid = ClaimInstance(**{**claim.__dict__, "label_basis": "heuristic_proxy"})
        with self.assertRaisesRegex(ValueError, "cannot assert"):
            invalid.validate()

    def test_jsonl_round_trip_is_canonical(self):
        claims = build_fixture(1)
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.jsonl"
            second = Path(directory) / "second.jsonl"
            write_jsonl(first, claims)
            restored = read_jsonl(first)
            write_jsonl(second, restored)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_edge_hiding_is_nested(self):
        claims = build_fixture(10)
        low = {c.claim_id for c in hide_edges(claims, 0.25) if not c.observed_parents}
        high = {c.claim_id for c in hide_edges(claims, 0.70) if not c.observed_parents}
        self.assertLessEqual(low, high)

    def test_mechanics_fixture_recovers_copied_majority(self):
        truth = build_fixture(10)
        observed = hide_edges(truth, 0.40)
        parents = infer_parents(c.feature_view() for c in observed)
        roots = roots_from_parents(parents)
        pair = root_pair_metrics(truth, roots)
        count = root_count_metrics(truth, roots)
        aggregation = aggregation_accuracy(truth, roots)
        self.assertGreaterEqual(pair["f1"], 0.60)
        self.assertEqual(count["meanAbsoluteError"], 0.0)
        self.assertEqual(aggregation["majority_accuracy"], 0.0)
        self.assertEqual(aggregation["declared_accuracy"], 1.0)
        self.assertEqual(aggregation["inferred_accuracy"], 1.0)

    def test_parent_metric_can_be_restricted_to_hidden_claims(self):
        truth = build_fixture(2)
        observed = hide_edges(truth, 0.40)
        hidden = {
            original.claim_id
            for original, visible in zip(truth, observed, strict=True)
            if original.observed_parents and not visible.observed_parents
        }
        parents = infer_parents(claim.feature_view() for claim in observed)
        restricted = parent_metrics(truth, parents, evaluate_claim_ids=hidden)
        self.assertEqual(restricted["evaluable"], len(hidden))


if __name__ == "__main__":
    unittest.main()
