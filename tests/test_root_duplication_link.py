"""The duplication link, enforced where the copier stands.

The attested-independence series ended on a wall: if shared origin is
unrecorded, the record left by five independent witnesses and by one witness
plus four copies is identical, and no reading rule can tell them apart
(`DR3.no_record_rule_is_immune`). The wall is around *reading*. The seam is the
copier -- the one process that holds the source and the destination at the same
instant and therefore knows, without inference, that the second is the first.

`origin_type` and `parent_roots` have been in the vendor-neutral contract since
v0.1, and `conformance/authority_evidence.py` has enforced that a copy may not
mint a fresh root. But a `RootRequest` had nowhere to carry them, so the rule
could only ever be applied at the contract boundary -- after issuance, to a root
that already existed. The socket was wired and nothing was plugged into it.

These tests cover the emission: the link is stateable at issuance, refused when
incoherent, covered by the signature, and -- the load-bearing one -- a copy
resolves to its parent's identity instead of a fresh root, which makes the
contract's rule true by construction rather than by later inspection.
"""

from __future__ import annotations

import pytest

from provenance.root_registry import (
    HmacIssuerVerifier,
    RootIssuanceError,
    RootRegistry,
    RootRequest,
)

KEY = (b"issuer-key" * 4)[:32]
INTEGRITY = (b"integrity-key" * 4)[:32]


def make_request(**overrides) -> RootRequest:
    base = dict(
        issuer_id="issuer-1",
        key_id="key-1",
        observation_id="obs-1",
        proposition_id="prop-1",
        value=True,
        evidence_digest="a" * 64,
        observed_at=1_700_000_000,
        nonce="nonce-1",
    )
    base.update(overrides)
    return RootRequest(**base)


@pytest.fixture
def registry(tmp_path):
    verifier = HmacIssuerVerifier({("issuer-1", "key-1"): KEY})
    return RootRegistry(
        tmp_path / "roots.db",
        verifier=verifier,
        integrity_key=INTEGRITY,
        clock=lambda: 1_700_000_000,
    )


def signed(registry: RootRegistry, request: RootRequest) -> RootRequest:
    return request.with_signature(registry.verifier.sign(request))


# --- the link is refused when it is incoherent -----------------------------


def test_copy_without_parents_is_refused(registry):
    """A copy that names no parent is the exact gap the field exists to close.

    Allowing it would be worse than having no field at all: it would let a
    copier assert `copied` and still mint a fresh root, which reads downstream
    as a disclosure while behaving as a duplicate.
    """
    request = signed(registry, make_request(origin_type="copied"))
    with pytest.raises(RootIssuanceError, match="must name its parent roots"):
        registry.issue(request)


def test_derived_without_parents_is_refused(registry):
    request = signed(registry, make_request(origin_type="derived"))
    with pytest.raises(RootIssuanceError, match="must name its parent roots"):
        registry.issue(request)


def test_parents_without_origin_type_is_refused(registry):
    """Naming a parent without saying what the relationship is leaves the most
    important part to inference, which is the habit this whole series indicts.
    """
    request = signed(registry, make_request(parent_roots=("root-a",)))
    with pytest.raises(RootIssuanceError, match="without an origin_type"):
        registry.issue(request)


def test_unrecognised_origin_type_is_refused(registry):
    request = signed(registry, make_request(origin_type="forwarded"))
    with pytest.raises(RootIssuanceError, match="unrecognised origin_type"):
        registry.issue(request)


def test_observation_needs_no_parents(registry):
    """The common case stays unencumbered; a first-hand observation says so and
    is issued with no link at all."""
    request = signed(registry, make_request(origin_type="observation"))
    receipt = registry.issue(request)
    assert receipt.root_id


# --- the load-bearing rule -------------------------------------------------


def test_copy_resolves_to_its_parent_identity(registry):
    """A copy does not get an identity of its own.

    This is the constructive answer to DR3. The theorem says no reading rule can
    separate five witnesses from one witness and four copies *when the origin is
    unrecorded*. Here the copier records it, at the only moment the fact is free
    to obtain, and the copy is therefore not a second root to be counted -- it
    resolves to the first one.
    """
    original = signed(registry, make_request(origin_type="observation"))
    parent_id = registry.root_identity(original)

    copy = make_request(
        observation_id="obs-2",
        nonce="nonce-2",
        origin_type="copied",
        parent_roots=(parent_id,),
    )
    assert registry.root_identity(copy) == parent_id


def test_copy_of_a_copy_still_resolves_to_the_first_root(registry):
    """Relay chains are where fan-out actually happens, so the link has to
    survive more than one hop."""
    original = signed(registry, make_request(origin_type="observation"))
    parent_id = registry.root_identity(original)

    first_copy = make_request(
        observation_id="obs-2", nonce="nonce-2",
        origin_type="copied", parent_roots=(parent_id,),
    )
    second_copy = make_request(
        observation_id="obs-3", nonce="nonce-3",
        origin_type="copied", parent_roots=(registry.root_identity(first_copy),),
    )
    assert registry.root_identity(second_copy) == parent_id


def test_independent_observations_keep_distinct_identities(registry):
    """The rule must not over-merge: two genuinely separate observations that
    declare themselves as such stay separate. A duplication check that collapses
    real witnesses would trade one failure for a worse one."""
    first = make_request(origin_type="observation")
    second = make_request(
        observation_id="obs-2", nonce="nonce-2", origin_type="observation",
    )
    assert registry.root_identity(first) != registry.root_identity(second)


def test_multiple_parents_resolve_deterministically(registry):
    """Whether a derivation from several roots deserves an identity of its own
    is a real modelling question this does not settle. It fails toward reuse,
    which cannot inflate a count, and it does so deterministically."""
    request = make_request(
        origin_type="derived", parent_roots=("root-b", "root-a", "root-c"),
    )
    assert registry.root_identity(request) == "root-a"
    reordered = make_request(
        origin_type="derived", parent_roots=("root-c", "root-a", "root-b"),
    )
    assert registry.root_identity(reordered) == "root-a"


# --- the link cannot be stripped in transit --------------------------------


def test_parent_roots_are_signature_covered(registry):
    """An intermediary must not be able to remove a parent and turn a copy back
    into an apparently fresh observation. That attack is precisely the one the
    theorem says is undetectable after the fact, so it has to be prevented
    before the fact, by the signature."""
    copy = make_request(origin_type="copied", parent_roots=("root-a",))
    signature = registry.verifier.sign(copy)

    stripped = make_request(origin_type="copied", parent_roots=())
    assert not registry.verifier.verify(
        stripped.issuer_id, stripped.key_id, stripped.canonical_bytes(), signature
    )


def test_origin_type_is_signature_covered(registry):
    copy = make_request(origin_type="copied", parent_roots=("root-a",))
    signature = registry.verifier.sign(copy)

    relabelled = make_request(origin_type="observation", parent_roots=("root-a",))
    assert not registry.verifier.verify(
        relabelled.issuer_id, relabelled.key_id,
        relabelled.canonical_bytes(), signature,
    )


def test_absent_link_is_byte_identical_to_the_previous_version():
    """Omit-if-absent. A request stating no link produces exactly the payload it
    produced before the field existed, so signatures made against the previous
    version still verify and no re-signing is required anywhere in the estate.
    """
    import json

    request = make_request()
    payload = json.loads(request.canonical_bytes())
    assert "origin_type" not in payload
    assert "parent_roots" not in payload
    assert set(payload) == {
        "evidence_digest", "issuer_id", "key_id", "nonce",
        "observation_id", "observed_at", "proposition_id", "value",
    }


def test_stated_link_appears_in_canonical_payload_sorted():
    import json

    request = make_request(origin_type="copied", parent_roots=("root-b", "root-a"))
    payload = json.loads(request.canonical_bytes())
    assert payload["origin_type"] == "copied"
    assert payload["parent_roots"] == ["root-a", "root-b"]
