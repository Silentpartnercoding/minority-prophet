"""Semantic conformance checks for authority-evidence contracts v0.1 and v0.2.

v0.2 adds four optional witness axes to `evidence_origin`. The checks below
apply only where those fields appear, so a v0.1 envelope is validated exactly as
it was before.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

SUPPORTED_VERSIONS = ("0.1", "0.2")

#: The estate's wire vocabulary, duplicated byte-for-byte from
#: `aggregation/independence_axes.py`. A conformance test asserts the copies are
#: identical; neither may drift.
WITNESS_AXES: dict[str, tuple[str, ...]] = {
    "witness_depth": ("reality", "method", "replication", "raw", "analysis",
                      "text", "unstated"),
    "depth_basis": ("declared", "procedural", "artifact", "device-attested"),
    "witness_identity": ("anonymous", "pseudonymous", "named", "verified",
                         "bonded"),
    "attestation": ("none", "self", "internal", "independent", "adversarial"),
}

#: Depth ordering, world first. `unstated` is not on it: it is the absence of a
#: claim rather than a shallow one.
DEPTH_ORDER = ("reality", "method", "replication", "raw", "analysis", "text")


def canonical_json(value: object) -> bytes:
    # ensure_ascii=False is the normative form (provenance/canonical_form.py).
    # Without it a non-ASCII value serialises to \uXXXX escapes and digests
    # disagree with every other producer in the estate the moment an accent
    # appears. Nothing here was frozen, so alignment is safe.
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


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
    version = envelope.get("schema_version")
    if version not in SUPPORTED_VERSIONS:
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
        errors.extend(_witness_axis_errors(origin, version))
    return errors


def _witness_axis_errors(origin: dict[str, Any], version: str) -> list[str]:
    """Checks for the v0.2 witness axes. Silent when none is stated.

    Nothing here rejects a depth deeper than its backing supports. Overclaiming
    is not an error in the envelope; it is simply ineffective, because a
    consumer grants only what the backing carries
    (`aggregation.independence_axes.admissible_depth`). This contract records a
    claim and what backs it. It does not adjudicate the claim.
    """
    stated = {field: origin[field] for field in WITNESS_AXES if field in origin}
    if not stated:
        return []
    if version != "0.2":
        # Fail closed rather than quietly accept: a v0.1 consumer does not know
        # to read these, and silently tolerating them would let a producer
        # believe it had said something that nobody downstream receives.
        return [f"schema_version {version} cannot carry witness axes"]

    errors: list[str] = []
    for field, value in stated.items():
        if value not in WITNESS_AXES[field]:
            errors.append(f"unrecognised {field}")

    depth = stated.get("witness_depth")
    if (origin.get("origin_type") == "copied" and depth in DEPTH_ORDER
            and DEPTH_ORDER.index(depth) < DEPTH_ORDER.index("text")):
        errors.append("copied evidence cannot claim to have reached the world")

    attestation = stated.get("attestation")
    if (origin.get("independence_basis") == "unknown"
            and attestation is not None and attestation != "none"):
        errors.append("unknown independence cannot carry a testament")
    return errors
