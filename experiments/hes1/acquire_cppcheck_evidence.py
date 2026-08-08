#!/usr/bin/env python3
"""Acquire the preregistered Cppcheck family without aggregating outcomes."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "experiments" / "hgd2" / "software-detector-records.json"
OUTPUT = ROOT / "experiments" / "hes1" / "cppcheck-evidence.json"
EXTRACTED = ROOT / "artifacts" / "hgd2-source" / "extracted"
COMMAND = ("cppcheck", "--xml", "--xml-version=2", "--enable=warning,performance",
           "--inconclusive", "--force")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    version = subprocess.check_output(["cppcheck", "--version"], text=True).strip()
    packet = json.loads(INPUT.read_text())
    records = []
    for item in sorted(packet["records"], key=lambda row: row["case"]):
        source = EXTRACTED / item["sourcePath"]
        if not source.is_file() or digest(source) != item["sourceSha256"]:
            raise RuntimeError(f"source commitment mismatch: {item['case']}")
        process = subprocess.run((*COMMAND, str(source)), capture_output=True, text=True)
        records.append({
            "case": item["case"],
            "command": [*COMMAND, "<frozen-source>"],
            "exit": process.returncode,
            "sourceSha256": item["sourceSha256"],
            "stdout": process.stdout,
            "stderr": process.stderr,
        })
    output = {
        "schema": "minority-prophet.hes1.cppcheck-evidence.v1",
        "tool": "Cppcheck",
        "version": version,
        "records": records,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
