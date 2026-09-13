"""Walking layer eight: who says so, and does the chain reach anything.

The criterion this was built against: a chain that terminates in a loop must be
detected and reported as a loop, not as support.
"""

import unittest

from canon.authority_debt import Ground, Link, TERMINAL, walk


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
