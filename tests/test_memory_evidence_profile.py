"""The memory-evidence profile's adversarial cases must actually run.

PR #29 shipped `interop/memory-evidence-profile-v0.1/validate.py` with four
examples and eight adversarial rejection cases. It works -- and nothing executed
it. Not the test suite, not CI, not a Makefile. Eight adversarial cases that never
run are eight cases that cannot fail, which is the defect this programme spends
most of its time finding elsewhere.

Discovered while merging #29: the suite count did not move when nine files
arrived, and a test count that does not move when tests arrive is the signal.

These wire the validator in and also check the property that makes it worth
running: that it can still reject. A validator whose adversarial cases all pass
because it accepts everything would satisfy a naive "does it exit 0" check.
"""
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILE = ROOT / "interop/memory-evidence-profile-v0.1"
VALIDATOR = PROFILE / "validate.py"


class TestMemoryEvidenceProfile(unittest.TestCase):

    def test_the_validator_runs_and_passes_its_own_corpus(self):
        result = subprocess.run((sys.executable, str(VALIDATOR)),
                                capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0,
                         f"{result.stdout}\n{result.stderr}")
        self.assertIn("adversarial cases rejected", result.stdout)

    def test_the_adversarial_corpus_is_not_empty(self):
        """An empty corpus makes 'all cases rejected' trivially true."""
        cases = json.loads((PROFILE / "adversarial-cases.json").read_text())
        self.assertGreaterEqual(len(cases) if isinstance(cases, list)
                                else len(cases.get("cases", cases)), 1,
                                "no adversarial cases to reject")

    def test_the_validator_can_still_reject(self):
        """The validator must be able to return both answers.

        If it accepted everything, all eight adversarial cases would still
        "pass" a check that only asks whether the program exits cleanly. The
        point of those cases is that it discriminates, so that is what is tested
        -- against the real entry points, `schema_validate` and
        `validate_semantics`, which raise on rejection.
        """
        sys.path.insert(0, str(PROFILE))
        import importlib
        module = importlib.import_module("validate")

        schema = json.loads((PROFILE / "schema.json").read_text())
        examples = sorted(p for p in PROFILE.glob("*.json")
                          if p.name not in {"schema.json", "adversarial-cases.json"})
        self.assertTrue(examples, "no example records to validate")

        good = json.loads(examples[0].read_text())
        module.schema_validate(good, schema)          # must not raise
        module.validate_semantics(good)               # must not raise

        with self.assertRaises(Exception,
                               msg="a record with no required fields was accepted; "
                                   "the validator cannot discriminate and its eight "
                                   "rejections mean nothing"):
            module.schema_validate({"schema": "wrong"}, schema)


if __name__ == "__main__":
    unittest.main()
