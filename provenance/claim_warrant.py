"""Produce the warrant fields the schema says are derivable.

`claim-warrant.schema.json` requires `verify_determinism` on every warrant and
says of it, in the schema's own words: "DERIVED, never author-supplied", and
"consumers recompute rather than trust it". Both halves of that instruction were
unimplemented. Nothing in the corpus derived the field, and nothing recomputed
it — three test files supplied it by hand, which is why the omission survived a
green suite for as long as it did.

`provenance/warrant_recheck.py` was right to refuse the job. It writes
`verify_outcome` into an existing warrant and explicitly declines to invent one,
because "only the producer knows the claim_type". This module is the producer
side it was deferring to.

`external_attestation` is the other half. The schema calls it an "opaque
passthrough ... Stored for audit, never interpreted by the ledger. Kept
unconstrained so no external schema becomes a dependency of this one." So the
correct implementation is one that carries it and never looks inside it. That is
a real constraint, not an absence of one: the moment anything here branches on
its contents, an external vocabulary has become a dependency of this schema.

PLACEMENT. A warrant is stored under the single reserved key `claim_warrant`
inside a node's `evidence` object, never flattened into it. `provenance/graph.py`
skips that key in `resolvable_reference`, because a warrant's `source_digest` is
a hex string matching the accepted `hash` form and a flattened warrant could
therefore satisfy `UnattributedRootError` — admitting a root that was previously
refused. Metadata must never satisfy the gate. `attach_to` is the only supported
way to place one.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

WARRANT_VERSION = 1

#: The four-way typology, from the schema. Ordering is not significance.
CLAIM_TYPES = ("measured", "inferred", "analogized", "cited")

#: The derivation, stated once. `measured` and `cited` are re-checkable
#: mechanically without a judge; `inferred` and `analogized` need a theorem
#: prover, structural matcher, fixed-metric oracle or LLM.
_DETERMINISTIC = frozenset({"measured", "cited"})
_ORACLE_CONDITIONAL = frozenset({"inferred", "analogized"})

DETERMINISM_VALUES = ("deterministic", "oracle_conditional")

#: The accepted `hash` form, duplicated from `provenance/graph.py`'s
#: `_RESOLVABLE_FORMS`. A conformance test asserts the copies agree; neither may
#: drift, because the whole point of the placement rule above is that these two
#: modules mean the same thing by "looks like a digest".
_HASH_FORM = re.compile(r"^[0-9a-f]{32,128}$", re.IGNORECASE)

#: Every key the schema permits. It sets `additionalProperties: false`, so an
#: unknown key is a malformed warrant rather than a tolerated extension.
_PERMITTED = frozenset({
    "warrant_version", "claim_type", "verify_determinism", "verify_outcome",
    "source_digest", "recheck_reference", "external_attestation",
})

WARRANT_KEY = "claim_warrant"


class ClaimWarrantError(ValueError):
    """A warrant cannot be produced or read as written."""


def derive_verify_determinism(claim_type: str) -> str:
    """The determinism entailed by a claim type.

    Total over `CLAIM_TYPES` and raises otherwise, rather than defaulting. A
    default here would silently label an unrecognised claim type as mechanically
    re-checkable, which is the direction that overstates what can be verified.
    """
    if claim_type in _DETERMINISTIC:
        return "deterministic"
    if claim_type in _ORACLE_CONDITIONAL:
        return "oracle_conditional"
    raise ClaimWarrantError(
        f"unrecognised claim_type {claim_type!r}; "
        f"expected one of {', '.join(CLAIM_TYPES)}"
    )


def build_warrant(
    claim_type: str,
    *,
    source_digest: str | None = None,
    recheck_reference: str | None = None,
    external_attestation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """A warrant for a claim of this type.

    `verify_determinism` is deliberately NOT a parameter. The schema says it is
    derived and never author-supplied, so offering a way to state it would be
    offering a way to state it wrongly.

    `source_digest` is optional and frequently absent. Its presence is what makes
    an offline re-check possible, so absence is recorded by omission rather than
    by a placeholder — an empty string here would later read as a digest that
    failed to match rather than as a digest that was never taken.
    """
    warrant: dict[str, Any] = {
        "warrant_version": WARRANT_VERSION,
        "claim_type": claim_type,
        "verify_determinism": derive_verify_determinism(claim_type),
    }
    if source_digest is not None:
        if not _HASH_FORM.match(source_digest.strip()):
            raise ClaimWarrantError(
                "source_digest must be 32-128 hex characters, the accepted hash form"
            )
        warrant["source_digest"] = source_digest.strip().lower()
    if recheck_reference is not None:
        reference = recheck_reference.strip()
        if not reference:
            raise ClaimWarrantError(
                "recheck_reference must name somewhere a re-check would go, or be omitted"
            )
        warrant["recheck_reference"] = reference
    if external_attestation is not None:
        if not isinstance(external_attestation, Mapping):
            raise ClaimWarrantError("external_attestation must be an object")
        # Copied, not referenced, so a later mutation by the caller cannot
        # retroactively change what the warrant recorded. Shallow: the schema
        # keeps this unconstrained, and walking it to copy deeply would mean
        # inspecting a structure this module has promised not to interpret.
        warrant["external_attestation"] = dict(external_attestation)
    return warrant


def attach_to(evidence: Mapping[str, Any], warrant: Mapping[str, Any]) -> dict[str, Any]:
    """A copy of `evidence` carrying `warrant` under the reserved key.

    The only supported placement. Never mutates the input, and never flattens —
    see the placement rule in this module's docstring for why flattening is a
    gate bypass rather than a style preference.
    """
    errors = warrant_errors(warrant)
    if errors:
        raise ClaimWarrantError("; ".join(errors))
    return {**dict(evidence), WARRANT_KEY: dict(warrant)}


def warrant_errors(warrant: object) -> list[str]:
    """Everything wrong with this warrant, as a list. Empty means well-formed.

    Recomputes `verify_determinism` rather than trusting it, which is what the
    schema asks of consumers. A producer that sets it inconsistently with
    `claim_type` is malformed, and saying so is the entire value of the field —
    a consumer that trusted the stated value would accept a claim labelled
    mechanically re-checkable when checking it actually requires an oracle.
    """
    if not isinstance(warrant, Mapping):
        return ["warrant must be an object"]

    errors: list[str] = []
    unknown = sorted(set(warrant) - _PERMITTED)
    if unknown:
        errors.append("unpermitted warrant keys: " + ", ".join(unknown))

    if warrant.get("warrant_version") != WARRANT_VERSION:
        errors.append(f"warrant_version must be {WARRANT_VERSION}")

    claim_type = warrant.get("claim_type")
    if claim_type not in CLAIM_TYPES:
        errors.append("unrecognised claim_type")
    else:
        expected = derive_verify_determinism(claim_type)
        stated = warrant.get("verify_determinism")
        if stated is None:
            errors.append("verify_determinism is required")
        elif stated != expected:
            errors.append(
                f"verify_determinism {stated!r} contradicts claim_type "
                f"{claim_type!r}, which derives {expected!r}"
            )

    # STRICT IN WHAT WE EMIT, EXACTLY CONFORMANT IN WHAT WE ACCEPT.
    #
    # `build_warrant` requires `source_digest` to match the accepted `hash` form
    # and refuses an empty `recheck_reference`, because those are the shapes the
    # estate has agreed to produce. This function must NOT enforce either.
    #
    # The schema types both as plain `string` — the hash form appears only in
    # prose, and `recheck_reference` is documented "free-form: this schema does
    # not constrain external vocabularies". A validator that rejected a
    # schema-valid document would refuse conforming evidence from a producer
    # that read the contract correctly, which is a worse failure than not
    # checking: it makes this implementation, rather than the published schema,
    # the real contract.
    digest = warrant.get("source_digest")
    if digest is not None and not isinstance(digest, str):
        errors.append("source_digest must be a string")

    reference = warrant.get("recheck_reference")
    if reference is not None and not isinstance(reference, str):
        errors.append("recheck_reference must be a string")

    attestation = warrant.get("external_attestation")
    if attestation is not None and not isinstance(attestation, Mapping):
        errors.append("external_attestation must be an object")

    errors.extend(_verify_outcome_errors(warrant.get("verify_outcome")))
    return errors


#: `verify_outcome`'s own keys, from the schema. It sets
#: `additionalProperties: false` and requires `result`.
_OUTCOME_PERMITTED = frozenset({"result", "reason", "checked_at", "checked_by"})

_OUTCOME_RESULTS = ("verified", "rejected", "unverifiable")


def _verify_outcome_errors(outcome: object) -> list[str]:
    """Checks for the nested re-check result.

    `unverifiable` is never collapsed into `rejected`. The schema is emphatic
    about why: "a claim whose source has become unreachable is not a claim that
    failed, and the difference is exactly the signal false-prophet screening
    depends on. A prophet can make claims unverifiable at no cost."
    """
    if outcome is None:
        return []
    if not isinstance(outcome, Mapping):
        return ["verify_outcome must be an object"]

    errors: list[str] = []
    unknown = sorted(set(outcome) - _OUTCOME_PERMITTED)
    if unknown:
        errors.append("unpermitted verify_outcome keys: " + ", ".join(unknown))
    if "result" not in outcome:
        errors.append("verify_outcome.result is required")
    elif outcome["result"] not in _OUTCOME_RESULTS:
        errors.append("verify_outcome.result must be verified, rejected or unverifiable")
    return errors
