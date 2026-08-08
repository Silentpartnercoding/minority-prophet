#!/usr/bin/env python3
"""Validate profile examples and prove the v0.1 semantic invariants."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PROFILE = "memory-evidence-profile-v0.1"


def load(name: str) -> dict[str, Any]:
    with (HERE / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_shape(document: dict[str, Any]) -> None:
    assert document["profile"] == PROFILE
    assert isinstance(document["proposition"], str) and document["proposition"]
    claims = document["claims"]
    assert isinstance(claims, list) and claims
    ids = [claim["id"] for claim in claims]
    assert len(ids) == len(set(ids))
    seen: set[str] = set()
    for claim in claims:
        assert set(claim) == {"id", "value", "source", "derived_from"}
        assert claim["id"] and claim["source"]
        assert isinstance(claim["derived_from"], list)
        assert set(claim["derived_from"]) <= seen, "ancestry must precede a claim"
        seen.add(claim["id"])
    search = document["search"]
    assert search["coverage"] in {"complete", "partial", "unknown"}
    assert isinstance(search["queried"], int) and search["queried"] >= 0
    assert search["total_known"] is None or search["total_known"] >= search["queried"]
    conclusion = document["conclusion"]
    assert conclusion["kind"] in {"support", "contradict", "absence", "inconclusive"}
    assert 0 <= conclusion["strength"] <= 1 and conclusion["uncertainty"]


def roots(document: dict[str, Any], claim_id: str) -> frozenset[str]:
    claims = {claim["id"]: claim for claim in document["claims"]}
    cache: dict[str, frozenset[str]] = {}

    def visit(current: str, stack: tuple[str, ...] = ()) -> frozenset[str]:
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


def independent_verifier_count(document: dict[str, Any]) -> int:
    return len({verifier["controller"] for verifier in document["verifiers"]})


def validate_semantics(document: dict[str, Any]) -> None:
    search = document["search"]
    if document["conclusion"]["kind"] == "absence":
        assert search["coverage"] == "complete", "absence requires complete coverage"
        assert search["total_known"] is not None
        assert search["queried"] == search["total_known"]


def main() -> None:
    copied = load("copied-consensus.json")
    incomplete = load("incomplete-search.json")
    shared = load("shared-control-verifier.json")
    opaque = load("opaque-memory-cell.json")["evidence_profile"]
    documents = [copied, incomplete, shared, opaque]
    for document in documents:
        validate_shape(document)
        validate_semantics(document)

    all_roots = set().union(*(roots(copied, claim["id"]) for claim in copied["claims"]))
    assert all_roots == {"observation-1"}, "copies must not inflate roots"
    assert incomplete["conclusion"]["kind"] != "absence"
    invalid_absence = json.loads(json.dumps(incomplete))
    invalid_absence["conclusion"]["kind"] = "absence"
    try:
        validate_semantics(invalid_absence)
    except AssertionError:
        pass
    else:
        raise AssertionError("incomplete search manufactured absence")
    assert len(shared["verifiers"]) == 2
    assert independent_verifier_count(shared) == 1, "common control manufactured independence"
    print("PASS: 4 examples; roots=1; partial-search absence rejected; verifier controllers=1")


if __name__ == "__main__":
    main()
