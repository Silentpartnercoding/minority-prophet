"""The forensic record: what a real system hands an investigator after a loss.

Deliberately separate from `benchmark.world`. A synthetic world carries its own
ground truth because the benchmark scores against it. A forensic record must
NOT, because the whole question is what can be recovered without it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class ExecutionEvent:
    """Who did what, and when. The layer ordinary observability already has."""

    seq: int
    actor: str
    action: str
    target: str | None = None
    detail: str = ""


@dataclass(frozen=True)
class AuthorityGrant:
    """Who permitted whom to do what, and within which bound."""

    grantor: str
    grantee: str
    scope: str
    limit: str | None = None
    attested: bool = False


ORIGIN_TYPES = ("observation", "derived", "copied", "unknown")
"""Vocabulary shared byte-for-byte with `invention_engine.models.OriginType`.

Recorded as a typed field, never as prose beside the claim. The recurring failure
in this programme is a status asserted in one place and contradicted by the
artifact it describes; a note saying "derived from claim-A" cannot be checked
against the root structure, and a typed origin plus an explicit edge can.
"""


@dataclass(frozen=True)
class EvidenceClaim:
    """A recorded belief and whatever the system retained about where it came from.

    Shaped to satisfy `aggregation.root_vote.RootedClaim`. `root_id` of None is
    the honest representation of an unrecorded origin, and is what forces
    escalation rather than a guess.
    """

    claim_id: str
    asserted_by: str
    value: bool
    root_id: str | None
    origin_type: str = "unknown"
    derived_from: str | None = None
    independence_basis: str | None = None
    witness_depth: str | None = None
    attestation: str | None = None
    witness_identity: str | None = None
    depth_basis: str | None = None
    suppressed_at: str | None = None
    note: str = ""


@dataclass(frozen=True)
class WorldObservation:
    """Whether anyone checked that the world actually reached the claimed state."""

    subject: str
    claimed_state: str
    verified: bool
    verified_by: str | None = None


@dataclass(frozen=True)
class ForensicRecord:
    incident_id: str
    summary: str
    execution: tuple[ExecutionEvent, ...] = ()
    authority: tuple[AuthorityGrant, ...] = ()
    evidence: tuple[EvidenceClaim, ...] = ()
    observations: tuple[WorldObservation, ...] = ()
    decision_claim: str = ""
    consequential_action: str = ""
    outcome: str = ""

    def redacted(self, *, drop_roots_for: frozenset[str]) -> "ForensicRecord":
        """Return the same incident with lineage removed for named claims.

        This is the degraded case. Nothing else changes: the actions still
        happened, the loss still happened, only the provenance is gone.
        """
        stripped = tuple(
            EvidenceClaim(
                claim_id=c.claim_id,
                asserted_by=c.asserted_by,
                value=c.value,
                root_id=None if c.claim_id in drop_roots_for else c.root_id,
                origin_type="unknown" if c.claim_id in drop_roots_for else c.origin_type,
                derived_from=None if c.claim_id in drop_roots_for else c.derived_from,
                independence_basis=None if c.claim_id in drop_roots_for else c.independence_basis,
                witness_depth=c.witness_depth,
                attestation=None if c.claim_id in drop_roots_for else c.attestation,
                witness_identity=c.witness_identity,
                depth_basis=c.depth_basis,
                suppressed_at=c.suppressed_at,
                note="lineage not recorded by the production system"
                if c.claim_id in drop_roots_for
                else c.note,
            )
            for c in self.evidence
        )
        return ForensicRecord(
            incident_id=self.incident_id + "-degraded",
            summary=self.summary,
            execution=self.execution,
            authority=self.authority,
            evidence=stripped,
            observations=self.observations,
            decision_claim=self.decision_claim,
            consequential_action=self.consequential_action,
            outcome=self.outcome,
        )


@dataclass(frozen=True)
class GroundTruth:
    """Held by the scenario author. Never passed to the reconstructor."""

    independent_roots: int
    apparent_agreement: int
    suppressed_claim: str | None
    responsible_node: str
    narrative: str
