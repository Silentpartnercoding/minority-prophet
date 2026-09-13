"""Three outcomes and precedent — why no threshold is required."""

import unittest

from canon.precedent import Case, Outcome, PrecedentGate
from canon.proximity import ErrorClass as E


def case(name, **kw):
    base = dict(witnesses={E.FABRICATION: 1}, reversibility=1.0,
                tail_risk=0.0, max_loss=1.0)
    base.update(kw)
    return Case(name, **base)


class HardDenialTests(unittest.TestCase):
    """What the laws settle with no preference at all."""

    def test_unbounded_undertaking(self):
        g = PrecedentGate()
        self.assertEqual(g.decide(case("u", max_loss=None))[0], Outcome.DENY)

    def test_zero_witnesses_against_the_governing_error(self):
        g = PrecedentGate()
        out, why = g.decide(case("z", witnesses={E.FABRICATION: 0}))
        self.assertEqual(out, Outcome.DENY)
        self.assertIn("no-independent-witness", why)

    def test_authority_expansion(self):
        g = PrecedentGate()
        self.assertEqual(
            g.decide(case("a", authority_expanded=True))[0], Outcome.DENY)

    def test_unverified_world_state(self):
        g = PrecedentGate()
        self.assertEqual(
            g.decide(case("w", world_verified=False))[0], Outcome.DENY)

    def test_hard_denials_need_no_precedent(self):
        """The extremes are determined on day one, with an empty case book."""
        g = PrecedentGate()
        self.assertEqual(len(g.precedents), 0)
        self.assertEqual(g.decide(case("u", max_loss=None))[0], Outcome.DENY)


class DominanceTests(unittest.TestCase):
    def setUp(self):
        self.g = PrecedentGate()
        self.probe = case("probe")
        self.g.record(self.probe, Outcome.ALLOW, "reversible and bounded", "owner")

    def test_strictly_better_case_is_allowed(self):
        better = case("better", witnesses={E.FABRICATION: 3}, max_loss=0.5)
        out, why = self.g.decide(better)
        self.assertEqual(out, Outcome.ALLOW)
        self.assertIn("dominates-allowed-precedent", why)

    def test_identical_case_is_allowed(self):
        self.assertEqual(self.g.decide(case("same"))[0], Outcome.ALLOW)

    def test_worse_case_escalates_rather_than_denying(self):
        """Being worse than an allowed case does not make you denied.

        It makes you undetermined. Only domination by a *denied* precedent
        denies — the gate never extrapolates past what it was told.
        """
        worse = case("worse", reversibility=0.1, max_loss=100.0)
        self.assertEqual(self.g.decide(worse)[0], Outcome.ESCALATE)

    def test_denied_precedent_denies_everything_below_it(self):
        bad = case("bad", reversibility=0.0, tail_risk=0.9, max_loss=1000.0)
        self.g.record(bad, Outcome.DENY, "irreversible and unbounded downside", "owner")
        worse = case("worse", reversibility=0.0, tail_risk=0.95, max_loss=5000.0)
        out, why = self.g.decide(worse)
        self.assertEqual(out, Outcome.DENY)
        self.assertIn("dominated-by-denied-precedent", why)

    def test_incomparable_cases_escalate(self):
        """Better on one axis, worse on another. Nothing is traded off."""
        mixed = case("mixed", witnesses={E.FABRICATION: 9}, reversibility=0.1)
        self.assertEqual(self.g.decide(mixed)[0], Outcome.ESCALATE)

    def test_no_axis_is_traded_against_another(self):
        """More witnesses never buys irreversibility. That trade is a preference."""
        many = case("many", witnesses={E.FABRICATION: 1000}, reversibility=0.0,
                    tail_risk=0.99, max_loss=10_000.0)
        self.assertNotEqual(self.g.decide(many)[0], Outcome.ALLOW)


class CaseLawTests(unittest.TestCase):
    def test_cold_start_escalates_everything_undetermined(self):
        """Correct behaviour, not a defect."""
        g = PrecedentGate()
        self.assertEqual(g.decide(case("first"))[0], Outcome.ESCALATE)
        self.assertEqual(g.escalation_rate, 1.0)

    def test_escalation_rate_falls_as_precedent_accumulates(self):
        g = PrecedentGate()
        g.decide(case("c0"))
        rate_before = g.escalation_rate
        g.record(case("c0"), Outcome.ALLOW, "decided", "owner")
        for i in range(9):
            g.decide(case(f"c{i+1}", witnesses={E.FABRICATION: 2}))
        self.assertLess(g.escalation_rate, rate_before)

    def test_precedent_requires_a_recorded_reason(self):
        """A precedent without reasoning is a number in disguise."""
        g = PrecedentGate()
        with self.assertRaises(ValueError):
            g.record(case("x"), Outcome.ALLOW, "   ", "owner")

    def test_escalation_is_not_itself_a_decision(self):
        g = PrecedentGate()
        with self.assertRaises(ValueError):
            g.record(case("x"), Outcome.ESCALATE, "punted", "owner")

    def test_preference_enters_visibly_and_is_attributable(self):
        g = PrecedentGate()
        g.record(case("c"), Outcome.ALLOW, "cheap and reversible", "owner")
        p = g.precedents[0]
        self.assertTrue(p.reason)
        self.assertTrue(p.decided_by)


if __name__ == "__main__":
    unittest.main()
