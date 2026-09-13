"""One controlled incident with known ground truth.

The shape is the canonical case from the research direction: an apparent 3-to-1
consensus that is really 1-to-1, a suppressed independent contradiction, an
action authorised on the strength of the apparent count, and a world state
nobody verified.
"""

from __future__ import annotations

from record import (
    AuthorityGrant,
    EvidenceClaim,
    ExecutionEvent,
    ForensicRecord,
    GroundTruth,
    WorldObservation,
)

VESSEL = "press-vessel-7"


def pressure_vessel_incident() -> tuple[ForensicRecord, GroundTruth]:
    """Three safety reports, one sensor, one suppressed dissent, one failure."""

    execution = (
        ExecutionEvent(1, "sensor-A", "emit", VESSEL, "pressure nominal"),
        ExecutionEvent(2, "monitor-1", "derive", "sensor-A", "restates sensor-A"),
        ExecutionEvent(3, "monitor-2", "derive", "monitor-1", "restates monitor-1"),
        ExecutionEvent(4, "sensor-B", "emit", VESSEL, "pressure exceeds limit"),
        ExecutionEvent(5, "aggregator", "aggregate", None, "4 inputs, majority rule"),
        ExecutionEvent(6, "aggregator", "drop", "claim-D", "minority, below quorum"),
        ExecutionEvent(7, "agent-ops", "decide", None, "safe to continue"),
        ExecutionEvent(8, "agent-ops", "invoke", "scheduler", "extend run window"),
        ExecutionEvent(9, "scheduler", "return", "agent-ops", "ok"),
        ExecutionEvent(10, VESSEL, "fail", None, "seal rupture"),
    )

    authority = (
        AuthorityGrant("owner", "agent-ops", "continue or halt production runs",
                       "halt required above advisory pressure", attested=True),
        AuthorityGrant("agent-ops", "scheduler", "extend run window",
                       "max one window", attested=False),
    )

    # Three claims that look independent. Two are copies of the first.
    evidence = (
        EvidenceClaim("claim-A", "sensor-A", True, "root-sensor-A",
                      origin_type="observation",
                      independence_basis="attested",
                      attestation="attested"),
        EvidenceClaim("claim-B", "monitor-1", True, "root-sensor-A",
                      origin_type="copied", derived_from="claim-A",
                      independence_basis="declared",
                      attestation="declared"),
        EvidenceClaim("claim-C", "monitor-2", True, "root-sensor-A",
                      origin_type="copied", derived_from="claim-B",
                      independence_basis="declared",
                      attestation="declared"),
        EvidenceClaim("claim-D", "sensor-B", False, "root-sensor-B",
                      origin_type="observation",
                      independence_basis="attested",
                      attestation="attested",
                      suppressed_at="aggregator"),
    )

    observations = (
        WorldObservation(VESSEL, "pressure within limit", verified=False),
    )

    record = ForensicRecord(
        incident_id="MP-DEMO-001",
        summary=("An operations agent extended a production run after three reports "
                 "indicated the vessel was safe. The vessel failed."),
        execution=execution,
        authority=authority,
        evidence=evidence,
        observations=observations,
        decision_claim="the vessel is safe to continue",
        consequential_action="extend run window",
        outcome="seal rupture",
    )

    truth = GroundTruth(
        independent_roots=2,
        apparent_agreement=3,
        suppressed_claim="claim-D",
        responsible_node="aggregator",
        narrative=("Three supporting reports descend from one sensor, so the decision "
                   "had one independent root supporting it, not three. An independent "
                   "sensor contradicted it and was dropped by the aggregator before the "
                   "agent ever saw it. The agent acted within its granted scope on the "
                   "evidence it was shown, and no one verified the resulting state."),
    )
    return record, truth
