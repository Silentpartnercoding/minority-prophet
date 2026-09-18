"""Frozen AID-4 confirmatory runner.

Do not invoke until the candidate record is committed. Do not evaluate the
confirmatory salt while editing the protocol or the world.

**This runner is mine; the world it runs is not.** The world, the arms and both
scoring modules were written by an author who did not design either policy, and
`scoring.evaluate` refuses the confirmatory salt unless `confirmatory=True` is
passed explicitly. That author deliberately shipped no runner, so that turning
the key would be a separate, recorded act. This file is that act.

The pin map covers the ten inputs named in `PREREGISTRATION.md` section 9,
including `aggregation/attested_independence.py` — the artifact whose two
successor proposals are under test. A runner that pins the world but not the
policy can measure a policy the record does not name.
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

from experiments.aid4run.scoring import evaluate, evaluate_criterion, semantic_hash

ROOT = Path(__file__).resolve().parents[2]

#: Protocol, world, and every repository module the world imports. Digests taken
#: after the world was delivered and before anything was frozen; no pinned file
#: has been edited since.
PINNED = {
    "experiments/aid4run/PREREGISTRATION.md": "821c3bf104d25af5e6205ff5df439d2e29d2086b7a85d929ede5aa2323af5f99",
    "experiments/aid4run/EXECUTION-CONFIG.json": "1d9c7dccbb08be040c34f3da0f05cdf775a06fcf0daa49babfc528b199a474e4",
    "experiments/aid4run/world.py": "234b7b1cf0ff819ae2b813794283e18553fba9589881a813d509a1620e28dd66",
    "experiments/aid4run/arms.py": "3dda798453281998f36b3ca07f3bf45a8d5eb32fbe797bd9f5d9a485c159404d",
    "experiments/aid4run/scoring.py": "df2e9c299555bedecd938e2af8de601f255f592ab440129ac3f1771055618149",
    "aggregation/attested_independence.py": "116d290f88895ec743205643aee442df7454993565f58425b4e92b14c538ea60",
    "aggregation/independence_axes.py": "324bab7f971ba1a0849329010c76aa048f8157dbbb7f3a440b8426639901c311",
    "canon/proximity.py": "15398c208bf391c9d150e23b2f18dad6affd9d271303129395df754ccb71ab3b",
    "canon/independent_set.py": "a0e9b357291f9175b8608d656d03eefc2159aaa9e25ae66477e515fe5206fb3c",
    "experiments/dri2/stats.py": "6f65060ff5cd366e6ca2a65fe85395210212e32f2abc3dfb0f72e7e3f06c9257",
}

#: The artifact whose successors are measured here, named so a reader need not
#: infer it from the list.
ARTIFACT_UNDER_TEST = "aggregation/attested_independence.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins(root: Path = ROOT) -> None:
    changed = sorted(name for name, digest in PINNED.items() if _sha256(root / name) != digest)
    if changed:
        raise ValueError("frozen AID-4 inputs changed: " + ", ".join(changed))


def load_config(root: Path = ROOT) -> dict[str, Any]:
    verify_pins(root)
    config = json.loads((root / "experiments/aid4run/EXECUTION-CONFIG.json").read_text())
    if config["status"] != "preregistered-unexecuted":
        raise ValueError("AID-4 configuration is not in its preregistered state")
    rule = config["success_criterion"]
    if rule["primary_b"] != "margin" or rule["primary_c"] != "priced":
        raise ValueError("AID-4 arms are not the ones the specification named")
    if rule["baseline"] != "ladder":
        raise ValueError("AID-4 baseline is not the ladder")
    return config


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def run_confirmatory(config: dict[str, Any]) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    salt = config["confirmatory_salt"]
    # `confirmatory=True` is the author's deliberate gate: nothing else in the
    # repository sets it, so evaluating the confirmatory salt is an explicit act
    # recorded here rather than a default anyone could trip over.
    first = evaluate(config, salt, confirmatory=True)
    second = evaluate(config, salt, confirmatory=True)
    hashes = [semantic_hash(first), semantic_hash(second)]
    return {
        "schema": "minority-prophet.aid4-confirmatory-result.v1",
        "status": "confirmatory-complete",
        "pins": PINNED,
        "artifactUnderTest": ARTIFACT_UNDER_TEST,
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
    criterion = result["criterion"]
    print(json.dumps({
        "supported": criterion["supported"],
        "supportedPolicyB": criterion["policyB"]["supported"],
        "supportedPolicyC": criterion["policyC"]["supported"],
        "reproducible": result["semanticResultSha256Runs"][0] == result["semanticResultSha256Runs"][1],
        "semanticSha256": result["semanticResultSha256Runs"][0],
        "outputSha256": _sha256(args.output),
    }, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
