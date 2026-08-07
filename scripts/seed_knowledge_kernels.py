#!/usr/bin/env python3
"""Materialize deterministic, explicitly incomplete kernel seeds."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "research" / "knowledge-ledger"
registry = json.loads((PROGRAM / "kernels.json").read_text())

for kernel in registry["kernels"]:
    directory = PROGRAM / "kernels" / kernel["id"]
    directory.mkdir(parents=True, exist_ok=True)
    protocol = f"""# {kernel['id']}: {kernel['realm']}

Status: **seeded, not preregistered or executed.**

## Question

{kernel['question']}

## Null hypothesis

{kernel['null']}

## Target hypothesis

{kernel['target']}

## Primary endpoint

{kernel['primaryEndpoint']}

## First gate

{kernel['firstGate']}

## Completion route

Complete every field in `preregistration.json` under the shared
[`EXPERIMENT-CONTRACT.md`](../../EXPERIMENT-CONTRACT.md), commit the protocol
before confirmatory inspection, and advance only through recorded gates. This
file is a seed and supports no result claim.
"""
    (directory / "PROTOCOL.md").write_text(protocol)
    preregistration = {
        "schema": "minority-prophet.preregistration.v0.1",
        "kernelId": kernel["id"],
        "status": "incomplete-seed",
        "question": kernel["question"],
        "null": kernel["null"],
        "target": kernel["target"],
        "population": None,
        "searchSpace": None,
        "rootDefinition": None,
        "baselines": [],
        "primaryEndpoint": kernel["primaryEndpoint"],
        "secondaryEndpoints": [],
        "effectSize": None,
        "uncertainty": None,
        "successCondition": None,
        "failureCondition": None,
        "invalidationCondition": None,
        "stopCondition": kernel["firstGate"],
        "frozenSeedsOrSplits": None,
        "protocolCommit": None,
        "safetyBoundary": None,
        "artifacts": []
    }
    (directory / "preregistration.json").write_text(json.dumps(preregistration, indent=2) + "\n")
    status = {
        "schema": "minority-prophet.kernel-status.v0.1",
        "kernelId": kernel["id"],
        "state": "seeded",
        "resultStatus": "none",
        "lastCompletedGate": "registry-entry",
        "nextGate": "complete and commit preregistration",
        "claimAllowed": "This kernel is seeded and supports no result claim."
    }
    (directory / "STATUS.json").write_text(json.dumps(status, indent=2) + "\n")

print(json.dumps({"materialized": len(registry["kernels"])}))
