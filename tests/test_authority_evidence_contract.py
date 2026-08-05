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
