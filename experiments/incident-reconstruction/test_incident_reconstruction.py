"""The demo's claims, as assertions."""

from reconstruct import reconstruct
from scenario import pressure_vessel_incident


def test_full_record_collapses_apparent_agreement_to_one_root():
    record, truth = pressure_vessel_incident()
    rec = reconstruct(record)
    assert rec.independent_roots == 1
    assert rec.apparent_support == truth.apparent_agreement


def test_full_record_reaches_a_supported_attribution():
    record, _ = pressure_vessel_incident()
    assert reconstruct(record).is_determinate


def test_suppressed_contradiction_is_named_and_counterfactualised():
    record, truth = pressure_vessel_incident()
    rec = reconstruct(record)
    statements = " ".join(f.statement for f in rec.findings)
    assert truth.suppressed_claim in statements
    assert "abstain" in statements


def test_ground_truth_never_reaches_the_reconstructor():
    record, _ = pressure_vessel_incident()
    assert "GroundTruth" not in str(type(record))
    assert not hasattr(record, "narrative")


def test_degraded_record_refuses_instead_of_guessing():
    record, _ = pressure_vessel_incident()
    degraded = record.redacted(
        drop_roots_for=frozenset({"claim-A", "claim-B", "claim-C", "claim-D"})
    )
    rec = reconstruct(degraded)
    assert not rec.is_determinate
    assert rec.missing_telemetry
    assert any("INDETERMINATE" in f.statement for f in rec.findings)


def test_typed_origin_is_recorded_not_prose():
    record, _ = pressure_vessel_incident()
    copied = [c for c in record.evidence if c.origin_type == "copied"]
    assert len(copied) == 2
    assert all(c.derived_from for c in copied)


def test_no_false_positive_on_a_consistent_record():
    record, _ = pressure_vessel_incident()
    rec = reconstruct(record)
    assert not any("cannot both be right" in f.statement for f in rec.findings)


def test_origin_structure_contradiction_is_caught():
    from record import EvidenceClaim
    record, _ = pressure_vessel_incident()
    bad = record.evidence + (
        EvidenceClaim("claim-E", "sensor-C", True, "root-sensor-A",
                      origin_type="observation", independence_basis="declared"),
    )
    import dataclasses
    rec = reconstruct(dataclasses.replace(record, evidence=bad))
    assert any("cannot both be right" in f.statement for f in rec.findings)


def test_authorization_needs_both_conditions():
    record, _ = pressure_vessel_incident()
    rec = reconstruct(record)
    auth = [f for f in rec.findings if f.heading == "Authorization preconditions"]
    assert auth and "Both are required" in auth[0].statement
