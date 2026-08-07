#!/usr/bin/env python3
"""Audit the experiment registry and preregistrations against RESEARCH-METHOD.md.

This reports disagreements. It never repairs them: a silent repair would erase
the evidence that the disagreement existed, and the program's own rules require
recording and reconciling such conflicts in a dedicated pull request.

Usage:
    python3 scripts/audit_preregistrations.py            # human-readable
    python3 scripts/audit_preregistrations.py --json     # machine-readable
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KL = ROOT / "research" / "knowledge-ledger"
EXPERIMENTS = KL / "experiments"
REGISTRY = KL / "EXPERIMENT-REGISTRY.json"

# The twelve numbered fields RESEARCH-METHOD.md requires of every
# preregistration, mapped to the preregistration.v0.1 key(s) that carry them.
# A requirement with no key is a schema gap, not an oversight in the data.
METHOD_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "1. identifier and immutable protocol version": ("experimentId", "protocolVersion"),
    "2. exact research question": ("question",),
    "3. null and target hypotheses": ("null", "target"),
    "4. population or generated-world distribution": ("population",),
    "5. search-space definition and enumeration method": ("searchSpace",),
    "6. evidence-root and shared-dependency definition": ("rootDefinition",),
    "7. baselines and ablations": ("baselines",),
    "8. primary and secondary endpoints": ("primaryEndpoint", "secondaryEndpoints"),
    "9. effect size, uncertainty interval, multiple-testing correction": (
        "effectSize",
        "uncertainty",
        "multipleTestingCorrection",
    ),
    "10. success, failure, invalidation, and stop conditions": (
        "successCondition",
        "failureCondition",
        "invalidationCondition",
        "stopCondition",
    ),
    "11. frozen seeds, splits, code commit, environment, artifact paths": (
        "frozenSeedsOrSplits",
        "protocolCommit",
        "environment",
        "artifacts",
    ),
    "12. safety boundary and required human authorization": (
        "safetyBoundary",
        "humanAuthorization",
    ),
}

# The per-experiment directory contents required by the run prompt.
REQUIRED_ENTRIES = (
    "PROTOCOL.md",
    "preregistration.json",
    "fixtures",
    "src",
    "tests",
    "results",
    "REPRODUCE.md",
    "STATUS.json",
)


def is_unpopulated(value: object) -> bool:
    """Empty collections are unpopulated in substance even when not null."""
    return value is None or value in ([], {}, "")


def audit() -> dict:
    registry = json.loads(REGISTRY.read_text())
    registry_ids = [e["id"] for e in registry["experiments"]]
    disk_ids = sorted(p.name for p in EXPERIMENTS.iterdir() if p.is_dir())

    experiments = {}
    for exp_id in disk_ids:
        directory = EXPERIMENTS / exp_id
        prereg_path = directory / "preregistration.json"
        prereg = json.loads(prereg_path.read_text()) if prereg_path.exists() else {}

        nulls = sorted(k for k, v in prereg.items() if v is None)
        empties = sorted(k for k, v in prereg.items() if v is not None and is_unpopulated(v))

        missing_keys: dict[str, list[str]] = {}
        unpopulated_reqs: dict[str, list[str]] = {}
        for requirement, keys in METHOD_REQUIREMENTS.items():
            absent = [k for k in keys if k not in prereg]
            present_but_empty = [
                k for k in keys if k in prereg and is_unpopulated(prereg[k])
            ]
            if absent:
                missing_keys[requirement] = absent
            if present_but_empty:
                unpopulated_reqs[requirement] = present_but_empty

        present_entries = {p.name for p in directory.iterdir()}
        experiments[exp_id] = {
            "keyCount": len(prereg),
            "status": prereg.get("status"),
            "nullFields": nulls,
            "emptyCollectionFields": empties,
            "unpopulatedCount": len(nulls) + len(empties),
            "methodRequirementsWithNoSchemaKey": missing_keys,
            "methodRequirementsUnpopulated": unpopulated_reqs,
            "missingDirectoryEntries": [
                e for e in REQUIRED_ENTRIES if e not in present_entries
            ],
        }

    return {
        "registryOnlyIds": sorted(set(registry_ids) - set(disk_ids)),
        "diskOnlyIds": sorted(set(disk_ids) - set(registry_ids)),
        "registryStatus": registry.get("status"),
        "experiments": experiments,
    }


def main() -> None:
    report = audit()
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    print(f"registry status: {report['registryStatus']}")
    print(f"ids in registry but not on disk: {report['registryOnlyIds'] or 'none'}")
    print(f"ids on disk but not in registry: {report['diskOnlyIds'] or 'none'}")
    print()
    for exp_id, data in sorted(report["experiments"].items()):
        print(
            f"{exp_id}: status={data['status']} "
            f"unpopulated={data['unpopulatedCount']} of {data['keyCount']} keys "
            f"({len(data['nullFields'])} null + "
            f"{len(data['emptyCollectionFields'])} empty)"
        )
        if data["missingDirectoryEntries"]:
            print(f"    missing dir entries: {', '.join(data['missingDirectoryEntries'])}")
        for requirement, keys in sorted(data["methodRequirementsWithNoSchemaKey"].items()):
            print(f"    NO SCHEMA KEY for {requirement}: {', '.join(keys)}")


if __name__ == "__main__":
    main()
