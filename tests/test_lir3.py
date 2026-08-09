import unittest

from experiments.lir1.synthetic_fixture import build_fixture, hide_edges
from experiments.lir3.pheme_provenance import split_for_case
from experiments.lir3.provenance_parent import (
    CONFIGURATIONS,
    Configuration,
    infer_parents,
    provenance_score,
)
from experiments.lir3.score_confirmatory import (
    BOOTSTRAP_SAMPLES,
    CONFIGURATION,
    INPUT_SHA256,
)


class LIR3Tests(unittest.TestCase):
    def test_candidate_grid_is_frozen(self):
        self.assertEqual(len(CONFIGURATIONS), 36)
        self.assertEqual(len({row.identifier for row in CONFIGURATIONS}), 36)

    def test_holdout_commitment_is_frozen(self):
        self.assertEqual(len(INPUT_SHA256), 64)
        self.assertEqual(CONFIGURATION.identifier, "author-0.00-margin-0.00-fallback-none")
        self.assertEqual(BOOTSTRAP_SAMPLES, 10_000)

    def test_split_is_deterministic(self):
        self.assertEqual(split_for_case("pheme:example"), split_for_case("pheme:example"))
        self.assertIn(split_for_case("pheme:example"), {"development", "confirmatory"})

    def test_provenance_score_uses_no_label_fields(self):
        left, right = [row.feature_view() for row in build_fixture(1)[:2]]
        before = provenance_score(left, right)
        left["true_root_id"] = "forbidden"
        left["content_truth"] = "false"
        self.assertEqual(before, provenance_score(left, right))

    def test_exposed_parent_is_preserved(self):
        claims = hide_edges(build_fixture(1), 0.0)
        config = Configuration(0.65, 0.20, "none")
        predictions = infer_parents(
            (claim.feature_view() for claim in claims), configuration=config
        )
        copied = next(claim for claim in claims if claim.observed_parents)
        self.assertEqual(predictions[copied.claim_id], copied.observed_parents[0])


if __name__ == "__main__":
    unittest.main()
