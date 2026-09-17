"""The attestation policy: silence never grants independence.

The case these tests exist for is the one the whole decision-relative
independence series failed to solve by observation — two witnesses drawing on a
hidden source with nothing recorded connecting them. DR3 proves no rule reading
the record can detect it. These tests pin the alternative: fail closed instead of
asserting the favourable reading.
"""

import itertools
import unittest

from aggregation.attested_independence import (
    ScopeViolation,
    UnstatedDepth,
    Use,
    Witness,
    divergence,
    effective_witnesses_for,
    independence_profile,
    independent_for,
    unattested_exposure,
    witness_bounds,
)
from aggregation.independence_axes import DepthBasis, WitnessDepth, WitnessIdentity
from canon.proximity import ErrorClass, Rung, Source
from canon.proximity import independent_for as ladder_independent_for


def W(name, claimed=WitnessDepth.UNSTATED, basis=DepthBasis.DECLARED,
      identity=WitnessIdentity.ANONYMOUS, ancestry=(), markers=(), complete=False):
    return Witness(name, claimed, basis, identity,
                   frozenset(ancestry), frozenset(markers), complete)


def backed(name, claimed=WitnessDepth.REALITY, **kw):
    """A witness whose depth claim is backed by something it could not author.

    An artifact is not unlimited backing: `DEPTH_FLOOR` grants it `METHOD`, so a
    `REALITY` claim on a log alone is still granted `METHOD`.
    """
    return W(name, claimed, basis=DepthBasis.ARTIFACT, **kw)


def witnessed(name, **kw):
    """A witness that actually reaches `REALITY`: signed by a keyholding device.

    The only other way to reach it is `BONDED` identity — a stake somebody else
    can enforce. Nothing cheaper buys the bottom rung.
    """
    return W(name, WitnessDepth.REALITY, basis=DepthBasis.DEVICE_ATTESTED, **kw)


class HiddenSharedSourceTests(unittest.TestCase):
    """The unsolved case, closed by policy rather than by detection."""

    def test_the_ladder_grants_full_independence_on_an_empty_record(self):
        """The defect, stated as a test so the fix cannot be read as a tweak."""
        a = Source("a", Rung.TEXT, frozenset(), frozenset())
        b = Source("b", Rung.TEXT, frozenset(), frozenset())
        for error in ErrorClass:
            self.assertTrue(ladder_independent_for(a, b, error), error.name)

    def test_unattested_pair_earns_nothing_from_an_empty_record(self):
        a, b = W("a", WitnessDepth.TEXT), W("b", WitnessDepth.TEXT)
        for error in (ErrorClass.FABRICATION, ErrorClass.SYSTEMATIC_METHOD,
                      ErrorClass.INSTRUMENT, ErrorClass.PROCESSING,
                      ErrorClass.ANALYSIS):
            self.assertFalse(independent_for(a, b, error), error.name)

    def test_they_still_catch_the_error_their_depth_reaches(self):
        """Failing closed is not the same as counting for nothing."""
        a, b = W("a", WitnessDepth.TEXT), W("b", WitnessDepth.TEXT)
        self.assertTrue(independent_for(a, b, ErrorClass.TRANSCRIPTION))

    def test_declaring_completeness_earns_nothing(self):
        """A witness cannot certify an absence it cannot see.

        This asserted the opposite until AID-1. Two reporters may honestly
        believe they share no source while drinking from one well, so taking
        their word for the silence is the same inference from absence that this
        module exists to refuse — relocated into someone else's mouth.
        """
        a = W("a", WitnessDepth.TEXT, complete=True)
        b = W("b", WitnessDepth.TEXT, complete=True)
        self.assertFalse(independent_for(a, b, ErrorClass.FABRICATION))

    def test_completeness_cannot_rescue_an_adversary_either(self):
        """The hole it opened: say the words, skip the backing entirely."""
        a = W("a", WitnessDepth.REALITY, complete=True)
        b = W("b", WitnessDepth.REALITY, complete=True)
        self.assertFalse(independent_for(a, b, ErrorClass.FABRICATION))

    def test_one_side_attesting_completeness_is_not_enough(self):
        a = W("a", WitnessDepth.TEXT, complete=True)
        b = W("b", WitnessDepth.TEXT, complete=False)
        self.assertFalse(independent_for(a, b, ErrorClass.FABRICATION))

    def test_depth_earns_independence_with_no_ancestry_record_at_all(self):
        """Depth is the other way to pay, and it does not need the record.

        Two witnesses that each demonstrably went to the world are independent
        against fabrication whether or not anyone attested their ancestry. That
        is the point of the ladder, and the policy leaves it intact.
        """
        a, b = witnessed("a"), witnessed("b")
        self.assertTrue(independent_for(a, b, ErrorClass.FABRICATION))


class DeclarationIsFreeTests(unittest.TestCase):
    """A policy keyed to bare declarations rewards the witness it must discount."""

    def test_a_bare_reality_claim_is_worth_a_re_reading(self):
        claimant = W("loud", WitnessDepth.REALITY)
        self.assertIs(claimant.admissible, WitnessDepth.TEXT)

    def test_two_loud_claimants_are_one_witness_against_fabrication(self):
        pair = [W("a", WitnessDepth.REALITY), W("b", WitnessDepth.REALITY)]
        self.assertEqual(
            effective_witnesses_for(pair, ErrorClass.FABRICATION,
                                    use=Use.PERMIT_ACTION), 1)

    def test_backing_is_what_separates_them(self):
        pair = [witnessed("a"), witnessed("b")]
        self.assertEqual(
            effective_witnesses_for(pair, ErrorClass.FABRICATION,
                                    use=Use.PERMIT_ACTION), 2)

    def test_an_artifact_buys_method_not_reality(self):
        """Backing is graded too. A log proves you did something, not that you
        stood in the room, so it stops one rung short of the world."""
        logged = backed("logged", claimed=WitnessDepth.REALITY)
        self.assertIs(logged.admissible, WitnessDepth.METHOD)
        pair = [logged, backed("logged2", claimed=WitnessDepth.REALITY)]
        self.assertEqual(
            effective_witnesses_for(pair, ErrorClass.FABRICATION,
                                    use=Use.PERMIT_ACTION), 1)
        self.assertEqual(
            effective_witnesses_for(pair, ErrorClass.SYSTEMATIC_METHOD,
                                    use=Use.PERMIT_ACTION), 2)

    def test_an_unreferenced_bond_does_not_reach_the_world(self):
        """A stake is worth what someone else can enforce.

        This asserted `REALITY` until AID-1, because the module called
        `admissible_depth` directly and skipped the `honoured_identity` check
        sitting one import away. A bond with nothing to point at is honoured as
        a bare claim of identity, and buys what that is worth.
        """
        sworn = W("sworn", WitnessDepth.REALITY, identity=WitnessIdentity.BONDED)
        self.assertIsNot(sworn.admissible, WitnessDepth.REALITY)

    def test_a_referenced_bond_still_caps_below_the_world_with_no_resolver(self):
        """Checkable and checked are different states. No registry, no top tier."""
        sworn = Witness("sworn", WitnessDepth.REALITY, DepthBasis.DECLARED,
                        WitnessIdentity.BONDED, stake_reference="bond-12345")
        self.assertIsNot(sworn.admissible, WitnessDepth.REALITY)

    def test_a_device_attestation_still_reaches_the_world(self):
        """The repair must not break what worked: backing still pays."""
        self.assertIs(witnessed("device").admissible, WitnessDepth.REALITY)

    def test_underclaiming_is_honoured_not_inflated(self):
        modest = backed("modest", claimed=WitnessDepth.REPLICATION)
        self.assertIs(modest.admissible, WitnessDepth.REPLICATION)


class SilenceStaysSilenceTests(unittest.TestCase):
    """A5: an unstated depth is not the bottom rung, it is no rung."""

    def test_unstated_depth_is_not_text(self):
        self.assertFalse(W("quiet").has_depth)

    def test_a_witness_with_no_depth_is_independent_of_nobody(self):
        quiet, solid = W("quiet"), backed("solid", complete=True)
        for error in ErrorClass:
            self.assertFalse(independent_for(quiet, solid, error), error.name)

    def test_placing_it_on_the_ladder_is_refused_rather_than_guessed(self):
        with self.assertRaises(UnstatedDepth):
            W("quiet").rung

    def test_it_is_still_one_witness_on_its_own(self):
        """Denying independence is not deleting the source."""
        self.assertEqual(
            effective_witnesses_for([W("quiet")], ErrorClass.TRANSCRIPTION,
                                    use=Use.PERMIT_ACTION), 1)


class MarkersAndSharedAncestryTests(unittest.TestCase):
    def test_shared_marker_defeats_every_backing(self):
        a = backed("a", ancestry="X", markers="typo7", complete=True)
        b = backed("b", ancestry="Y", markers="typo7", complete=True)
        self.assertFalse(independent_for(a, b, ErrorClass.TRANSCRIPTION))

    def test_shared_ancestry_keeps_the_ladders_answer(self):
        a = W("a", WitnessDepth.ANALYSIS, basis=DepthBasis.ARTIFACT, ancestry="S")
        b = W("b", WitnessDepth.ANALYSIS, basis=DepthBasis.ARTIFACT, ancestry="S")
        self.assertTrue(independent_for(a, b, ErrorClass.ANALYSIS))
        self.assertFalse(independent_for(a, b, ErrorClass.INSTRUMENT))

    def test_completeness_cannot_override_recorded_shared_ancestry(self):
        """Attesting that the record is complete does not erase what it says."""
        a = W("a", WitnessDepth.TEXT, ancestry="S", complete=True)
        b = W("b", WitnessDepth.TEXT, ancestry="S", complete=True)
        self.assertFalse(independent_for(a, b, ErrorClass.INSTRUMENT))

    def test_divergence_is_the_weaker_of_the_two_admissible_depths(self):
        deep, shallow = backed("deep"), W("shallow", WitnessDepth.TEXT)
        self.assertEqual(divergence(deep, shallow), Rung.TEXT)


class NeverMorePermissiveTests(unittest.TestCase):
    """The policy may only ever remove independence, never add it."""

    def test_exhaustively_over_depth_backing_ancestry_and_completeness(self):
        depths = [WitnessDepth.REALITY, WitnessDepth.REPLICATION,
                  WitnessDepth.ANALYSIS, WitnessDepth.TEXT]
        bases = [DepthBasis.DECLARED, DepthBasis.ARTIFACT,
                 DepthBasis.DEVICE_ATTESTED]
        ancestries = [(), ("S",)]
        checked = 0
        for (da, ba, aa, ca), (db, bb, ab, cb) in itertools.product(
                itertools.product(depths, bases, ancestries, (False, True)),
                repeat=2):
            a = W("a", da, basis=ba, ancestry=aa, complete=ca)
            b = W("b", db, basis=bb, ancestry=ab, complete=cb)
            ladder_a = Source("a", Rung(int(da)), frozenset(aa), frozenset())
            ladder_b = Source("b", Rung(int(db)), frozenset(ab), frozenset())
            for error in ErrorClass:
                if independent_for(a, b, error):
                    self.assertTrue(
                        ladder_independent_for(ladder_a, ladder_b, error),
                        f"policy more permissive than the ladder: "
                        f"{a} {b} {error.name}")
                checked += 1
        self.assertGreater(checked, 1000)

    def test_and_it_is_strictly_stricter_somewhere(self):
        """Otherwise the policy is a no-op dressed as a fix."""
        a, b = W("a", WitnessDepth.TEXT), W("b", WitnessDepth.TEXT)
        ladder_a = Source("a", Rung.TEXT, frozenset(), frozenset())
        ladder_b = Source("b", Rung.TEXT, frozenset(), frozenset())
        self.assertTrue(ladder_independent_for(ladder_a, ladder_b,
                                               ErrorClass.FABRICATION))
        self.assertFalse(independent_for(a, b, ErrorClass.FABRICATION))


class ProfileTests(unittest.TestCase):
    def test_profile_never_decreases_as_errors_get_shallower(self):
        pool = [W("r1", WitnessDepth.TEXT, complete=True),
                W("r2", WitnessDepth.TEXT, complete=True),
                W("a1", WitnessDepth.ANALYSIS, basis=DepthBasis.ARTIFACT,
                  complete=True),
                backed("m1", complete=True),
                W("quiet")]
        counts = [independence_profile(pool)[e.name] for e in ErrorClass]
        self.assertEqual(counts, sorted(counts))

    def test_profile_is_order_invariant(self):
        pool = [backed("m1", complete=True),
                W("a1", WitnessDepth.ANALYSIS, basis=DepthBasis.ARTIFACT),
                W("r1", WitnessDepth.TEXT), W("quiet")]
        self.assertEqual(independence_profile(pool),
                         independence_profile(list(reversed(pool))))


class ScopeTests(unittest.TestCase):
    """The policy deflates counts, so one direction of use is an attack."""

    def test_counting_to_decide_a_claims_survival_is_refused(self):
        pool = [W("a", WitnessDepth.TEXT), W("b", WitnessDepth.TEXT)]
        with self.assertRaises(ScopeViolation):
            effective_witnesses_for(pool, ErrorClass.FABRICATION,
                                    use=Use.DECIDE_SURVIVAL)

    def test_the_use_must_be_stated(self):
        with self.assertRaises(TypeError):
            effective_witnesses_for([], ErrorClass.FABRICATION)


class BoundsTests(unittest.TestCase):
    """A range, because one number cannot serve two opposite conservatisms."""

    def test_earned_independence_is_the_lower_bound_and_the_ladder_the_upper(self):
        pair = [W("a", WitnessDepth.TEXT), W("b", WitnessDepth.TEXT)]
        bounds = witness_bounds(pair, ErrorClass.FABRICATION)
        self.assertEqual((bounds.lower, bounds.upper), (1, 2))
        self.assertFalse(bounds.determined)

    def test_backed_witnesses_determine_the_count(self):
        pair = [witnessed("a"), witnessed("b")]
        bounds = witness_bounds(pair, ErrorClass.FABRICATION)
        self.assertTrue(bounds.determined)
        self.assertEqual(bounds.lower, 2)

    def test_a_shared_marker_determines_it_the_other_way(self):
        pair = [witnessed("a", markers="typo7"), witnessed("b", markers="typo7")]
        bounds = witness_bounds(pair, ErrorClass.FABRICATION)
        self.assertTrue(bounds.determined)
        self.assertEqual(bounds.upper, 1)

    def test_the_bound_never_inverts(self):
        for pool in ([W("q")], [W("a", WitnessDepth.TEXT), witnessed("b")],
                     [witnessed("a"), W("b"), W("c", WitnessDepth.ANALYSIS)]):
            for error in ErrorClass:
                bounds = witness_bounds(pool, error)
                self.assertLessEqual(bounds.lower, bounds.upper)

    def test_the_suppression_case_is_refused_instead_of_settled(self):
        """AID-1's failure, as a unit test.

        An attested majority asserting a falsehood against an unattestable
        minority carrying the truth. The point estimate deflated the minority
        and settled against it. The range does not: the majority is determined
        at three, the minority runs from one to three, so at one end the
        majority carries it and at the other the sides are level. The decision
        differs across the range, which means the evidence does not decide it.
        """
        majority = [witnessed(f"m{i}") for i in range(3)]
        minority = [W(f"n{i}", WitnessDepth.REALITY) for i in range(3)]
        maj = witness_bounds(majority, ErrorClass.FABRICATION)
        mino = witness_bounds(minority, ErrorClass.FABRICATION)
        self.assertEqual((maj.lower, maj.upper), (3, 3))
        self.assertEqual((mino.lower, mino.upper), (1, 3))
        majority_wins_at_lower = maj.lower > mino.lower
        majority_wins_at_upper = maj.upper > mino.upper
        self.assertTrue(majority_wins_at_lower)
        self.assertFalse(majority_wins_at_upper)
        self.assertNotEqual(majority_wins_at_lower, majority_wins_at_upper)


class ExposureTests(unittest.TestCase):
    """Policy C: if the unattested are counted anyway, publish the number."""

    def test_it_counts_what_the_policy_would_have_discounted(self):
        pool = [witnessed("solid", complete=True),
                W("loud", WitnessDepth.REALITY),
                W("quiet")]
        self.assertEqual(unattested_exposure(pool), {
            "witnesses": 3,
            "no_admissible_depth": 1,
            "ancestry_not_attested": 2,
            "overclaimed_depth": 1,
        })


if __name__ == "__main__":
    unittest.main()
