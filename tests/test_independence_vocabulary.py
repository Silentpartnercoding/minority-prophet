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
    INDEPENDENCE_VOCABULARY_VERSION,
    Attestation,
    IndependenceAxes,
    VocabularyError,
    WitnessDepth,
    from_wire,
    to_wire,
    vocabulary_coverage,
)
from aggregation.root_vote import IndependenceBasis

#: Duplicated verbatim in the invention-graph test.
CONTRACT_VERSION = 2
CONTRACT_BASIS = ["attested", "declared", "inferred", "unknown"]
CONTRACT_DEPTH = ["reality", "method", "replication", "raw", "analysis",
                  "text", "unstated"]
CONTRACT_ATTESTATION = ["none", "self", "internal", "independent", "adversarial"]


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

    def test_wire_maps_are_total(self):
        self.assertEqual(len(DEPTH_WIRE), len(WitnessDepth))
        self.assertEqual(len(ATTESTATION_WIRE), len(Attestation))


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
                axes = IndependenceAxes(depth, attestation)
                self.assertEqual(from_wire(to_wire(axes)), axes)

    def test_v1_expressed_four_of_thirty(self):
        self.assertEqual(vocabulary_coverage(), (4, 30))


class BackwardCompatibilityTests(unittest.TestCase):
    def test_a_v1_producer_still_parses(self):
        """Only `independence_basis` on the wire: read it, do not fail."""
        self.assertEqual(
            from_wire({"independence_basis": "attested"}),
            IndependenceAxes(WitnessDepth.UNSTATED, Attestation.INDEPENDENT))

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
                         IndependenceAxes(WitnessDepth.UNSTATED, Attestation.NONE))


if __name__ == "__main__":
    unittest.main()
