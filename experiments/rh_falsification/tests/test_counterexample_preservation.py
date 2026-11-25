"""H2.1 / H2.4: valid rare falsifiers must survive to verification;
ambiguous anomalies must not produce a commitment."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ledger_adapter import build_ledger_from_reports  # noqa: E402
from rh_decision import (  # noqa: E402
    TowerRecheck,
    UniversalLedger,
    VerificationRecord,
    decide,
    universal_with_confirmations,
)

CERT = "sha256:synthetic-outside-certificate"


def _tower(result_hash="tower_work", passed=True, software="tower_interval_suite",
           interval_bounds=True):
    return TowerRecheck(result_hash=result_hash, software=software,
                        machine="tower-host-1", interval_bounds=interval_bounds,
                        passed=passed)


def _certified(tower=None):
    return VerificationRecord(6, "reproduced", True, True,
                              external_certificate=CERT, tower_recheck=tower)

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
        self.assertEqual(set(load_controls()), {f"CONTROL_{x}" for x in "ABCDEFGH"})

    def test_certified_worlds_state_level_6_and_a_tower_recheck(self):
        controls = load_controls()
        for cid in ("CONTROL_G", "CONTROL_H"):
            v = controls[cid]["verification"]
            self.assertEqual(v["level"], 6, cid)
            self.assertTrue(v["external_certificate"], cid)
            self.assertTrue(v["tower_recheck"]["interval_bounds"], cid)
        self.assertTrue(controls["CONTROL_G"]["verification"]["tower_recheck"]["passed"])
        self.assertFalse(controls["CONTROL_H"]["verification"]["tower_recheck"]["passed"])

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

    def test_certified_with_tower_recheck_refutes_against_999(self):
        """AC1 and AC2: the tower's recheck root refutes; 999 confirmations unread."""
        d = self._decide(999, _certified(_tower()))
        self.assertEqual(d.action, "escalate")
        self.assertEqual(d.next_state, "CANDIDATE_FALSIFIER")
        self.assertEqual(d.universal_outcome, "refuted")
        self.assertEqual(d.decisive_roots, 1)
        self.assertEqual(d.ignored_confirming_roots, 999)

    def test_level_4_or_5_is_not_enough(self):
        for level in (4, 5):
            record = VerificationRecord(level, "reproduced", True, True,
                                        external_certificate=CERT, tower_recheck=_tower())
            d = self._decide(999, record)
            self.assertEqual(d.action, "verify", level)
            self.assertEqual(d.universal_outcome, "not_refuted", level)

    def test_level_6_without_certificate_is_not_enough(self):
        record = VerificationRecord(6, "reproduced", True, True, tower_recheck=_tower())
        self.assertEqual(self._decide(999, record).action, "verify")

    def test_certified_without_tower_recheck_keeps_verifying(self):
        d = self._decide(999, _certified(None))
        self.assertEqual(d.action, "verify")
        self.assertEqual(d.reason, "certified; awaiting tower recheck")
        self.assertEqual(d.universal_outcome, "not_refuted")

    def test_failed_tower_recheck_rejects_the_candidate(self):
        d = self._decide(999, _certified(_tower(passed=False)))
        self.assertEqual(d.action, "reject")
        self.assertEqual(d.reason, "tower recheck failed")

    def test_tower_recheck_must_be_its_own_calculation(self):
        for tower in (_tower(result_hash="hash_A_min"),   # replays the finder
                      _tower(software="m"),               # finder's software
                      _tower(interval_bounds=False)):      # no error bounds
            d = self._decide(999, _certified(tower))
            self.assertEqual(d.action, "verify", tower)
            self.assertEqual(d.universal_outcome, "not_refuted", tower)

    def test_certified_replays_are_still_one_decisive_root(self):
        ledger = build_ledger_from_reports(
            [_cand(f"r{i}", "one_work") for i in range(20)]
        )
        universal = universal_with_confirmations("world:replay", 10, "replay")
        d = decide(ledger, [f"r{i}" for i in range(20)],
                   claim_type="counterexample",
                   record=_certified(_tower()),
                   universal=universal)
        self.assertEqual(d.universal_outcome, "refuted")
        self.assertEqual(d.decisive_roots, 1)

    def test_tower_is_capped_at_two_roots_per_hour(self):
        universal = UniversalLedger("world:tower-cap")
        actions = []
        for i in range(3):
            ledger = build_ledger_from_reports([_cand(f"c{i}", f"find_{i}")])
            d = decide(ledger, [f"c{i}"], claim_type="candidate_counterexample",
                       record=_certified(_tower(result_hash=f"tower_{i}")),
                       universal=universal)
            actions.append((d.action, d.reason))
        self.assertEqual(actions[0][0], "escalate")
        self.assertEqual(actions[1][0], "escalate")
        self.assertEqual(actions[2], ("verify", "tower issuance cap reached for this hour"))


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
        d = self._decide(_certified(_tower()))
        self.assertEqual(d.action, "abstain")
        self.assertEqual(d.universal_outcome, "not_refuted")


if __name__ == "__main__":
    unittest.main()
