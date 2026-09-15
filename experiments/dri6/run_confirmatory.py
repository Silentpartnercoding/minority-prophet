"""Frozen DRI-6 confirmatory runner.

Pins the protocol, configuration, implementation, reused DRI-5, DRI-6 and DRI-3 files and engine, runs the full
evaluation twice on the confirmatory salt, and applies the preregistered criterion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.dri6.scoring import evaluate, evaluate_criterion, semantic_hash

ROOT = Path(__file__).resolve().parents[2]
PINNED = {
    "experiments/dri6/PREREGISTRATION.md": "bc9512571400a0de45901e6bd19cecb9fd93065783055112228a6d11acff0c25",
    "experiments/dri6/EXECUTION-CONFIG.json": "78c212dc3d187f9e066999f8f7e564d643fa221f0f6a37dd3e602cbde8958bbd",
    "experiments/dri6/world.py": "401f660d46f72964a426743b172d124b845953983718d65a7fa75e06bd8a5261",
    "experiments/dri6/arms.py": "891cf000a9b19b36b3cd02aeb040d7d09c63099823373a4a9c75126c4ccbbc5d",
    "experiments/dri6/scoring.py": "577f633944680e511ff67348f122c247dfb1379330afaff178b4240f7dbb6f74",
    "experiments/dri5/world.py": "90792bb6de2e86ad18440327ac1ab90c5a73b3f19e6b9874ce05b37bbae966c1",
    "experiments/dri4/world.py": "6a316cc375302f36d7f06449d7a11f2a65bdd2456b56521fc561b25de8f692bf",
    "experiments/dri3/world.py": "f6401442a47ba6179680203914a0c850ace2306ad1eb8101ea0e22996509d592",
    "experiments/dri3/arms.py": "104fedd3695719ca8fc7d92c0db789c5090d00973813d4eb0cc80004a7983c13",
    "experiments/dri3/scoring.py": "4c4d02f0bd59eee951c59b06d4527821f0484c00a357387a459200940afb5093",
    "experiments/dri2/stats.py": "6f65060ff5cd366e6ca2a65fe85395210212e32f2abc3dfb0f72e7e3f06c9257",
    "provenance/dependence_robustness.py": "c5273b6d4dbe7faa22351ba456c6781ac19a4b911b002167362d41ecd1d921bf",
    "provenance/decision_relative.py": "f9fe5d9b95982e42c754fa3a187628f09be5408f69f7fa6873029bdad3046b13",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins(root: Path = ROOT) -> None:
    changed = sorted(name for name, digest in PINNED.items() if _sha256(root / name) != digest)
    if changed:
        raise ValueError("frozen DRI-6 inputs changed: " + ", ".join(changed))


def load_config(root: Path = ROOT) -> dict[str, Any]:
    verify_pins(root)
    config = json.loads((root / "experiments/dri6/EXECUTION-CONFIG.json").read_text())
    if config["status"] != "preregistered-unexecuted":
        raise ValueError("DRI-6 configuration is not in its preregistered state")
    return config


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def run_confirmatory(config: dict[str, Any]) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    first = evaluate(config, config["confirmatory_salt"])
    second = evaluate(config, config["confirmatory_salt"])
    hashes = [semantic_hash(first), semantic_hash(second)]
    return {
        "schema": "minority-prophet.dri6-confirmatory-result.v1",
        "status": "confirmatory-complete",
        "pins": PINNED,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "commit": _git("rev-parse", "HEAD"),
            "dirtyWorktree": bool(_git("status", "--porcelain")),
        },
        "startedAt": started,
        "finishedAt": datetime.now(timezone.utc).isoformat(),
        "semanticResultSha256Runs": hashes,
        "criterion": evaluate_criterion(first, config, hashes[0] == hashes[1]),
        "semanticResult": first,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = run_confirmatory(load_config())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "criterionSupported": result["criterion"]["supported"],
        "reproducible": result["semanticResultSha256Runs"][0] == result["semanticResultSha256Runs"][1],
        "semanticSha256": result["semanticResultSha256Runs"][0],
        "outputSha256": _sha256(args.output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
