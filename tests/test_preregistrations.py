"""Preregistration v0.2 conformance: enforcement, not prose (SCH-001 repair).

The schema definition of record is
research/knowledge-ledger/schemas/preregistration-v0.2.json. A v0.2 kernel
preregistration that omits a required field, carries a bare null outside the
registered protocolCommit design, ships an empty required collection, or
records an unanswered field without a non-empty reason FAILS the suite --
the M26/I12 discipline applied to the schema layer.

Scope (per the schema definition): each kernel's base preregistration.json,
twelve files. KL-000's version-specific registrations
(preregistration-v1.*.json) are frozen research records predating this
definition and are governed by their own registration chains.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (REPO / "research" / "knowledge-ledger" / "schemas" / "preregistration-v0.2.json").read_text()
)
REQUIRED_FIELDS = [f["field"] for f in SCHEMA["requiredFields"]]
EXPERIMENTS = REPO / "research" / "knowledge-ledger" / "experiments"

KERNELS = sorted(p.name for p in EXPERIMENTS.iterdir() if (p / "preregistration.json").exists())


def violations(doc: dict) -> list[str]:
    """All conformance violations of a v0.2 document; empty list == conforming."""
    problems = []
    if doc.get("schema") != "minority-prophet.preregistration.v0.2":
        problems.append(f"schema is {doc.get('schema')!r}, not v0.2")
        return problems
    for field in REQUIRED_FIELDS:
        if field not in doc:
            problems.append(f"missing required field: {field}")
    if "protocolCommit" in doc and doc["protocolCommit"] is None:
        note = doc.get("protocolCommitNote")
        if not (isinstance(note, str) and note.strip()):
            problems.append("protocolCommit is null without a non-empty protocolCommitNote")

    def walk(value, path):
        if value is None:
            if path != "protocolCommit":
                problems.append(f"bare null at {path}")
            return
        if isinstance(value, dict):
            if value.get("status") == "unanswered":
                reason = value.get("reason")
                if not (isinstance(reason, str) and reason.strip()):
                    problems.append(f"unanswered without a non-empty reason at {path}")
                return
            for k, v in value.items():
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, f"{path}[{i}]")

    for field in REQUIRED_FIELDS:
        if field in doc:
            walk(doc[field], field)
            if doc[field] in ([], {}):
                problems.append(f"empty required collection at {field} (use the unanswered convention)")
    return problems


@pytest.mark.parametrize("kernel", KERNELS)
def test_kernel_preregistration_conforms_to_v02(kernel):
    doc = json.loads((EXPERIMENTS / kernel / "preregistration.json").read_text())
    problems = violations(doc)
    assert not problems, f"{kernel}/preregistration.json: {problems}"


def test_all_twelve_kernels_are_covered():
    assert len(KERNELS) == 12, f"expected 12 kernel preregistrations, found {len(KERNELS)}: {KERNELS}"


def test_schema_definition_covers_every_method_item():
    """The definition's own claim, checked: all twelve RESEARCH-METHOD items map
    to at least one required field that actually exists in the field list."""
    coverage = SCHEMA["methodCoverage"]["items"]
    assert sorted(coverage.keys(), key=int) == [str(i) for i in range(1, 13)]
    for item, fields in coverage.items():
        assert fields, f"method item {item} maps to no fields"
        for field in fields:
            assert field in REQUIRED_FIELDS, f"method item {item} cites unknown field {field}"


# --- the validator itself is tested against planted defects (BL-036 spirit) --

def _conforming_stub():
    doc = {f: f"x-{f}" for f in REQUIRED_FIELDS}
    doc["schema"] = "minority-prophet.preregistration.v0.2"
    doc["protocolCommit"] = None
    doc["protocolCommitNote"] = "null by design; sidecar binds at registration"
    return doc


def test_validator_accepts_a_conforming_stub():
    assert violations(_conforming_stub()) == []


@pytest.mark.parametrize("defect,mutate", [
    ("missing field", lambda d: d.pop("safetyBoundary")),
    ("bare null", lambda d: d.__setitem__("population", None)),
    ("null protocolCommit without note", lambda d: d.__setitem__("protocolCommitNote", "  ")),
    ("unanswered without reason", lambda d: d.__setitem__("uncertainty", {"status": "unanswered", "reason": ""})),
    ("empty required collection", lambda d: d.__setitem__("controls", [])),
    ("nested bare null", lambda d: d.__setitem__("baselines", [{"id": "B1", "expectedOutcome": None}])),
])
def test_validator_rejects_planted_defects(defect, mutate):
    doc = _conforming_stub()
    mutate(doc)
    assert violations(doc), f"validator failed to reject: {defect}"
