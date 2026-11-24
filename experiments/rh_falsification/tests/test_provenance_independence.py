"""H2.3: the independence count must come from fingerprinted work-product
roots in the canonical evidence graph, never from raw report counts or
declared lineage.

Pins the omitted-parent threat: a copy that forgets to cite its parent
must still collapse when the computation fingerprint matches.
Only recorded/fingerprinted copies are collapsed.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ledger_adapter import (  # noqa: E402
    KnowledgeLedger,
    LedgerEntry,
    build_ledger_from_reports,
)

from aggregation.root_vote import Verdict  # noqa: E402
from provenance.graph import EvidenceGraph  # noqa: E402


def _report(claim_id, agent_id, parents=(), claim_type="candidate_counterexample", method="m", result_hash="", candidate_key=""):
    rec = {
        "claim_id": claim_id,
        "agent_id": agent_id,
        "claim_type": claim_type,
        "parent_evidence_ids": list(parents),
        "method": method,
    }
    if result_hash:
        rec["result_hash"] = result_hash
    if candidate_key:
        rec["candidate_key"] = candidate_key
    return rec


class TestCopiedConsensusDiscount(unittest.TestCase):
    """CONTROL_D / FP5: N copies of one origin count as 1 independent."""

    def test_twenty_copies_share_one_root(self):
        reports = [_report("origin", "agent_fp5_origin", result_hash="fp5_origin_work")]
        reports += [
            _report(f"copy_{i}", f"agent_{i}", parents=["origin"]) for i in range(20)
        ]
        ledger = build_ledger_from_reports(reports)
        copies = [f"copy_{i}" for i in range(20)]
        self.assertEqual(ledger.raw_support_count(copies), 20)
        self.assertEqual(ledger.independent_support_count(copies), 1)

    def test_hundred_copies_control_d(self):
        reports = [_report("origin", "agent_fp_origin", result_hash="control_d_work")]
        reports += [
            _report(f"c{i}", f"a{i}", parents=["origin"]) for i in range(100)
        ]
        ledger = build_ledger_from_reports(reports)
        ids = [f"c{i}" for i in range(100)]
        self.assertEqual(ledger.independent_support_count(ids), 1)

    def test_transitive_copying_is_still_one_root(self):
        """A -> B -> C -> D chain: all four resolve to root A."""
        ledger = build_ledger_from_reports(
            [
                _report("A", "agent_a", result_hash="chain_work"),
                _report("B", "agent_b", parents=["A"]),
                _report("C", "agent_c", parents=["B"]),
                _report("D", "agent_d", parents=["C"]),
            ]
        )
        self.assertEqual(ledger.independent_support_count(["B", "C", "D"]), 1)
        self.assertEqual(ledger.provenance_roots("D"), ledger.provenance_roots("A"))
        self.assertEqual(len(ledger.provenance_roots("D")), 1)


class TestGenuineIndependence(unittest.TestCase):
    """CONTROL_E: three independent finders count as 3."""

    def test_three_independent_roots(self):
        ledger = build_ledger_from_reports(
            [
                _report("min_1", "agent_min_1", method="method_alpha", result_hash="hash_E_1"),
                _report("min_2", "agent_min_2", method="method_beta", result_hash="hash_E_2"),
                _report("min_3", "agent_min_3", method="method_gamma", result_hash="hash_E_3"),
            ]
        )
        ids = ["min_1", "min_2", "min_3"]
        self.assertEqual(ledger.independent_support_count(ids), 3)

    def test_mixed_provenance(self):
        """2 independent + 3 copies of one of them = 2 independent roots."""
        ledger = build_ledger_from_reports(
            [
                _report("r1", "a1", result_hash="hash_r1"),
                _report("r2", "a2", result_hash="hash_r2"),
                _report("cp1", "a3", parents=["r1"]),
                _report("cp2", "a4", parents=["r1"]),
                _report("cp3", "a5", parents=["cp1"]),
            ]
        )
        ids = ["r1", "r2", "cp1", "cp2", "cp3"]
        self.assertEqual(ledger.raw_support_count(ids), 5)
        self.assertEqual(ledger.independent_support_count(ids), 2)


class TestLedgerInvariants(unittest.TestCase):
    def test_append_only(self):
        ledger = build_ledger_from_reports([_report("x", "a")])
        with self.assertRaises(ValueError):
            ledger.append(
                LedgerEntry(claim_id="x", agent_id="b", claim_type="anomaly")
            )

    def test_parents_must_exist(self):
        ledger = KnowledgeLedger()
        with self.assertRaises(ValueError):
            ledger.append(
                LedgerEntry(
                    claim_id="child",
                    agent_id="a",
                    claim_type="anomaly",
                    parent_evidence_ids=frozenset({"ghost"}),
                )
            )

    def test_anomaly_never_jumps_to_falsified(self):
        ledger = build_ledger_from_reports(
            [_report("anom", "a", claim_type="anomaly")]
        )
        with self.assertRaises(ValueError):
            ledger.transition("anom", "FALSIFIED")

    def test_anomaly_may_enter_verifying(self):
        ledger = build_ledger_from_reports(
            [_report("anom", "a", claim_type="anomaly")]
        )
        successor = ledger.transition("anom", "VERIFYING")
        self.assertEqual(successor.claim_state, "VERIFYING")


class TestOmittedParentStillCollapses(unittest.TestCase):
    """Hostile case: parents omitted, fingerprint still collapses.

    Pins the omitted-parent threat. Twenty agents reporting the same
    work-product hash are one root even when none cites a parent.
    Only recorded/fingerprinted copies collapse.
    """

    def test_twenty_same_hash_no_parents_count_one(self):
        reports = [
            _report(f"clone_{i}", f"agent_{i}", result_hash="same_work_product")
            for i in range(20)
        ]
        ledger = build_ledger_from_reports(reports)
        ids = [f"clone_{i}" for i in range(20)]
        self.assertEqual(ledger.raw_support_count(ids), 20)
        self.assertEqual(ledger.independent_support_count(ids), 1)

    def test_parentless_unattributed_quarantined_to_zero(self):
        """Empty parents + no fingerprint is unattributed, not a root."""
        reports = [_report(f"anon_{i}", f"a{i}") for i in range(5)]
        ledger = build_ledger_from_reports(reports)
        ids = [f"anon_{i}" for i in range(5)]
        self.assertEqual(ledger.independent_support_count(ids), 0)
        self.assertEqual(ledger.unattributed_count(ids), 5)

    def test_treat_as_root_is_explicit_opt_in(self):
        reports = [_report(f"anon_{i}", f"a{i}") for i in range(5)]
        ledger = build_ledger_from_reports(reports, unattributed_policy="treat_as_root")
        ids = [f"anon_{i}" for i in range(5)]
        self.assertEqual(ledger.independent_support_count(ids), 5)

    def test_abstain_if_decisive_counts_zero_and_withholds(self):
        """root_vote's meaning: unattributed claims are not roots, and a
        verdict they could change is withheld."""
        reports = [_report(f"anon_{i}", f"a{i}") for i in range(3)]
        reports.append(_report("named", "b", result_hash="named_work"))
        ledger = build_ledger_from_reports(
            reports, unattributed_policy="abstain_if_decisive"
        )
        ids = [f"anon_{i}" for i in range(3)] + ["named"]
        self.assertEqual(ledger.independent_support_count(ids), 1)
        self.assertEqual(ledger.unattributed_count(ids), 3)
        cv = ledger.candidate_verdict(ids)
        self.assertEqual(cv.verdict, Verdict.ABSTAIN)
        self.assertEqual(cv.unattributed, 3)

    def test_quarantine_does_not_withhold(self):
        reports = [_report(f"anon_{i}", f"a{i}") for i in range(3)]
        reports.append(_report("named", "b", result_hash="named_work"))
        ledger = build_ledger_from_reports(reports)
        ids = [f"anon_{i}" for i in range(3)] + ["named"]
        cv = ledger.candidate_verdict(ids)
        self.assertEqual(cv.verdict, Verdict.TRUE)
        self.assertEqual(cv.margin, 1)

    def test_two_agents_same_table_are_one_root(self):
        """Two agents reading the same table are one person."""
        ledger = build_ledger_from_reports(
            [
                _report("reader_a", "agent_a", method="table_lookup", result_hash="table_T"),
                _report("reader_b", "agent_b", method="table_lookup", result_hash="table_T"),
            ]
        )
        self.assertEqual(ledger.independent_support_count(["reader_a", "reader_b"]), 1)

    def test_two_interval_proofs_are_two_roots(self):
        """Two different algorithms with interval proofs are two roots."""
        ledger = build_ledger_from_reports(
            [
                _report("rs_proof", "agent_rs", method="interval_rs", result_hash="proof_rs"),
                _report("os_proof", "agent_os", method="interval_os", result_hash="proof_os"),
            ]
        )
        self.assertEqual(ledger.independent_support_count(["rs_proof", "os_proof"]), 2)


class TestCanonicalStorage(unittest.TestCase):
    """The ledger stores reports in provenance.graph and counts with root_vote."""

    def test_storage_is_the_canonical_graph(self):
        ledger = build_ledger_from_reports(
            [_report(f"c{i}", f"a{i}", result_hash="one_work") for i in range(20)]
        )
        self.assertIsInstance(ledger.graph, EvidenceGraph)
        self.assertEqual(
            ledger.graph.root_set(), frozenset({"source:urn:rh-calc:hash:one_work"})
        )
        self.assertEqual(ledger.independent_support_count([f"c{i}" for i in range(20)]), 1)
        self.assertEqual(ledger.raw_support_count([f"c{i}" for i in range(20)]), 20)

    def test_quarantined_reports_never_enter_the_graph(self):
        ledger = build_ledger_from_reports([_report("anon", "a")])
        self.assertTrue(ledger.is_quarantined("anon"))
        self.assertEqual(len(ledger.graph.nodes()), 0)
        self.assertEqual(len(ledger), 1)

    def test_recorded_copy_with_its_own_hash_adds_no_root(self):
        """A report that declares a parent is a recorded copy. Its own
        fingerprint does not mint a second root (copy invariance)."""
        ledger = build_ledger_from_reports([
            _report("orig", "a", result_hash="h_orig"),
            _report("copy", "b", parents=["orig"], result_hash="h_rehashed"),
        ])
        self.assertEqual(ledger.independent_support_count(["orig", "copy"]), 1)

    def test_copy_of_quarantined_parent_falls_back_to_own_fingerprint(self):
        ledger = build_ledger_from_reports([
            _report("anon", "a"),
            _report("child_hash", "b", parents=["anon"], result_hash="h_child"),
            _report("child_bare", "c", parents=["anon"]),
        ])
        self.assertEqual(ledger.independent_support_count(["child_hash"]), 1)
        self.assertTrue(ledger.is_quarantined("child_bare"))

    def test_raw_result_hash_is_refused(self):
        with self.assertRaises(ValueError):
            build_ledger_from_reports([{
                "claim_id": "x", "agent_id": "a",
                "claim_type": "candidate_counterexample", "raw_result_hash": "h",
            }])

    def test_confirmations_are_a_different_proposition(self):
        with self.assertRaises(ValueError):
            build_ledger_from_reports([_report("c", "a", claim_type="confirmation",
                                               result_hash="h")])

    def test_unknown_policy_refused(self):
        with self.assertRaises(ValueError):
            KnowledgeLedger(unattributed_policy="weighted")


class TestRhProvenUnrepresentable(unittest.TestCase):
    def test_rh_proven_is_not_a_claim_state(self):
        import ledger_adapter
        self.assertNotIn("RH_PROVEN", ledger_adapter.CLAIM_STATES)
        ledger = build_ledger_from_reports([_report("c", "a", result_hash="h")])
        with self.assertRaises(ValueError):
            ledger.transition("c", "RH_PROVEN")


if __name__ == "__main__":
    unittest.main()
