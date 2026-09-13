"""Source weight, taken apart.

These pin claims about the shipped code, not opinions about it. Each one is
checked against `aggregation` rather than asserted, so if the baseline is ever
made principled these fail and the decomposition has to be rewritten -- which is
the correct outcome.
"""

import inspect
import unittest

from aggregation import baselines
from canon.decomposition import Fill, Layer
from canon.decompositions.weight import WEIGHT


class ShapeTest(unittest.TestCase):
    def test_three_layers_come_back_empty(self):
        self.assertEqual([c.layer for c in WEIGHT.findings()],
                         [Layer.EVIDENCE_LINEAGE, Layer.AUTHORITY, Layer.FALSIFIERS])

    def test_nothing_was_left_unexamined(self):
        """Unlike the wheel, every layer here was looked at, so every EMPTY is a
        statement about the artifact rather than about our effort."""
        self.assertEqual(WEIGHT.unexamined(), ())
        self.assertEqual(WEIGHT.coverage(), (7, 10))


class GroundedInTheCodeTest(unittest.TestCase):
    """Each claim the decomposition makes, checked against what ships."""

    def setUp(self):
        self.src = inspect.getsource(baselines.weighted_vote)
        # The executable body only. Prose in the docstring must not be able to
        # satisfy or break a claim about what the code does.
        doc = inspect.getdoc(baselines.weighted_vote) or ""
        body = self.src
        for line in doc.splitlines():
            body = body.replace(line, "")
        self.body = body

    def test_the_two_coordinates_are_multiplied_into_one(self):
        self.assertIn("confidence", self.body)
        self.assertIn("competence", self.body)
        self.assertIn("*", self.body)

    def test_negative_weights_are_silently_clamped(self):
        self.assertIn("max(0.0", self.body)

    def test_the_baseline_deduplicates_nothing(self):
        """The EVIDENCE_LINEAGE finding depends on this being true."""
        self.assertNotIn("root", self.body)
        self.assertNotIn("set(", self.body)
        self.assertNotIn("seen", self.body)

    def test_no_capability_is_checked(self):
        """The AUTHORITY finding depends on this. A plain function over claims
        cannot check a capability it never receives."""
        params = list(inspect.signature(baselines.weighted_vote).parameters)
        self.assertEqual(params, ["claims"])

    def test_no_outcome_is_ever_read_back(self):
        """The FALSIFIERS finding: nothing in the weighting path can learn that a
        weight was wrong, because no ground truth reaches it."""
        for banned in ("outcome", "resolved", "ground_truth", "actual", "correct"):
            self.assertNotIn(banned, self.body)


class DoctrineTest(unittest.TestCase):
    def test_the_corpus_already_calls_a_declared_quantity_worthless_alone(self):
        """The OBSERVABLES finding is not our opinion; it is the independence
        vocabulary applied to the baseline's own inputs."""
        from aggregation import independence_axes
        src = inspect.getsource(independence_axes)
        self.assertIn("Free, therefore worthless alone", src)

    def test_the_baseline_is_a_baseline_and_its_naivety_is_the_point(self):
        """Guard against someone 'fixing' weighted_vote. It exists to lose."""
        self.assertIn("baseline", inspect.getdoc(baselines).lower())


if __name__ == "__main__":
    unittest.main()
