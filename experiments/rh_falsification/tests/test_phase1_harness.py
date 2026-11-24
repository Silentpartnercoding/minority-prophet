"""Phase 1 synthetic harness: H2.1-H2.4 vs majority vote.

No zeta math. Deterministic seed. No scores or weights.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from phase1_harness import SEED, run_phase1


class TestPhase1Harness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_phase1(seed=SEED)

    def _h(self, hid):
        return next(h for h in self.result["hypotheses"] if h["hypothesis_id"] == hid)

    def test_seed_and_synthetic_flags(self):
        self.assertEqual(self.result["seed"], SEED)
        self.assertTrue(self.result["synthetic_only"])
        self.assertFalse(self.result["zeta_math"])
        self.assertFalse(self.result["unrecomputed_numbers"])
        self.assertEqual(self.result["gate_path"], "forbidden")
        self.assertFalse(self.result["scores_or_weights"])
        self.assertEqual(self.result["unattributed_policy"], "quarantine")

    def test_h21_retains_valid_falsifiers_majority_does_not(self):
        h = self._h("H2.1")
        self.assertTrue(h["success"])
        self.assertFalse(h["failure"])
        self.assertGreater(h["mp_metric"], h["baseline_metric"])

    def test_h22_rejects_false_prophets_fp5_count_one(self):
        h = self._h("H2.2")
        self.assertTrue(h["success"])
        self.assertFalse(h["failure"])
        fp5 = next(r for r in self.result["false_prophets"] if r["fp_id"] == "FP5")
        self.assertEqual(fp5["independent_support_count"], 1)
        self.assertEqual(fp5["raw_support_count"], 20)
        for row in self.result["false_prophets"]:
            self.assertNotEqual(row["mp_action"], "escalate", row["fp_id"])
            self.assertNotEqual(row["terminal_for_scoring"], "FALSIFIED", row["fp_id"])

    def test_h23_fingerprint_counts(self):
        h = self._h("H2.3")
        self.assertTrue(h["success"])
        self.assertFalse(h["failure"])
        d = next(r for r in self.result["controls"] if r["control_id"] == "CONTROL_D")
        e = next(r for r in self.result["controls"] if r["control_id"] == "CONTROL_E")
        self.assertEqual(d["independent_support_count"], 1)
        self.assertEqual(d["raw_support_count"], 100)
        self.assertEqual(e["independent_support_count"], 3)

    def test_h24_abstains_on_ambiguous_anomaly(self):
        h = self._h("H2.4")
        self.assertTrue(h["success"])
        self.assertFalse(h["failure"])
        f = next(r for r in self.result["controls"] if r["control_id"] == "CONTROL_F")
        self.assertIn(f["mp_action"], ("verify", "abstain"))
        self.assertEqual(f["majority_winner"], "confirmation")

    def test_all_success(self):
        self.assertTrue(self.result["all_success"])

    def test_rh_proven_absent_from_report(self):
        blob = str(self.result)
        self.assertNotIn("RH_PROVEN", blob)

    def test_no_score_fields_in_report(self):
        for row in self.result["controls"] + self.result["false_prophets"]:
            for key in row:
                self.assertNotIn("score", key)
                self.assertNotIn("confidence", key)
                self.assertNotIn("weight", key)

    def test_only_the_tower_rechecked_world_refutes(self):
        """Only CONTROL_G has a level 6 certificate plus a passed tower recheck."""
        for row in self.result["controls"]:
            want = "refuted" if row["control_id"] == "CONTROL_G" else "not_refuted"
            self.assertEqual(row["universal_outcome"], want, row["control_id"])
        for row in self.result["false_prophets"]:
            self.assertEqual(row["universal_outcome"], "not_refuted", row["fp_id"])

    def test_h25_certified_path_stops_at_candidate_falsifier(self):
        h = self._h("H2.5")
        self.assertTrue(h["success"])
        self.assertFalse(h["failure"])
        g = next(r for r in self.result["controls"] if r["control_id"] == "CONTROL_G")
        self.assertEqual(g["mp_next_state"], "CANDIDATE_FALSIFIER")
        self.assertEqual(g["majority_winner"], "confirmation")
        for row in self.result["controls"] + self.result["false_prophets"]:
            self.assertNotEqual(row["mp_next_state"], "FALSIFIED")

    def test_all_policies_pass(self):
        for policy in ("quarantine", "abstain_if_decisive", "treat_as_root"):
            self.assertTrue(run_phase1(unattributed_policy=policy)["all_success"], policy)

    def test_replay_is_deterministic(self):
        again = run_phase1(seed=SEED)
        self.assertEqual(again["hypotheses"], self.result["hypotheses"])
        self.assertEqual(again["controls"], self.result["controls"])


if __name__ == "__main__":
    unittest.main()
