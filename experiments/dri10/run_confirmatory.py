"""Frozen DRI-10 confirmatory runner.

Pins the protocol, configuration, implementation, reused DRI-9 rule, DRI-8
identities, DRI-3/DRI-2 helpers and the engine. Runs the full evaluation twice
on the confirmatory salt. Do not invoke this until the candidate record is
committed. Do not evaluate the confirmatory salt while editing the protocol.
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

from experiments.dri10.scoring import evaluate, evaluate_criterion, semantic_hash

ROOT = Path(__file__).resolve().parents[2]
PINNED = {
    "experiments/dri10/PREREGISTRATION.md": "bae5e3fa1293fe423388f343a0c87c12193d0e4c50a7a1a7c721d931ad2d94f1",
    "experiments/dri10/EXECUTION-CONFIG.json": "ce86c43871278fc2889d129b66aa9929ac9c7bf23f9c6101984d981b9c103b50",
    "experiments/dri10/world.py": "ee8b3593c72d0874ea2019d043110e35daa7c3359dd0c50081aea66f46eaa988",
    "experiments/dri10/arms.py": "c3a8d03fbeaaa548e9716ae6a8c95d930d6a5f23aca490f4726551d334620f80",
    "experiments/dri10/scoring.py": "37cadab302e7ffaa3e38fc18fa77134ca09e23aa50e0f10963e3c663d58cf539",
    "experiments/dri9/rule.py": "6ef60455220f355228878bf9f8585f46e72fe3ac789840a1ea752b9478714405",
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
        raise ValueError("frozen DRI-10 inputs changed: " + ", ".join(changed))


def load_config(root: Path = ROOT) -> dict[str, Any]:
    verify_pins(root)
    config = json.loads((root / "experiments/dri10/EXECUTION-CONFIG.json").read_text())
    if config["status"] != "preregistered-unexecuted":
        raise ValueError("DRI-10 configuration is not in its preregistered state")
    if config["success_criterion"]["method_under_test"] != "bait":
        raise ValueError("DRI-10 method under test is not the named bait arm")
    return config


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def run_confirmatory(config: dict[str, Any]) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    first = evaluate(config, config["confirmatory_salt"])
    second = evaluate(config, config["confirmatory_salt"])
    hashes = [semantic_hash(first), semantic_hash(second)]
    return {
        "schema": "minority-prophet.dri10-confirmatory-result.v1",
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
