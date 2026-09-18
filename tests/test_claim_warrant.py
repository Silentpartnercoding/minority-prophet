"""The producer side of the claim warrant, which nothing implemented.

`claim-warrant.schema.json` requires `verify_determinism` and says two things
about it that were both unimplemented: it is "DERIVED, never author-supplied",
and "consumers recompute rather than trust it". Three test files supplied the
value by hand, so the suite was green over a field no code could produce.

`external_attestation` is the companion case — declared as an opaque passthrough
"stored for audit, never interpreted", and referenced by nothing at all.
"""

from __future__ import annotations

import pytest

from provenance.claim_warrant import (
    CLAIM_TYPES,
    WARRANT_KEY,
    ClaimWarrantError,
    attach_to,
    build_warrant,
    derive_verify_determinism,
    warrant_errors,
)
from provenance.graph import _RESOLVABLE_FORMS

DIGEST = "a" * 64


# --- the derivation -------------------------------------------------------


@pytest.mark.parametrize("claim_type", ["measured", "cited"])
def test_mechanical_claims_are_deterministic(claim_type):
    assert derive_verify_determinism(claim_type) == "deterministic"


@pytest.mark.parametrize("claim_type", ["inferred", "analogized"])
def test_judged_claims_are_oracle_conditional(claim_type):
    assert derive_verify_determinism(claim_type) == "oracle_conditional"


def test_every_claim_type_derives_something():
    """Total over the typology. A claim type with no derivation would be a
    warrant that cannot be built, discovered at runtime by whoever tried."""
    for claim_type in CLAIM_TYPES:
        assert derive_verify_determinism(claim_type) in (
            "deterministic", "oracle_conditional",
        )


def test_unknown_claim_type_raises_rather_than_defaulting():
    """Defaulting would label an unrecognised claim mechanically re-checkable,
    which overstates what can be verified — the direction that matters."""
    with pytest.raises(ClaimWarrantError, match="unrecognised claim_type"):
        derive_verify_determinism("vibes")


# --- the producer ---------------------------------------------------------


def test_build_warrant_derives_determinism():
    warrant = build_warrant("cited")
    assert warrant["verify_determinism"] == "deterministic"
    assert warrant["warrant_version"] == 1
    assert warrant_errors(warrant) == []


def test_verify_determinism_cannot_be_supplied():
    """The schema says never author-supplied. Offering the parameter would be
    offering a way to state it wrongly."""
    with pytest.raises(TypeError):
        build_warrant("cited", verify_determinism="oracle_conditional")


def test_absent_source_digest_is_omitted_not_blanked():
    """Absence must be recorded as absence. An empty string would later read as
    a digest that failed to match rather than one that was never taken."""
    warrant = build_warrant("measured")
    assert "source_digest" not in warrant


def test_source_digest_must_match_the_hash_form():
    with pytest.raises(ClaimWarrantError, match="hash form"):
        build_warrant("measured", source_digest="not-a-digest")


def test_source_digest_is_normalised():
    warrant = build_warrant("measured", source_digest="  " + DIGEST.upper() + " ")
    assert warrant["source_digest"] == DIGEST


# --- the opaque passthrough ----------------------------------------------


def test_external_attestation_round_trips_unchanged():
    """Stored for audit, never interpreted. The test is that it survives, not
    that anything understood it."""
    attestation = {"issuer": "an external service", "nested": {"claim": [1, 2, 3]}}
    warrant = build_warrant("cited", external_attestation=attestation)
    assert warrant["external_attestation"] == attestation
    assert warrant_errors(warrant) == []


def test_external_attestation_is_copied_not_referenced():
    """A later mutation by the caller must not retroactively change what the
    warrant recorded."""
    attestation = {"issuer": "original"}
    warrant = build_warrant("cited", external_attestation=attestation)
    attestation["issuer"] = "mutated"
    assert warrant["external_attestation"]["issuer"] == "original"


def test_external_attestation_contents_are_never_constrained():
    """Kept unconstrained so no external schema becomes a dependency of this
    one. Anything object-shaped is acceptable, however strange."""
    for payload in ({}, {"a": None}, {"deeply": {"nested": {"and": ["odd"]}}}):
        assert warrant_errors(build_warrant("cited", external_attestation=payload)) == []


def test_external_attestation_must_be_an_object():
    with pytest.raises(ClaimWarrantError, match="must be an object"):
        build_warrant("cited", external_attestation="a signed blob")


# --- the consumer recompute ----------------------------------------------


def test_consumer_rejects_a_contradictory_determinism():
    """The whole value of the field. A consumer that trusted the stated value
    would accept a claim labelled mechanically re-checkable when checking it
    actually requires an oracle."""
    warrant = build_warrant("inferred")
    warrant["verify_determinism"] = "deterministic"
    errors = warrant_errors(warrant)
    assert any("contradicts claim_type" in error for error in errors)


def test_consumer_rejects_unpermitted_keys():
    warrant = build_warrant("cited")
    warrant["confidence"] = 0.9
    assert any("unpermitted" in error for error in warrant_errors(warrant))


def test_consumer_rejects_a_missing_determinism():
    warrant = build_warrant("cited")
    del warrant["verify_determinism"]
    assert any("required" in error for error in warrant_errors(warrant))


def test_verify_outcome_stays_three_valued():
    warrant = build_warrant("cited")
    warrant["verify_outcome"] = {"result": "unverifiable", "reason": "fetch_failed"}
    assert warrant_errors(warrant) == []
    warrant["verify_outcome"] = {"result": "failed"}
    assert any("verified, rejected or unverifiable" in e for e in warrant_errors(warrant))


# --- placement ------------------------------------------------------------


def test_attach_to_uses_the_reserved_key_and_does_not_mutate():
    evidence = {"source": "https://example.org/paper"}
    attached = attach_to(evidence, build_warrant("cited", source_digest=DIGEST))
    assert attached[WARRANT_KEY]["claim_type"] == "cited"
    assert WARRANT_KEY not in evidence


def test_attach_to_refuses_a_malformed_warrant():
    with pytest.raises(ClaimWarrantError):
        attach_to({}, {"warrant_version": 1, "claim_type": "cited",
                       "verify_determinism": "oracle_conditional"})


def test_a_warrant_digest_never_satisfies_the_attribution_gate():
    """The placement rule, which is a gate bypass rather than a style choice.

    A warrant's `source_digest` matches the accepted `hash` form, so a flattened
    warrant could satisfy `resolvable_reference` and admit a root that
    `UnattributedRootError` had previously refused. Metadata must never satisfy
    the gate.
    """
    from provenance.graph import resolvable_reference

    properly_placed = attach_to({}, build_warrant("measured", source_digest=DIGEST))
    assert resolvable_reference(properly_placed) is None


def test_hash_form_has_not_drifted_from_the_graph_module():
    """`claim_warrant` duplicates the accepted `hash` form from `graph`. The
    placement rule only holds if both modules mean the same thing by "looks like
    a digest", so the copies are asserted equal rather than assumed."""
    from provenance.claim_warrant import _HASH_FORM

    graph_hash = dict(_RESOLVABLE_FORMS)["hash"]
    assert _HASH_FORM.pattern == graph_hash.pattern
