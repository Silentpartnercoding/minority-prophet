#!/usr/bin/env python3
"""Create or promote a Minority Prophet research lifecycle record safely."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from typing import Any


SCHEMA = "minority-prophet.research-record.v1"
IDENTIFIER = re.compile(r"^[A-Z0-9][A-Z0-9._/-]*$")
SOURCE_COMMIT = re.compile(r"^[0-9a-f]{7,64}$")


class RecordError(ValueError):
    """An actionable record-scaffolding failure."""


def _git(root: pathlib.Path, *args: str, binary: bool = False):
    return subprocess.run(
        ("git",) + args,
        cwd=root,
        capture_output=True,
        text=not binary,
    )


def _record_path(root: pathlib.Path, identifier: str) -> pathlib.Path:
    if not IDENTIFIER.fullmatch(identifier):
        raise RecordError(
            "record id must start with A-Z or 0-9 and contain only A-Z, 0-9, ., _, /, or -"
        )
    return root / "research" / "records" / f"{identifier.replace('/', '--')}.json"


def _relative_file(root: pathlib.Path, value: str) -> tuple[pathlib.Path, str]:
    root = root.resolve()
    candidate = (root / value).resolve()
    try:
        relative = candidate.relative_to(root).as_posix()
    except ValueError as exc:
        raise RecordError(f"{value}: path must stay inside the repository") from exc
    if not candidate.is_file():
        raise RecordError(f"{relative}: file does not exist")
    return candidate, relative


def _full_commit(root: pathlib.Path, value: str) -> str:
    result = _git(root, "rev-parse", "--verify", f"{value}^{{commit}}")
    if result.returncode != 0:
        raise RecordError(f"{value}: commit does not exist; commit the artifact first")
    return result.stdout.strip()


def _committed_artifact(root: pathlib.Path, value: str, commit: str) -> dict[str, str]:
    current, relative = _relative_file(root, value)
    full_commit = _full_commit(root, commit)
    pinned = _git(root, "show", f"{full_commit}:{relative}", binary=True)
    if pinned.returncode != 0:
        raise RecordError(
            f"{relative}: file is absent at {full_commit[:9]}; commit it before creating the record"
        )
    pinned_bytes = pinned.stdout
    if current.read_bytes() != pinned_bytes:
        raise RecordError(
            f"{relative}: working copy differs from {full_commit[:9]}; commit or restore it first"
        )
    return {
        "path": relative,
        "sha256": hashlib.sha256(pinned_bytes).hexdigest(),
        "commit": full_commit,
    }


def _current_artifact(root: pathlib.Path, value: str) -> dict[str, Any]:
    current, relative = _relative_file(root, value)
    return {
        "path": relative,
        "sha256": hashlib.sha256(current.read_bytes()).hexdigest(),
        "commit": None,
    }


def _base_record(identifier: str, stage: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "id": identifier,
        "stage": stage,
        "authorityEffect": "none",
        "origin": {
            "mode": "repository-native",
            "controlRelationship": "same-control-domain",
            "sourceRepository": None,
            "sourceCommit": None,
        },
        "protocol": None,
        "result": None,
        "manifest": None,
        "verdict": None,
        "artifacts": [],
        "independenceClaims": [],
    }


def _write_new(path: pathlib.Path, document: dict[str, Any]) -> None:
    if path.exists():
        raise RecordError(
            f"{path.as_posix()}: record already exists; do not overwrite an existing lifecycle"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")


def create_exploratory(root: pathlib.Path, identifier: str) -> pathlib.Path:
    path = _record_path(root, identifier)
    _write_new(path, _base_record(identifier, "exploratory"))
    return path


def create_candidate(
    root: pathlib.Path,
    identifier: str,
    protocol: str,
    protocol_commit: str,
) -> pathlib.Path:
    path = _record_path(root, identifier)
    document = _base_record(identifier, "candidate")
    document["protocol"] = _committed_artifact(root, protocol, protocol_commit)
    document["artifacts"] = [document["protocol"]["path"]]
    _write_new(path, document)
    return path


def _load_candidate(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        raise RecordError(f"{path.as_posix()}: create and commit a candidate record first")
    try:
        document = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise RecordError(f"{path.as_posix()}: existing record is malformed JSON") from exc
    if not isinstance(document, dict) or document.get("stage") != "candidate":
        raise RecordError(f"{path.as_posix()}: only a candidate record can become canonical")
    if not isinstance(document.get("protocol"), dict):
        raise RecordError(f"{path.as_posix()}: candidate has no pinned protocol")
    return document


def promote_canonical(
    root: pathlib.Path,
    identifier: str,
    result: str,
    result_commit: str,
    manifest: str,
    manifest_commit: str,
    verdict: str,
) -> pathlib.Path:
    path = _record_path(root, identifier)
    document = _load_candidate(path)
    result_artifact = _committed_artifact(root, result, result_commit)
    manifest_artifact = _committed_artifact(root, manifest, manifest_commit)

    result_commit_full = result_artifact["commit"]
    relative_record = path.relative_to(root.resolve()).as_posix()
    prior = _git(root, "show", f"{result_commit_full}:{relative_record}")
    if prior.returncode != 0:
        raise RecordError(
            f"{relative_record}: candidate record was not committed before the result; "
            "commit the candidate before running confirmation"
        )
    try:
        prior_document = json.loads(prior.stdout)
    except json.JSONDecodeError as exc:
        raise RecordError(f"{relative_record}: committed candidate is malformed") from exc
    if prior_document.get("stage") != "candidate" or prior_document.get("protocol") != document["protocol"]:
        raise RecordError(
            f"{relative_record}: result commit does not descend from the matching candidate state"
        )

    document.update({
        "stage": "canonical",
        "result": result_artifact,
        "manifest": manifest_artifact,
        "verdict": verdict,
        "artifacts": list(dict.fromkeys([
            document["protocol"]["path"],
            result_artifact["path"],
            manifest_artifact["path"],
        ])),
    })
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return path


def create_imported(
    root: pathlib.Path,
    identifier: str,
    protocol: str,
    result: str,
    manifest: str,
    verdict: str,
    source_repository: str,
    source_commit: str,
    control_relationship: str,
) -> pathlib.Path:
    if not SOURCE_COMMIT.fullmatch(source_commit):
        raise RecordError("source commit must be 7-64 lowercase hexadecimal characters")
    path = _record_path(root, identifier)
    document = _base_record(identifier, "imported")
    document["origin"] = {
        "mode": "out-of-tree-import",
        "controlRelationship": control_relationship,
        "sourceRepository": source_repository,
        "sourceCommit": source_commit,
    }
    document["protocol"] = _current_artifact(root, protocol)
    document["result"] = _current_artifact(root, result)
    document["manifest"] = _current_artifact(root, manifest)
    document["verdict"] = verdict
    document["artifacts"] = [
        document["protocol"]["path"],
        document["result"]["path"],
        document["manifest"]["path"],
    ]
    _write_new(path, document)
    return path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a valid research lifecycle record without guessing its shape."
    )
    parser.add_argument("--root", default=".", help="repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    exploratory = subparsers.add_parser("exploratory", help="create a non-promoted record")
    exploratory.add_argument("id")

    candidate = subparsers.add_parser("candidate", help="freeze a committed protocol")
    candidate.add_argument("id")
    candidate.add_argument("--protocol", required=True)
    candidate.add_argument("--protocol-commit", default="HEAD")

    canonical = subparsers.add_parser("canonical", help="close an existing candidate")
    canonical.add_argument("id")
    canonical.add_argument("--result", required=True)
    canonical.add_argument("--result-commit", default="HEAD")
    canonical.add_argument("--manifest", required=True)
    canonical.add_argument("--manifest-commit", default="HEAD")
    canonical.add_argument(
        "--verdict",
        required=True,
        choices=("supported", "rejected", "incomplete", "invalidated"),
    )

    imported = subparsers.add_parser("imported", help="record an out-of-tree result")
    imported.add_argument("id")
    imported.add_argument("--protocol", required=True)
    imported.add_argument("--result", required=True)
    imported.add_argument("--manifest", required=True)
    imported.add_argument(
        "--verdict",
        required=True,
        choices=("supported", "rejected", "incomplete", "invalidated"),
    )
    imported.add_argument("--source-repository", required=True)
    imported.add_argument("--source-commit", required=True)
    imported.add_argument(
        "--control-relationship",
        default="unknown",
        choices=("same-control-domain", "external-control", "unknown"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    try:
        if args.command == "exploratory":
            path = create_exploratory(root, args.id)
            next_step = "Label any output exploratory; run make verify before opening a PR."
        elif args.command == "candidate":
            path = create_candidate(root, args.id, args.protocol, args.protocol_commit)
            next_step = "Commit this candidate before inspecting confirmatory evidence."
        elif args.command == "canonical":
            path = promote_canonical(
                root,
                args.id,
                args.result,
                args.result_commit,
                args.manifest,
                args.manifest_commit,
                args.verdict,
            )
            next_step = "Update the evidence indexes, preserve the verdict, and run make verify."
        else:
            path = create_imported(
                root,
                args.id,
                args.protocol,
                args.result,
                args.manifest,
                args.verdict,
                args.source_repository,
                args.source_commit,
                args.control_relationship,
            )
            next_step = "Commit the imported packet and run make verify; import is not external validation."
    except RecordError as exc:
        print(f"Could not create research record: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {path.relative_to(root).as_posix()}")
    print(f"Next: {next_step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
