"""A brake that stops a conclusion it believes is correct.

The criterion this was built against: the brake can fire on a conclusion the
system believes is correct, for a stated reason that is not uncertainty.
"""

import unittest

from canon.reflexive_brake import (
    CONFIDENT, Firing, Footprint, Reflexive, Stance, check,
)

REACHES = {
    Reflexive.FOOTPRINT_EXCEEDS_MANDATE:
        Footprint(Stance.INTERVENTION, ("a third party",), within_declared_domain=False),
    Reflexive.FORECAST_CONFIRMS_OUR_OWN_EFFECT:
        Footprint(Stance.POST_INTERVENTION_FORECAST, ("the operator",)),
    Reflexive.OBSERVATION_IS_INTERVENTION:
        Footprint(Stance.PREDICTION, ("the subject",), measuring_disturbs_the_subject=True),
    Reflexive.SELF_INVALIDATING:
        Footprint(Stance.PREDICTION, ("the subject",), subject_can_observe_us=True),
    Reflexive.SELF_FULFILLING:
        Footprint(Stance.INTERVENTION, ("the market",), subject_can_observe_us=True),
}


class NotAnUncertaintyStopTest(unittest.TestCase):
    def test_it_fires_on_a_conclusion_held_confidently(self):
        f = check(0.93, REACHES[Reflexive.FORECAST_CONFIRMS_OUR_OWN_EFFECT])
        self.assertIsInstance(f, Firing)
        self.assertGreaterEqual(f.belief, CONFIDENT)
        self.assertIn("NOT being disputed", f.report())
        self.assertIn("not an uncertainty stop", f.report())

    def test_it_is_silent_exactly_where_an_uncertainty_stop_would_speak(self):
        """Deferring below the threshold is the boundary, not an oversight: a
        brake indistinguishable from the uncertainty machinery adds nothing."""
        for reason, fp in REACHES.items():
            self.assertIsNone(check(CONFIDENT - 0.01, fp), reason)

    def test_no_severity_score_is_exposed(self):
        f = check(0.9, REACHES[Reflexive.SELF_INVALIDATING])
        for banned in ("severity", "score", "harm", "magnitude"):
            self.assertFalse(hasattr(f, banned), f"Firing exposes {banned}")

    def test_a_firing_names_who_bears_the_cost_and_what_releases_it(self):
        """Decomposing 'materially unsafe' rather than asserting it."""
        f = check(0.9, REACHES[Reflexive.FOOTPRINT_EXCEEDS_MANDATE])
        self.assertEqual(f.bears_the_cost, ("a third party",))
        self.assertTrue(f.releases_when)


class ReachabilityTest(unittest.TestCase):
    def test_every_reason_is_reachable(self):
        """A brake with a reason it can never give is the wheel's defect: a cell
        that exists and can never be filled. See canon/WHEEL-WORKED-EXAMPLE.md."""
        self.assertEqual(set(REACHES), set(Reflexive))
        for reason, fp in REACHES.items():
            f = check(0.9, fp)
            self.assertIsNotNone(f, reason)
            self.assertIs(f.reason, reason)


class StanceTest(unittest.TestCase):
    def test_the_three_stances_are_distinct(self):
        self.assertEqual(len(list(Stance)), 3)

    def test_a_forecast_made_after_intervening_is_not_an_ordinary_prediction(self):
        """The reflexive case: a forecast about a world we already altered."""
        after = check(0.9, Footprint(Stance.POST_INTERVENTION_FORECAST, ("x",)))
        plain = check(0.9, Footprint(Stance.PREDICTION, ("x",)))
        self.assertIs(after.reason, Reflexive.FORECAST_CONFIRMS_OUR_OWN_EFFECT)
        self.assertIsNone(plain)

    def test_observation_disturbance_is_distinct_from_the_subject_reading_us(self):
        """Withholding the output helps in one case and not the other."""
        disturb = check(0.9, Footprint(Stance.PREDICTION, ("x",),
                                       measuring_disturbs_the_subject=True))
        reacts = check(0.9, Footprint(Stance.PREDICTION, ("x",),
                                      subject_can_observe_us=True))
        self.assertIs(disturb.reason, Reflexive.OBSERVATION_IS_INTERVENTION)
        self.assertIs(reacts.reason, Reflexive.SELF_INVALIDATING)

    def test_a_confident_conclusion_with_no_footprint_does_not_fire(self):
        """The brake must not fire on everything, or it is not a brake."""
        self.assertIsNone(check(0.99, Footprint(Stance.PREDICTION, ("x",))))

    def test_belief_outside_the_unit_interval_is_refused(self):
        with self.assertRaises(ValueError):
            check(1.2, Footprint(Stance.PREDICTION))


if __name__ == "__main__":
    unittest.main()
