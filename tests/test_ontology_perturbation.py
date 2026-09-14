"""Hold the phenomenon fixed and change the vocabulary instead.

The criteria this was built against: a conclusion that dies when two categories
merge must be reported as resting on that distinction rather than as a survival
rate; and a vocabulary that cannot state the conclusion must never be counted as
disagreeing with it.
"""

import unittest

from canon.ontology_perturbation import (
    Inexpressible, Kind, Outcome, Perturbation, add_instrument_dimension,
    drop, merge, probe, rename, split,
)

WHEEL = frozenset({"earthy", "camphor", "storage", "dry-leaf-shape", "dry-leaf-colour"})


def concludes_fermented(vocab: frozenset[str]) -> str:
    """Toy conclusion resting entirely on 'camphor' being its own category.

    Stands in for the real thing: a verdict that looks like a fact about tea and
    is actually a fact about the category scheme.
    """
    if "camphor" not in vocab and "earthy-camphor" not in vocab:
        raise Inexpressible("no camphor category, so the question cannot be put")
    return "fermented" if "camphor" in vocab else "undetermined"


class WhatTheConclusionRestsOnTest(unittest.TestCase):
    def setUp(self):
        self.p = probe(
            "Monascus fermentation is detectable on the wheel",
            concludes_fermented,
            WHEEL,
            [
                drop(WHEEL, "storage"),
                merge(WHEEL, "earthy", "camphor", into="earthy-camphor"),
                rename(WHEEL, {"storage": "cellar"}),
                add_instrument_dimension(WHEEL, "methoxyphenol-ppm"),
            ],
        )

    def test_the_baseline_is_recorded(self):
        self.assertEqual(self.p.baseline, "fermented")

    def test_an_irrelevant_category_can_be_dropped_without_effect(self):
        by_kind = {r.perturbation.kind: r.outcome for r in self.p.results}
        self.assertIs(by_kind[Kind.DROP], Outcome.SURVIVED)
        self.assertIs(by_kind[Kind.RENAME], Outcome.SURVIVED)
        self.assertIs(by_kind[Kind.ADD_INSTRUMENT], Outcome.SURVIVED)

    def test_merging_the_load_bearing_categories_overturns_it(self):
        by_kind = {r.perturbation.kind: r.outcome for r in self.p.results}
        self.assertIs(by_kind[Kind.MERGE], Outcome.OVERTURNED)

    def test_the_report_names_what_it_was_resting_on_not_a_rate(self):
        report = self.p.report()
        self.assertIn("RESTING ON", report)
        self.assertIn("merged", report)
        self.assertNotIn("3 of 4", report)
        self.assertNotIn("75", report)

    def test_no_survival_score_is_exposed_anywhere(self):
        for attr in ("score", "survival", "survival_rate", "passed", "ratio"):
            self.assertFalse(hasattr(self.p, attr), attr)


class InexpressibleIsNotDisagreementTest(unittest.TestCase):
    """The tea wheel's defect, as a test."""

    def setUp(self):
        self.p = probe("as above", concludes_fermented, WHEEL,
                       [drop(WHEEL, "camphor")])

    def test_a_vocabulary_with_no_cell_is_not_an_overturn(self):
        self.assertEqual(len(self.p.overturned_by), 0)
        self.assertEqual(len(self.p.inexpressible_under), 1)
        self.assertIs(self.p.results[0].outcome, Outcome.INEXPRESSIBLE)

    def test_it_is_reported_as_producing_no_evidence(self):
        self.assertIn("inexpressible", self.p.report())
        self.assertNotIn("RESTING ON", self.p.report())


class FailuresAreSurfacedNotSwallowedTest(unittest.TestCase):
    def test_an_errored_perturbation_is_reported_as_not_run(self):
        """A silently dropped perturbation reads as coverage that never ran."""
        def explodes(vocab):
            if "storage" not in vocab:
                raise RuntimeError("model timed out")
            return "fermented"

        p = probe("x", explodes, WHEEL, [drop(WHEEL, "storage")])
        self.assertIs(p.results[0].outcome, Outcome.ERRORED)
        self.assertEqual(len(p.not_run), 1)
        self.assertIn("NOT RUN", p.report())
        self.assertIn("RuntimeError", p.results[0].detail)

    def test_a_clean_run_does_not_claim_coverage_it_lacks(self):
        p = probe("x", concludes_fermented, WHEEL, [drop(WHEEL, "storage")])
        self.assertIn("perturbations not run", p.report())


class ConstructorGuardsTest(unittest.TestCase):
    def test_a_probe_with_no_perturbations_is_refused(self):
        with self.assertRaises(ValueError) as ctx:
            probe("x", concludes_fermented, WHEEL, [])
        self.assertIn("would read as a pass", str(ctx.exception))

    def test_perturbing_a_term_that_is_not_there_is_an_error(self):
        for call in (lambda: drop(WHEEL, "absent"),
                     lambda: merge(WHEEL, "earthy", "absent", into="x"),
                     lambda: split(WHEEL, "absent", ("a", "b")),
                     lambda: rename(WHEEL, {"absent": "x"})):
            with self.assertRaises(ValueError):
                call()

    def test_a_perturbation_must_say_what_it_changed(self):
        with self.assertRaises(ValueError):
            Perturbation(Kind.DROP, "", WHEEL)

    def test_a_split_produces_at_least_two_terms(self):
        with self.assertRaises(ValueError):
            split(WHEEL, "storage", ("cellar",))


if __name__ == "__main__":
    unittest.main()
