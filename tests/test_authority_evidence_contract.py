import copy
import unittest

from conformance.authority_evidence import sha256_uri, validate


def valid_envelope():
    action = {"type": "github.comment", "target": "repo#1", "payload_digest": "sha256:" + "a" * 64}
    return {
        "schema_version": "0.1",
        "request": {
            "request_id": "req-1", "subject_id": "agent-1", "principal_id": "human-1",
            "delegation_id": "del-1", "action": action,
            "created_at": "2026-08-05T00:00:00Z", "nonce": "0123456789abcdef",
        },
        "receipt": {
            "receipt_id": "rec-1", "request_id": "req-1", "action_digest": sha256_uri(action),
            "subject_id": "agent-1", "principal_id": "human-1",
            "delegation": {"delegation_id": "del-1", "status": "active",
                           "not_before": "2026-08-05T00:00:00Z", "expires_at": "2026-08-06T00:00:00Z"},
            "decision": "allow", "effect": {"status": "succeeded", "attempt_count": 1,
                                               "idempotency_key": "0123456789abcdef"},
            "evidence_origin": {"claim_digest": "sha256:" + "b" * 64,
                                "origin_type": "observation", "root_id": "root-1",
                                "parent_roots": [], "independence_basis": "attested"},
            "provider": {"provider_id": "provider.example", "key_id": "key-1"},
            "issued_at": "2026-08-05T00:00:01Z",
            "signature": {"algorithm": "example", "key_id": "key-1", "value": "not-a-real-signature"},
        },
    }


class AuthorityEvidenceContractTests(unittest.TestCase):
    def test_allow_executes_exactly_once(self):
        self.assertEqual(validate(valid_envelope()), [])
        record = valid_envelope()
        record["receipt"]["effect"]["attempt_count"] = 0
        self.assertIn("allow must execute exactly once", validate(record))

    def test_deny_executes_zero_times(self):
        record = valid_envelope()
        record["receipt"]["decision"] = "deny"
        self.assertIn("deny must execute zero times", validate(record))

    def test_revoked_authority_fails_closed(self):
        record = valid_envelope()
        record["receipt"]["delegation"]["status"] = "revoked"
        self.assertIn("revoked authority must fail closed", validate(record))

    def test_expired_by_time_fails_closed_even_if_labeled_active(self):
        record = valid_envelope()
        record["receipt"]["issued_at"] = "2026-08-07T00:00:00Z"
        self.assertIn("inactive-time authority must fail closed", validate(record))

    def test_action_identity_and_delegation_are_bound(self):
        for path, value, expected in (
            (("receipt", "action_digest"), "sha256:" + "0" * 64, "action digest mismatch"),
            (("receipt", "subject_id"), "agent-2", "subject identity substitution"),
            (("receipt", "principal_id"), "human-2", "principal substitution"),
            (("receipt", "delegation", "delegation_id"), "del-2", "delegation substitution"),
            (("receipt", "signature", "key_id"), "key-2", "signature key substitution"),
        ):
            record = valid_envelope()
            target = record
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            self.assertIn(expected, validate(record))

    def test_copy_cannot_mint_root(self):
        record = valid_envelope()
        record["receipt"]["evidence_origin"] = {
            "claim_digest": "sha256:" + "b" * 64, "origin_type": "copied",
            "root_id": "fresh-root", "parent_roots": ["root-1"],
            "independence_basis": "declared",
        }
        self.assertIn("copied evidence cannot mint a fresh root", validate(record))

    def test_unknown_origin_cannot_claim_independence(self):
        record = copy.deepcopy(valid_envelope())
        record["receipt"]["evidence_origin"]["origin_type"] = "unknown"
        self.assertIn("unknown origin cannot claim independence", validate(record))


def v2_envelope(**axes):
    """A v0.2 envelope: v0.1 plus whatever witness axes the caller states."""
    record = copy.deepcopy(valid_envelope())
    record["schema_version"] = "0.2"
    record["receipt"]["evidence_origin"].update(axes)
    return record


class WitnessAxesTests(unittest.TestCase):
    """v0.2 gives a producer somewhere to say how far its witness went.

    The census in `experiments/aid1/` found no published format had such a
    field, so nobody could state one even if they wanted to. These tests pin
    what the field accepts and what it refuses.
    """

    def test_a_stated_eyewitness_is_valid(self):
        self.assertEqual(validate(v2_envelope(
            witness_depth="reality", depth_basis="device-attested",
            witness_identity="verified", attestation="independent")), [])

    def test_v2_without_axes_is_exactly_v1(self):
        """Omit-if-absent: the addition costs a silent producer nothing."""
        self.assertEqual(validate(v2_envelope()), [])
        plain = copy.deepcopy(valid_envelope())
        self.assertEqual(validate(plain), [])
        self.assertEqual(plain["receipt"]["action_digest"],
                         v2_envelope()["receipt"]["action_digest"])

    def test_v1_may_not_carry_the_new_fields(self):
        """Fail closed: a v0.1 consumer does not know to read these, so a
        producer must not believe it has said something nobody receives."""
        record = copy.deepcopy(valid_envelope())
        record["receipt"]["evidence_origin"]["witness_depth"] = "reality"
        self.assertIn("schema_version 0.1 cannot carry witness axes",
                      validate(record))

    def test_unknown_values_are_refused_not_coerced(self):
        for field, bogus in (("witness_depth", "very-deep"),
                             ("depth_basis", "vibes"),
                             ("witness_identity", "famous"),
                             ("attestation", "enthusiastic")):
            self.assertIn(f"unrecognised {field}",
                          validate(v2_envelope(**{field: bogus})))

    def test_a_copy_cannot_claim_to_have_reached_the_world(self):
        record = v2_envelope(witness_depth="reality")
        record["receipt"]["evidence_origin"].update(
            origin_type="copied", root_id="root-1", parent_roots=["root-1"])
        self.assertIn("copied evidence cannot claim to have reached the world",
                      validate(record))

    def test_a_copy_may_still_say_it_re_read_the_text(self):
        record = v2_envelope(witness_depth="text")
        record["receipt"]["evidence_origin"].update(
            origin_type="copied", root_id="root-1", parent_roots=["root-1"])
        self.assertEqual(validate(record), [])

    def test_unknown_independence_cannot_carry_a_testament(self):
        record = v2_envelope(attestation="independent")
        record["receipt"]["evidence_origin"].update(
            origin_type="unknown", independence_basis="unknown")
        self.assertIn("unknown independence cannot carry a testament",
                      validate(record))

    def test_unstated_is_a_statement_that_nothing_was_stated(self):
        self.assertEqual(validate(v2_envelope(witness_depth="unstated")), [])


class VocabularyDoesNotDriftTests(unittest.TestCase):
    """Three copies of one vocabulary. A silent drift is worse than no sharing."""

    def test_checker_matches_the_aggregator(self):
        from aggregation.independence_axes import (
            ATTESTATION_WIRE, DEPTH_BASIS_WIRE, DEPTH_WIRE, IDENTITY_WIRE,
        )
        from conformance.authority_evidence import WITNESS_AXES

        for field, wire in (("witness_depth", DEPTH_WIRE),
                            ("depth_basis", DEPTH_BASIS_WIRE),
                            ("witness_identity", IDENTITY_WIRE),
                            ("attestation", ATTESTATION_WIRE)):
            self.assertEqual(set(WITNESS_AXES[field]), set(wire.values()), field)

    def test_schema_matches_the_checker(self):
        import json
        from pathlib import Path

        from conformance.authority_evidence import WITNESS_AXES

        schema = json.loads(
            (Path(__file__).resolve().parents[1]
             / "contracts/authority-evidence-v0.2/schema.json").read_text())
        origin = (schema["$defs"]["receipt"]["properties"]
                  ["evidence_origin"]["properties"])
        for field, values in WITNESS_AXES.items():
            self.assertEqual(origin[field]["enum"], list(values), field)

    def test_v2_is_v1_plus_exactly_the_four_axes(self):
        import json
        from pathlib import Path

        root = Path(__file__).resolve().parents[1] / "contracts"
        v1 = json.loads((root / "authority-evidence-v0.1/schema.json").read_text())
        v2 = json.loads((root / "authority-evidence-v0.2/schema.json").read_text())

        def origin(schema):
            return (schema["$defs"]["receipt"]["properties"]
                    ["evidence_origin"]["properties"])

        self.assertEqual(set(origin(v2)) - set(origin(v1)), {
            "witness_depth", "depth_basis", "witness_identity", "attestation"})
        self.assertEqual(set(origin(v1)) - set(origin(v2)), set())
        for field, definition in origin(v1).items():
            self.assertEqual(origin(v2)[field], definition, field)
        v1_required = v1["$defs"]["receipt"]["properties"]["evidence_origin"]["required"]
        v2_required = v2["$defs"]["receipt"]["properties"]["evidence_origin"]["required"]
        self.assertEqual(v1_required, v2_required, "no new field may be required")
