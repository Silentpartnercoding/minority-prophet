"""Frozen DRI-9 confirmatory runner.

Pins the protocol, configuration, implementation, reused DRI-5, DRI-9 and DRI-3 files and engine, runs the full
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

from experiments.dri9.scoring import evaluate, evaluate_criterion, semantic_hash

ROOT = Path(__file__).resolve().parents[2]
PINNED = {
    "experiments/dri9/PREREGISTRATION.md": "67549892cb17cb806af9152304154343609b5ba8b33e692e092b27bfca0eeba4",
    "experiments/dri9/EXECUTION-CONFIG.json": "96d75f85b0636e7eeda911d8a7283cc7aaa96c7e500f8897c4aff8dbab7ae6ab",
    "experiments/dri9/rule.py": "6ef60455220f355228878bf9f8585f46e72fe3ac789840a1ea752b9478714405",
    "experiments/dri9/world.py": "c1ccc28ec16fbb02b4536ef0fe046d4be0710d556c24212d0193623b8a1f1667",
    "experiments/dri9/arms.py": "76e968ad60a6ff61d0d6a3f2c4e93dbb0daa7b66a24cf07c4cb8d1bf145fed74",
    "experiments/dri9/scoring.py": "2e8215d6a1eea8937522733bd6d5366b7d5fa0f5d96684f6231a6a03124ad798",
    "experiments/dri8/world.py": "38c85209be2a5a56bc07224dfe26c6d1e6455f2154575832a6700f69772e3b30",
    "experiments/dri3/world.py": "f6401442a47ba6179680203914a0c850ace2306ad1eb8101ea0e22996509d592",
    "experiments/dri2/stats.py": "6f65060ff5cd366e6ca2a65fe85395210212e32f2abc3dfb0f72e7e3f06c9257",
    "provenance/dependence_robustness.py": "c5273b6d4dbe7faa22351ba456c6781ac19a4b911b002167362d41ecd1d921bf",
    "provenance/decision_relative.py": "f9fe5d9b95982e42c754fa3a187628f09be5408f69f7fa6873029bdad3046b13",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins(root: Path = ROOT) -> None:
    changed = sorted(name for name, digest in PINNED.items() if _sha256(root / name) != digest)
    if changed:
        raise ValueError("frozen DRI-9 inputs changed: " + ", ".join(changed))


def load_config(root: Path = ROOT) -> dict[str, Any]:
    verify_pins(root)
    config = json.loads((root / "experiments/dri9/EXECUTION-CONFIG.json").read_text())
    if config["status"] != "preregistered-unexecuted":
        raise ValueError("DRI-9 configuration is not in its preregistered state")
    return config


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def run_confirmatory(config: dict[str, Any]) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    first = evaluate(config, config["confirmatory_salt"])
    second = evaluate(config, config["confirmatory_salt"])
    hashes = [semantic_hash(first), semantic_hash(second)]
    return {
        "schema": "minority-prophet.dri9-confirmatory-result.v1",
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
