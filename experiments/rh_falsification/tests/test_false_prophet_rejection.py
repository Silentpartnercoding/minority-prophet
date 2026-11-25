"""H2.2: every FP1 to FP7 case must end in rejection or abstention, and none
may reach FALSIFIED. FP5 counts come from the canonical ledger.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ledger_adapter import LedgerEntry, build_ledger_from_reports  # noqa: E402
from phase1_harness import _fp_record, materialize_fp_reports  # noqa: E402
from rh_decision import UniversalLedger, VerificationRecord, decide  # noqa: E402

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_fp_cases():
    with open(os.path.join(FIXTURES, "false_prophet_cases.json")) as fh:
        return json.load(fh)["cases"]


def _fp5_copied_reports():
    """20 parentless copies of one work-product. Same result_hash."""
    return [
        {
            "claim_id": f"fp5_{i}",
            "agent_id": f"agent_fp5_{i}",
            "claim_type": "candidate_counterexample",
            "method": "replay",
            "result_hash": "fp5_shared_work_product",
            "parent_evidence_ids": [],
        }
        for i in range(20)
    ]


def _fp5_independent_reports():
    """20 genuinely distinct work-products (distinct hashes, same method)."""
    return [
        {
            "claim_id": f"ind_{i}",
            "agent_id": f"agent_ind_{i}",
            "claim_type": "candidate_counterexample",
            "method": "replay",
            "result_hash": f"distinct_work_{i}",
            "parent_evidence_ids": [],
        }
        for i in range(20)
    ]


def _decide_case(case, policy="quarantine"):
    reports = materialize_fp_reports(case)
    ledger = build_ledger_from_reports(reports, unattributed_policy=policy)
    return decide(
        ledger,
        [r["claim_id"] for r in reports],
        claim_type="candidate_counterexample",
        record=_fp_record(case),
        universal=UniversalLedger(f"rh:{case['fp_id']}"),
    )


class TestFixtureContract(unittest.TestCase):
    def test_all_seven_families_present(self):
        ids = {c["fp_id"] for c in load_fp_cases()}
        self.assertEqual(ids, {f"FP{i}" for i in range(1, 8)})

    def test_no_case_may_reach_falsified(self):
        for case in load_fp_cases():
            self.assertEqual(case["must_never_reach"], "FALSIFIED", case["fp_id"])
            self.assertIn(
                case["expected_terminal_state"],
                ("REJECTED_FALSE_POSITIVE", "ABSTAIN"),
                case["fp_id"],
            )


class TestDecisionRejectsFalseProphets(unittest.TestCase):
    def test_every_fp_case_rejected_never_escalated(self):
        for policy in ("quarantine", "abstain_if_decisive", "treat_as_root"):
            for case in load_fp_cases():
                d = _decide_case(case, policy)
                self.assertIn(d.action, ("reject", "verify", "abstain"),
                              f"{policy} {case['fp_id']} -> {d.action}")
                self.assertEqual(d.universal_outcome, "not_refuted", case["fp_id"])

    def test_fp6_has_no_attributable_root_and_is_rejected(self):
        case = next(c for c in load_fp_cases() if c["fp_id"] == "FP6")
        d = _decide_case(case)
        self.assertEqual(d.independent_roots, 0)
        self.assertEqual(d.unattributed, 1)
        self.assertEqual(d.action, "reject")

    def test_fp6_under_abstain_if_decisive_is_withheld(self):
        case = next(c for c in load_fp_cases() if c["fp_id"] == "FP6")
        d = _decide_case(case, "abstain_if_decisive")
        self.assertEqual(d.independent_roots, 0)
        self.assertEqual(d.action, "abstain")

    def test_fp6_under_treat_as_root_becomes_one_root(self):
        case = next(c for c in load_fp_cases() if c["fp_id"] == "FP6")
        d = _decide_case(case, "treat_as_root")
        self.assertEqual(d.independent_roots, 1)
        self.assertEqual(d.action, "verify")

    def test_fp7_internal_inconsistency_rejected(self):
        case = next(c for c in load_fp_cases() if c["fp_id"] == "FP7")
        d = _decide_case(case)
        self.assertEqual(d.action, "reject")
        self.assertEqual(d.reason, "record contradicts itself")

    def test_stated_confidence_has_no_input_path(self):
        """The FP6 fixture states 0.99 in prose. Nothing can read it."""
        case = next(c for c in load_fp_cases() if c["fp_id"] == "FP6")
        self.assertIn("prose_confidence", case["injected_report"])
        for report in materialize_fp_reports(case):
            self.assertNotIn("prose_confidence", report)
            self.assertNotIn("confidence", report)
        self.assertNotIn("confidence", LedgerEntry.__dataclass_fields__)
        self.assertNotIn("confidence", VerificationRecord.__dataclass_fields__)

    def test_fp5_count_comes_from_ledger(self):
        case = next(c for c in load_fp_cases() if c["fp_id"] == "FP5")
        d = _decide_case(case)
        self.assertEqual(d.independent_roots, 1)
        self.assertEqual(d.raw_reports, 20)
        self.assertEqual(d.action, "reject")

    def test_fp5_copied_vs_independent_counts(self):
        copied = build_ledger_from_reports(_fp5_copied_reports())
        independent = build_ledger_from_reports(_fp5_independent_reports())
        self.assertEqual(
            copied.independent_support_count([f"fp5_{i}" for i in range(20)]), 1
        )
        self.assertEqual(
            independent.independent_support_count([f"ind_{i}" for i in range(20)]), 20
        )


class TestNothingDecisiveBeforeCertifiedVerification(unittest.TestCase):
    def test_three_reproduced_roots_at_level3_keep_verifying(self):
        ledger = build_ledger_from_reports(_fp5_independent_reports()[:3])
        universal = UniversalLedger("rh:level3")
        d = decide(
            ledger,
            ["ind_0", "ind_1", "ind_2"],
            claim_type="counterexample",
            record=VerificationRecord(3, "reproduced", True, True),
            universal=universal,
        )
        self.assertEqual(d.independent_roots, 3)
        self.assertEqual(d.action, "verify")
        self.assertEqual(d.universal_outcome, "not_refuted")


if __name__ == "__main__":
    unittest.main()
