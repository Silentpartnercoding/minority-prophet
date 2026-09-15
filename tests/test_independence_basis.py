"""Independence basis: how a root's independence was established.

Added after cross-project conformance experiment MP-IG-CONFORMANCE-001 showed
that Invention Graph feeds roots in as DECLARED and UNKNOWN, and none of that
survived into a Minority Prophet verdict. The verdicts agreed; the reason they
agreed was invisible.

Nothing in formal/lean/ is wrong about this. T4 and T5 count roots and are
correct to. They say nothing about how hard each root is to forge.
"""

import unittest
from types import SimpleNamespace
from unittest import mock

from aggregation import root_vote
from aggregation.root_vote import (BASIS_RANK, IndependenceBasis, Verdict,
                                   asymmetric_verdict, verdict)


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

    def test_retired_rank_constant_is_unchanged_for_importers(self):
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

    def test_str_of_a_member_is_not_its_value(self):
        """The reason the enum path needs handling at all.

        `IndependenceBasis` mixes in `str`, but `Enum.__str__` wins, so `str()`
        on a member yields the qualified name. Coercing with `str()` before
        lookup therefore rejects the vocabulary's own members. Pinned here so
        the branch in `_basis_of` is not later removed as redundant.
        """
        self.assertEqual("IndependenceBasis.ATTESTED", str(IndependenceBasis.ATTESTED))
        self.assertNotEqual("attested", str(IndependenceBasis.ATTESTED))

    def test_a_member_is_accepted_as_itself(self):
        """A caller reaching for the enum must not be silently downgraded."""
        for member in IndependenceBasis:
            with self.subTest(basis=member.value):
                by_member = verdict([Claim(True, "a", member), Claim(False, "b", member)])
                by_string = verdict([Claim(True, "a", member.value),
                                     Claim(False, "b", member.value)])
                self.assertEqual(member.value, by_member.weakest_basis)
                self.assertEqual(by_string.weakest_basis, by_member.weakest_basis)
                self.assertEqual(by_string.basis_counts, by_member.basis_counts)

    def test_an_attested_member_still_counts_as_attested(self):
        """The consequence that made this worth fixing.

        `attested_margin` and the ATTESTED path in `asymmetric_verdict` both key
        off this value. A basis downgraded to UNKNOWN does not merely lose
        detail -- it removes a root from the attested count, which is an input
        to a decision rather than a label on one.
        """
        result = verdict([Claim(True, "a", IndependenceBasis.ATTESTED),
                          Claim(False, "b", IndependenceBasis.ATTESTED)])
        self.assertEqual({"attested": 2}, result.basis_counts)
        self.assertEqual(0, result.attested_margin)
        self.assertEqual("attested", result.weakest_basis)

    def test_unrecognised_values_still_read_as_unknown(self):
        """Genuine junk still reads as unknown: it states nothing."""
        for junk in ("ATTESTED", "somewhat-attested", "", 7):
            with self.subTest(junk=junk):
                result = verdict([Claim(True, "a", junk), Claim(False, "b", "attested")])
                self.assertEqual("unknown", result.weakest_basis)


def _v3(value, root_id, basis=None, **axes):
    return SimpleNamespace(value=value, root_id=root_id, independence_basis=basis,
                           witness_depth=axes.get("depth"),
                           attestation=axes.get("attestation"),
                           witness_identity=axes.get("identity"),
                           depth_basis=axes.get("depth_basis"))


class LadderRetiredTests(unittest.TestCase):
    """`BASIS_RANK` is retired: no output is computed from it."""

    CASES = [
        [Claim(True, "a", "attested"), Claim(True, "b", "inferred"),
         Claim(False, "c", "declared")],
        [Claim(True, "a", "attested"), Claim(True, "a", "inferred"),
         Claim(False, "b", "unknown")],
        [Claim(True, "a", "declared"), Claim(False, "b", "attested")],
    ]

    def test_verdict_does_not_read_the_ladder(self):
        """Reversing the retired rank changes nothing."""
        reversed_rank = {b: 3 - r for b, r in BASIS_RANK.items()}
        for claims in self.CASES:
            before = verdict(claims)
            with mock.patch.dict(root_vote.BASIS_RANK, reversed_rank):
                after = verdict(claims)
            self.assertEqual(before, after)

    def test_asymmetric_verdict_does_not_read_the_ladder(self):
        reversed_rank = {b: 3 - r for b, r in BASIS_RANK.items()}
        claims = [Claim(False, "a", "attested"), Claim(False, "b", "inferred"),
                  Claim(True, "c", "declared")]
        before = asymmetric_verdict(claims, claim_shape="universal")
        with mock.patch.dict(root_vote.BASIS_RANK, reversed_rank):
            after = asymmetric_verdict(claims, claim_shape="universal")
        self.assertEqual(before, after)

    def test_incomparable_decisive_roots_report_their_meet(self):
        """A notarised counterexample and a reasoned one: the ladder called the
        weaker 'inferred'. Neither is below the other, so the label is their
        greatest lower bound, and the outcome still notes weak decisive evidence."""
        result = asymmetric_verdict(
            [Claim(False, "a", "attested"), Claim(False, "b", "inferred")],
            claim_shape="universal")
        self.assertEqual("unknown", result.weakest_basis)
        self.assertTrue(any("decisive evidence rests on" in n for n in result.notes))

    def test_stated_independent_attestation_counts_as_attested(self):
        """A v3 producer that states the attestation axis is counted on it. The
        ladder read only the legacy label and missed these roots."""
        result = verdict([_v3(True, "a", attestation="independent"),
                          _v3(True, "b", attestation="adversarial"),
                          _v3(False, "c", "declared")])
        self.assertEqual(2, result.attested_margin)
        self.assertEqual({"attested": 2, "declared": 1}, result.basis_counts)

    def test_stated_self_attestation_overrides_an_attested_label(self):
        """A root labelled attested whose producer says the source vouched for
        itself is not attested. The axis is the record; the label was a summary."""
        result = verdict([_v3(True, "a", "attested", attestation="self"),
                          _v3(False, "b", "attested")])
        self.assertEqual(-1, result.attested_margin)
        self.assertEqual("declared", result.weakest_basis)

    def test_attested_margin_is_about_forgery_not_depth(self):
        """Notarised hearsay still counts toward attested_margin: forging its
        attestation is exactly as hard. Its missing depth shows in weakest_axes."""
        hearsay = _v3(True, "a", attestation="independent", depth="text")
        eyewitness = _v3(True, "b", attestation="none", depth="reality",
                         depth_basis="artifact")
        result = verdict([hearsay, eyewitness])
        self.assertEqual(1, result.attested_margin)
        self.assertFalse(result.weakest_basis_well_defined)
        self.assertEqual(2, len(result.weakest_axes))


if __name__ == "__main__":
    unittest.main()
