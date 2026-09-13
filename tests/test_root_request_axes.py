"""The v3 axes on a minted root, and why no id migration was needed."""

import unittest

from provenance.root_registry import RootRegistry, RootRequest

BASE = dict(issuer_id="issuer-1", key_id="key-1", observation_id="obs-1",
            proposition_id="prop-1", value=True, evidence_digest="dig",
            observed_at=1_000, nonce="n1")


class NoIdMigrationTests(unittest.TestCase):
    """The migration that turned out not to exist."""

    def test_root_id_ignores_the_v3_axes(self):
        plain = RootRequest(**BASE)
        stated = RootRequest(**BASE, witness_depth="reality",
                             witness_identity="named")
        self.assertEqual(RootRegistry.root_identity(plain),
                         RootRegistry.root_identity(stated))

    def test_identity_cannot_be_used_to_mint_a_second_id(self):
        """CE-05 territory: if identity were in the digest, one observation
        could be minted repeatedly by varying it, inflating the root count from
        inside quota."""
        ids = {RootRegistry.root_identity(
                   RootRequest(**BASE, witness_identity=who))
               for who in ("anonymous", "named", "verified", "bonded")}
        self.assertEqual(len(ids), 1)

    def test_learning_a_name_later_does_not_create_a_phantom_root(self):
        before = RootRegistry.root_identity(RootRequest(**BASE))
        after = RootRegistry.root_identity(
            RootRequest(**BASE, witness_identity="verified"))
        self.assertEqual(before, after)


class SignatureCompatibilityTests(unittest.TestCase):
    def test_payload_is_byte_identical_when_no_axis_is_stated(self):
        """Omit-if-absent: signatures made before v3 still verify."""
        self.assertEqual(RootRequest(**BASE).canonical_bytes(),
                         RootRequest(**BASE, witness_depth=None,
                                     attestation=None,
                                     witness_identity=None).canonical_bytes())

    def test_a_stated_axis_is_covered_by_the_signature(self):
        """An intermediary must not be able to upgrade hearsay to eyewitness."""
        hearsay = RootRequest(**BASE, witness_depth="text")
        eyewitness = RootRequest(**BASE, witness_depth="reality")
        self.assertNotEqual(hearsay.canonical_bytes(),
                            eyewitness.canonical_bytes())

    def test_each_axis_is_covered_independently(self):
        base = RootRequest(**BASE).canonical_bytes()
        for field, value in (("witness_depth", "reality"),
                             ("attestation", "adversarial"),
                             ("witness_identity", "bonded")):
            self.assertNotEqual(RootRequest(**BASE, **{field: value}).canonical_bytes(),
                                base, f"{field} must be signed")

    def test_payload_stays_canonically_ordered(self):
        raw = RootRequest(**BASE, witness_identity="named",
                          attestation="self").canonical_bytes().decode()
        keys = [p.split('"')[1] for p in raw.split("},")[0].split(",") if '":' in p]
        self.assertEqual(keys, sorted(keys), "keys must stay sorted")

    def test_with_signature_preserves_the_axes(self):
        signed = RootRequest(**BASE, witness_depth="reality").with_signature("sig")
        self.assertEqual(signed.witness_depth, "reality")
        self.assertEqual(signed.signature, "sig")


if __name__ == "__main__":
    unittest.main()
