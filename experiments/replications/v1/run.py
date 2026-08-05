#!/usr/bin/env python3
"""Portable, deterministic replay harness for canonical replications v1."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HANDOFF = ROOT / "research/evidence/2026-08-04/archives/minority-prophet-handoff.zip"
ONESHOT = ROOT / "research/evidence/2026-08-04/archives/minority-prophet-oneshot.zip"
EXP008 = ROOT / "experiments/exp008_shootout.py"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def archive_member(archive: Path, member: str) -> bytes:
    with zipfile.ZipFile(archive) as source:
        return source.read(member)


def portable(source: bytes, workspace: Path) -> bytes:
    return source.replace(b"/home/claude", os.fsencode(workspace))


def execute(script: Path, *args: str) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=script.parent,
        env={"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": [script.name, *args],
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def one_run(protocol_commit: str) -> tuple[dict[str, object], dict[str, bytes]]:
    outputs: dict[str, bytes] = {}
    executions: dict[str, dict[str, object]] = {}
    sources: dict[str, str] = {}

    members = {
        "exp003.py": (HANDOFF, "handoff/reference/exp003.py"),
        "exp004.py": (HANDOFF, "handoff/reference/exp004.py"),
        "exp004b.py": (HANDOFF, "handoff/reference/exp004b.py"),
        "exp005.py": (HANDOFF, "handoff/reference/exp005.py"),
        "exp006_h5.py": (ONESHOT, "final/results/exp006_h5.py"),
        "exp007_finisher.py": (ONESHOT, "final/results/exp007_finisher.py"),
    }

    with tempfile.TemporaryDirectory(prefix="minority-prophet-replay-") as tmp:
        workspace = Path(tmp)
        (workspace / "final/results").mkdir(parents=True)
        for name, (archive, member) in members.items():
            raw = archive_member(archive, member)
            sources[f"{archive.name}:{member}"] = digest(raw)
            destination = workspace / name
            destination.write_bytes(portable(raw, workspace))

        schedule = [
            ("EXP003R", workspace / "exp003.py", ("200",)),
            ("EXP004R-primary", workspace / "exp004.py", ()),
            ("EXP004R-corrected", workspace / "exp004b.py", ()),
            ("EXP005R", workspace / "exp005.py", ()),
            ("EXP006R", workspace / "exp006_h5.py", ()),
            ("EXP007R", workspace / "exp007_finisher.py", ()),
            ("EXP008R", EXP008, ()),
        ]
        for label, script, args in schedule:
            result = execute(script, *args)
            outputs[f"{label}.stdout.txt"] = result.pop("stdout")  # type: ignore[assignment]
            outputs[f"{label}.stderr.txt"] = result.pop("stderr")  # type: ignore[assignment]
            executions[label] = result

        generated = {
            "EXP003R.raw.jsonl": workspace / "raw.jsonl",
            "EXP003R.summary.md": workspace / "summary.md",
            "EXP004R.primary.json": workspace / "exp004_sweep.json",
            "EXP004R.corrected.json": workspace / "exp004b.json",
            "EXP005R.json": workspace / "exp005.json",
            "EXP006R.json": workspace / "final/results/exp006_h5.json",
        }
        for name, path in generated.items():
            if path.exists():
                outputs[name] = path.read_bytes()

    exp007_text = outputs.get("EXP007R.stdout.txt", b"").decode(errors="replace")
    verdicts = {
        "EXP003R": "reproduced" if executions["EXP003R"]["exit_code"] == 0 and "EXP003R.raw.jsonl" in outputs else "execution-error",
        "EXP004R": "reproduced" if all(executions[x]["exit_code"] == 0 for x in ("EXP004R-primary", "EXP004R-corrected")) and "EXP004R.corrected.json" in outputs else "execution-error",
        "EXP005R": "reproduced" if executions["EXP005R"]["exit_code"] == 0 and "EXP005R.json" in outputs else "execution-error",
        "EXP006R": "reproduced" if executions["EXP006R"]["exit_code"] == 0 and "H5 VERDICT:" in outputs.get("EXP006R.stdout.txt", b"").decode(errors="replace") else "execution-error",
        "EXP007R": "reproduced" if executions["EXP007R"]["exit_code"] == 0 and "OPTIMIZER VERDICT:" in exp007_text else ("incomplete" if executions["EXP007R"]["exit_code"] == 0 else "execution-error"),
        "EXP008R": "reproduced" if executions["EXP008R"]["exit_code"] == 0 and "ATTACK (optimizer mix)" in outputs.get("EXP008R.stdout.txt", b"").decode(errors="replace") else "execution-error",
    }
    receipt = {
        "schema": "minority-prophet.canonical-replication.v1",
        "protocol_commit": protocol_commit,
        "source_archives": {HANDOFF.name: digest(HANDOFF.read_bytes()), ONESHOT.name: digest(ONESHOT.read_bytes())},
        "source_members": sources | {str(EXP008.relative_to(ROOT)): digest(EXP008.read_bytes())},
        "executions": executions,
        "verdicts": verdicts,
        "outputs": {name: {"sha256": digest(data), "bytes": len(data)} for name, data in sorted(outputs.items())},
    }
    return receipt, outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    receipt, outputs = one_run(args.protocol_commit)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    for name, data in outputs.items():
        (args.output_dir / name).write_bytes(data)
    environment = {
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
    }
    (args.output_dir / "environment.json").write_bytes(canonical_json(environment))
    receipt["environment_sha256"] = digest((args.output_dir / "environment.json").read_bytes())
    (args.output_dir / "receipt.json").write_bytes(canonical_json(receipt))
    print(json.dumps(receipt["verdicts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
