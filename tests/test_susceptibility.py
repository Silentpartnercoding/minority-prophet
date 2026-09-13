"""The pressure-susceptibility probe.

The criterion this was built against: the output has interpretable parts, and the
action change is reported separately from the belief change.
"""

import unittest

from canon.decision_sensitivity import Action
from canon.susceptibility import Opinion, Pressure, Probe, Reading, probe


def make_judge(sensitivities, base=0.52, threshold=0.525):
    """A deterministic stand-in. The probe measures a judge; it is not one."""
    def judge(evidence, pressures):
        b = base + sum(sensitivities.get(p, 0.0) * v for p, v in pressures.items())
        b = max(0.0, min(1.0, b))
        return Opinion(b, Action.PROCEED if b >= threshold else Action.ESCALATE)
    return judge


class SeparationTest(unittest.TestCase):
    """Belief and action are reported apart because they are not proportional."""

    def setUp(self):
        self.p = probe(make_judge({Pressure.PRESTIGE: 0.30, Pressure.CONSENSUS: 0.01}),
                       "the deployment is safe", "fixed evidence bundle")

    def test_belief_and_action_movement_are_different_sets(self):
        self.assertEqual({r.pressure for r in self.p.moved_belief()},
                         {Pressure.PRESTIGE})
        self.assertEqual({r.pressure for r in self.p.moved_action()},
                         {Pressure.PRESTIGE, Pressure.CONSENSUS})

    def test_a_tiny_belief_move_that_flips_the_action_is_named(self):
        """The case a single number would hide."""
        crossings = {r.pressure for r in self.p.threshold_crossings()}
        self.assertEqual(crossings, {Pressure.CONSENSUS})

    def test_a_large_belief_move_that_flips_is_not_a_threshold_crossing(self):
        """Prestige moved belief 0.30 and flipped the action. That is a big move
        doing a big thing, which is a different finding from a nudge."""
        prestige = next(r for r in self.p.readings if r.pressure is Pressure.PRESTIGE)
        self.assertTrue(prestige.action_changed)
        self.assertFalse(prestige.flipped_action_without_moving_belief)

    def test_the_report_states_both_counts_separately(self):
        r = self.p.report()
        self.assertIn("belief moved on 1 of 5", r)
        self.assertIn("action moved on 2 of 5", r)


class NoHeadlineNumberTest(unittest.TestCase):
    def test_the_probe_exposes_no_aggregate_score(self):
        """A scalar rebuilds the black box confidence scores were, renamed."""
        p = probe(make_judge({}), "p", "e")
        for banned in ("score", "susceptibility_score", "total", "aggregate", "index"):
            self.assertFalse(hasattr(p, banned), f"Probe exposes {banned}")

    def test_the_report_says_why_there_is_no_score(self):
        self.assertIn("no aggregate score is reported", probe(make_judge({}), "p", "e").report())

    def test_every_dimension_is_reported_even_when_nothing_moves(self):
        p = probe(make_judge({}), "p", "e")
        self.assertEqual(len(p.readings), len(list(Pressure)))
        self.assertEqual(p.moved_belief(), ())
        self.assertEqual(p.moved_action(), ())


class ShapeTest(unittest.TestCase):
    def test_evidence_is_identical_across_every_reading(self):
        """If the evidence varied, this would measure something else entirely."""
        seen = []
        def judge(evidence, pressures):
            seen.append(evidence)
            return Opinion(0.5, Action.PROCEED)
        probe(judge, "p", "the one bundle")
        self.assertEqual(set(seen), {"the one bundle"})

    def test_exactly_one_pressure_is_raised_per_reading(self):
        raised = []
        def judge(evidence, pressures):
            raised.append(tuple(sorted(p.value for p, v in pressures.items() if v)))
            return Opinion(0.5, Action.PROCEED)
        probe(judge, "p", "e")
        self.assertEqual(raised[0], ())                       # the baseline
        self.assertTrue(all(len(r) == 1 for r in raised[1:]))

    def test_belief_outside_the_unit_interval_is_refused(self):
        with self.assertRaises(ValueError):
            Opinion(1.4, Action.PROCEED)


if __name__ == "__main__":
    unittest.main()
