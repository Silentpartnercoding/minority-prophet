"""The rung assignment table."""

import unittest

from canon.proximity import ErrorClass, Rung, Source, effective_witnesses_for
from canon.rungs import ALL, BY_NAME, contested, rung_of


class TableTests(unittest.TestCase):
    def test_every_assignment_has_a_rationale(self):
        for a in ALL:
            self.assertTrue(a.rationale.strip(), a.procedure)

    def test_procedure_names_are_unique(self):
        self.assertEqual(len(BY_NAME), len(ALL))

    def test_unknown_procedure_refuses_rather_than_defaulting(self):
        """Unknown != TEXT. An unassigned procedure is a stated refusal."""
        with self.assertRaises(KeyError) as ctx:
            rung_of("some-procedure-nobody-classified")
        self.assertIn("publish before drawing a sample", str(ctx.exception))

    def test_nothing_is_contested_because_the_four_were_not_close_calls(self):
        """The four entries once flagged here were resolved structurally rather
        than by signature: a rung is a property of a (procedure, proposition)
        pair, and `canon/targets.py` holds that table. Reinstating a flag here
        would re-open a decision that was made, so this asserts the resolution
        rather than the old snapshot."""
        self.assertEqual(contested(), ())

    def test_every_formerly_contested_procedure_is_target_resolved(self):
        """The flags are gone because the ambiguity moved, not because it was
        dropped. Each one must have at least one (procedure, target) entry."""
        from canon.targets import RUNG_BY_TARGET
        for procedure in ("different-lab-same-protocol", "peer-review",
                          "retrieved-original-document",
                          "second-model-reviewing-first-model"):
            resolved = [t for (p, t) in RUNG_BY_TARGET if p == procedure]
            self.assertTrue(resolved, f"{procedure} has no target-resolved rung")

    def test_attestation_never_substitutes_for_witness_depth(self):
        """Peer review is a testament, not a witness. Its rigour lives on the
        attestation axis; moving it down the ladder would let vouching buy the
        appearance of looking."""
        from canon.targets import ATTESTATION, Attestation
        self.assertIs(ATTESTATION["peer-review"], Attestation.INDEPENDENT)
        self.assertIs(BY_NAME["peer-review"].rung, Rung.TEXT)


class LoadBearingAssignmentTests(unittest.TestCase):
    def test_reasoning_over_context_is_hearsay(self):
        """Reasoning is not observation. The bootstrap earns nothing."""
        self.assertEqual(rung_of("model-reasoning-over-given-context"), Rung.TEXT)

    def test_meta_analysis_is_not_near_the_world(self):
        """Fifty studies sharing one bad instrument inherit the flaw fifty times."""
        self.assertEqual(
            rung_of("meta-analysis-of-published-effects"), Rung.ANALYSIS)
        pool = [Source(f"study{i}", rung_of("meta-analysis-of-published-effects"),
                       frozenset({"instrument"})) for i in range(50)]
        self.assertEqual(
            effective_witnesses_for(pool, ErrorClass.INSTRUMENT), 1)

    def test_peer_review_adds_no_independent_witness_as_assigned(self):
        self.assertEqual(rung_of("peer-review"), Rung.TEXT)

    def test_replication_outranks_reanalysis(self):
        self.assertLess(rung_of("direct-replication-same-protocol"),
                        rung_of("reanalysis-from-published-figures"))

    def test_different_method_outranks_same_protocol(self):
        self.assertLess(rung_of("independent-replication-different-method"),
                        rung_of("direct-replication-same-protocol"))

    def test_direct_observation_is_the_floor(self):
        for name in ("original-experiment", "physical-inventory-count",
                     "witnessed-directly", "tool-call-observing-live-state"):
            self.assertEqual(rung_of(name), Rung.REALITY)


if __name__ == "__main__":
    unittest.main()
