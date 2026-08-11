"""KL-012's root measure must not merge accounts an exchange funded.

Fifty accounts funded from one exchange are fifty people. Merging them would make
the method appear predictive for a reason unrelated to independence -- and
exchange-funded accounts skew retail, which correlates with everything. That error
would not announce itself: it produces a good-looking result.

The pilot could not measure hubs at all. Fourteen of thirty-two funders exceeded a
4,000-transaction cap, so their true size was unknown, which is why an unknown
funder is now classified HUB and merges nothing.

These test the clustering logic against a synthetic funding graph. No RPC, so they
run in CI, and they were written before the collector produced a single qualifying
token.
"""
import pathlib
import sys
import unittest

KL012 = (pathlib.Path(__file__).resolve().parents[1] /
         "research/knowledge-ledger/experiments/KL-012")
sys.path.insert(0, str(KL012 / "src"))


def _load():
    import os
    os.environ.setdefault("KL012_SPEC", str(KL012 / "COLLECTION-SPEC-v0.1.json"))
    import roots
    return roots


FUNDING = {"a1": "f1", "a2": "f1", "a3": "f2", "a4": "EXCH", "a5": "EXCH",
           "a6": None, "f1": "g1", "f2": "g1", "g1": None}
HUBS = {"EXCH": {"hub": True}}


class RootClustering(unittest.TestCase):

    def setUp(self):
        self.roots = _load()
        self._f, self._c = self.roots.funder_of, self.roots.classify
        self.roots.funder_of = lambda a, cache: FUNDING.get(a)
        self.roots.classify = lambda a, cache: HUBS.get(a, {"hub": False})

    def tearDown(self):
        self.roots.funder_of, self.roots.classify = self._f, self._c

    def n(self, signers):
        return self.roots.cluster(signers, {}, {})

    def test_shared_direct_funder_is_one_root(self):
        self.assertEqual(self.n(["a1", "a2"]), 1)

    def test_shared_ancestor_within_max_hops_is_one_root(self):
        """a1->f1->g1 and a3->f2->g1: different funders, same grandparent."""
        self.assertEqual(self.n(["a1", "a3"]), 1)

    def test_exchange_funded_accounts_stay_separate(self):
        """The finding that would be fabricated if this failed."""
        self.assertEqual(self.n(["a4", "a5"]), 2,
                         "two accounts funded by a hub must remain two roots")

    def test_a_hub_never_bridges_a_cluster(self):
        self.assertEqual(self.n(["a1", "a4"]), 2)

    def test_an_unfundable_account_merges_with_nothing(self):
        self.assertEqual(self.n(["a6", "a1"]), 2)

    def test_a_mixed_population_resolves_correctly(self):
        self.assertEqual(self.n(["a1", "a2", "a3", "a4", "a5"]), 3)

    def test_the_spec_thresholds_are_read_not_hardcoded(self):
        spec = __import__("json").loads((KL012 / "COLLECTION-SPEC-v0.1.json").read_text())
        rm = spec["rootMeasure"]
        self.assertEqual(self.roots.MAX_HOPS, rm["MAX_HOPS"])
        self.assertEqual(self.roots.HUB_TX, rm["hubExclusion"]["HUB_MIN_TX"])


if __name__ == "__main__":
    unittest.main()
