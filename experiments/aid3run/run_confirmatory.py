"""Frozen AID-3 confirmatory runner.

Do not invoke until the candidate record is committed. Do not evaluate the
confirmatory salt while editing the protocol.

Provenance: the world this runs was written by the adversarial review and
submitted as PR #214 against AID-1. It is relocated here and run against the
**repaired** policy, which is the point of AID-3. This runner is the reviewer's,
with the pin map re-derived over the new paths and the repaired policy digest,
the schema string renamed, and the refusal messages renamed. Every change is
listed in `research/attested-independence/AID-3-REGISTRATION-NOTE.md`.
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

from experiments.aid3run.scoring import evaluate, evaluate_criterion, semantic_hash

ROOT = Path(__file__).resolve().parents[2]
PINNED = {
    "experiments/aid3run/PREREGISTRATION.md": "174afec11039c8297446a37f8388f835f36bec464a4d62eda36117e89dbb714c",
    "experiments/aid3run/CONFIRMATORY-CONFIG.json": "597aaa84fdd2cbfc7846e29fdbf01e75f20b506d58617b96dc7d917a6b2eb7c3",
    "experiments/aid3run/world.py": "b5cb965a12ddec6901280038ece8602c8504ecb4f4c9b6de3b3997e2ee1d82d9",
    "experiments/aid3run/arms.py": "c15e6a7af7d6e27bee00c276bd295a2fe1430a295ef4bff84df2c2a5d11b4516",
    "experiments/aid3run/scoring.py": "eba23d4c997a76a298554695a95b0c180bdb2b5fc840d726f5d9081b0545cee2",
    "aggregation/attested_independence.py": "116d290f88895ec743205643aee442df7454993565f58425b4e92b14c538ea60",
    "aggregation/independence_axes.py": "324bab7f971ba1a0849329010c76aa048f8157dbbb7f3a440b8426639901c311",
    "canon/proximity.py": "15398c208bf391c9d150e23b2f18dad6affd9d271303129395df754ccb71ab3b",
    "canon/independent_set.py": "a0e9b357291f9175b8608d656d03eefc2159aaa9e25ae66477e515fe5206fb3c",
    "experiments/dri2/stats.py": "6f65060ff5cd366e6ca2a65fe85395210212e32f2abc3dfb0f72e7e3f06c9257",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins(root: Path = ROOT) -> None:
    changed = sorted(name for name, digest in PINNED.items() if _sha256(root / name) != digest)
    if changed:
        raise ValueError("frozen AID-3 inputs changed: " + ", ".join(changed))


def load_config(root: Path = ROOT) -> dict[str, Any]:
    verify_pins(root)
    config = json.loads((root / "experiments/aid3run/CONFIRMATORY-CONFIG.json").read_text())
    if config["status"] != "preregistered-unexecuted":
        raise ValueError("AID-3 configuration is not in its preregistered state")
    if config["success_criterion"]["primary"] != "attested":
        raise ValueError("AID-3 primary is not attested")
    return config


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def run_confirmatory(config: dict[str, Any]) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    first = evaluate(config, config["confirmatory_salt"])
    second = evaluate(config, config["confirmatory_salt"])
    hashes = [semantic_hash(first), semantic_hash(second)]
    return {
        "schema": "minority-prophet.aid3-confirmatory-result.v1",
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
