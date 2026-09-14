"""`verdict()` carries the two-axis view alongside the legacy scale."""

import unittest
from itertools import combinations

from aggregation.independence_axes import Attestation, WitnessDepth, decompose
from aggregation.root_vote import verdict


class Claim:
    def __init__(self, value, root_id, basis=None):
        self.value = value
        self.root_id = root_id
        self.independence_basis = basis


class BackwardCompatibilityTests(unittest.TestCase):
    """Where the legacy scale was right, nothing changes."""

    def test_legacy_fields_are_untouched(self):
        r = verdict([Claim(True, "r1", "attested"), Claim(True, "r2", "declared")])
        self.assertEqual(r.weakest_basis, "declared")
        self.assertEqual(r.basis_counts, {"attested": 1, "declared": 1})
        self.assertEqual(r.margin, 2)

    def test_new_fields_default_safely_when_absent(self):
        r = verdict([Claim(True, "r1")])
        self.assertIsInstance(r.weakest_axes, tuple)
        self.assertIsInstance(r.weakest_basis_well_defined, bool)


class LegacyScaleTests(unittest.TestCase):
    """How much of the legacy ordering is real.

    `BASIS_RANK` asserts UNKNOWN < INFERRED < DECLARED < ATTESTED -- a total
    order over four values, so six pairwise relationships. **Two of the six do
    not exist.** `inferred` is the only value that states a depth; `attested`
    and `declared` state only a testament. Ranking them against each other
    invents an exchange rate between looking and vouching.
    """

    def test_only_unknown_is_a_genuine_bottom(self):
        for other in ("attested", "declared", "inferred"):
            self.assertTrue(decompose(other).dominates(decompose("unknown")),
                            f"{other} should dominate unknown")

    def test_attested_genuinely_beats_declared(self):
        """Same silence about depth, better testament. A real ordering."""
        self.assertTrue(decompose("attested").dominates(decompose("declared")))

    def test_inferred_is_incomparable_with_attested(self):
        """The rank claims ATTESTED(3) > INFERRED(1). It is not."""
        a, i = decompose("attested"), decompose("inferred")
        self.assertFalse(a.dominates(i))
        self.assertFalse(i.dominates(a))

    def test_inferred_is_incomparable_with_declared(self):
        """The rank claims DECLARED(2) > INFERRED(1). It is not."""
        d, i = decompose("declared"), decompose("inferred")
        self.assertFalse(d.dominates(i))
        self.assertFalse(i.dominates(d))

    def test_two_of_six_legacy_orderings_are_invented(self):
        real = incomparable = 0
        for a, b in combinations(("attested", "declared", "inferred", "unknown"), 2):
            x, y = decompose(a), decompose(b)
            if x.dominates(y) or y.dominates(x):
                real += 1
            else:
                incomparable += 1
        self.assertEqual((real, incomparable), (4, 2))


class WellDefinedTests(unittest.TestCase):
    def test_uniform_basis_has_one_weakest(self):
        r = verdict([Claim(True, f"r{i}", "attested") for i in range(4)])
        self.assertTrue(r.weakest_basis_well_defined)

    def test_unknown_present_gives_a_genuine_bottom(self):
        """`unknown` is weaker on both axes than everything, so it restores a
        single weakest wherever it appears."""
        r = verdict([Claim(True, "r1", "attested"),
                     Claim(True, "r2", "inferred"),
                     Claim(True, "r3", "unknown")])
        self.assertTrue(r.weakest_basis_well_defined)
        self.assertEqual(len(r.weakest_axes), 1)

    def test_attested_plus_declared_is_ordered(self):
        r = verdict([Claim(True, "r1", "attested"), Claim(True, "r2", "declared")])
        self.assertTrue(r.weakest_basis_well_defined)


class AmbiguityTests(unittest.TestCase):
    """The case `weakest_basis` cannot express."""

    def test_attested_and_inferred_have_no_single_weakest(self):
        """A notarised statement and something reached by reasoning are weakest
        in different ways: one has no testament, the other never looked.

        The retired ladder reported 'inferred' here. That was a fiction -- it
        ranked a depth against a testament, and there is no exchange rate between
        them.
        """
        r = verdict([Claim(True, "r1", "attested"), Claim(True, "r2", "inferred")])
        self.assertFalse(r.weakest_basis_well_defined)
        self.assertEqual(len(r.weakest_axes), 2)

    def test_the_legacy_field_reports_the_greatest_lower_bound(self):
        """No root is below both, so the label is their meet: weaker than each
        on every axis, with no exchange rate invented. The retired ladder said
        'inferred', ranking the reasoned inference below the notarised statement
        on the one axis where it is not weaker."""
        r = verdict([Claim(True, "r1", "attested"), Claim(True, "r2", "inferred")])
        self.assertEqual(r.weakest_basis, "unknown")
        self.assertFalse(r.weakest_basis_well_defined)

    def test_the_two_minimal_positions_are_each_better_on_one_axis(self):
        r = verdict([Claim(True, "r1", "attested"), Claim(True, "r2", "inferred")])
        depths = {a.depth for a in r.weakest_axes}
        attests = {a.attestation for a in r.weakest_axes}
        self.assertIn(WitnessDepth.TEXT, depths)
        self.assertIn(WitnessDepth.UNSTATED, depths)
        self.assertIn(Attestation.INDEPENDENT, attests)
        self.assertIn(Attestation.NONE, attests)

    def test_declared_and_inferred_also_have_no_single_weakest(self):
        """The second invented ordering, seen through the live verdict path."""
        r = verdict([Claim(True, "r1", "declared"), Claim(True, "r2", "inferred")])
        self.assertFalse(r.weakest_basis_well_defined)


if __name__ == "__main__":
    unittest.main()
