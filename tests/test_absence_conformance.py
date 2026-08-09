"""KL-001 v0.4 — the absence rule is enumerated, not sampled.

v0.3 measured a false-clean rate over a synthetic corpus. The verdict turned out
to be a total function of two bits, which means both of v0.3's rates were fixed by
corpus composition: every term in them is a generator setting. They were chosen,
then read back. Enlarging the corpus would tighten a confidence interval around an
authored number -- worse than an underpowered estimate, because it looks like
evidence.

What the rule does can be settled exactly instead. Two inputs, four combinations,
no sampling.

These tests also check that each input is load-bearing. A table walked by a rule
that ignores one of its inputs still yields four rows and three correct verdicts,
so "all cells pass" is not on its own evidence that the cells matter.
"""
import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from knowledge_ledger import evaluate_transaction

CONFORMANCE = (pathlib.Path(__file__).resolve().parents[1] /
               "research/knowledge-ledger/experiments/KL-001/conformance")
sys.path.insert(0, str(CONFORMANCE))

from verify_absence_rule import EXPECTED, cells_load_bearing, enumerate_table, transaction


class TestAbsenceRuleIsTotal(unittest.TestCase):

    def test_every_combination_of_inputs_is_covered(self):
        """Four cells for two boolean inputs. Exhaustive, so no corpus, no sample
        size and no confidence interval are involved."""
        rows = enumerate_table()
        self.assertEqual(len(rows), 4)
        seen = {(r["hasOpposing"], r["coverageComplete"]) for r in rows}
        self.assertEqual(seen, set(itertools.product((True, False), repeat=2)))

    def test_every_cell_matches_the_declared_table(self):
        for row in enumerate_table():
            with self.subTest(cell=(row["hasOpposing"], row["coverageComplete"])):
                self.assertEqual(row["verdict"], row["expected"])

    def test_incomplete_coverage_never_reads_as_absence(self):
        """The claim the dual ledger exists to make. Stated directly rather than
        inferred from a rate."""
        verdict = evaluate_transaction(transaction(False, False))["conclusion"]
        self.assertEqual(verdict, "not_established")
        self.assertNotEqual(verdict, "absent_within_declared_scope")

    def test_opposing_evidence_outranks_coverage(self):
        """A found defect is `present` whether or not the search was complete.
        Incomplete coverage cannot downgrade a positive finding."""
        for complete in (True, False):
            with self.subTest(complete=complete):
                self.assertEqual(
                    evaluate_transaction(transaction(True, complete))["conclusion"],
                    "present")


class TestCellsAreLoadBearing(unittest.TestCase):

    def test_both_inputs_decide_at_least_one_cell(self):
        for finding in cells_load_bearing():
            with self.subTest(input=finding["input"]):
                self.assertGreater(
                    finding["decidesCells"], 0,
                    f"{finding['input']} changes no verdict, so the rule ignores it")

    def test_coverage_decides_exactly_the_cell_the_mechanism_claims(self):
        """Coverage matters only when nothing was found -- which is the mechanism,
        stated as a property rather than as a percentage. If coverage decided both
        pairs the rule would be downgrading positive findings; if it decided
        neither, the dual ledger would do nothing at all."""
        coverage = next(f for f in cells_load_bearing()
                        if f["input"] == "coverageComplete")
        self.assertEqual(coverage["decidesCells"], 1)
        self.assertEqual(coverage["detail"][0]["otherInput"], False,
                         "coverage must be decisive precisely when nothing opposed")

    def test_a_rule_that_ignores_coverage_breaks_a_cell(self):
        """The mutant that would make this experiment vacuous.

        A rule reading only `hasOpposing` reproduces three of four cells. If no
        cell caught it, the coverage bit would be decorative and v0.3's entire
        result would reduce to 'the scanner found things'.
        """
        def mutant(has_opposing: bool, _coverage: bool) -> str:
            return "present" if has_opposing else "absent_within_declared_scope"

        disagreements = [
            (a, b) for a, b in itertools.product((True, False), repeat=2)
            if mutant(a, b) != EXPECTED[(a, b)]
        ]
        self.assertEqual(disagreements, [(False, False)],
                         "exactly the incomplete-coverage cell must catch this mutant")

    def test_a_rule_that_ignores_findings_breaks_two_cells(self):
        def mutant(_has_opposing: bool, coverage: bool) -> str:
            return "absent_within_declared_scope" if coverage else "not_established"

        disagreements = [
            (a, b) for a, b in itertools.product((True, False), repeat=2)
            if mutant(a, b) != EXPECTED[(a, b)]
        ]
        self.assertEqual(sorted(disagreements), [(True, False), (True, True)])


if __name__ == "__main__":
    unittest.main()
