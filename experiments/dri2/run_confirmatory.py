"""Frozen DRI-2 confirmatory runner.

Refuses to run if the protocol, configuration or implementation differs from the
bytes frozen at protocol v1. Runs the full evaluation twice on the confirmatory
salt and applies the preregistered criterion.
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

HERE = Path(__file__).parent
PINNED = {
    "PREREGISTRATION.md": "8d05327d3505d943aa7947aacefcd656be0d59be5f6b1d881d8ec2fc0cc2a94e",
    "EXECUTION-CONFIG.json": "c13304c3801a30a1e4982a69d075b3c5ded4edfe3258b9dd04b27f91501bb125",
    "world.py": "30327cc6a46542f1dba52cbaf4faf5fd2386510cd5b9bcd7d5b5078c4db24161",
    "arms.py": "39bee408c92072ef0b55bfe06d18070dbae843621101b0063ebb4a0d1d47e7a8",
    "stats.py": "6f65060ff5cd366e6ca2a65fe85395210212e32f2abc3dfb0f72e7e3f06c9257",
    "scoring.py": "e9e9275d2e8b9f22d844b4e9e62e2e9b67f46e7a83a67e77d9390570b67a1be1",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins(directory: Path = HERE) -> None:
    changed = sorted(name for name, digest in PINNED.items() if _sha256(directory / name) != digest)
    if changed:
        raise ValueError("frozen DRI-2 inputs changed: " + ", ".join(changed))


def load_config(directory: Path = HERE) -> dict[str, Any]:
    verify_pins(directory)
    config = json.loads((directory / "EXECUTION-CONFIG.json").read_text())
    if config["status"] != "preregistered-unexecuted":
        raise ValueError("DRI-2 configuration is not in its preregistered state")
    return config


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def environment() -> dict[str, Any]:
    return {
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "commit": _git("rev-parse", "HEAD"),
        "dirtyWorktree": bool(_git("status", "--porcelain")),
    }


def run_confirmatory(config: dict[str, Any]) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    first = evaluate(config, config["confirmatory_salt"])
    second = evaluate(config, config["confirmatory_salt"])
    hashes = [semantic_hash(first), semantic_hash(second)]
    return {
        "schema": "minority-prophet.dri2-confirmatory-result.v1",
        "status": "confirmatory-complete",
        "pins": PINNED,
        "environment": environment(),
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
        "semanticSha256": result["semanticResultSha256Runs"][0],
        "reproducible": result["semanticResultSha256Runs"][0] == result["semanticResultSha256Runs"][1],
        "outputSha256": _sha256(args.output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
