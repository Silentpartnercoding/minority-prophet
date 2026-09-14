"""Walking layer eight: who says so, and does the chain reach anything.

The criterion this was built against: a chain that terminates in a loop must be
detected and reported as a loop, not as support.
"""

import unittest

from canon.authority_debt import Authority, Ground, Link, TERMINAL, walk


def chain(*links):
    return {l.name: l for l in links}


class LinkTest(unittest.TestCase):
    def test_deference_must_name_who_it_defers_to(self):
        with self.assertRaises(ValueError):
            Link("a", Ground.DEFERENCE)

    def test_a_grounded_link_cannot_also_defer(self):
        """If it stands on its own it has nothing to point at."""
        with self.assertRaises(ValueError):
            Link("a", Ground.EVIDENCE, defers_to="b")

    def test_unknown_is_a_terminal_ground(self):
        """A chain ending in an honest admission is sound, not deficient."""
        self.assertIn(Ground.UNKNOWN, TERMINAL)
        self.assertNotIn(Ground.DEFERENCE, TERMINAL)


class LoopTest(unittest.TestCase):
    def setUp(self):
        self.c = chain(
            Link("deploy", Ground.DEFERENCE, defers_to="lead"),
            Link("lead", Ground.DEFERENCE, defers_to="policy"),
            Link("policy", Ground.DEFERENCE, defers_to="deploy"),
        )

    def test_a_loop_is_reported_as_a_loop_and_not_as_support(self):
        w = walk(self.c, "deploy")
        self.assertTrue(w.is_loop)
        self.assertEqual(w.loop_at, "deploy")
        self.assertIsNone(w.terminated_in)
        self.assertIn("LOOP", w.report())
        self.assertIn("not support", w.report())

    def test_a_loop_terminates_in_nothing_rather_than_in_a_ground(self):
        """The distinction that matters: no ground at all, not a weak one."""
        self.assertIsNone(walk(self.c, "deploy").terminated_in)

    def test_the_walk_returns_rather_than_hanging_or_raising(self):
        w = walk(self.c, "lead")
        self.assertTrue(w.is_loop)

    def test_debt_alone_cannot_distinguish_a_loop_from_a_long_sound_chain(self):
        """Why is_loop is its own field and not a number. Both are 100% deference;
        one reaches evidence at the end and one reaches nothing."""
        sound = chain(
            Link("a", Ground.DEFERENCE, defers_to="b"),
            Link("b", Ground.DEFERENCE, defers_to="c"),
            Link("c", Ground.EVIDENCE, note="measured"),
        )
        looped = walk(self.c, "deploy")
        ok = walk(sound, "a")
        self.assertEqual(looped.debt, 1.0)
        self.assertAlmostEqual(ok.debt, 2 / 3)
        self.assertTrue(looped.is_loop)
        self.assertFalse(ok.is_loop)
        self.assertIs(ok.terminated_in, Ground.EVIDENCE)


class TerminationTest(unittest.TestCase):
    def test_each_terminal_ground_ends_the_walk_at_itself(self):
        for g in TERMINAL:
            c = chain(Link("top", Ground.DEFERENCE, defers_to="base"),
                      Link("base", g, note="x"))
            w = walk(c, "top")
            self.assertIs(w.terminated_in, g)
            self.assertEqual(w.path, ("top", "base"))

    def test_an_honest_unknown_carries_zero_debt(self):
        c = chain(Link("risk", Ground.UNKNOWN, note="nobody knows, and we say so"))
        w = walk(c, "risk")
        self.assertIs(w.terminated_in, Ground.UNKNOWN)
        self.assertEqual(w.debt, 0.0)

    def test_debt_counts_only_the_deference_steps(self):
        c = chain(Link("a", Ground.DEFERENCE, defers_to="b"),
                  Link("b", Ground.MECHANISM, note="rerunnable"))
        self.assertEqual(walk(c, "a").deference_steps, 1)
        self.assertEqual(walk(c, "a").debt, 0.5)


class DanglingTest(unittest.TestCase):
    def test_deferring_to_a_name_that_does_not_exist_is_not_grounded(self):
        c = chain(Link("a", Ground.DEFERENCE, defers_to="ghost"))
        w = walk(c, "a")
        self.assertEqual(w.dangling_at, "ghost")
        self.assertIsNone(w.terminated_in)
        self.assertFalse(w.is_loop)
        self.assertIn("DANGLING", w.report())

    def test_dangling_and_loop_are_distinct_findings(self):
        c = chain(Link("a", Ground.DEFERENCE, defers_to="ghost"))
        self.assertFalse(walk(c, "a").is_loop)

    def test_walking_from_an_unknown_start_raises(self):
        with self.assertRaises(KeyError):
            walk(chain(Link("a", Ground.EVIDENCE, note="x")), "nope")


if __name__ == "__main__":
    unittest.main()


class CoordinationIsNotEpistemicTest(unittest.TestCase):
    """The guard ORIGINS.md recorded as owed to the code.

    The criterion: the two cases the prose calls out must come apart. A sound
    institutional chain must stop reading as pathological, and a chain that ends
    only because someone senior said so must stop reading as sound.
    """

    def test_a_title_cannot_settle_a_proposition(self):
        c = chain(
            Link("ship it", Ground.DEFERENCE, defers_to="vp",
                 defers_as=Authority.COORDINATION),
            Link("vp", Ground.JUDGMENT, accountable="VP eng, owns the outage budget"),
        )
        w = walk(c, "ship it")
        self.assertEqual(w.mistaken_authority, ("ship it",))
        self.assertIn("MISTAKEN AUTHORITY", w.report())
        self.assertIn("cannot settle a proposition", w.report())

    def test_coordination_authority_is_never_discounted(self):
        """Even on a walk that reaches evidence, a title borrowed nothing."""
        c = chain(
            Link("a", Ground.DEFERENCE, defers_to="b", defers_as=Authority.COORDINATION),
            Link("b", Ground.EVIDENCE, note="measured"),
        )
        w = walk(c, "a")
        self.assertTrue(w.is_grounded)
        self.assertEqual(w.borrowed_competence, ())
        self.assertEqual(w.bare_debt, 0.5)

    def test_a_finding_is_not_a_percentage(self):
        """Same reason is_loop is its own field: it must not average away."""
        c = chain(
            Link("a", Ground.DEFERENCE, defers_to="b", defers_as=Authority.COORDINATION),
            Link("b", Ground.DEFERENCE, defers_to="c", defers_as=Authority.EPISTEMIC),
            Link("c", Ground.DEFERENCE, defers_to="d", defers_as=Authority.EPISTEMIC),
            Link("d", Ground.EVIDENCE, note="trials"),
        )
        w = walk(c, "a")
        self.assertEqual(w.mistaken_authority, ("a",))
        self.assertLess(w.bare_debt, 0.5)  # diluted by sound links...
        self.assertTrue(w.mistaken_authority)  # ...but still reported on its own


class InstitutionalCompetenceTest(unittest.TestCase):
    """Institutions accumulate expertise no individual has. The module must be able
    to say so without that becoming a licence to defer to anything."""

    def setUp(self):
        self.c = chain(
            Link("clinician", Ground.DEFERENCE, defers_to="guideline",
                 defers_as=Authority.EPISTEMIC),
            Link("guideline", Ground.DEFERENCE, defers_to="trials",
                 defers_as=Authority.EPISTEMIC),
            Link("trials", Ground.EVIDENCE, note="randomised, published"),
        )

    def test_a_sound_institutional_chain_no_longer_reads_as_pathological(self):
        w = walk(self.c, "clinician")
        self.assertTrue(w.is_grounded)
        self.assertAlmostEqual(w.debt, 2 / 3)   # still two thirds deference...
        self.assertEqual(w.bare_debt, 0.0)      # ...and none of it borrowed nothing

    def test_the_discount_is_named_rather_than_silent(self):
        w = walk(self.c, "clinician")
        self.assertEqual(w.borrowed_competence, ("clinician", "guideline"))
        self.assertIn("borrowed competence", w.report())

    def test_promised_expertise_that_never_arrives_is_not_discounted(self):
        """The failure mode of the discount itself: borrowing on trust."""
        c = chain(
            Link("clinician", Ground.DEFERENCE, defers_to="guideline",
                 defers_as=Authority.EPISTEMIC),
            Link("guideline", Ground.DEFERENCE, defers_to="clinician",
                 defers_as=Authority.EPISTEMIC),
        )
        w = walk(c, "clinician")
        self.assertTrue(w.is_loop)
        self.assertEqual(w.borrowed_competence, ())
        self.assertEqual(w.bare_debt, 1.0)


class UngroundedJudgmentTest(unittest.TestCase):
    """"What is unsound is a chain that ends only because someone senior said so."
    The first version said that in the docstring and did not check it."""

    def test_a_judgment_naming_nobody_does_not_terminate_the_walk_soundly(self):
        c = chain(Link("a", Ground.DEFERENCE, defers_to="b",
                       defers_as=Authority.EPISTEMIC),
                  Link("b", Ground.JUDGMENT))
        w = walk(c, "a")
        self.assertIs(w.terminated_in, Ground.JUDGMENT)  # it did stop there
        self.assertFalse(w.is_grounded)                  # but it did not land
        self.assertEqual(w.ungrounded_judgment, "b")
        self.assertIn("seniority, not a foundation", w.report())

    def test_an_accountable_judgment_does(self):
        c = chain(Link("a", Ground.DEFERENCE, defers_to="b",
                       defers_as=Authority.EPISTEMIC),
                  Link("b", Ground.JUDGMENT,
                       accountable="on-call lead, stated 60-80% confidence"))
        w = walk(c, "b")
        self.assertTrue(w.is_grounded)
        self.assertIsNone(w.ungrounded_judgment)

    def test_an_ungrounded_judgment_withholds_the_competence_discount(self):
        c = chain(Link("a", Ground.DEFERENCE, defers_to="b",
                       defers_as=Authority.EPISTEMIC),
                  Link("b", Ground.JUDGMENT))
        self.assertEqual(walk(c, "a").borrowed_competence, ())


class UndeclaredDeferenceTest(unittest.TestCase):
    def test_deference_that_does_not_say_what_it_borrows_is_treated_as_bare(self):
        """A guard that defaults to generous is worth less than no guard."""
        c = chain(Link("a", Ground.DEFERENCE, defers_to="b"),
                  Link("b", Ground.EVIDENCE, note="measured"))
        w = walk(c, "a")
        self.assertEqual(w.undeclared_deference, ("a",))
        self.assertEqual(w.bare_debt, 0.5)
        self.assertIn("undeclared", w.report())

    def test_the_original_unannotated_chains_keep_their_original_reading(self):
        """Back-compatibility is a property, not an accident: every pre-existing
        chain is undeclared, so bare_debt equals debt exactly as debt did before."""
        c = chain(Link("a", Ground.DEFERENCE, defers_to="b"),
                  Link("b", Ground.DEFERENCE, defers_to="c"),
                  Link("c", Ground.EVIDENCE, note="measured"))
        w = walk(c, "a")
        self.assertEqual(w.bare_debt, w.debt)


class AuthorityFieldGuardsTest(unittest.TestCase):
    def test_only_a_deference_can_borrow_authority(self):
        with self.assertRaises(ValueError):
            Link("a", Ground.EVIDENCE, defers_as=Authority.EPISTEMIC)

    def test_accountability_means_nothing_outside_a_judgment(self):
        with self.assertRaises(ValueError):
            Link("a", Ground.EVIDENCE, accountable="someone")

    def test_the_two_authorities_are_not_interchangeable_values(self):
        self.assertNotEqual(Authority.EPISTEMIC, Authority.COORDINATION)
