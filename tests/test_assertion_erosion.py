"""The proposed ASSERTION EROSION check."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "research" / "epistemic-ci-proposals"))

from assertion_erosion import (  # noqa: E402
    ASSERTION_STRENGTH,
    _assertions,
    check_assertion_erosion,
    covered_modules,
    module_changed,
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


class CoveredModuleTests(unittest.TestCase):
    """`covered_module_changed` is what `needs_review` turns on, and nothing
    derived it. These cover the deriver, not the judgement: it names candidates
    from the test's own imports and leaves the diff to the caller."""

    SOURCE = """
import json
from pathlib import Path
import pytest

from provenance.claim_warrant import build_warrant
from provenance.graph import resolvable_reference
import aggregation.root_vote
"""

    def test_first_party_imports_become_repository_paths(self):
        found = covered_modules(self.SOURCE, roots=("provenance", "aggregation"))
        self.assertEqual(found, {"provenance/claim_warrant.py",
                                 "provenance/graph.py",
                                 "aggregation/root_vote.py"})

    def test_the_standard_library_is_not_covered_code(self):
        """A test importing json does not cover json. Including stdlib would
        make every test look as though it covered the standard library."""
        found = covered_modules(self.SOURCE, roots=("provenance", "aggregation"))
        self.assertNotIn("json.py", found)
        self.assertNotIn("pathlib.py", found)

    def test_roots_limit_the_result(self):
        found = covered_modules(self.SOURCE, roots=("aggregation",))
        self.assertEqual(found, {"aggregation/root_vote.py"})

    def test_without_roots_third_party_over_reports_rather_than_dropping(self):
        """Over-reporting is the safe direction: a missed real module would
        silently disarm needs_review."""
        found = covered_modules(self.SOURCE)
        self.assertIn("pytest.py", found)
        self.assertIn("provenance/claim_warrant.py", found)

    def test_relative_imports_are_skipped(self):
        self.assertEqual(covered_modules("from . import sibling"), set())

    def test_unparseable_source_yields_nothing(self):
        self.assertEqual(covered_modules("def (:"), set())

    def test_module_changed_is_the_overlap(self):
        self.assertTrue(module_changed(self.SOURCE, ["provenance/graph.py"],
                                       roots=("provenance",)))
        self.assertFalse(module_changed(self.SOURCE, ["app/page.tsx"],
                                        roots=("provenance",)))

    def test_leading_dot_slash_is_tolerated(self):
        self.assertTrue(module_changed(self.SOURCE, ["./provenance/graph.py"],
                                       roots=("provenance",)))

    def test_no_changes_is_not_a_review_trigger(self):
        self.assertFalse(module_changed(self.SOURCE, [], roots=("provenance",)))


class BareAssertTests(unittest.TestCase):
    """A bare `assert` in pytest carries its comparison, not the keyword.

    Scoring the keyword made every pytest-style assertion strength 1, and at
    strength 1 nothing can be WEAKENED -- only removed. Measured on
    tests/test_root_duplication_link.py as submitted: 13 of 13 assertions were
    bare, all scored 1, and an equality downgraded to truthiness returned
    eroded=False. The check was blind to every downgrade in this repository.
    """

    def test_equality_downgraded_to_truthiness_is_erosion(self):
        report = check_assertion_erosion("def test_x():\n    assert a == b\n",
                                         "def test_x():\n    assert a\n")
        self.assertTrue(report.eroded)
        self.assertEqual(report.weakened, [("test_x", "assert ==", "assert")])

    def test_membership_downgraded_to_truthiness_is_erosion(self):
        report = check_assertion_erosion("def test_x():\n    assert a in b\n",
                                         "def test_x():\n    assert a\n")
        self.assertTrue(report.eroded)

    def test_equality_is_not_weakened_by_changing_the_expected_value(self):
        """The negative fixture from the issue, in bare-assert form."""
        report = check_assertion_erosion("def test_x():\n    assert s == APPROVED\n",
                                         "def test_x():\n    assert s == PENDING\n")
        self.assertFalse(report.eroded)

    def test_negation_is_classified_by_what_it_negates(self):
        report = check_assertion_erosion("def test_x():\n    assert not a == b\n",
                                         "def test_x():\n    assert not a\n")
        self.assertTrue(report.eroded)

    def test_pytest_raises_is_an_assertion(self):
        source = """
def test_x():
    with pytest.raises(ValueError):
        boom()
"""
        report = check_assertion_erosion(source, "def test_x():\n    boom()\n")
        self.assertTrue(report.eroded)
        self.assertEqual([a.method for a in report.removed], ["assert raises"])

    def test_this_repository_no_longer_scores_everything_one(self):
        """Regression guard for the measured defect."""
        from collections import Counter
        import pathlib as _p
        source = (_p.Path(__file__).resolve().parents[1]
                  / "tests" / "test_root_duplication_link.py").read_text()
        kinds = Counter(m for calls in _assertions(source).values() for m in calls)
        self.assertGreater(len(kinds), 1,
                           "a pytest-style suite must not collapse to one kind")
        self.assertIn("assert ==", kinds)


class DerivedFlagTests(unittest.TestCase):
    """changed_paths wires covered_modules to its caller. Before this, the
    deriver existed and nothing called it."""

    SOURCE = "from provenance.graph import x\ndef test_x():\n    assert a\n"

    def test_changed_paths_derives_the_flag(self):
        report = check_assertion_erosion(
            "def test_x():\n    assert a == b\n",
            self.SOURCE,
            changed_paths=["provenance/graph.py"], roots=("provenance",))
        self.assertTrue(report.needs_review)

    def test_an_unrelated_change_does_not_demand_review(self):
        report = check_assertion_erosion(
            "def test_x():\n    assert a == b\n",
            self.SOURCE,
            changed_paths=["app/page.tsx"], roots=("provenance",))
        self.assertTrue(report.eroded)
        self.assertFalse(report.needs_review)

    def test_the_explicit_flag_still_works(self):
        report = check_assertion_erosion("def test_x():\n    assert a == b\n",
                                         "def test_x():\n    assert a\n",
                                         covered_module_changed=True)
        self.assertTrue(report.needs_review)

