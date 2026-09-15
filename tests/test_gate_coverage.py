"""Tests for the gate-coverage staleness check.

Half of these are ablations. A check that only ever passes is untested however
often it runs -- the repository's recurring single-valued finding -- so each
ablation below breaks the map in one specific way and asserts the check notices.
"""

import copy
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAP = ROOT / "research/knowledge-ledger/GATE-COVERAGE.json"
SCRIPT = ROOT / "scripts/check_gate_coverage.py"


def _run():
    return subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                          capture_output=True, text=True)


class GateCoverageTests(unittest.TestCase):
    def setUp(self):
        self.original = MAP.read_text(encoding="utf-8")

    def tearDown(self):
        MAP.write_text(self.original, encoding="utf-8")

    def _with(self, mutate):
        document = json.loads(self.original)
        mutate(document)
        MAP.write_text(json.dumps(document, indent=2), encoding="utf-8")
        return _run()

    def test_passes_as_committed(self):
        result = _run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fires_when_a_gate_phrase_drifts(self):
        """The gate was rewritten, so the coverage claim may no longer apply."""
        result = self._with(lambda d: d["entries"][0].__setitem__(
            "gatePhrase", "a phrase that appears in no status file"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("no longer in STATUS.json", result.stdout)

    def test_fires_when_a_cited_artifact_disappears(self):
        result = self._with(lambda d: d["entries"][0].__setitem__(
            "coveredBy", ["experiments/does-not-exist.md"]))
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing", result.stdout)

    def test_fires_when_an_entry_omits_what_it_does_not_discharge(self):
        """Coverage without a stated limit is how adjacent evidence gets
        admitted as if it were direct."""
        result = self._with(lambda d: d["entries"][0].pop("doesNotDischarge"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("does NOT discharge", result.stdout)

    def test_fires_when_a_pending_branch_lands(self):
        """Merging must force promotion into entries[], not leave an
        unverifiable citation sitting in the map."""
        result = self._with(lambda d: d["pendingEntries"][0].__setitem__(
            "coveredBy", ["CLAIMS.md"]))
        self.assertEqual(result.returncode, 1)
        self.assertIn("has landed", result.stdout)

    def test_fires_on_an_undeclared_strength(self):
        result = self._with(lambda d: d["entries"][0].__setitem__("strength", "definitely"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown strength", result.stdout)

    def test_every_pending_entry_names_its_pull_request(self):
        document = json.loads(self.original)
        for entry in document.get("pendingEntries", []):
            self.assertIsInstance(entry.get("pendingPullRequest"), int, entry["experiment"])

    def test_no_covered_experiment_was_promoted(self):
        """Coverage is never evidence for the experiment it covers."""
        document = json.loads(self.original)
        program = ROOT / "research/knowledge-ledger/experiments"
        for entry in document["entries"]:
            status = json.loads((program / entry["experiment"] / "STATUS.json").read_text())
            self.assertIn(status["state"], {"seeded", "fixture-passed"}, entry["experiment"])

    def test_adjacent_entries_are_marked_inadmissible(self):
        """An `adjacent` row must never read as though it discharges its gate."""
        document = json.loads(self.original)
        for entry in document["entries"] + document.get("pendingEntries", []):
            if entry["strength"] == "adjacent":
                self.assertTrue(entry["doesNotDischarge"], entry["experiment"])


if __name__ == "__main__":
    unittest.main()
