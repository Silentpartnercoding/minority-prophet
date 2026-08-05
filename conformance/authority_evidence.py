"""Semantic conformance checks for authority-evidence contract v0.1."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256_uri(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def validate(envelope: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if envelope.get("schema_version") != "0.1":
        return ["unsupported schema_version"]
    request = envelope.get("request")
    receipt = envelope.get("receipt")
    if not isinstance(request, dict) or not isinstance(receipt, dict):
        return ["request and receipt must be objects"]

    for field in ("request_id", "subject_id", "principal_id", "delegation_id", "action"):
        if field not in request:
            errors.append(f"request missing {field}")
    for field in ("request_id", "subject_id", "principal_id", "action_digest", "delegation",
                  "decision", "effect", "evidence_origin"):
        if field not in receipt:
            errors.append(f"receipt missing {field}")
    if errors:
        return errors

    if receipt["request_id"] != request["request_id"]:
        errors.append("request_id substitution")
    if receipt["subject_id"] != request["subject_id"]:
        errors.append("subject identity substitution")
    if receipt["principal_id"] != request["principal_id"]:
        errors.append("principal substitution")
    delegation = receipt["delegation"]
    if not isinstance(delegation, dict) or delegation.get("delegation_id") != request["delegation_id"]:
        errors.append("delegation substitution")
    if receipt["action_digest"] != sha256_uri(request["action"]):
        errors.append("action digest mismatch")

    effect = receipt["effect"]
    if not isinstance(effect, dict):
        errors.append("effect must be an object")
    else:
        attempts = effect.get("attempt_count")
        status = effect.get("status")
        if receipt["decision"] == "deny" and (attempts != 0 or status != "prevented"):
            errors.append("deny must execute zero times")
        if receipt["decision"] == "allow" and (attempts != 1 or status != "succeeded"):
            errors.append("allow must execute exactly once")
        if attempts not in (0, 1):
            errors.append("attempt_count must be zero or one")

    authority_status = delegation.get("status") if isinstance(delegation, dict) else None
    issued_at = parse_time(receipt.get("issued_at"))
    not_before = parse_time(delegation.get("not_before")) if isinstance(delegation, dict) else None
    expires_at = parse_time(delegation.get("expires_at")) if isinstance(delegation, dict) else None
    time_invalid = (issued_at is None or not_before is None or expires_at is None
                    or issued_at < not_before or issued_at >= expires_at)
    if authority_status in ("expired", "revoked") or time_invalid:
        if receipt["decision"] != "deny" or effect.get("attempt_count") != 0:
            reason = authority_status if authority_status in ("expired", "revoked") else "inactive-time"
            errors.append(f"{reason} authority must fail closed")

    provider = receipt.get("provider")
    signature = receipt.get("signature")
    if (not isinstance(provider, dict) or not isinstance(signature, dict)
            or provider.get("key_id") != signature.get("key_id")):
        errors.append("signature key substitution")

    origin = receipt["evidence_origin"]
    if not isinstance(origin, dict):
        errors.append("evidence_origin must be an object")
    else:
        origin_type = origin.get("origin_type")
        parents = origin.get("parent_roots")
        root_id = origin.get("root_id")
        if origin_type in ("copied", "derived"):
            if not isinstance(parents, list) or not parents:
                errors.append(f"{origin_type} evidence requires parent roots")
            elif root_id not in parents:
                errors.append(f"{origin_type} evidence cannot mint a fresh root")
        if origin_type == "unknown" and origin.get("independence_basis") != "unknown":
            errors.append("unknown origin cannot claim independence")
    return errors
