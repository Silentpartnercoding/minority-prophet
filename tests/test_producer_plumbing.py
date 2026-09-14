"""End-to-end: a producer states the axes and the verdict counts on them.

Before this, `verdict()` read one field off each claim -- `independence_basis` --
so every root arrived with no depth and no identity regardless of what the
producer knew. These tests pin the path from a claim that states its axes
through to the verdict that uses them.
"""

import unittest

from aggregation.independence_axes import (
    Attestation,
    WitnessDepth,
    WitnessIdentity,
)
from aggregation.root_vote import verdict


class Claim:
    """A v3 producer. Any field may be omitted."""

    def __init__(self, value, root_id, basis=None, depth=None,
                 attestation=None, identity=None):
        self.value = value
        self.root_id = root_id
        self.independence_basis = basis
        self.witness_depth = depth
        self.attestation = attestation
        self.witness_identity = identity


class LegacyProducerTests(unittest.TestCase):
    """A v1 producer must behave exactly as it did before."""

    def test_legacy_claim_reads_as_before(self):
        r = verdict([Claim(True, "r1", "attested"), Claim(True, "r2", "attested")])
        self.assertEqual(r.weakest_basis, "attested")
        self.assertEqual(r.margin, 2)

    def test_legacy_claims_are_anonymous_with_no_depth(self):
        """The honest reading of silence, and why the bounds are a range."""
        r = verdict([Claim(True, "r1", "attested"), Claim(True, "r2", "attested")])
        for axes in r.weakest_axes:
            self.assertEqual(axes.depth, WitnessDepth.UNSTATED)
            self.assertEqual(axes.identity, WitnessIdentity.ANONYMOUS)
        self.assertEqual(r.witness_bounds, (1, 2))


class DepthReachesTheVerdictTests(unittest.TestCase):
    def test_a_stated_eyewitness_arrives_as_an_eyewitness(self):
        """The thing that was impossible this morning."""
        r = verdict([Claim(True, "r1", depth="reality", identity="named")])
        self.assertEqual(r.weakest_axes[0].depth, WitnessDepth.REALITY)
        self.assertEqual(r.weakest_axes[0].identity, WitnessIdentity.NAMED)

    def test_an_eyewitness_and_a_reader_no_longer_look_alike(self):
        eyewitness = verdict([Claim(True, "r1", depth="reality", identity="named")])
        reader = verdict([Claim(True, "r1", depth="text", identity="named")])
        self.assertNotEqual(eyewitness.weakest_axes, reader.weakest_axes)

    def test_partial_statement_falls_back_per_axis(self):
        """State depth only: attestation still comes from the legacy basis."""
        r = verdict([Claim(True, "r1", basis="attested", depth="reality")])
        axes = r.weakest_axes[0]
        self.assertEqual(axes.depth, WitnessDepth.REALITY)
        self.assertEqual(axes.attestation, Attestation.INDEPENDENT)


class IdentityBoundsTests(unittest.TestCase):
    def test_named_witnesses_give_a_determined_count(self):
        claims = [Claim(True, f"r{i}", depth="reality", identity="named")
                  for i in range(3)]
        r = verdict(claims)
        self.assertEqual(r.witness_bounds, (3, 3))

    def test_anonymous_witnesses_give_a_range(self):
        claims = [Claim(True, f"r{i}", depth="reality", identity="anonymous")
                  for i in range(3)]
        r = verdict(claims)
        self.assertEqual(r.witness_bounds, (1, 3))

    def test_mixed_identity_bounds_only_the_anonymous_part(self):
        claims = [Claim(True, "r1", depth="reality", identity="named"),
                  Claim(True, "r2", depth="reality", identity="named"),
                  Claim(True, "r3", depth="reality", identity="anonymous"),
                  Claim(True, "r4", depth="reality", identity="anonymous")]
        r = verdict(claims)
        self.assertEqual(r.witness_bounds, (3, 4))

    def test_the_count_is_never_collapsed_to_the_floor(self):
        claims = [Claim(True, f"r{i}", identity="anonymous") for i in range(4)]
        r = verdict(claims)
        self.assertEqual(r.witness_bounds[1], 4, "upper bound must keep them apart")


class DisagreementTests(unittest.TestCase):
    """Two claims about one root resolve to the componentwise meet."""

    def test_conflicting_depth_takes_the_shallower(self):
        r = verdict([Claim(True, "r1", depth="reality", identity="named"),
                     Claim(True, "r1", depth="text", identity="named")])
        self.assertEqual(r.weakest_axes[0].depth, WitnessDepth.TEXT)

    def test_conflicting_identity_takes_the_weaker(self):
        r = verdict([Claim(True, "r1", depth="reality", identity="named"),
                     Claim(True, "r1", depth="reality", identity="anonymous")])
        self.assertEqual(r.weakest_axes[0].identity, WitnessIdentity.ANONYMOUS)

    def test_the_meet_is_taken_on_every_axis_at_once(self):
        r = verdict([Claim(True, "r1", depth="reality", attestation="independent",
                           identity="named"),
                     Claim(True, "r1", depth="analysis", attestation="self",
                           identity="pseudonymous")])
        axes = r.weakest_axes[0]
        self.assertEqual(axes.depth, WitnessDepth.ANALYSIS)
        self.assertEqual(axes.attestation, Attestation.SELF)
        self.assertEqual(axes.identity, WitnessIdentity.PSEUDONYMOUS)


class RefusalTests(unittest.TestCase):
    def test_an_unrecognised_axis_value_reads_as_unstated(self):
        """A producer sending a word this version does not know has not stated
        the axis. Silence claims nothing; the wire boundary is
        where unknown strings are refused."""
        r = verdict([Claim(True, "r1", basis="attested", depth="vibes")])
        self.assertEqual(r.weakest_axes[0].depth, WitnessDepth.UNSTATED)


if __name__ == "__main__":
    unittest.main()
