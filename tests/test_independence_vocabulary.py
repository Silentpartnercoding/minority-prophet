"""Conformance test for the independence vocabulary shared with Invention Graph.

The literals below ARE the contract. The matching test lives at
`tests/test_independence_vocabulary.py` in invention-graph and asserts the same
strings. If either project edits its enum, both tests fail -- which is the point:
"aligned byte-for-byte" is only true if something checks it.
"""

import unittest

from aggregation.independence_axes import (
    ATTESTATION_WIRE,
    DEPTH_WIRE,
    IDENTITY_WIRE,
    INDEPENDENCE_VOCABULARY_VERSION,
    Attestation,
    IndependenceAxes,
    VocabularyError,
    WitnessDepth,
    WitnessIdentity,
    from_wire,
    indistinguishable,
    to_wire,
    vocabulary_coverage,
)
from aggregation.root_vote import IndependenceBasis

#: Duplicated verbatim in the invention-graph test.
CONTRACT_VERSION = 3
CONTRACT_BASIS = ["attested", "declared", "inferred", "unknown"]
CONTRACT_DEPTH = ["reality", "method", "replication", "raw", "analysis",
                  "text", "unstated"]
CONTRACT_ATTESTATION = ["none", "self", "internal", "independent", "adversarial"]
CONTRACT_IDENTITY = ["anonymous", "pseudonymous", "named", "verified", "bonded"]


class VocabularyConformanceTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(INDEPENDENCE_VOCABULARY_VERSION, CONTRACT_VERSION)

    def test_v1_basis_is_unchanged(self):
        self.assertEqual([b.value for b in IndependenceBasis], CONTRACT_BASIS)

    def test_depth_vocabulary(self):
        self.assertEqual([DEPTH_WIRE[d] for d in WitnessDepth], CONTRACT_DEPTH)

    def test_attestation_vocabulary(self):
        self.assertEqual([ATTESTATION_WIRE[a] for a in Attestation],
                         CONTRACT_ATTESTATION)

    def test_identity_vocabulary(self):
        self.assertEqual([IDENTITY_WIRE[i] for i in WitnessIdentity],
                         CONTRACT_IDENTITY)

    def test_wire_maps_are_total(self):
        self.assertEqual(len(DEPTH_WIRE), len(WitnessDepth))
        self.assertEqual(len(ATTESTATION_WIRE), len(Attestation))
        self.assertEqual(len(IDENTITY_WIRE), len(WitnessIdentity))


class GapClosedTests(unittest.TestCase):
    def test_an_eyewitness_now_survives_the_wire(self):
        """The whole point of v2. Under v1 this collapsed onto 'inferred'."""
        eyewitness = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE)
        self.assertEqual(from_wire(to_wire(eyewitness)), eyewitness)

    def test_eyewitness_and_reasoning_model_no_longer_collide(self):
        eyewitness = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE)
        reasoning = IndependenceAxes(WitnessDepth.TEXT, Attestation.NONE)
        self.assertNotEqual(to_wire(eyewitness), to_wire(reasoning))

    def test_every_point_in_the_space_round_trips(self):
        for depth in WitnessDepth:
            for attestation in Attestation:
                for identity in WitnessIdentity:
                    axes = IndependenceAxes(depth, attestation, identity)
                    self.assertEqual(from_wire(to_wire(axes)), axes)

    def test_v1_expressed_four_of_one_hundred_and_fifty(self):
        self.assertEqual(vocabulary_coverage(), (4, 150))


class WitnessIdentityTests(unittest.TestCase):
    """Owner review: an anonymous eyewitness and one who states their identity
    are not the same thing, and neither existing axis separates them."""

    def test_anonymous_and_named_eyewitness_differ_only_in_identity(self):
        anon = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                WitnessIdentity.ANONYMOUS)
        named = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                 WitnessIdentity.NAMED)
        self.assertEqual(anon.depth, named.depth)
        self.assertEqual(anon.attestation, named.attestation)
        self.assertTrue(named.dominates(anon))
        self.assertFalse(anon.dominates(named))

    def test_the_whistleblower_keeps_all_three_facts(self):
        """Anonymous source, independently verified account.

        Under two axes the testament overwrote the anonymity -- the same defect
        that made a testament overwrite the depth.
        """
        w = IndependenceAxes(WitnessDepth.REALITY, Attestation.INDEPENDENT,
                             WitnessIdentity.ANONYMOUS)
        wire = to_wire(w)
        self.assertEqual(wire["witness_identity"], "anonymous")
        self.assertEqual(wire["attestation"], "independent")
        self.assertEqual(from_wire(wire), w)

    def test_identity_is_orthogonal_to_attestation(self):
        """Named-but-unvouched and anonymous-but-vouched are incomparable."""
        named_unvouched = IndependenceAxes(
            WitnessDepth.REALITY, Attestation.NONE, WitnessIdentity.NAMED)
        anon_vouched = IndependenceAxes(
            WitnessDepth.REALITY, Attestation.INDEPENDENT,
            WitnessIdentity.ANONYMOUS)
        self.assertFalse(named_unvouched.dominates(anon_vouched))
        self.assertFalse(anon_vouched.dominates(named_unvouched))

    def test_two_anonymous_witnesses_cannot_be_shown_distinct(self):
        """They may be one person reporting twice. This is the open half of U1."""
        anon = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                WitnessIdentity.ANONYMOUS)
        self.assertTrue(indistinguishable(anon, anon))

    def test_vouching_does_not_make_anonymous_witnesses_distinct(self):
        """A testament about a claim says nothing about whether two sources
        are the same source."""
        a = IndependenceAxes(WitnessDepth.REALITY, Attestation.ADVERSARIAL,
                             WitnessIdentity.ANONYMOUS)
        self.assertTrue(indistinguishable(a, a))

    def test_named_witnesses_are_distinguishable_in_principle(self):
        named = IndependenceAxes(WitnessDepth.REALITY, Attestation.NONE,
                                 WitnessIdentity.NAMED)
        self.assertFalse(indistinguishable(named, named))

    def test_v1_could_not_identify_a_witness_at_all(self):
        for basis in ("attested", "declared", "inferred", "unknown"):
            self.assertEqual(from_wire({"independence_basis": basis}).identity,
                             WitnessIdentity.ANONYMOUS)


class BackwardCompatibilityTests(unittest.TestCase):
    def test_a_v1_producer_still_parses(self):
        """Only `independence_basis` on the wire: read it, do not fail."""
        self.assertEqual(
            from_wire({"independence_basis": "attested"}),
            IndependenceAxes(WitnessDepth.UNSTATED, Attestation.INDEPENDENT,
                             WitnessIdentity.ANONYMOUS))

    def test_v1_silence_about_depth_is_preserved_not_guessed(self):
        parsed = from_wire({"independence_basis": "declared"})
        self.assertEqual(parsed.depth, WitnessDepth.UNSTATED)

    def test_a_v2_reader_prefers_the_explicit_axes(self):
        """When both are present, the richer encoding wins."""
        payload = {"independence_basis": "unknown",
                   "witness_depth": "reality", "attestation": "none"}
        self.assertEqual(from_wire(payload).depth, WitnessDepth.REALITY)

    def test_partial_v2_payload_records_silence_on_the_missing_axis(self):
        parsed = from_wire({"witness_depth": "reality"})
        self.assertEqual(parsed.depth, WitnessDepth.REALITY)
        self.assertEqual(parsed.attestation, Attestation.NONE)


class RefusalTests(unittest.TestCase):
    def test_unknown_depth_string_is_refused(self):
        with self.assertRaises(VocabularyError):
            from_wire({"witness_depth": "vibes"})

    def test_unknown_attestation_string_is_refused(self):
        with self.assertRaises(VocabularyError):
            from_wire({"attestation": "trust-me"})

    def test_unknown_legacy_basis_is_refused(self):
        with self.assertRaises(VocabularyError):
            from_wire({"independence_basis": "probably-fine"})

    def test_empty_payload_reads_as_unknown_not_as_an_error(self):
        """Absence of any independence claim is a defined state: nothing known."""
        self.assertEqual(from_wire({}),
                         IndependenceAxes(WitnessDepth.UNSTATED, Attestation.NONE,
                                          WitnessIdentity.ANONYMOUS))

    def test_unknown_identity_string_is_refused(self):
        with self.assertRaises(VocabularyError):
            from_wire({"witness_identity": "probably-someone"})


if __name__ == "__main__":
    unittest.main()
