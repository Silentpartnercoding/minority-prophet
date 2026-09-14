"""IndependenceBasis decomposed into two axes."""

import unittest

from aggregation.independence_axes import (
    DECOMPOSITION,
    Attestation,
    DepthBasis,
    admissible_depth,
    effective_basis,
    IndependenceAxes,
    WitnessDepth,
    WitnessIdentity,
    decompose,
    legacy_basis,
    rank_inversion_witness,
)
from aggregation.root_vote import BASIS_RANK, IndependenceBasis


class InversionTests(unittest.TestCase):
    """The concrete failure a single rank produces."""

    def test_legacy_rank_puts_notarised_hearsay_above_an_eyewitness(self):
        """The retired constant still says so, which is why nothing reads it."""
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
        shallow_but_vouched = IndependenceAxes(
            WitnessDepth.TEXT, Attestation.ADVERSARIAL,
            WitnessIdentity.ANONYMOUS, DepthBasis.DEVICE_ATTESTED)
        deep_unvouched = IndependenceAxes(
            WitnessDepth.REALITY, Attestation.NONE,
            WitnessIdentity.ANONYMOUS, DepthBasis.ARTIFACT)
        self.assertFalse(shallow_but_vouched.dominates(deep_unvouched))

    def test_depth_does_not_buy_vouching(self):
        deep_unvouched = IndependenceAxes(
            WitnessDepth.REALITY, Attestation.NONE,
            WitnessIdentity.ANONYMOUS, DepthBasis.ARTIFACT)
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


class DepthBasisTests(unittest.TestCase):
    """A stated depth is worth what its backing is worth."""

    def test_an_unbacked_eyewitness_claim_is_hearsay(self):
        """Not a regression of the inversion -- an honest reading of it.

        "I was there" costs nothing, so an adversary says it as readily as an
        honest witness. Granted TEXT, which is what a bare assertion has always
        been worth.
        """
        bare = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                WitnessIdentity.ANONYMOUS, DepthBasis.DECLARED)
        self.assertEqual(bare.admissible, WitnessDepth.TEXT)

    def test_a_backed_eyewitness_keeps_its_depth(self):
        backed = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                  WitnessIdentity.ANONYMOUS,
                                  DepthBasis.DEVICE_ATTESTED)
        self.assertEqual(backed.admissible, WitnessDepth.REALITY)

    def test_overclaiming_buys_nothing(self):
        for basis in DepthBasis:
            claimed = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                       WitnessIdentity.ANONYMOUS, basis)
            honest = IndependenceAxes(claimed.admissible, Attestation.NONE,
                                      WitnessIdentity.ANONYMOUS, basis)
            self.assertEqual(claimed.admissible, honest.admissible)

    def test_underclaiming_is_honoured(self):
        """Strong backing on a modest claim does not inflate it."""
        modest = IndependenceAxes(WitnessDepth.TEXT, Attestation.NONE,
                                  WitnessIdentity.ANONYMOUS,
                                  DepthBasis.DEVICE_ATTESTED)
        self.assertEqual(modest.admissible, WitnessDepth.TEXT)

    def test_claiming_to_have_only_read_it_needs_no_backing(self):
        """A claim against interest: nobody lies to look weaker. That is the
        hearsay exception, from the same source as proximate cause."""
        self.assertEqual(
            IndependenceAxes(WitnessDepth.TEXT, Attestation.NONE,
                             WitnessIdentity.ANONYMOUS,
                             DepthBasis.DECLARED).admissible,
            WitnessDepth.TEXT)

    def test_the_ladder_is_monotone(self):
        granted = [IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                    WitnessIdentity.ANONYMOUS, b).admissible
                   for b in DepthBasis]
        self.assertEqual(granted, sorted(granted, reverse=True),
                         "stronger backing must never grant a shallower depth")


class OathTests(unittest.TestCase):
    """Sworn testimony carries no artifact and is still strong evidence.

    Owner review raised it; the resolution is that the oath is not an exception
    to the cost rule but another way of paying it. An artifact is expensive to
    fabricate; sworn testimony is expensive to be caught on. The teeth are the
    perjury statute, not the ceremony.
    """

    @staticmethod
    def _sworn(identity, reference="Case 2026-CV-118"):
        return IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                identity, DepthBasis.DECLARED, reference)

    def test_a_resolved_bond_gets_full_depth_with_no_artifact(self):
        sworn = self._sworn(WitnessIdentity.BONDED)
        self.assertEqual(
            admissible_depth(sworn.depth, sworn.depth_basis,
                             sworn.honoured_identity_with(lambda r: True)),
            WitnessDepth.REALITY)

    def test_an_anonymous_oath_stakes_nothing(self):
        """Nobody to prosecute, so nothing is risked, so nothing is earned.

        The model predicts why anonymous testimony is generally inadmissible
        rather than merely accommodating it.
        """
        self.assertEqual(self._sworn(WitnessIdentity.ANONYMOUS).admissible,
                         WitnessDepth.TEXT)

    def test_a_pseudonym_stakes_nothing_either(self):
        """Reputation without enforcement is not exposure."""
        self.assertEqual(self._sworn(WitnessIdentity.PSEUDONYMOUS).admissible,
                         WitnessDepth.TEXT)

    def test_exposure_scales_the_depth_it_supports(self):
        granted = [admissible_depth(a.depth, a.depth_basis,
                                    a.honoured_identity_with(lambda r: True))
                   for a in (self._sworn(i) for i in WitnessIdentity)]
        self.assertEqual(granted, sorted(granted, reverse=True),
                         "more at stake must never support a shallower claim")

    def test_stake_and_artifact_are_alternative_payments(self):
        """Either route reaches REALITY; neither is required if the other holds."""
        by_stake = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                    WitnessIdentity.BONDED, DepthBasis.DECLARED,
                                    "Case 2026-CV-118")
        resolved = admissible_depth(by_stake.depth, by_stake.depth_basis,
                                    by_stake.honoured_identity_with(lambda r: True))
        by_artifact = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                       WitnessIdentity.ANONYMOUS,
                                       DepthBasis.DEVICE_ATTESTED)
        self.assertEqual(resolved, WitnessDepth.REALITY)
        self.assertEqual(by_artifact.admissible, WitnessDepth.REALITY)

    def test_the_stronger_of_the_two_payments_is_used(self):
        self.assertEqual(
            effective_basis(DepthBasis.DECLARED, WitnessIdentity.BONDED),
            DepthBasis.DEVICE_ATTESTED)
        self.assertEqual(
            effective_basis(DepthBasis.ARTIFACT, WitnessIdentity.ANONYMOUS),
            DepthBasis.ARTIFACT)


class StakeReferenceTests(unittest.TestCase):
    """Minority Prophet does not punish anyone -- it is the assayer, not the
    sheriff. `BONDED` records that a claim sits under someone else's
    consequence regime; it never creates one.

    Which makes the reference load-bearing. `BONDED` unlocks `REALITY` with no
    artifact, so a self-declared stake would be the cheapest lie in the system
    and the most valuable one.
    """

    @staticmethod
    def _bonded(reference):
        return IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                WitnessIdentity.BONDED, DepthBasis.DECLARED,
                                reference)

    def test_an_unreferenced_stake_is_not_honoured(self):
        self.assertEqual(self._bonded(None).honoured_identity,
                         WitnessIdentity.NAMED)

    def test_an_unreferenced_stake_does_not_unlock_reality(self):
        self.assertEqual(self._bonded(None).admissible, WitnessDepth.RAW)

    def test_the_three_tiers_are_ordered(self):
        absent = self._bonded(None).honoured_identity
        checkable = self._bonded("Case 1").honoured_identity
        checked = self._bonded("Case 1").honoured_identity_with(lambda r: True)
        self.assertLess(absent, checkable)
        self.assertLess(checkable, checked)

    def test_a_reference_alone_is_checkable_not_checked(self):
        """A bond IS checkable -- issuer, number, amount, expiry. But
        "checkable" and "checked" are different states, and collapsing them is
        how a disposition passes for a fact."""
        bonded = self._bonded("Case 2026-CV-118")
        self.assertEqual(bonded.honoured_identity, WitnessIdentity.VERIFIED)
        self.assertEqual(bonded.admissible, WitnessDepth.METHOD)

    def test_a_resolved_reference_is_honoured_in_full(self):
        bonded = self._bonded("Case 2026-CV-118")
        self.assertEqual(bonded.honoured_identity_with(lambda r: True),
                         WitnessIdentity.BONDED)

    def test_a_rejected_reference_falls_back_to_checkable(self):
        """Resolver says it does not exist: the claim still named something."""
        bonded = self._bonded("Case 2026-CV-118")
        self.assertEqual(bonded.honoured_identity_with(lambda r: False),
                         WitnessIdentity.VERIFIED)

    def test_no_resolver_means_nothing_resolves(self):
        """MP operates no registries. With none injected, fail closed."""
        self.assertEqual(self._bonded("Case 2026-CV-118").honoured_identity,
                         WitnessIdentity.VERIFIED)

    def test_whitespace_is_not_a_reference(self):
        self.assertEqual(self._bonded("   ").honoured_identity,
                         WitnessIdentity.NAMED)

    def test_verified_also_requires_a_reference(self):
        """Cryptographic binding is a claim about a key that must point at one."""
        unreferenced = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                        WitnessIdentity.VERIFIED,
                                        DepthBasis.DECLARED, None)
        self.assertEqual(unreferenced.honoured_identity, WitnessIdentity.NAMED)

    def test_weaker_identities_need_no_reference(self):
        """Claiming to be findable, or not to be, stakes nothing to check."""
        for identity in (WitnessIdentity.ANONYMOUS, WitnessIdentity.PSEUDONYMOUS,
                         WitnessIdentity.NAMED):
            axes = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                    identity, DepthBasis.DECLARED, None)
            self.assertEqual(axes.honoured_identity, identity)

    def test_an_artifact_still_works_without_any_stake(self):
        """The two payments stay independent: no reference needed to produce
        evidence, no evidence needed to be exposed."""
        by_artifact = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                       WitnessIdentity.ANONYMOUS,
                                       DepthBasis.DEVICE_ATTESTED, None)
        self.assertEqual(by_artifact.admissible, WitnessDepth.REALITY)
