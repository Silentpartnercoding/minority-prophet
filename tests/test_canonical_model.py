import copy
import json
import unittest
from pathlib import Path

from scripts.check_canonical_model import validate_registry_data, validate_repository


ROOT = Path(__file__).resolve().parents[1]


class CanonicalModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "canon/model-registry.json").read_text())

    def problems_for(self, mutate):
        candidate = copy.deepcopy(self.registry)
        mutate(candidate)
        return validate_registry_data(ROOT, candidate)

    def assert_problem(self, problems, fragment):
        self.assertTrue(
            any(fragment in problem for problem in problems),
            f"expected {fragment!r} in:\n" + "\n".join(problems),
        )

    def test_repository_registry_is_reconciled(self):
        self.assertEqual(validate_repository(ROOT), [])

    def test_duplicate_ids_and_normative_labels_are_rejected(self):
        problems = self.problems_for(
            lambda model: model["terms"].append(copy.deepcopy(model["terms"][0]))
        )
        self.assert_problem(problems, "duplicate term id")
        self.assert_problem(problems, "duplicate normative term label")

    def test_closed_layer_and_disposition_vocabularies_are_enforced(self):
        def mutate(model):
            model["terms"][0]["layer"] = "L99"
            model["mechanisms"][0]["disposition"] = "probably-fine"

        problems = self.problems_for(mutate)
        self.assert_problem(problems, "unknown layer")
        self.assert_problem(problems, "unknown disposition")

    def test_artifact_and_authority_references_must_resolve(self):
        def mutate(model):
            model["terms"][0]["authority"][0]["artifact"] = "missing/nope.py"
            model["mechanisms"][0]["theorems"] = ["NO-SUCH-THEOREM"]
            model["mechanisms"][1]["researchRecords"] = ["NO-SUCH-RECORD"]

        problems = self.problems_for(mutate)
        self.assert_problem(problems, "missing artifact path")
        self.assert_problem(problems, "unknown theorem id")
        self.assert_problem(problems, "unknown research record id")

    def test_replacement_ids_must_resolve(self):
        problems = self.problems_for(
            lambda model: model["mechanisms"][0].update(replacement="missing-mechanism")
        )
        self.assert_problem(problems, "unknown replacement")

    def test_rejected_experiment_cannot_promote_a_current_mechanism(self):
        def mutate(model):
            mechanism = model["mechanisms"][0]
            mechanism["disposition"] = "current"
            mechanism["theorems"] = []
            mechanism["researchRecords"] = ["AID-4-V1"]

        problems = self.problems_for(mutate)
        self.assert_problem(problems, "only rejected research records")

    def test_manifest_pin_path_and_worktree_digest_are_verified(self):
        def missing_path(model):
            model["mechanisms"][0]["pins"][0]["path"] = "missing/pinned.py"

        self.assert_problem(self.problems_for(missing_path), "does not bind")

        def wrong_digest(model):
            model["mechanisms"][0]["pins"][0]["sha256"] = "0" * 64

        problems = self.problems_for(wrong_digest)
        self.assert_problem(problems, "declared digest")

    def test_status_banner_must_match_registry(self):
        def mutate(model):
            model["artifacts"][0]["class"] = "historical_snapshot"

        problems = self.problems_for(mutate)
        self.assert_problem(problems, "status banner")

    def test_status_authority_ids_must_resolve(self):
        def mutate(model):
            model["artifacts"][0]["researchRecords"] = ["NO-SUCH-RECORD"]

        problems = self.problems_for(mutate)
        self.assert_problem(problems, "unknown research record id")


if __name__ == "__main__":
    unittest.main()
