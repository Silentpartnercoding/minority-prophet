"""Exact counting, and why the greedy approximation was retired."""

import unittest

from canon.independent_set import (
    CountingBudgetExceeded,
    greedy_independent_set_size,
    maximum_independent_set_size,
)

#: A hub cited by three otherwise-unrelated witnesses.
HUB_DEP = lambda a, b: "X" in (a, b)


class GreedyAttackTests(unittest.TestCase):
    def test_ATTACK_greedy_order_dependence(self):
        """Same evidence, two answers, chosen by whoever controls the ordering.

        This is a censorship primitive, not conservatism: an attacker who cannot
        inflate a count can still deflate one, making genuinely independent
        evidence look derivative and suppressing a true claim.
        """
        self.assertEqual(greedy_independent_set_size(["X", "A", "B", "C"], HUB_DEP), 1)
        self.assertEqual(greedy_independent_set_size(["A", "B", "C", "X"], HUB_DEP), 3)

    def test_exact_is_order_invariant(self):
        self.assertEqual(maximum_independent_set_size(["X", "A", "B", "C"], HUB_DEP), 3)
        self.assertEqual(maximum_independent_set_size(["A", "B", "C", "X"], HUB_DEP), 3)

    def test_greedy_never_exceeds_exact(self):
        for order in (["X", "A", "B", "C"], ["A", "B", "C", "X"]):
            self.assertLessEqual(
                greedy_independent_set_size(order, HUB_DEP),
                maximum_independent_set_size(order, HUB_DEP))


class ExactnessTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(maximum_independent_set_size([], lambda a, b: True), 0)

    def test_all_independent(self):
        self.assertEqual(
            maximum_independent_set_size(list(range(20)), lambda a, b: False), 20)

    def test_all_dependent(self):
        self.assertEqual(
            maximum_independent_set_size(list(range(20)), lambda a, b: True), 1)

    def test_components_are_summed(self):
        """Two disjoint cliques of three: one witness from each."""
        dep = lambda a, b: (a < 3) == (b < 3)
        self.assertEqual(maximum_independent_set_size(list(range(6)), dep), 2)

    def test_path_endpoints(self):
        """0—1—2: the endpoints are independent."""
        dep = lambda a, b: abs(a - b) == 1
        self.assertEqual(maximum_independent_set_size([0, 1, 2], dep), 2)


class BudgetTests(unittest.TestCase):
    def test_budget_refuses_rather_than_approximating(self):
        """Unknown != allow. A count that cannot be established is a denial."""
        dense = list(range(40))
        dep = lambda a, b: (a + b) % 3 != 0
        with self.assertRaises(CountingBudgetExceeded):
            maximum_independent_set_size(dense, dep, budget=5)

    def test_budget_message_says_refuse(self):
        with self.assertRaises(CountingBudgetExceeded) as ctx:
            maximum_independent_set_size(
                list(range(40)), lambda a, b: (a + b) % 3 != 0, budget=5)
        self.assertIn("refuse rather than approximate", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
