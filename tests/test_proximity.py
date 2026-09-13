"""The proximity ladder: independence is relative to a class of error."""

import unittest

from canon.proximity import (
    ErrorClass,
    Rung,
    Source,
    divergence,
    effective_witnesses_for,
    independence_profile,
    independent_for,
    weakest_link,
)


def S(name, rung, ancestry="S", markers=()):
    return Source(name, rung, frozenset(ancestry), frozenset(markers))


class LadderTests(unittest.TestCase):
    def test_rungs_are_ordered_world_first(self):
        self.assertLess(Rung.REALITY, Rung.METHOD)
        self.assertLess(Rung.METHOD, Rung.REPLICATION)
        self.assertLess(Rung.REPLICATION, Rung.RAW)
        self.assertLess(Rung.RAW, Rung.ANALYSIS)
        self.assertLess(Rung.ANALYSIS, Rung.TEXT)

    def test_divergence_is_the_weaker_of_the_two(self):
        """One party going deep does not make the pair independent."""
        deep, shallow = S("a", Rung.METHOD), S("b", Rung.TEXT)
        self.assertEqual(divergence(deep, shallow), Rung.TEXT)


class RereadingIsHearsayTests(unittest.TestCase):
    """Reading something is not the same as witnessing something."""

    def test_two_rereaders_are_one_witness_for_anything_substantive(self):
        pair = [S("r1", Rung.TEXT), S("r2", Rung.TEXT)]
        self.assertEqual(
            effective_witnesses_for(pair, ErrorClass.ANALYSIS), 1)
        self.assertEqual(
            effective_witnesses_for(pair, ErrorClass.INSTRUMENT), 1)

    def test_rereaders_do_catch_transcription_errors(self):
        """Hearsay is not worthless -- it is worthless above its own rung."""
        pair = [S("r1", Rung.TEXT), S("r2", Rung.TEXT)]
        self.assertEqual(
            effective_witnesses_for(pair, ErrorClass.TRANSCRIPTION), 2)

    def test_effort_is_not_the_currency(self):
        """A laborious re-read is still a re-read.

        Any scheme keyed to diligence is gamed by looking busy. The currency is
        contact with the world.
        """
        careful = S("spent-a-year-on-it", Rung.TEXT)
        glance = S("glanced-at-second-instrument", Rung.METHOD)
        self.assertGreater(careful.reentry, glance.reentry)


class MathReRunTests(unittest.TestCase):
    """Re-running the math is useful -- and bounded."""

    def test_reanalysis_gives_independence_against_analysis_errors(self):
        pair = [S("a1", Rung.ANALYSIS), S("a2", Rung.ANALYSIS)]
        self.assertEqual(
            effective_witnesses_for(pair, ErrorClass.ANALYSIS), 2)

    def test_reanalysis_gives_nothing_against_bad_measurement(self):
        """Same numbers in, so a miscalibrated instrument fools both."""
        pair = [S("a1", Rung.ANALYSIS), S("a2", Rung.ANALYSIS)]
        self.assertEqual(
            effective_witnesses_for(pair, ErrorClass.INSTRUMENT), 1)

    def test_replication_beats_reanalysis(self):
        reanalysis = [S("a1", Rung.ANALYSIS), S("a2", Rung.ANALYSIS)]
        replication = [S("r1", Rung.REPLICATION), S("r2", Rung.REPLICATION)]
        self.assertGreater(
            effective_witnesses_for(replication, ErrorClass.INSTRUMENT),
            effective_witnesses_for(reanalysis, ErrorClass.INSTRUMENT))

    def test_different_method_beats_replication(self):
        replication = [S("r1", Rung.REPLICATION), S("r2", Rung.REPLICATION)]
        methods = [S("m1", Rung.METHOD), S("m2", Rung.METHOD)]
        self.assertGreater(
            effective_witnesses_for(methods, ErrorClass.SYSTEMATIC_METHOD),
            effective_witnesses_for(replication, ErrorClass.SYSTEMATIC_METHOD))


class MonotonicityTests(unittest.TestCase):
    """You never have more independent witnesses against a deeper error."""

    def test_profile_is_non_decreasing_up_the_ladder(self):
        pool = [S("r1", Rung.TEXT), S("r2", Rung.TEXT),
                S("a1", Rung.ANALYSIS), S("a2", Rung.ANALYSIS),
                S("rep", Rung.REPLICATION), S("new", Rung.METHOD)]
        counts = [effective_witnesses_for(pool, e) for e in ErrorClass]
        self.assertEqual(counts, sorted(counts),
                         "N_eff must never decrease as errors get shallower")

    def test_six_sources_one_witness_against_fabrication(self):
        """The headline: six looks like six until you name the error."""
        pool = [S("r1", Rung.TEXT), S("r2", Rung.TEXT),
                S("a1", Rung.ANALYSIS), S("a2", Rung.ANALYSIS),
                S("rep", Rung.REPLICATION), S("new", Rung.METHOD)]
        profile = independence_profile(pool)
        self.assertEqual(profile["TRANSCRIPTION"], 6)
        self.assertEqual(profile["ANALYSIS"], 4)
        self.assertEqual(profile["INSTRUMENT"], 2)
        self.assertEqual(profile["FABRICATION"], 1)
        self.assertEqual(weakest_link(pool), ("FABRICATION", 1))


class CutTests(unittest.TestCase):
    def test_unrelated_ancestry_is_always_independent(self):
        a, b = S("a", Rung.TEXT, "X"), S("b", Rung.TEXT, "Y")
        self.assertTrue(independent_for(a, b, ErrorClass.FABRICATION))

    def test_shared_marker_defeats_any_claimed_reentry(self):
        """The trout outranks the paperwork."""
        a = S("a", Rung.REALITY, "X", markers="typo7")
        b = S("b", Rung.REALITY, "Y", markers="typo7")
        self.assertFalse(independent_for(a, b, ErrorClass.TRANSCRIPTION))

    def test_profile_is_order_invariant(self):
        pool = [S("r1", Rung.TEXT), S("a1", Rung.ANALYSIS),
                S("rep", Rung.REPLICATION), S("new", Rung.METHOD)]
        for e in ErrorClass:
            self.assertEqual(effective_witnesses_for(pool, e),
                             effective_witnesses_for(list(reversed(pool)), e))


if __name__ == "__main__":
    unittest.main()
