import unittest

from experiments.lir1.infer import infer_parents, roots_from_parents
from experiments.lir1.llm_echo.score_confirmatory import (
    BOOTSTRAP_SAMPLES,
    THRESHOLD,
    bootstrap_primary,
)
from experiments.lir1.synthetic_fixture import build_fixture, hide_edges


class LIR1EConfirmatoryTests(unittest.TestCase):
    def test_confirmatory_constants_are_frozen(self):
        self.assertEqual(THRESHOLD, 0.85)
        self.assertEqual(BOOTSTRAP_SAMPLES, 10_000)

    def test_case_bootstrap_is_deterministic(self):
        truth = build_fixture(36)
        visible = hide_edges(truth, 0.40)
        parents = infer_parents((row.feature_view() for row in visible), threshold=THRESHOLD)
        roots = roots_from_parents(parents)
        first = bootstrap_primary(truth, roots)
        second = bootstrap_primary(truth, roots)
        self.assertEqual(first, second)
        self.assertEqual(first["samples"], 10_000)


if __name__ == "__main__":
    unittest.main()
