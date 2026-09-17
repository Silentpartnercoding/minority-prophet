"""Frozen AID-2 confirmatory runner.

Do not invoke until the candidate record is committed. Do not evaluate the
confirmatory salt while editing the protocol or the world.

The pin list is derived from what the world actually imports, not from memory,
and it includes `aggregation/attested_independence.py` — the artifact under
test, in its repaired form as merged to main. A runner that pins the world but
not the policy can measure a policy the record does not name.
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

from experiments.aid2run.scoring import evaluate, evaluate_criterion, semantic_hash

ROOT = Path(__file__).resolve().parents[2]

#: Protocol, world, the artifact under test, and every repository module the
#: world imports. Digests taken at freeze time.
PINNED = {
    "experiments/aid2run/PREREGISTRATION.md": "5b221963227dbc93286aa2de0bef5e533d738b6584b9c8f55cfa20c93bd5a2a9",
    "experiments/aid2run/EXECUTION-CONFIG.json": "e09363790c181998a0b40113c5f563cf0770ae090cf07eeb3ff501e03e47110d",
    "experiments/aid2run/world.py": "4b20171486e5daa0e8a03e2f30949cc7435dffc4026c21161368bc6692b843d9",
    "experiments/aid2run/arms.py": "b11d14f666d69f4b3275a2acbb6ee4cee220f9047bc3d3ec556eaa4d245d9177",
    "experiments/aid2run/scoring.py": "82feca363b1a798c39cce577b9b61820352796d99fbe5f76eb088156fb58b0b9",
    "aggregation/attested_independence.py": "116d290f88895ec743205643aee442df7454993565f58425b4e92b14c538ea60",
    "aggregation/independence_axes.py": "324bab7f971ba1a0849329010c76aa048f8157dbbb7f3a440b8426639901c311",
    "canon/independent_set.py": "a0e9b357291f9175b8608d656d03eefc2159aaa9e25ae66477e515fe5206fb3c",
    "canon/proximity.py": "15398c208bf391c9d150e23b2f18dad6affd9d271303129395df754ccb71ab3b",
    "experiments/dri2/stats.py": "6f65060ff5cd366e6ca2a65fe85395210212e32f2abc3dfb0f72e7e3f06c9257",
    "experiments/dri3/world.py": "f6401442a47ba6179680203914a0c850ace2306ad1eb8101ea0e22996509d592",
    "provenance/decision_relative.py": "f9fe5d9b95982e42c754fa3a187628f09be5408f69f7fa6873029bdad3046b13",
    "provenance/dependence_robustness.py": "c5273b6d4dbe7faa22351ba456c6781ac19a4b911b002167362d41ecd1d921bf",
}

#: The artifact whose behaviour this experiment measures, named separately so a
#: reader does not have to infer it from the list.
ARTIFACT_UNDER_TEST = "aggregation/attested_independence.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins(root: Path = ROOT) -> None:
    changed = sorted(name for name, digest in PINNED.items() if _sha256(root / name) != digest)
    if changed:
        raise ValueError("frozen AID-2 inputs changed: " + ", ".join(changed))


def load_config(root: Path = ROOT) -> dict[str, Any]:
    verify_pins(root)
    config = json.loads((root / "experiments/aid2run/EXECUTION-CONFIG.json").read_text())
    if config["status"] != "preregistered-unexecuted":
        raise ValueError("AID-2 configuration is not in its preregistered state")
    rule = config["success_criterion"]
    if rule["primary_arm"] != "attested_bounds" or rule["baseline_arm"] != "ladder":
        raise ValueError("AID-2 arms are not the ones the specification named")
    return config


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def run_confirmatory(config: dict[str, Any]) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    first = evaluate(config, config["confirmatory_salt"])
    second = evaluate(config, config["confirmatory_salt"])
    hashes = [semantic_hash(first), semantic_hash(second)]
    return {
        "schema": "minority-prophet.aid2-confirmatory-result.v1",
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
        "verdict": criterion["verdict"],
        "supported": criterion["supported"],
        "reproducible": result["semanticResultSha256Runs"][0] == result["semanticResultSha256Runs"][1],
        "semanticSha256": result["semanticResultSha256Runs"][0],
        "outputSha256": _sha256(args.output),
    }, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
