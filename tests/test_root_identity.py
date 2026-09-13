"""Property tests for U1 — proximate root identity.

Tests marked ATTACK pin a known failure so it cannot be reintroduced silently.
"""

import unittest

from canon.root_identity import (
    Witness,
    effective_witnesses,
    proximately_dependent,
    shares_ancestry,
)


def W(name, ancestry=(), markers=()):
    return Witness(name, frozenset(ancestry), frozenset(markers))


class QuotientReductionTests(unittest.TestCase):
    """It must generalize the old definition, not contradict it."""

    def test_copies_of_one_source_count_once(self):
        ws = [W("orig", "z"), W("copy1", "z"), W("copy2", "z")]
        self.assertEqual(effective_witnesses(ws), 1)

    def test_unrelated_sources_count_separately(self):
        ws = [W("a", "x"), W("b", "y"), W("c", "z")]
        self.assertEqual(effective_witnesses(ws), 3)

    def test_two_clean_lineages(self):
        ws = [W("a1", "x"), W("a2", "x"), W("b1", "y"), W("b2", "y")]
        self.assertEqual(effective_witnesses(ws), 2)


class NonTransitivityTests(unittest.TestCase):
    """The case that broke the quotient definition."""

    def test_path_returns_two_not_one(self):
        """A—B—C with A,C unrelated. Transitive closure said 1. Truth is 2."""
        ws = [W("A", "x"), W("B", "xy"), W("C", "y")]
        self.assertTrue(shares_ancestry(ws[0], ws[1]))
        self.assertTrue(shares_ancestry(ws[1], ws[2]))
        self.assertFalse(shares_ancestry(ws[0], ws[2]))
        self.assertEqual(effective_witnesses(ws), 2)

    def test_longer_chain(self):
        """A—B—C—D: the endpoints and the alternating pair are independent."""
        ws = [W("A", "1"), W("B", "12"), W("C", "23"), W("D", "3")]
        self.assertEqual(effective_witnesses(ws), 2)


class ProximateCutTests(unittest.TestCase):
    """Novus actus interveniens — an independent re-derivation breaks the chain."""

    def test_rederivation_cuts_shared_ancestry(self):
        a, b = W("a", "z"), W("b", "z")
        self.assertTrue(proximately_dependent(a, b))
        cut = lambda x, y: True          # both independently re-derived
        self.assertFalse(proximately_dependent(a, b, rederived=cut))

    def test_rederived_witnesses_count_separately(self):
        ws = [W("a", "z"), W("b", "z")]
        dep = lambda x, y: proximately_dependent(x, y, rederived=lambda p, q: True)
        self.assertEqual(effective_witnesses(ws, dep), 2)

    def test_shared_marker_overrides_claimed_rederivation(self):
        """The trout beats the paperwork.

        A shared idiosyncratic error is direct evidence that no re-derivation
        occurred, whatever the provenance record asserts.
        """
        a = W("a", "z", markers="typo7")
        b = W("b", "z", markers="typo7")
        self.assertTrue(proximately_dependent(a, b, rederived=lambda x, y: True))

    def test_marker_detects_dependence_with_no_recorded_ancestry(self):
        """Provenance is silent; content is not."""
        a, b = W("a", markers="typo7"), W("b", markers="typo7")
        self.assertFalse(shares_ancestry(a, b))
        self.assertTrue(proximately_dependent(a, b))
        self.assertEqual(effective_witnesses([a, b]), 1)


class BoundTests(unittest.TestCase):
    def test_count_is_order_invariant(self):
        """Exact counting does not depend on presentation order.

        The greedy approximation does -- see
        ``tests/test_independent_set.py::test_ATTACK_greedy_order_dependence``.
        That is why greedy was retired as a fallback rather than kept for speed.
        """
        ws = [W("A", "1"), W("B", "12"), W("C", "23"), W("D", "3")]
        self.assertEqual(effective_witnesses(ws),
                         effective_witnesses(list(reversed(ws))))

    def test_empty_is_zero(self):
        self.assertEqual(effective_witnesses([]), 0)

    def test_single_witness_is_one(self):
        self.assertEqual(effective_witnesses([W("a", "z")]), 1)


class AttackTests(unittest.TestCase):
    def test_ATTACK_laundered_provenance_inflates_the_count(self):
        """The residual exposure, stated as a failing-by-design property.

        Three copies of one source. If the attacker strips the ancestry record
        and scrubs the shared markers, the graph has no edges and the count is
        3 instead of 1. No counting rule fixes this — only detection does, and
        detection can only report 'no trace found'. R3 margin sufficiency is
        what absorbs the residual.
        """
        honest = [W("o", "z"), W("c1", "z"), W("c2", "z")]
        self.assertEqual(effective_witnesses(honest), 1)

        laundered = [W("o"), W("c1"), W("c2")]     # ancestry erased
        self.assertEqual(effective_witnesses(laundered), 3)   # over-reports

    def test_ATTACK_marker_survives_partial_laundering(self):
        """Scrubbing provenance is not enough — content still betrays it."""
        laundered = [W("o", markers="typo7"), W("c1", markers="typo7"),
                     W("c2", markers="typo7")]
        self.assertEqual(effective_witnesses(laundered), 1)


if __name__ == "__main__":
    unittest.main()
