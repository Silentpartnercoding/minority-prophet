"""H2.1 / H2.4: valid rare falsifiers must survive to verification;
ambiguous anomalies must not produce a commitment."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ledger_adapter import build_ledger_from_reports  # noqa: E402
from rh_decision import (  # noqa: E402
    UniversalLedger,
    VerificationRecord,
    decide,
    universal_with_confirmations,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_controls():
    with open(os.path.join(FIXTURES, "true_prophet_cases.json")) as fh:
        return {c["control_id"]: c for c in json.load(fh)["controls"]}


def _cand(claim_id, result_hash, claim_type="candidate_counterexample", method="m"):
    return {
        "claim_id": claim_id,
        "agent_id": f"agent_{claim_id}",
        "claim_type": claim_type,
        "method": method,
        "result_hash": result_hash,
    }


class TestFixtureContract(unittest.TestCase):
    def test_controls_a_through_f_present(self):
        self.assertEqual(set(load_controls()), {f"CONTROL_{x}" for x in "ABCDEF"})

    def test_expected_independent_support_matches_roots(self):
        controls = load_controls()
        self.assertEqual(controls["CONTROL_D"]["expected_independent_support"], 1)
        self.assertEqual(controls["CONTROL_D"]["expected_raw_support"], 100)
        self.assertEqual(controls["CONTROL_E"]["expected_independent_support"], 3)


class TestControlAMinorityNotSuppressed(unittest.TestCase):
    """1 valid candidate vs 999 confirmations: routed to verification."""

    def _decide(self, n_confirmations, record):
        ledger = build_ledger_from_reports([_cand("min_1", "hash_A_min")])
        universal = universal_with_confirmations("world:A", n_confirmations, "A")
        return decide(ledger, ["min_1"], claim_type="candidate_counterexample",
                      record=record, universal=universal)

    def test_fresh_minority_claim_is_verified_not_rejected(self):
        d = self._decide(999, VerificationRecord(0, "not_attempted", True, True))
        self.assertEqual(d.action, "verify")
        self.assertEqual(d.independent_roots, 1)

    def test_confirmation_count_never_changes_the_action(self):
        record = VerificationRecord(2, "reproduced", True, True)
        few = self._decide(0, record)
        many = self._decide(999, record)
        self.assertEqual(few.action, many.action)
        self.assertEqual(few.independent_roots, many.independent_roots)
        self.assertEqual(many.ignored_confirming_roots, 999)

    def test_certified_counterexample_refutes_against_999(self):
        """AC1 and AC2: one certified root refutes; 999 confirmations unread."""
        d = self._decide(999, VerificationRecord(4, "reproduced", True, True))
        self.assertEqual(d.action, "escalate")
        self.assertEqual(d.next_state, "CANDIDATE_FALSIFIER")
        self.assertEqual(d.universal_outcome, "refuted")
        self.assertEqual(d.decisive_roots, 1)
        self.assertEqual(d.ignored_confirming_roots, 999)

    def test_certified_replays_are_still_one_decisive_root(self):
        ledger = build_ledger_from_reports(
            [_cand(f"r{i}", "one_work") for i in range(20)]
        )
        universal = universal_with_confirmations("world:replay", 10, "replay")
        d = decide(ledger, [f"r{i}" for i in range(20)],
                   claim_type="counterexample",
                   record=VerificationRecord(6, "reproduced", True, True),
                   universal=universal)
        self.assertEqual(d.universal_outcome, "refuted")
        self.assertEqual(d.decisive_roots, 1)


class TestControlCReproduction(unittest.TestCase):
    def test_control_c_ledger_counts_two_roots(self):
        ledger = build_ledger_from_reports([
            _cand("min_1", "hash_C_find", method="method_alpha"),
            _cand("ver_1", "hash_C_repro", "counterexample", "method_beta"),
        ])
        self.assertEqual(ledger.independent_support_count(["min_1", "ver_1"]), 2)

    def test_control_c_same_hash_is_one_root(self):
        """A replay of the same work-product is not an independent reproduction."""
        ledger = build_ledger_from_reports([
            _cand("min_1", "same_work"),
            _cand("ver_1", "same_work", "counterexample"),
        ])
        self.assertEqual(ledger.independent_support_count(["min_1", "ver_1"]), 1)


class TestControlFAbstention(unittest.TestCase):
    def _decide(self, record):
        ledger = build_ledger_from_reports([_cand("anom_1", "hash_F", "anomaly")])
        return decide(ledger, ["anom_1"], claim_type="anomaly", record=record,
                      universal=UniversalLedger("world:F"))

    def test_unresolved_anomaly_never_escalates(self):
        d = self._decide(VerificationRecord(2, "partial", True, True))
        self.assertIn(d.action, ("verify", "abstain"))

    def test_fully_verified_but_unresolvable_anomaly_abstains(self):
        d = self._decide(VerificationRecord(4, "partial", True, True))
        self.assertEqual(d.action, "abstain")

    def test_anomaly_is_never_a_counterexample_root(self):
        d = self._decide(VerificationRecord(6, "reproduced", True, True))
        self.assertEqual(d.action, "abstain")
        self.assertEqual(d.universal_outcome, "not_refuted")


if __name__ == "__main__":
    unittest.main()
