"""Frozen DRI-2 v2 confirmatory runner.

Pins the v2 protocol and configuration and the unchanged v1 implementation, runs
the full evaluation twice on the v2 confirmatory salt, and applies the v2
criterion (v1's without the speed checks).
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

from experiments.dri2.scoring import evaluate, evaluate_criterion, semantic_hash

ROOT = Path(__file__).resolve().parents[2]
PINNED = {
    "experiments/dri2v2/PREREGISTRATION.md": "a887ede0423b550f7112966dcaeec65cd0712a4f242aab07a7772cdc506be115",
    "experiments/dri2v2/EXECUTION-CONFIG.json": "e5895176e71dacc2ed904fdd748d9295acba42049533b9b98efc0d54b7896c4c",
    "experiments/dri2/PREREGISTRATION.md": "8d05327d3505d943aa7947aacefcd656be0d59be5f6b1d881d8ec2fc0cc2a94e",
    "experiments/dri2/world.py": "30327cc6a46542f1dba52cbaf4faf5fd2386510cd5b9bcd7d5b5078c4db24161",
    "experiments/dri2/arms.py": "39bee408c92072ef0b55bfe06d18070dbae843621101b0063ebb4a0d1d47e7a8",
    "experiments/dri2/stats.py": "6f65060ff5cd366e6ca2a65fe85395210212e32f2abc3dfb0f72e7e3f06c9257",
    "experiments/dri2/scoring.py": "e9e9275d2e8b9f22d844b4e9e62e2e9b67f46e7a83a67e77d9390570b67a1be1",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins(root: Path = ROOT) -> None:
    changed = sorted(name for name, digest in PINNED.items() if _sha256(root / name) != digest)
    if changed:
        raise ValueError("frozen DRI-2 v2 inputs changed: " + ", ".join(changed))


def load_config(root: Path = ROOT) -> dict[str, Any]:
    verify_pins(root)
    config = json.loads((root / "experiments/dri2v2/EXECUTION-CONFIG.json").read_text())
    if config["status"] != "preregistered-unexecuted" or config["success_criterion"]["faster_than"]:
        raise ValueError("DRI-2 v2 configuration is not in its preregistered state")
    return config


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def run_confirmatory(config: dict[str, Any]) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    first = evaluate(config, config["confirmatory_salt"])
    second = evaluate(config, config["confirmatory_salt"])
    hashes = [semantic_hash(first), semantic_hash(second)]
    return {
        "schema": "minority-prophet.dri2-v2-confirmatory-result.v1",
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
