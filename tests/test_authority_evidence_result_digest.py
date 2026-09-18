"""`effect.result_digest`, declared in both contract versions and never read.

A receipt could carry a malformed digest, or a digest of a result that by its own
account never happened, and pass conformance.
"""

from __future__ import annotations

from conformance.authority_evidence import sha256_uri, validate

DIGEST = "sha256:" + "b" * 64


def envelope(decision="allow", **effect_overrides):
    action = {"verb": "publish", "target": "doc-1"}
    effect = {
        "status": "succeeded" if decision == "allow" else "prevented",
        "attempt_count": 1 if decision == "allow" else 0,
        "idempotency_key": "idem-0123456789abcdef",
    }
    effect.update(effect_overrides)
    return {
        "schema_version": "0.2",
        "request": {
            "request_id": "req-1", "subject_id": "sub-1", "principal_id": "prin-1",
            "delegation_id": "del-1", "action": action,
        },
        "receipt": {
            "request_id": "req-1", "subject_id": "sub-1", "principal_id": "prin-1",
            "action_digest": sha256_uri(action),
            "delegation": {
                "delegation_id": "del-1", "status": "active",
                "not_before": "2026-01-01T00:00:00Z",
                "expires_at": "2027-01-01T00:00:00Z",
            },
            "decision": decision,
            "effect": effect,
            "issued_at": "2026-06-01T00:00:00Z",
            "provider": {"key_id": "key-1"},
            "signature": {"key_id": "key-1", "algorithm": "ed25519"},
            "evidence_origin": {"origin_type": "observation", "root_id": "root-1"},
        },
    }


def test_a_valid_result_digest_passes():
    assert validate(envelope(result_digest=DIGEST)) == []


def test_an_absent_result_digest_is_still_permitted():
    """The schema leaves it optional. A checker that demanded it would be
    tightening the contract rather than enforcing it, which belongs in a version
    bump with its interop consequences, not in a validator."""
    assert validate(envelope()) == []


def test_a_malformed_result_digest_is_refused():
    errors = validate(envelope(result_digest="b" * 64))
    assert any("result_digest" in error for error in errors)


def test_a_non_string_result_digest_is_refused():
    errors = validate(envelope(result_digest=12345))
    assert any("result_digest" in error for error in errors)


def test_a_prevented_action_cannot_carry_a_result_digest():
    """The asymmetry that makes this worth checking. An absent digest is a
    producer declining to record one, which the contract permits. A digest on an
    action that never ran is a producer contradicting itself."""
    errors = validate(envelope(decision="deny", result_digest=DIGEST))
    assert any("prevented action cannot carry a result digest" in e for e in errors)


def test_v0_1_receipts_are_checked_the_same_way():
    """The field is declared in both versions, so the check is not v0.2-only."""
    document = envelope(result_digest="not-a-digest")
    document["schema_version"] = "0.1"
    document["receipt"]["evidence_origin"] = {"origin_type": "observation",
                                              "root_id": "root-1"}
    errors = validate(document)
    assert any("result_digest" in error for error in errors)
