"""The decomposition primitive, and its first real subject.

What these pin is mostly refusals. The primitive exists because a missing layer
is invisible when layers are fused, so every way of making a layer disappear
quietly has to be an error rather than a convenience.
"""

import unittest

from canon.decomposition import Cell, Decomposition, Fill, Layer, LAYER_QUESTION, Question
from canon.decompositions.wheel import WHEEL


def _full(overrides=None):
    overrides = overrides or {}
    cells = [overrides.get(l, Cell(l, Fill.STATED, content=f"{l.name} content"))
             for l in Layer]
    return Decomposition(subject="fixture", cells=tuple(cells))


class LayerOrderTest(unittest.TestCase):
    def test_the_ten_layers_are_ordered_and_complete(self):
        self.assertEqual(len(list(Layer)), 10)
        self.assertEqual([l.name for l in Layer][:3],
                         ["BOUNDARY", "COORDINATES", "OBSERVABLES"])
        self.assertEqual(list(Layer)[-1], Layer.FALSIFIERS)

    def test_every_layer_declares_a_question(self):
        """The layers cut; the questions file. Neither derives the other."""
        self.assertEqual(set(LAYER_QUESTION), set(Layer))
        self.assertTrue(all(isinstance(a, Question) for a in LAYER_QUESTION.values()))


class ReservedWordTest(unittest.TestCase):
    def test_the_word_axes_is_not_reused_for_these_four(self):
        """EPISTEMIC-MODEL.md reserves `axes` for the independence vocabulary.
        Calling these four axes too is the collision that reservation exists to
        prevent, and this module reintroduced it once already."""
        import canon.decomposition as m
        self.assertFalse(hasattr(m, "Axis"))
        self.assertFalse(hasattr(m, "LAYER_AXIS"))
        self.assertTrue(hasattr(m, "Question"))


class RefusalTest(unittest.TestCase):
    def test_a_decomposition_missing_a_layer_is_refused(self):
        """Skipping a layer hides exactly what the primitive is for."""
        cells = tuple(Cell(l, Fill.STATED, content="x")
                      for l in Layer if l is not Layer.FALSIFIERS)
        with self.assertRaises(ValueError) as e:
            Decomposition(subject="truncated", cells=cells)
        self.assertIn("FALSIFIERS", str(e.exception))

    def test_empty_without_a_finding_is_refused(self):
        """An unfilled layer is a finding, not an omission."""
        with self.assertRaises(ValueError):
            Cell(Layer.FALSIFIERS, Fill.EMPTY)

    def test_unexamined_may_not_carry_a_finding(self):
        """Not looking establishes nothing about the artifact. ASSAYER A5."""
        with self.assertRaises(ValueError):
            Cell(Layer.EVIDENCE_LINEAGE, Fill.UNEXAMINED, finding="none found")

    def test_stated_without_content_is_refused(self):
        with self.assertRaises(ValueError):
            Cell(Layer.BOUNDARY, Fill.STATED)

    def test_a_repeated_layer_is_refused(self):
        cells = tuple(Cell(l, Fill.STATED, content="x") for l in Layer)
        with self.assertRaises(ValueError):
            Decomposition(subject="dupe", cells=cells + (cells[0],))


class ReportingTest(unittest.TestCase):
    def test_empty_and_unexamined_are_never_conflated(self):
        d = _full({
            Layer.FALSIFIERS: Cell(Layer.FALSIFIERS, Fill.EMPTY, finding="none exist"),
            Layer.MECHANISM: Cell(Layer.MECHANISM, Fill.UNEXAMINED),
        })
        self.assertEqual([c.layer for c in d.findings()], [Layer.FALSIFIERS])
        self.assertEqual([c.layer for c in d.unexamined()], [Layer.MECHANISM])

    def test_coverage_is_a_pair_and_excludes_what_was_not_examined(self):
        """Never one ratio: which layer is missing is the finding, and a ratio hides it."""
        d = _full({
            Layer.FALSIFIERS: Cell(Layer.FALSIFIERS, Fill.EMPTY, finding="none exist"),
            Layer.MECHANISM: Cell(Layer.MECHANISM, Fill.UNEXAMINED),
        })
        self.assertEqual(d.coverage(), (8, 9))

    def test_by_question_partitions_every_layer_exactly_once(self):
        d = _full()
        seen = [c.layer for q in Question for c in d.by_question(q)]
        self.assertCountEqual(seen, list(Layer))


class WheelTest(unittest.TestCase):
    """The first real subject. The plan's completion criterion is that one real
    claim is decomposed end to end and at least one layer comes back empty."""

    def test_all_ten_layers_are_present(self):
        self.assertEqual({c.layer for c in WHEEL.cells}, set(Layer))

    def test_falsifiers_is_empty_and_that_is_the_finding(self):
        cell = WHEEL[Layer.FALSIFIERS]
        self.assertIs(cell.fill, Fill.EMPTY)
        self.assertIn("cannot record its own refutation", cell.finding)
        self.assertEqual([c.layer for c in WHEEL.findings()], [Layer.FALSIFIERS])

    def test_the_theory_is_recorded_as_implied_not_stated(self):
        """The trajectory is asserted by the ordering and never announced. If this
        ever reads STATED, either the instrument changed or the reading got lazy."""
        self.assertIs(WHEEL[Layer.MECHANISM].fill, Fill.IMPLIED)

    def test_the_missing_citation_is_visible_rather_than_glossed(self):
        self.assertIs(WHEEL[Layer.AUTHORITY].fill, Fill.IMPLIED)
        self.assertIn("not been recovered", WHEEL[Layer.AUTHORITY].content)

    def test_lineage_is_unexamined_and_is_not_counted_as_a_finding(self):
        self.assertIs(WHEEL[Layer.EVIDENCE_LINEAGE].fill, Fill.UNEXAMINED)
        self.assertNotIn(Layer.EVIDENCE_LINEAGE, [c.layer for c in WHEEL.findings()])

    def test_coverage_reports_eight_of_nine(self):
        self.assertEqual(WHEEL.coverage(), (8, 9))


if __name__ == "__main__":
    unittest.main()
