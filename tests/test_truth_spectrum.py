"""Where a claim sits on the ladder, and what stops it climbing.

The criteria this was built against: the ladder must be cumulative, so a
mechanistic story for an unreplicated phenomenon must not score as a mechanism;
and the spectrum must not be confusable with the proximity ladder, which grades a
different thing.
"""

import unittest

from canon.proximity import Rung
from canon.truth_spectrum import REQUIREMENT, Level, Support, assess


class LadderTest(unittest.TestCase):
    def test_the_wheel_sits_at_bounded_ontology(self):
        """ORIGINS records the wheel as level three, possibly four."""
        s = assess("Monascus fermentation increases the camphor note",
                   Support(observed=True, recorded_in_words=True,
                           vocabulary_declared=True))
        self.assertIs(s.level, Level.BOUNDED_ONTOLOGY)
        self.assertEqual(s.level.value, 3)
        self.assertIs(s.next_level, Level.CALIBRATED)
        self.assertIn("independent observers", s.binding_constraint)

    def test_a_second_panel_agreeing_moves_it_to_four(self):
        s = assess("same claim",
                   Support(observed=True, recorded_in_words=True,
                           vocabulary_declared=True,
                           independent_observers_agreed=True))
        self.assertIs(s.level, Level.CALIBRATED)

    def test_nothing_observed_is_raw_state(self):
        s = assess("a thing is so", Support())
        self.assertIs(s.level, Level.RAW_STATE)
        self.assertIn("somebody observed it", s.binding_constraint)


class CumulativeTest(unittest.TestCase):
    """The failure the ladder exists to catch."""

    def setUp(self):
        # A mechanism and an invariance result, for something two observers have
        # never agreed on. Real work; it does not lift the claim past the gap.
        self.s = assess(
            "unanimous detectors are trustworthy",
            Support(observed=True, recorded_in_words=True,
                    vocabulary_declared=True,
                    independent_observers_agreed=False,
                    mechanism_given=True,
                    survived_representation_change=True),
        )

    def test_a_mechanism_does_not_lift_a_claim_over_a_missing_rung(self):
        self.assertIs(self.s.level, Level.BOUNDED_ONTOLOGY)
        self.assertIsNot(self.s.level, Level.MECHANISM)

    def test_the_work_done_above_the_gap_is_named_rather_than_ignored(self):
        """Silently dropping it would let a summary imply it counted."""
        self.assertEqual(len(self.s.claimed_beyond), 2)
        self.assertIn("mechanistic account", " ".join(self.s.claimed_beyond))
        self.assertIn("does not count yet", self.s.report())

    def test_the_top_of_the_ladder_has_no_binding_constraint(self):
        s = assess("holds", Support(**{f.name: True for f in Support.__dataclass_fields__.values()}))
        self.assertIs(s.level, Level.INVARIANT)
        self.assertEqual(s.binding_constraint, "")


class NotTheProximityLadderTest(unittest.TestCase):
    """Two axes. Confusing them would make a single original experiment look
    either maximally or minimally established depending on which was read."""

    def test_one_original_experiment_is_top_of_proximity_and_low_here(self):
        self.assertEqual(Rung.REALITY.value, 0)  # strongest witness
        s = assess("measured it once", Support(observed=True, recorded_in_words=True))
        self.assertIs(s.level, Level.NAMED_OBSERVATION)  # weak claim
        self.assertLess(s.level.value, Level.CALIBRATED.value)

    def test_the_two_enums_share_no_member_names(self):
        self.assertEqual(set(Level.__members__) & set(Rung.__members__), set())


class RequirementTableTest(unittest.TestCase):
    def test_every_level_above_raw_state_has_a_stated_requirement(self):
        expected = {lvl for lvl in Level if lvl is not Level.RAW_STATE}
        self.assertEqual(set(REQUIREMENT), expected)

    def test_an_empty_claim_is_refused(self):
        with self.assertRaises(ValueError):
            assess("", Support(observed=True))


if __name__ == "__main__":
    unittest.main()
