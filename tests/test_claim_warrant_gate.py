"""The claim warrant must not move the unattributed-root gate.

A warrant describes how a claim could be checked. It is not evidence that the
claim named anything. Its `source_digest` is a hex string matching the accepted
`hash` form, so a warrant stored flat in `evidence` could satisfy
`resolvable_reference` and admit a root that was previously refused -- a hard
gate moving as a side effect of attaching metadata.

These tests pin that it does not.
"""

import unittest

from provenance.graph import WARRANT_KEY, resolvable_reference

DIGEST = "a" * 64  # a well-formed sha256 hex digest

WARRANT = {
    "warrant_version": 1,
    "claim_type": "cited",
    "verify_determinism": "deterministic",
    "source_digest": DIGEST,
}


class ClaimWarrantGateTests(unittest.TestCase):
    def test_bare_digest_still_resolves(self):
        """Unchanged behaviour: a hash sitting directly in evidence counts."""
        self.assertEqual(resolvable_reference({"digest": DIGEST}), "hash")

    def test_warrant_does_not_make_prose_resolvable(self):
        """The gate result is identical with and without a warrant attached."""
        prose = {"note": "the model asserted this without citing anything"}
        before = resolvable_reference(dict(prose))
        after = resolvable_reference({**prose, WARRANT_KEY: WARRANT})
        self.assertIsNone(before)
        self.assertEqual(before, after)

    def test_warrant_does_not_mask_a_real_reference(self):
        """Attaching a warrant does not suppress a genuine reference either."""
        real = {"source": "https://example.org/paper"}
        self.assertEqual(
            resolvable_reference(dict(real)),
            resolvable_reference({**real, WARRANT_KEY: WARRANT}),
        )

    def test_flattened_warrant_would_have_moved_the_gate(self):
        """Why the reserved key exists. This is the failure being prevented."""
        prose = {"note": "no citation here"}
        self.assertIsNone(resolvable_reference(dict(prose)))
        flattened = {**prose, **WARRANT}
        self.assertEqual(resolvable_reference(flattened), "hash")


if __name__ == "__main__":
    unittest.main()
