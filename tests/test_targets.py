"""Target-relative depth, and the attestation axis.

Every test in this file encodes a statement made in owner review. They exist so
the four formerly-"contested" assignments cannot be re-collapsed into a single
target-independent answer.
"""

import unittest

from canon.proximity import ErrorClass, Rung, Source, effective_witnesses_for
from canon.targets import (
    Attestation,
    Target,
    TargetUndefined,
    attestation_of,
    required_margin,
    rung_for,
)


class DocumentTests(unittest.TestCase):
    """'The original document should be original 1 of 1, but you can have
    multiple independent witnesses of it — it depends on the context in which
    you're measuring.'"""

    def test_document_is_the_world_for_a_claim_about_the_document(self):
        self.assertEqual(
            rung_for("retrieved-original-document", Target.DOCUMENT), Rung.REALITY)

    def test_document_is_only_a_record_for_a_claim_about_events(self):
        self.assertEqual(
            rung_for("retrieved-original-document", Target.WORLD), Rung.RAW)

    def test_many_independent_readers_of_one_original(self):
        """The artifact is 1-of-1; the witnesses of it need not be."""
        readers = [Source(f"r{i}", rung_for("retrieved-original-document",
                                            Target.DOCUMENT), frozenset({f"eyes{i}"}))
                   for i in range(3)]
        self.assertEqual(
            effective_witnesses_for(readers, ErrorClass.FABRICATION), 3)


class ModelTests(unittest.TestCase):
    """'If you're measuring models then a second model could be a new witness,
    but if you're modeling reality, a second one running off text is not.'"""

    def test_second_model_is_a_witness_to_model_behavior(self):
        self.assertEqual(
            rung_for("second-model-reviewing-first-model", Target.MODEL_BEHAVIOR),
            Rung.REALITY)

    def test_second_model_is_hearsay_about_reality(self):
        self.assertEqual(
            rung_for("second-model-reviewing-first-model", Target.WORLD), Rung.TEXT)

    def test_two_models_are_one_witness_about_the_world(self):
        pair = [Source("m1", rung_for("second-model-reviewing-first-model",
                                      Target.WORLD), frozenset({"prompt"})),
                Source("m2", rung_for("second-model-reviewing-first-model",
                                      Target.WORLD), frozenset({"prompt"}))]
        self.assertEqual(effective_witnesses_for(pair, ErrorClass.FABRICATION), 1)

    def test_model_agreement_is_same_control_domain(self):
        self.assertEqual(
            attestation_of("second-model-reviewing-first-model"),
            Attestation.INTERNAL)


class PeerReviewTests(unittest.TestCase):
    """'Peer review is NOT a witness, it's a testament — it has more rigor
    than someone re-reading the text.'"""

    def test_peer_review_witnesses_nothing_about_the_world(self):
        self.assertEqual(rung_for("peer-review", Target.WORLD), Rung.TEXT)

    def test_peer_review_is_a_real_measurement_of_the_process(self):
        self.assertEqual(rung_for("peer-review", Target.PROCESS), Rung.METHOD)

    def test_peer_review_is_an_independent_testament(self):
        self.assertEqual(attestation_of("peer-review"), Attestation.INDEPENDENT)

    def test_peer_review_outranks_bare_rereading_on_the_attestation_axis(self):
        self.assertGreater(attestation_of("peer-review"),
                           attestation_of("citation"))


class DifferentLabTests(unittest.TestCase):
    """'Different lab, same protocol is replication — but some action was
    taken. In a different context it counts for more.'"""

    def test_it_is_replication_for_a_claim_about_the_world(self):
        self.assertEqual(
            rung_for("different-lab-same-protocol", Target.WORLD),
            Rung.REPLICATION)

    def test_it_is_direct_observation_of_reproducibility(self):
        self.assertEqual(
            rung_for("different-lab-same-protocol", Target.PROCESS), Rung.REALITY)

    def test_action_taken_shows_up_as_attestation(self):
        self.assertEqual(attestation_of("different-lab-same-protocol"),
                         Attestation.INDEPENDENT)


class AttestationAxisTests(unittest.TestCase):
    """Attestation never adds a witness. It lowers the R3 margin."""

    def test_attestation_does_not_change_witness_count(self):
        pair = [Source("a", Rung.TEXT, frozenset({"S"})),
                Source("b", Rung.TEXT, frozenset({"S"}))]
        before = effective_witnesses_for(pair, ErrorClass.ANALYSIS)
        self.assertEqual(before, 1)
        # No API exists to raise this with attestation, and that is the point.

    def test_independent_attestation_lowers_required_margin(self):
        self.assertLess(required_margin(3, [Attestation.INDEPENDENT]),
                        required_margin(3, [Attestation.NONE]))

    def test_self_attestation_lowers_nothing(self):
        """The bootstrap earns no credit."""
        self.assertEqual(required_margin(3, [Attestation.SELF]),
                         required_margin(3, [Attestation.NONE]))

    def test_internal_attestation_lowers_nothing(self):
        """Same control domain is internal replication, not validation."""
        self.assertEqual(required_margin(3, [Attestation.INTERNAL]),
                         required_margin(3, [Attestation.NONE]))

    def test_adversarial_attestation_is_worth_most(self):
        self.assertLess(required_margin(4, [Attestation.ADVERSARIAL]),
                        required_margin(4, [Attestation.INDEPENDENT]))

    def test_margin_never_reaches_zero(self):
        """A testament lowers the floor. It never removes it."""
        self.assertGreaterEqual(required_margin(2, [Attestation.ADVERSARIAL]), 1)
        self.assertGreaterEqual(required_margin(9, [Attestation.ADVERSARIAL]), 1)


class RefusalTests(unittest.TestCase):
    def test_undefined_pair_is_refused_not_guessed(self):
        with self.assertRaises(TargetUndefined):
            rung_for("some-unclassified-procedure", Target.WORLD)

    def test_target_independent_procedures_fall_back_cleanly(self):
        """An experiment observes the world whatever you are asking about."""
        self.assertEqual(rung_for("original-experiment", Target.WORLD),
                         Rung.REALITY)

    def test_unlisted_procedure_attests_nothing(self):
        self.assertEqual(attestation_of("citation"), Attestation.NONE)


if __name__ == "__main__":
    unittest.main()
