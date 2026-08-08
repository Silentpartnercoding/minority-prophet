import unittest

from experiments.hgd2.run_hgd2 import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    SHIFTS,
    software_outcome,
    software_records,
)


class Hgd2RunnerTests(unittest.TestCase):
    def test_frozen_configuration(self):
        self.assertEqual(BOOTSTRAP_SEED, 20260810)
        self.assertEqual(BOOTSTRAP_RESAMPLES, 10_000)
        self.assertEqual(SHIFTS, (-20.0, -10.0, -5.0, 5.0, 10.0, 20.0))

    def test_software_packet_is_confirmatory_and_family_bound(self):
        records, families = software_records()
        self.assertEqual(len(records), 36)
        self.assertEqual(set(families), {"compiler", "flawfinder", "lexical"})
        outcome = software_outcome(records[0], families, "interval")
        self.assertIn(outcome["state"], {"ANSWER", "ABSTAIN"})


if __name__ == "__main__":
    unittest.main()
