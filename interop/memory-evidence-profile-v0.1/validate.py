#!/usr/bin/env python3
"""Validate the profile schema, semantic invariants, and adversarial cases."""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def load(name: str) -> dict[str, Any]:
    with (HERE / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def schema_validate(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    """Validate the JSON-Schema keywords used by this self-contained profile."""
    if "const" in schema:
        assert value == schema["const"], f"{path}: const mismatch"
    if "enum" in schema:
        assert value in schema["enum"], f"{path}: value outside enum"
    expected = schema.get("type")
    if expected:
        allowed = expected if isinstance(expected, list) else [expected]
        checks = {
            "object": lambda item: isinstance(item, dict),
            "array": lambda item: isinstance(item, list),
            "string": lambda item: isinstance(item, str),
            "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
            "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
            "null": lambda item: item is None,
        }
        assert any(checks[kind](value) for kind in allowed), f"{path}: wrong type"
    if isinstance(value, dict):
        required = schema.get("required", [])
        assert set(required) <= set(value), f"{path}: missing required property"
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            assert set(value) <= set(properties), f"{path}: unexpected property"
        for key, child in value.items():
            if key in properties:
                schema_validate(child, properties[key], f"{path}.{key}")
    if isinstance(value, list):
        assert len(value) >= schema.get("minItems", 0), f"{path}: too few items"
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            assert len(encoded) == len(set(encoded)), f"{path}: duplicate items"
        if "items" in schema:
            for index, child in enumerate(value):
                schema_validate(child, schema["items"], f"{path}[{index}]")
    if isinstance(value, str):
        assert len(value) >= schema.get("minLength", 0), f"{path}: string too short"
        if "pattern" in schema:
            assert re.fullmatch(schema["pattern"], value), f"{path}: pattern mismatch"
        if schema.get("format") == "date-time":
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        assert value >= schema.get("minimum", value), f"{path}: below minimum"
        assert value <= schema.get("maximum", value), f"{path}: above maximum"


def roots(document: dict[str, Any], claim_id: str) -> frozenset[str]:
    claims = {claim["id"]: claim for claim in document["claims"]}
    cache: dict[str, frozenset[str]] = {}

    def visit(current: str, stack: tuple[str, ...] = ()) -> frozenset[str]:
        assert current in claims, "unknown ancestor"
        assert current not in stack, "derivation cycle"
        if current in cache:
            return cache[current]
        parents = claims[current]["derived_from"]
        result = frozenset({current}) if not parents else frozenset().union(
            *(visit(parent, stack + (current,)) for parent in parents)
        )
        cache[current] = result
        return result

    return visit(claim_id)


def validate_semantics(document: dict[str, Any]) -> None:
    claims = {claim["id"]: claim for claim in document["claims"]}
    assert len(claims) == len(document["claims"]), "duplicate claim id"
    for claim in document["claims"]:
        roots(document, claim["id"])
        auth = claim["root_authentication"]
        if auth["status"] == "authenticated":
            assert not claim["derived_from"], "derived claim cannot mint an authenticated root"
            assert all(auth[field] for field in ("issuer", "key_id", "method"))
        else:
            assert all(auth[field] is None for field in ("issuer", "key_id", "method"))

    conclusion = document["conclusion"]
    assert set(conclusion["input_claims"]) <= set(claims), "unknown conclusion input"
    lifecycle = document["lifecycle"]
    observed = datetime.fromisoformat(lifecycle["observed_at"].replace("Z", "+00:00"))
    expires = datetime.fromisoformat(lifecycle["expires_at"].replace("Z", "+00:00"))
    assert expires > observed, "non-positive evidence lifetime"
    decisive = conclusion["kind"] != "inconclusive"
    if decisive:
        assert lifecycle["revocation_status"] == "active", "revoked or unknown evidence is not decisive"
        input_roots = set().union(*(roots(document, item) for item in conclusion["input_claims"]))
        assert input_roots, "decisive conclusion has no roots"
        assert all(
            claims[root]["root_authentication"]["status"] == "authenticated"
            for root in input_roots
        ), "declared root cannot support a decisive conclusion"
    if conclusion["kind"] == "absence":
        search = document["search"]
        assert search["coverage"] == "complete", "absence requires complete coverage"
        assert search["total_known"] is not None
        assert search["queried"] == search["total_known"]


def apply_mutation(document: dict[str, Any], mutation: dict[str, Any]) -> None:
    target: Any = document
    parts = mutation["path"].split(".")
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    final = parts[-1]
    if isinstance(target, list):
        target[int(final)] = mutation["value"]
    else:
        target[final] = mutation["value"]


def main() -> None:
    schema = load("schema.json")
    names = [
        "copied-consensus.json",
        "incomplete-search.json",
        "shared-control-verifier.json",
        "stale-derived-status.json",
    ]
    documents = [load(name) for name in names]
    documents.append(load("opaque-memory-cell.json")["evidence_profile"])
    for document in documents:
        schema_validate(document, schema)
        validate_semantics(document)

    copied = documents[0]
    all_roots = set().union(*(roots(copied, claim["id"]) for claim in copied["claims"]))
    assert all_roots == {"observation-1"}, "copies inflated roots"
    assert len({item["controller"] for item in documents[2]["verifiers"]}) == 1

    # stale-derived-status: a restatement of an older observation, carried in a
    # cell whose only recorded time is its own. The roots collapse correctly --
    # that part the profile already handles -- but nothing in the document dates
    # the observation the restatement rests on, so a proposition about a CURRENT
    # state cannot be aged by a consumer.
    #
    # The assertion below is deliberately an assertion of absence. A claim-level
    # observation time would resolve this case; that it does not exist is the
    # finding, and this test exists so that adding one is a visible change here
    # rather than a silent improvement nobody notices.
    stale = documents[3]
    stale_roots = set().union(*(roots(stale, claim["id"]) for claim in stale["claims"]))
    assert stale_roots == {"observation-1"}, "restatement inflated roots"
    assert all("observed_at" not in claim for claim in stale["claims"]), (
        "a claim-level observation time would let a consumer age the root; "
        "its absence is what this case reports"
    )

    adversarial = load("adversarial-cases.json")["cases"]
    for case in adversarial:
        candidate = copy.deepcopy(documents[case["base_document"]])
        apply_mutation(candidate, case["mutation"])
        try:
            schema_validate(candidate, schema)
            validate_semantics(candidate)
        except (AssertionError, ValueError):
            continue
        raise AssertionError(f"adversarial case accepted: {case['id']}")

    nonces = [document["lifecycle"]["nonce"] for document in documents]
    assert len(nonces) == len(set(nonces)), "replayed nonce across examples"
    print(f"PASS: {len(documents)} examples; {len(adversarial)} adversarial cases rejected")


if __name__ == "__main__":
    main()
