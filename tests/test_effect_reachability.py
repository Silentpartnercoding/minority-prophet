"""BL-060 — an experiment whose population cannot exhibit the effect must not run.

KL-001 v0.2 was preregistered, commit-pinned, identically instrumented in both
arms, and produced a number that could not have come out any other way: its corpus
contained zero instances of the feature its mechanism acts on. Preregistration,
ablation and mutation testing all interrogate the instrument, and the instrument
was fine. Nothing looked at the population.

These tests build their own fixtures rather than leaning on the real corpora, so
they demonstrate the behaviour instead of asserting a historical number.

Stdlib only; CI runs `unittest discover`.
"""
import json
import pathlib
import tempfile
import unittest

from scripts.check_effect_reachability import check

# A probe that counts files whose name marks them as carrying the property. Kept
# trivial so the tests are about the checker, not about the probe.
PROBE_SOURCE = '''\
import pathlib, sys
print(sum(1 for p in pathlib.Path(sys.argv[1]).iterdir() if p.name.startswith("has-")))
'''


class Fixture:
    def __init__(self, tmp: pathlib.Path):
        self.root = tmp
        (tmp / "probe.py").write_text(PROBE_SOURCE)
        self.rich = tmp / "rich"
        self.poor = tmp / "poor"
        self.rich.mkdir(); self.poor.mkdir()
        (self.rich / "has-one.txt").write_text("x")
        (self.rich / "ordinary.txt").write_text("x")
        (self.poor / "ordinary.txt").write_text("x")

    def declare(self, name="prereg.json", **overrides) -> pathlib.Path:
        requirement = {
            "property": "an item carrying the feature the mechanism acts on",
            "probe": ["python3", "probe.py", "{population}"],
            "population": "rich",
            "negativeControl": "poor",
            "minimum": 1,
        }
        requirement.update(overrides)
        path = self.root / name
        path.write_text(json.dumps({"effectRequires": [requirement]}))
        return path


class TestEffectReachability(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.f = Fixture(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_a_population_carrying_the_property_passes(self):
        self.assertEqual(check(self.f.declare(), self.f.root), [])

    def test_a_population_without_the_property_is_refused(self):
        problems = check(self.f.declare(population="poor"), self.f.root)
        self.assertTrue(problems)
        self.assertIn("EFFECT UNREACHABLE", problems[0])

    def test_an_undeclared_requirement_fails_rather_than_skipping(self):
        """Silence is the v0.2 failure. 'My mechanism depends on no property of
        the population' is a strong claim; it has to be made out loud."""
        path = self.f.root / "silent.json"
        path.write_text(json.dumps({"primaryEndpoint": "false-clean rate"}))
        problems = check(path, self.f.root)
        self.assertTrue(problems)
        self.assertIn("declares no `effectRequires`", problems[0])

    def test_a_probe_that_fires_on_anything_is_rejected(self):
        """The trap must not destroy the test. A probe reporting a large number
        for any input would satisfy this check while proving nothing -- exactly
        the vacuity that made a MUST-be-0 assertion decoration in LIN-000."""
        problems = check(
            self.f.declare(probe=["python3", "-c", "print(999)"]), self.f.root)
        self.assertTrue(problems)
        self.assertIn("UNFALSIFIABLE", problems[0])

    def test_an_unfalsifiable_probe_is_reported_before_the_verdict(self):
        """Ordering matters: if the probe cannot fail, the reachability verdict is
        meaningless in both directions and must not be the headline."""
        problems = check(
            self.f.declare(probe=["python3", "-c", "print(999)"], population="poor"),
            self.f.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("UNFALSIFIABLE", problems[0])
        self.assertNotIn("UNREACHABLE", problems[0])

    def test_a_missing_negative_control_is_refused(self):
        path = self.f.root / "nocontrol.json"
        path.write_text(json.dumps({"effectRequires": [{
            "property": "p", "probe": ["python3", "probe.py", "{population}"],
            "population": "rich", "minimum": 1}]}))
        problems = check(path, self.f.root)
        self.assertTrue(problems)
        self.assertIn("negativeControl", problems[0])

    def test_a_probe_that_cannot_run_is_a_failure_not_a_pass(self):
        problems = check(
            self.f.declare(probe=["python3", "no-such-probe.py", "{population}"]),
            self.f.root)
        self.assertTrue(problems)
        self.assertIn("probe exited", problems[0])

    def test_a_probe_that_prints_prose_is_a_failure(self):
        problems = check(
            self.f.declare(probe=["python3", "-c", "print('looks fine')"]),
            self.f.root)
        self.assertTrue(problems)
        self.assertIn("one integer", problems[0])

    def test_the_minimum_is_honoured(self):
        """One instance is not always enough to power an endpoint. An author who
        needs ten must be able to say ten and be refused at nine."""
        problems = check(self.f.declare(minimum=10), self.f.root)
        self.assertTrue(problems)
        self.assertIn("contains 1 (needs 10)", problems[0])


if __name__ == "__main__":
    unittest.main()
