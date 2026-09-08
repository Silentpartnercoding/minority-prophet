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

    def test_contested_entries_are_few_and_flagged(self):
        self.assertEqual(len(contested()), 4)
        for a in contested():
            self.assertTrue(a.contested)


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
