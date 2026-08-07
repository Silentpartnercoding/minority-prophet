#!/usr/bin/env python3
"""Materialize deterministic, explicitly incomplete experiment seeds."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "research" / "knowledge-ledger"
registry = json.loads((PROGRAM / "EXPERIMENT-REGISTRY.json").read_text())

for experiment in registry["experiments"]:
    directory = PROGRAM / "experiments" / experiment["id"]
    directory.mkdir(parents=True, exist_ok=True)
    protocol = f"""# {experiment['id']}: {experiment['realm']}

Status: **seeded, not preregistered or executed.**

## Question

{experiment['question']}

## Null hypothesis

{experiment['null']}

## Target hypothesis

{experiment['target']}

## Primary endpoint

{experiment['primaryEndpoint']}

## First gate

{experiment['firstGate']}

## Completion route

Complete every field in `preregistration.json` under the shared
[`RESEARCH-METHOD.md`](../../RESEARCH-METHOD.md), commit the protocol
before confirmatory inspection, and advance only through recorded gates. This
file is a seed and supports no result claim.
"""
    (directory / "PROTOCOL.md").write_text(protocol)
    preregistration = {
        "schema": "minority-prophet.preregistration.v0.1",
        "experimentId": experiment["id"],
        "status": "incomplete-seed",
        "question": experiment["question"],
        "null": experiment["null"],
        "target": experiment["target"],
        "population": None,
        "searchSpace": None,
        "rootDefinition": None,
        "baselines": [],
        "primaryEndpoint": experiment["primaryEndpoint"],
        "secondaryEndpoints": [],
        "effectSize": None,
        "uncertainty": None,
        "successCondition": None,
        "failureCondition": None,
        "invalidationCondition": None,
        "stopCondition": experiment["firstGate"],
        "frozenSeedsOrSplits": None,
        "protocolCommit": None,
        "safetyBoundary": None,
        "artifacts": []
    }
    (directory / "preregistration.json").write_text(json.dumps(preregistration, indent=2) + "\n")
    status = {
        "schema": "minority-prophet.experiment-status.v0.1",
        "experimentId": experiment["id"],
        "state": "seeded",
        "resultStatus": "none",
        "lastCompletedGate": "registry-entry",
        "nextGate": "complete and commit preregistration",
        "claimAllowed": "This experiment is seeded and supports no result claim."
    }
    (directory / "STATUS.json").write_text(json.dumps(status, indent=2) + "\n")

print(json.dumps({"materializedExperiments": len(registry["experiments"])}))
