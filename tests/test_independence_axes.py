"""IndependenceBasis decomposed into two axes."""

import unittest

from aggregation.independence_axes import (
    DECOMPOSITION,
    Attestation,
    IndependenceAxes,
    WitnessDepth,
    decompose,
    legacy_basis,
    rank_inversion_witness,
)
from aggregation.root_vote import BASIS_RANK, IndependenceBasis


class InversionTests(unittest.TestCase):
    """The concrete failure a single rank produces."""

    def test_legacy_rank_puts_notarised_hearsay_above_an_eyewitness(self):
        self.assertGreater(BASIS_RANK[IndependenceBasis.ATTESTED],
                           BASIS_RANK[IndependenceBasis.INFERRED])

    def test_on_the_axes_they_are_incomparable(self):
        hearsay, eyewitness = rank_inversion_witness()
        self.assertFalse(hearsay.dominates(eyewitness))
        self.assertFalse(eyewitness.dominates(hearsay))
        self.assertFalse(hearsay.comparable_to(eyewitness))

    def test_each_is_better_on_exactly_one_axis(self):
        hearsay, eyewitness = rank_inversion_witness()
        self.assertGreater(hearsay.attestation, eyewitness.attestation)
        self.assertLess(eyewitness.depth, hearsay.depth)


class AxisIndependenceTests(unittest.TestCase):
    def test_vouching_does_not_buy_depth(self):
        shallow_but_vouched = IndependenceAxes(WitnessDepth.TEXT,
                                               Attestation.ADVERSARIAL)
        deep_unvouched = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE)
        self.assertFalse(shallow_but_vouched.dominates(deep_unvouched))

    def test_depth_does_not_buy_vouching(self):
        deep_unvouched = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE)
        shallow_vouched = IndependenceAxes(WitnessDepth.TEXT,
                                           Attestation.INDEPENDENT)
        self.assertFalse(deep_unvouched.dominates(shallow_vouched))

    def test_better_on_both_axes_dominates(self):
        better = IndependenceAxes(WitnessDepth.REALITY, Attestation.INDEPENDENT)
        worse = IndependenceAxes(WitnessDepth.TEXT, Attestation.SELF)
        self.assertTrue(better.dominates(worse))
        self.assertFalse(worse.dominates(better))

    def test_identical_axes_dominate_each_other(self):
        a = IndependenceAxes(WitnessDepth.RAW, Attestation.SELF)
        self.assertTrue(a.dominates(a))


class DecompositionTests(unittest.TestCase):
    def test_every_legacy_value_decomposes(self):
        for basis in IndependenceBasis:
            self.assertIn(basis, DECOMPOSITION)

    def test_attested_and_declared_differ_only_in_who_vouched(self):
        a = decompose(IndependenceBasis.ATTESTED)
        d = decompose(IndependenceBasis.DECLARED)
        self.assertEqual(a.depth, d.depth)
        self.assertNotEqual(a.attestation, d.attestation)

    def test_three_of_four_legacy_values_carry_no_depth(self):
        """The vocabulary was silent about depth, and silence is recorded."""
        unstated = [b for b in IndependenceBasis
                    if decompose(b).depth is WitnessDepth.UNSTATED]
        self.assertEqual(len(unstated), 3)

    def test_inferred_is_the_only_one_that_states_a_depth(self):
        self.assertEqual(decompose(IndependenceBasis.INFERRED).depth,
                         WitnessDepth.TEXT)

    def test_silence_is_never_defaulted_to_a_depth(self):
        """ASSAYER A5: report the gap, do not fill it in."""
        self.assertNotEqual(decompose(IndependenceBasis.UNKNOWN).depth,
                            WitnessDepth.TEXT)


class WireCompatibilityTests(unittest.TestCase):
    """The vocabulary shared byte-for-byte with invention_engine is untouched."""

    def test_legacy_vocabulary_is_unchanged(self):
        self.assertEqual([b.value for b in IndependenceBasis],
                         ["attested", "declared", "inferred", "unknown"])

    def test_legacy_rank_is_unchanged(self):
        self.assertEqual(BASIS_RANK[IndependenceBasis.UNKNOWN], 0)
        self.assertEqual(BASIS_RANK[IndependenceBasis.ATTESTED], 3)

    def test_projection_back_to_the_wire_is_stable_on_attestation(self):
        for basis in (IndependenceBasis.ATTESTED, IndependenceBasis.DECLARED):
            self.assertEqual(legacy_basis(decompose(basis)), basis)

    def test_depth_cannot_survive_the_round_trip(self):
        """Lossy by construction: the wire format has nowhere to put depth."""
        eyewitness = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE)
        recovered = decompose(legacy_basis(eyewitness))
        self.assertNotEqual(recovered.depth, WitnessDepth.REALITY)


if __name__ == "__main__":
    unittest.main()


class MissingTopTests(unittest.TestCase):
    """The hole owner review found: the vocabulary has no word for 'I was there'.

    `inferred` is the only legacy value carrying a depth, and it carries the
    *shallowest* one. There is no encoding for a root that reached reality, so
    the strongest possible evidence has nowhere to go.
    """

    def test_no_legacy_value_means_observed_reality(self):
        for basis in IndependenceBasis:
            self.assertNotEqual(decompose(basis).depth, WitnessDepth.REALITY,
                                f"{basis.value} unexpectedly encodes REALITY")

    def test_the_only_stated_depth_is_the_worst_one(self):
        stated = [decompose(b).depth for b in IndependenceBasis
                  if decompose(b).depth is not WitnessDepth.UNSTATED]
        self.assertEqual(stated, [WitnessDepth.TEXT])

    def test_an_eyewitness_and_a_reasoning_model_encode_identically(self):
        """The collapse, stated as a fact.

        Someone who was in the room and a model that reasoned over text both
        become `inferred`, rank 1. The wire format cannot tell them apart.
        """
        eyewitness = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE)
        reasoning = IndependenceAxes(WitnessDepth.TEXT, Attestation.NONE)
        self.assertEqual(legacy_basis(eyewitness), legacy_basis(reasoning))
        self.assertEqual(legacy_basis(eyewitness), "inferred")

    def test_witnessing_reality_is_not_expressible_at_any_attestation(self):
        """Adding a testament does not rescue it -- it overwrites the depth."""
        for attestation in Attestation:
            axes = IndependenceAxes(WitnessDepth.REALITY, attestation)
            recovered = decompose(legacy_basis(axes))
            self.assertNotEqual(recovered.depth, WitnessDepth.REALITY)
