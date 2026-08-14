"""Independence basis: how a root's independence was established.

Added after cross-project conformance experiment MP-IG-CONFORMANCE-001 showed
that Invention Graph feeds roots in as DECLARED and UNKNOWN, and none of that
survived into a Minority Prophet verdict. The verdicts agreed; the reason they
agreed was invisible.

Nothing in formal/lean/ is wrong about this. T4 and T5 count roots and are
correct to. They say nothing about how hard each root is to forge.
"""

import unittest

from aggregation.root_vote import BASIS_RANK, IndependenceBasis, Verdict, verdict


class Claim:
    def __init__(self, value, root_id, basis=None):
        self.value = value
        self.root_id = root_id
        self.independence_basis = basis


class IndependenceBasisTests(unittest.TestCase):
    def test_vocabulary_matches_invention_graph_byte_for_byte(self):
        """Aligned so the two projects interoperate without translation."""
        self.assertEqual(
            [b.value for b in IndependenceBasis],
            ["attested", "declared", "inferred", "unknown"],
        )

    def test_absent_basis_reads_as_unknown_not_as_trusted(self):
        """A claim that does not say how independence was established has not
        established it. Existing callers keep working, reported as unknown."""
        result = verdict([Claim(True, "a"), Claim(True, "b"), Claim(False, "c")])
        self.assertEqual(result.weakest_basis, "unknown")
        self.assertEqual(result.basis_counts, {"unknown": 3})

    def test_unrecognised_basis_reads_as_unknown(self):
        result = verdict([Claim(True, "a", "vibes"), Claim(False, "b", "attested")])
        self.assertEqual(result.basis_counts, {"unknown": 1, "attested": 1})

    def test_identical_headcount_can_hide_opposite_security_stories(self):
        """The finding this whole feature exists for."""
        strong = [Claim(True, "a", "attested"), Claim(True, "b", "attested"),
                  Claim(True, "c", "attested"), Claim(False, "d", "attested")]
        weak = [Claim(True, "a", "declared"), Claim(True, "b", "unknown"),
                Claim(True, "c", "inferred"), Claim(False, "d", "attested")]

        a, b = verdict(strong), verdict(weak)
        # Indistinguishable on every pre-existing output.
        self.assertEqual(a.verdict, b.verdict)
        self.assertEqual(a.margin, b.margin)
        self.assertEqual(a.flip_budget, b.flip_budget)
        # And opposite once basis is counted.
        self.assertEqual(a.attested_margin, 2)
        self.assertEqual(b.attested_margin, -1)
        self.assertTrue(any("disagree in sign" in n for n in b.notes))
        self.assertFalse(any("disagree in sign" in n for n in a.notes))

    def test_margin_resting_on_no_attested_root_is_called_out(self):
        result = verdict([Claim(True, "a", "declared"), Claim(True, "b", "declared"),
                          Claim(False, "c", "declared")])
        self.assertEqual(result.margin, 1)
        self.assertEqual(result.attested_margin, 0)
        self.assertTrue(any("not a security budget" in n for n in result.notes))

    def test_a_root_takes_its_weakest_reported_basis(self):
        """Two accounts of one root may disagree. A root is only as
        independently established as its weakest supporting account."""
        result = verdict([Claim(True, "a", "attested"), Claim(True, "a", "unknown"),
                          Claim(False, "b", "attested")])
        self.assertEqual(result.basis_counts, {"unknown": 1, "attested": 1})
        self.assertEqual(result.weakest_basis, "unknown")

    def test_rank_orders_weakest_to_strongest(self):
        self.assertLess(BASIS_RANK[IndependenceBasis.UNKNOWN],
                        BASIS_RANK[IndependenceBasis.INFERRED])
        self.assertLess(BASIS_RANK[IndependenceBasis.INFERRED],
                        BASIS_RANK[IndependenceBasis.DECLARED])
        self.assertLess(BASIS_RANK[IndependenceBasis.DECLARED],
                        BASIS_RANK[IndependenceBasis.ATTESTED])

    def test_abstention_is_unaffected_by_basis(self):
        """Basis qualifies a margin; it does not create or destroy one."""
        result = verdict([Claim(True, "a", "attested"), Claim(False, "b", "unknown")])
        self.assertIs(result.verdict, Verdict.ABSTAIN)
        self.assertEqual(result.margin, 0)


if __name__ == "__main__":
    unittest.main()
