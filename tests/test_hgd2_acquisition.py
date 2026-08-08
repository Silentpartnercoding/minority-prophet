import unittest

from experiments.hgd2.acquire_software_evidence import BAD_ROOT, GOOD_ROOT, selected_pairs


class Hgd2AcquisitionTests(unittest.TestCase):
    @unittest.skipUnless(GOOD_ROOT.exists() and BAD_ROOT.exists(), "frozen source archives not local")
    def test_reciprocal_candidate_pairs_and_pair_safe_split(self):
        pairs, development = selected_pairs()
        self.assertGreater(len(pairs), 20)
        for good, bad in pairs:
            self.assertEqual(good["state"], "good")
            self.assertEqual(bad["state"], "bad")
            self.assertEqual(good["cwe"], bad["cwe"])
            self.assertEqual(good["case"] in development, bad["case"] in development)
        self.assertEqual(sum(good["case"] not in development for good, _ in pairs), 20)


if __name__ == "__main__":
    unittest.main()
