"""The zero-weight reconciliation.

`formal/EXTENSION-SOCKETS.md` section 2 says the two readings must be reconciled
before any weighted theorem is stated. These pin that the reconciliation names
the policy rather than picking a winner, and that it fails closed only where the
choice actually changes the verdict.
"""

import unittest
from dataclasses import dataclass

from aggregation import weighted_vote
from aggregation.root_vote import Verdict, verdict
from aggregation.zero_weight import (
    Reading, ZeroWeightAmbiguity, ZeroWeightPolicy, read, resolve,
)


@dataclass
class C:
    value: bool
    confidence: float
    competence: float
    root_id: str = ""
    proposition: str = "p"


DISAGREES = [C(True, 1.0, 1.0, root_id="r1"),
             C(True, 0.0, 1.0, root_id="r2"),   # the zero weight
             C(False, 1.0, 1.0, root_id="r3")]

AGREES = [C(True, 1.0, 1.0, root_id="r1"),
          C(True, 1.0, 1.0, root_id="r2"),
          C(True, 0.0, 1.0, root_id="r3"),
          C(False, 1.0, 1.0, root_id="r4")]


class TheDefectIsRealTest(unittest.TestCase):
    """Before reconciling it, show the two shipped aggregators really differ."""

    def test_the_two_shipped_aggregators_disagree_on_one_corpus(self):
        w = weighted_vote(DISAGREES)
        r = verdict(DISAGREES)
        self.assertIsNone(w.belief)                 # mass ties, so it abstains
        self.assertIs(r.verdict, Verdict.TRUE)      # cardinality sees 2 against 1
        self.assertEqual(w.support_true, w.support_false)


class PolicyTest(unittest.TestCase):
    def test_the_default_refuses_when_the_choice_changes_the_verdict(self):
        with self.assertRaises(ZeroWeightAmbiguity) as e:
            resolve(DISAGREES)
        self.assertIn("as roots", str(e.exception))
        self.assertIn("as mass", str(e.exception))

    def test_each_explicit_policy_returns_its_own_reading(self):
        self.assertEqual(resolve(DISAGREES, policy=ZeroWeightPolicy.COUNTS_AS_A_ROOT),
                         "true")
        self.assertEqual(resolve(DISAGREES, policy=ZeroWeightPolicy.EXCLUDED),
                         "abstain")

    def test_it_does_not_refuse_when_both_readings_agree(self):
        """Decision sensitivity, applied. An unresolved ambiguity that changes
        nothing is recorded, not escalated."""
        r = read(AGREES)
        self.assertTrue(r.has_zero_weights)
        self.assertFalse(r.decision_material)
        self.assertEqual(resolve(AGREES), "true")

    def test_no_zero_weights_means_the_policy_never_engages(self):
        clean = [C(True, 1.0, 1.0), C(False, 1.0, 1.0), C(True, 0.5, 1.0)]
        self.assertFalse(read(clean).has_zero_weights)
        self.assertEqual(resolve(clean), "true")

    def test_refuse_is_the_default_and_not_something_a_caller_must_remember(self):
        import inspect
        default = inspect.signature(resolve).parameters["policy"].default
        self.assertIs(default, ZeroWeightPolicy.REFUSE)


class ReportingTest(unittest.TestCase):
    def test_both_readings_are_always_reported_not_just_the_chosen_one(self):
        text = read(DISAGREES).report()
        self.assertIn("as roots", text)
        self.assertIn("as mass", text)
        self.assertIn("DECISION-MATERIAL", text)

    def test_the_agreeing_case_says_the_ambiguity_is_recorded_not_closed(self):
        text = read(AGREES).report()
        self.assertIn("not decision-material", text)
        self.assertIn("recorded", text)

    def test_zero_weight_arises_from_either_factor(self):
        """competence zero and confidence zero are the same defect."""
        self.assertEqual(read([C(True, 0.0, 1.0)]).zero_weight_claims, 1)
        self.assertEqual(read([C(True, 1.0, 0.0)]).zero_weight_claims, 1)

    def test_a_negative_weight_is_a_zero_weight_here_too(self):
        """Clamping is what the shipped code does; this reads the same claims."""
        self.assertEqual(read([C(True, -3.0, 1.0)]).zero_weight_claims, 1)


if __name__ == "__main__":
    unittest.main()
