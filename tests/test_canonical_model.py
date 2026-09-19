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

    def test_declared_json_schema_is_enforced(self):
        def mutate(model):
            del model["terms"][0]["definition"]
            model["terms"][0]["unexpected"] = True

        problems = self.problems_for(mutate)
        self.assert_problem(problems, "schema")
        self.assert_problem(problems, "required property 'definition'")
        self.assert_problem(problems, "additional property 'unexpected'")

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
        def mutate(model):
            model["mechanisms"][0]["replacement"] = "missing-mechanism"
            model["artifacts"][0]["replacement"] = "missing-artifact"

        problems = self.problems_for(mutate)
        self.assert_problem(problems, "unknown replacement")
        self.assert_problem(problems, "missing-artifact")

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

    def test_load_bearing_status_surfaces_are_registered(self):
        by_path = {entry["path"]: entry for entry in self.registry["artifacts"]}
        expected = {
            "canon/ATTESTED-INDEPENDENCE.md": "rejected_policy",
            "aggregation/README.md": "current",
            "research/attested-independence/README.md": "current",
            "docs/evidence/STATUS.md": "current",
            "formal/CLAIM-SCOPE.md": "current",
            "formal/DEFINITION-AUDIT.md": "historical_snapshot",
            "experiments/DECISION-RELATIVE-INDEPENDENCE-SERIES-CLOSURE.md": "historical_snapshot",
            "experiments/ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md": "historical_snapshot",
        }
        for path, artifact_class in expected.items():
            self.assertIn(path, by_path)
            self.assertEqual(by_path[path]["class"], artifact_class)

        aid_records = {"AID-1-V1", "AID-2-V1", "AID-3-V1", "AID-4-V1"}
        self.assertTrue(
            aid_records.issubset(by_path["docs/evidence/STATUS.md"]["researchRecords"])
        )

    def test_rejected_mechanisms_cannot_be_recommended(self):
        def mutate(model):
            model["artifacts"][0]["recommendedMechanisms"] = [
                "attested_independence_point_policy"
            ]

        problems = self.problems_for(mutate)
        self.assert_problem(problems, "recommends rejected mechanism")

    def test_current_guidance_uses_layered_root_terms(self):
        terms = {entry["id"]: entry["label"] for entry in self.registry["terms"]}
        self.assertEqual(terms["recorded_root"], "recorded root")
        self.assertEqual(terms["issued_root_identity"], "issued root identity")
        self.assertEqual(terms["effective_witness"], "effective witness")

        glossary = (ROOT / "GLOSSARY.md").read_text()
        for heading in ("**Recorded root**", "**Issued root identity**", "**Effective witness**"):
            self.assertIn(heading, glossary)
        self.assertNotIn("**Evidence root**", glossary)
        self.assertNotIn("**Evidence root (recorded)**", glossary)

    def test_reader_model_is_linked_and_preserves_the_negative_boundary(self):
        model = (ROOT / "docs/evidence/MODEL.md").read_text()
        evidence_index = (ROOT / "docs/evidence/README.md").read_text()
        foundations = (ROOT / "FOUNDATIONS.md").read_text()
        alignment = (ROOT / "EVIDENCE-ALIGNMENT.md").read_text()
        readme = (ROOT / "README.md").read_text()
        model_prose = " ".join(model.split())

        self.assertIn("MODEL.md", evidence_index)
        self.assertIn("A missing edge means", model)
        self.assertIn("not proof of independent observation", model_prose)
        self.assertIn("transport/relay", model)
        self.assertIn("cache/fan-out", model)
        self.assertIn("conceptual framing", foundations.casefold())
        self.assertIn("recorded copy link", foundations)
        self.assertNotIn("The next formal step is", foundations)
        self.assertIn("2026-09-19 model reconciliation", alignment)
        self.assertIn("canon/model-registry.json", alignment)
        self.assertIn("docs/evidence/MODEL.md", readme)
        self.assertNotIn("one recorded source against one independent source", readme)

    def test_reconciliation_is_a_local_and_ci_integrity_gate(self):
        makefile = (ROOT / "Makefile").read_text()
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        verify_line = next(
            line for line in makefile.splitlines() if line.startswith("verify-integrity:")
        )
        self.assertIn("check-canonical-model", verify_line)
        self.assertIn("check-canonical-model:", makefile)
        self.assertIn("scripts/check_canonical_model.py", makefile)
        self.assertIn("make check-canonical-model", ci)


if __name__ == "__main__":
    unittest.main()
