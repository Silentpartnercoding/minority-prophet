import random
import unittest

from experiments.hvi1.run_hvi1 import (
    BASE_WORLDS_PER_SEED,
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    SEEDS,
    answer,
    generate_base,
    hidden_domain_count,
    materialize,
)


class Hvi1RunnerTests(unittest.TestCase):
    def setUp(self):
        self.base = generate_base(random.Random(401), 401, 0)

    def test_configuration_matches_public_preregistration(self):
        self.assertEqual(SEEDS, tuple(range(401, 421)))
        self.assertEqual(BASE_WORLDS_PER_SEED, 250)
        self.assertEqual(BOOTSTRAP_SEED, 20260807)
        self.assertEqual(BOOTSTRAP_RESAMPLES, 10_000)

    def test_aliases_keys_and_services_do_not_change_control_mass(self):
        expected = answer(materialize(self.base, "single"), "control_domain")["mass"]
        for variant in ("alias_2", "alias_8", "alias_32", "key_rotation_8", "service_split_8"):
            self.assertEqual(answer(materialize(self.base, variant), "control_domain")["mass"], expected)

    def test_self_verification_adds_no_root(self):
        receipts = materialize(self.base, "self_verified_8")
        self.assertEqual(answer(receipts, "control_domain")["mass"], 6)

    def test_unknown_control_escalates(self):
        outcome = answer(materialize(self.base, "unknown_control_8"), "control_domain")
        self.assertEqual(outcome["state"], "ESCALATE")
        self.assertEqual(outcome["mass"], 0)

    def test_genuine_and_partial_control_domains_remain_distinct(self):
        genuine = materialize(self.base, "genuine_8")
        partial = materialize(self.base, "partial_shared_8")
        self.assertEqual(hidden_domain_count(genuine), 14)
        self.assertEqual(answer(genuine, "control_domain")["mass"], 14)
        self.assertEqual(hidden_domain_count(partial), 8)
        self.assertEqual(answer(partial, "control_domain")["mass"], 8)


if __name__ == "__main__":
    unittest.main()
