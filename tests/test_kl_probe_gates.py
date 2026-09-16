"""Run the KL-002 and KL-005 unregistered probe suites from the root suite.

`testpaths = ["tests"]` means a suite living under `research/.../experiments/`
is never collected, so it would pass locally and never run in CI -- a test that
cannot fail in the place that matters. This file puts them in the root suite's
path.

It also asserts the probes are filed as probes: a `results/` directory under a
seeded experiment is what `test_no_experiment_claims_progress_without_the_evidence_for_it`
refuses, and these two must stay on the right side of that line.
"""

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "research/knowledge-ledger/experiments"


class KLProbeGateTests(unittest.TestCase):
    def _run_suite(self, experiment):
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(EXPERIMENTS / experiment / "tests"), "-q"],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, f"{experiment}:\n{result.stdout}\n{result.stderr}")

    def test_kl002_probe_suite_passes(self):
        self._run_suite("KL-002")

    def test_kl005_probe_suite_passes(self):
        self._run_suite("KL-005")

    def test_probes_are_filed_as_probes_not_results(self):
        """Flips the moment someone promotes a probe by moving the directory."""
        for experiment in ("KL-002", "KL-005"):
            directory = EXPERIMENTS / experiment
            status = json.loads((directory / "STATUS.json").read_text())
            self.assertEqual(status["state"], "seeded", experiment)
            self.assertEqual(status["resultStatus"], "none", experiment)
            self.assertFalse((directory / "results").exists(),
                             f"{experiment}: a seeded experiment must not carry results/")
            self.assertTrue((directory / "probe/first-gate.json").is_file(), experiment)
            self.assertIs(status["unregisteredProbe"]["isAResult"], False, experiment)

    def test_kl002_probe_records_a_gate_that_does_not_hold(self):
        """The probe's value is the negative outcome. If this ever reads True,
        either the root rule changed or the fixture was weakened."""
        probe = json.loads((EXPERIMENTS / "KL-002/probe/first-gate.json").read_text())
        self.assertFalse(probe["gateHoldsUnderByteIdentity"])
        laundered = probe["populations"]["laundered"]["byRule"]
        self.assertEqual(laundered["byte_identity"]["distinctRoots"], 20)
        self.assertEqual(laundered["declared_origin"]["distinctRoots"], 1)
        self.assertTrue(probe["falseClaimOutscoresTrueClaim"])

    def test_kl002_repair_never_manufactures_independence(self):
        """The repair's actual claim. Over-counting creates a false belief;
        under-counting creates an abstention. Only one is dangerous."""
        probe = json.loads((EXPERIMENTS / "KL-002/probe/first-gate.json").read_text())
        direction = probe["errorDirection"]
        self.assertTrue(direction["ancestry"]["neverOvercounts"])
        self.assertFalse(direction["byte_identity"]["neverOvercounts"])
        self.assertFalse(direction["declared_origin"]["neverOvercounts"])

    def test_no_root_rule_is_correct_everywhere_and_that_is_recorded(self):
        probe = json.loads((EXPERIMENTS / "KL-002/probe/first-gate.json").read_text())
        self.assertEqual(probe["rulesCorrectOnEveryPopulation"], [])
        self.assertIn("fail-closed", probe["whyNoRuleIsFullyCorrect"])

    def test_kl005_probe_shows_silence_winning_the_one_sided_metric(self):
        """The defect must stay demonstrable. If `silent` ever stops winning the
        one-sided endpoint, the broken metric was silently repaired and the
        comparison no longer shows anything."""
        probe = json.loads((EXPERIMENTS / "KL-005/probe/first-gate.json").read_text())
        self.assertEqual(probe["oneSidedWinner"], "silent")
        self.assertEqual(probe["twoSidedWinner"], "root_aware")
        self.assertTrue(probe["gates"]["syndicationCannotManufactureIndependence"])
        self.assertTrue(probe["gates"]["twoSidedMetricDeniesSilenceTheWin"])


if __name__ == "__main__":
    unittest.main()
