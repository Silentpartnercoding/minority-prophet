"""The proposed ASSERTION EROSION check."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "research" / "epistemic-ci-proposals"))

from assertion_erosion import (  # noqa: E402
    ASSERTION_STRENGTH,
    check_assertion_erosion,
)

STRONG = """
class T:
    def test_one(self):
        self.assertEqual(a, b)
        self.assertEqual(c, d)
"""

WEAKENED = """
class T:
    def test_one(self):
        self.assertTrue(a)
        self.assertEqual(c, d)
"""

TRUNCATED = """
class T:
    def test_one(self):
        self.assertEqual(a, b)
"""

DELETED = """
class T:
    pass
"""


class ErosionTests(unittest.TestCase):
    def test_weakening_an_assertion_is_detected(self):
        report = check_assertion_erosion(STRONG, WEAKENED)
        self.assertTrue(report.eroded)
        self.assertEqual(report.weakened, [("test_one", "assertEqual", "assertTrue")])

    def test_dropping_an_assertion_is_detected(self):
        report = check_assertion_erosion(STRONG, TRUNCATED)
        self.assertEqual(len(report.removed), 1)

    def test_deleting_a_test_is_detected(self):
        report = check_assertion_erosion(STRONG, DELETED)
        self.assertEqual(report.tests_removed, ["test_one"])
        self.assertEqual(len(report.removed), 2)

    def test_unchanged_source_is_clean(self):
        self.assertFalse(check_assertion_erosion(STRONG, STRONG).eroded)

    def test_strengthening_is_not_erosion(self):
        self.assertFalse(check_assertion_erosion(WEAKENED, STRONG).eroded)

    def test_adding_a_test_is_not_erosion(self):
        extended = STRONG + """
    def test_two(self):
        self.assertEqual(e, f)
"""
        report = check_assertion_erosion(STRONG, extended)
        self.assertFalse(report.eroded)
        self.assertEqual(len(report.added), 1)


class ReviewTriggerTests(unittest.TestCase):
    """Erosion alone is ordinary. Erosion beside a change to the code under
    test is the shape of a test edited to accommodate rather than to judge."""

    def test_erosion_alone_does_not_demand_review(self):
        report = check_assertion_erosion(STRONG, WEAKENED,
                                         covered_module_changed=False)
        self.assertTrue(report.eroded)
        self.assertFalse(report.needs_review)

    def test_erosion_with_a_module_change_demands_review(self):
        report = check_assertion_erosion(STRONG, WEAKENED,
                                         covered_module_changed=True)
        self.assertTrue(report.needs_review)

    def test_a_module_change_alone_does_not_demand_review(self):
        report = check_assertion_erosion(STRONG, STRONG,
                                         covered_module_changed=True)
        self.assertFalse(report.needs_review)

    def test_the_summary_asks_the_question_rather_than_answering_it(self):
        report = check_assertion_erosion(STRONG, WEAKENED,
                                         covered_module_changed=True)
        self.assertIn("correction or convenience", report.summary())


class StrengthOrderingTests(unittest.TestCase):
    def test_exact_comparisons_outrank_truthiness(self):
        self.assertGreater(ASSERTION_STRENGTH["assertEqual"],
                           ASSERTION_STRENGTH["assertTrue"])

    def test_raises_is_a_strong_assertion(self):
        self.assertEqual(ASSERTION_STRENGTH["assertRaises"],
                         ASSERTION_STRENGTH["assertEqual"])

    def test_bounds_are_weaker_than_equality(self):
        self.assertLess(ASSERTION_STRENGTH["assertGreaterEqual"],
                        ASSERTION_STRENGTH["assertEqual"])


class SelfApplicationTests(unittest.TestCase):
    """The instance that produced this proposal, run through it."""

    def test_it_flags_the_bond_reference_edit_that_prompted_it(self):
        before = """
class T:
    def test_a_referenced_stake_is_honoured(self):
        self.assertEqual(bonded.honoured_identity, BONDED)
        self.assertEqual(bonded.admissible, REALITY)
"""
        after = """
class T:
    def test_a_referenced_stake_is_honoured(self):
        self.assertEqual(bonded.honoured_identity, VERIFIED)
        self.assertEqual(bonded.admissible, METHOD)
"""
        report = check_assertion_erosion(before, after,
                                         covered_module_changed=True)
        self.assertFalse(report.eroded,
                         "changing an expected VALUE is not weakening the "
                         "assertion -- the check must not cry wolf on it")

    def test_it_does_flag_a_downgrade_to_truthiness(self):
        before = """
class T:
    def test_x(self):
        self.assertEqual(bonded.honoured_identity, BONDED)
"""
        after = """
class T:
    def test_x(self):
        self.assertTrue(bonded.honoured_identity)
"""
        self.assertTrue(check_assertion_erosion(before, after).eroded)


class LimitsTests(unittest.TestCase):
    def test_a_split_commit_defeats_it(self):
        """Stated rather than hidden: this is a speed bump, not a wall."""
        report = check_assertion_erosion(STRONG, WEAKENED,
                                         covered_module_changed=False)
        self.assertFalse(report.needs_review,
                         "weakening in a separate commit escapes the trigger")

    def test_unparseable_source_is_not_treated_as_erosion(self):
        report = check_assertion_erosion("def (:", "def (:")
        self.assertFalse(report.eroded)


if __name__ == "__main__":
    unittest.main()
