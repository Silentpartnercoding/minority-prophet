#!/usr/bin/env python3
"""Enforce narrow, graduated lifecycle rules for newly enrolled research.

Ordinary code, documentation, adapters, and exploratory branches remain under
the existing tests. This checker governs per-record lifecycle files, newly
promoted result directories, and public claim indexes. It validates declared
evidence; it cannot discover hidden common control or decide truth.
"""

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
RECORDS = pathlib.PurePosixPath("research/records")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
IDENTIFIER = re.compile(r"^[A-Z0-9][A-Z0-9._/-]*$")
STAGES = {"exploratory", "candidate", "canonical", "imported"}
VERDICTS = {"supported", "rejected", "incomplete", "invalidated"}
CONTROL_RELATIONSHIPS = {"same-control-domain", "external-control", "unknown"}
ASSESSMENTS = {"dependent", "partially-dependent", "unknown", "independent"}
POLICY_PATHS = {
    "AGENTS.md",
    "CONTRIBUTING.md",
    "research/integrity/research-record.schema.json",
    "research/integrity/README.md",
    "scripts/check_research_integrity.py",
    ".github/workflows/ci.yml",
}
INTEGRITY_TEST = "tests/test_research_integrity.py"


def _git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git",) + args,
        cwd=root,
        capture_output=True,
        text=True,
    )


def _safe_relative(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    path = pathlib.PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("./"):
        return None
    return path.as_posix()


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_at(root: pathlib.Path, ref: str, path: str) -> dict[str, Any] | None:
    result = _git(root, "show", f"{ref}:{path}")
    if result.returncode != 0:
        return None
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _is_ancestor(root: pathlib.Path, older: str, newer: str) -> bool:
    return _git(root, "merge-base", "--is-ancestor", older, newer).returncode == 0


def _validate_artifact(
    root: pathlib.Path,
    label: str,
    value: object,
    head: str,
    *,
    commit_required: bool,
) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}: expected an artifact object"]
    if set(value) != {"path", "sha256", "commit"}:
        return [f"{label}: artifact keys must be path, sha256, and commit"]
    path = _safe_relative(value.get("path"))
    digest = value.get("sha256")
    commit = value.get("commit")
    problems: list[str] = []
    if path is None:
        problems.append(f"{label}: path must be a safe repository-relative path")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        problems.append(f"{label}: sha256 must be 64 lowercase hexadecimal characters")
    if commit_required and (not isinstance(commit, str) or not COMMIT.fullmatch(commit)):
        problems.append(f"{label}: a pinned commit is required")
    elif commit is not None and (not isinstance(commit, str) or not COMMIT.fullmatch(commit)):
        problems.append(f"{label}: commit must be null or a 7-40 character commit id")
    if problems or path is None or not isinstance(digest, str):
        return problems

    current = root / path
    if not current.is_file():
        problems.append(f"{label}: {path} does not exist at the checked-out head")
    elif _sha256(current) != digest:
        problems.append(f"{label}: {path} does not match its declared sha256")

    if isinstance(commit, str) and COMMIT.fullmatch(commit):
        if _git(root, "cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
            problems.append(f"{label}: pinned commit {commit[:9]} does not exist")
        elif not _is_ancestor(root, commit, head):
            problems.append(f"{label}: pinned commit {commit[:9]} is not an ancestor of {head}")
        else:
            pinned = _git(root, "show", f"{commit}:{path}")
            if pinned.returncode != 0:
                problems.append(f"{label}: {path} is absent at pinned commit {commit[:9]}")
            elif hashlib.sha256(pinned.stdout.encode()).hexdigest() != digest:
                problems.append(f"{label}: {path} differs from its pinned commit")
    return problems


def validate_record(
    root: pathlib.Path,
    path: pathlib.Path,
    document: dict[str, Any],
    head: str,
) -> list[str]:
    label = path.relative_to(root).as_posix()
    required = {
        "schema", "id", "stage", "authorityEffect", "origin", "protocol",
        "result", "manifest", "verdict", "artifacts", "independenceClaims",
    }
    problems: list[str] = []
    if set(document) != required:
        missing = sorted(required - set(document))
        extra = sorted(set(document) - required)
        problems.append(f"{label}: record keys differ; missing={missing}, extra={extra}")
        return problems
    if document["schema"] != SCHEMA:
        problems.append(f"{label}: schema must be {SCHEMA}")
    identifier = document["id"]
    if not isinstance(identifier, str) or not IDENTIFIER.fullmatch(identifier):
        problems.append(f"{label}: invalid record id")
    elif path.stem != identifier.replace("/", "--"):
        expected = identifier.replace("/", "--") + ".json"
        problems.append(f"{label}: filename must be {expected} for record id {identifier}")
    stage = document["stage"]
    if stage not in STAGES:
        problems.append(f"{label}: unknown stage {stage!r}")
        return problems
    if document["authorityEffect"] != "none":
        problems.append(f"{label}: research records cannot grant an authority effect")

    origin = document["origin"]
    if not isinstance(origin, dict):
        problems.append(f"{label}: origin must be an object")
        origin = {}
    allowed_origin = {"mode", "controlRelationship", "sourceRepository", "sourceCommit"}
    if not {"mode", "controlRelationship"}.issubset(origin) or not set(origin).issubset(allowed_origin):
        problems.append(f"{label}: origin keys are invalid")
    mode = origin.get("mode")
    relationship = origin.get("controlRelationship")
    if mode not in {"repository-native", "out-of-tree-import"}:
        problems.append(f"{label}: origin mode is invalid")
    if relationship not in CONTROL_RELATIONSHIPS:
        problems.append(f"{label}: origin controlRelationship is invalid")

    artifacts = document["artifacts"]
    if not isinstance(artifacts, list) or len(artifacts) != len(set(artifacts)):
        problems.append(f"{label}: artifacts must be a unique list")
        artifacts = []
    for artifact in artifacts:
        safe = _safe_relative(artifact)
        if safe is None or not (root / safe).is_file():
            problems.append(f"{label}: artifact {artifact!r} is absent or unsafe")

    verdict = document["verdict"]
    refs = {name: document[name] for name in ("protocol", "result", "manifest")}
    if stage == "exploratory":
        if any(value is not None for value in refs.values()) or verdict is not None:
            problems.append(f"{label}: exploratory records cannot contain promoted result fields")
    elif stage == "candidate":
        if refs["protocol"] is None:
            problems.append(f"{label}: candidate requires a frozen protocol")
        if refs["result"] is not None or refs["manifest"] is not None or verdict is not None:
            problems.append(f"{label}: candidate cannot contain confirmation result fields")
    else:
        if any(value is None for value in refs.values()):
            problems.append(f"{label}: {stage} record requires protocol, result, and manifest")
        if verdict not in VERDICTS:
            problems.append(f"{label}: {stage} record requires an honest closed verdict")
    if stage == "canonical" and mode != "repository-native":
        problems.append(f"{label}: canonical record must be repository-native")
    if stage == "imported":
        if mode != "out-of-tree-import":
            problems.append(f"{label}: imported record must declare out-of-tree-import")
        if not isinstance(origin.get("sourceRepository"), str) or not origin.get("sourceRepository"):
            problems.append(f"{label}: imported record requires sourceRepository")
        source_commit = origin.get("sourceCommit")
        if not isinstance(source_commit, str) or not re.fullmatch(r"[0-9a-f]{7,64}", source_commit):
            problems.append(f"{label}: imported record requires sourceCommit")

    for name, value in refs.items():
        if value is not None:
            problems.extend(_validate_artifact(
                root,
                f"{label}:{name}",
                value,
                head,
                commit_required=stage in {"candidate", "canonical"},
            ))

    claims = document["independenceClaims"]
    if not isinstance(claims, list):
        problems.append(f"{label}: independenceClaims must be a list")
        claims = []
    for index, claim in enumerate(claims):
        claim_label = f"{label}:independenceClaims[{index}]"
        if not isinstance(claim, dict) or set(claim) != {
            "assessment", "witness", "witnessControlRelationship",
        }:
            problems.append(f"{claim_label}: invalid claim shape")
            continue
        assessment = claim["assessment"]
        witness_relationship = claim["witnessControlRelationship"]
        if assessment not in ASSESSMENTS:
            problems.append(f"{claim_label}: invalid assessment")
        if witness_relationship not in CONTROL_RELATIONSHIPS:
            problems.append(f"{claim_label}: invalid witness control relationship")
        if assessment == "independent":
            if witness_relationship != "external-control":
                problems.append(f"{claim_label}: independent requires external-control witness")
            if claim["witness"] is None:
                problems.append(f"{claim_label}: independent requires a content-bound witness")
        if claim["witness"] is not None:
            problems.extend(_validate_artifact(
                root,
                f"{claim_label}:witness",
                claim["witness"],
                head,
                commit_required=False,
            ))
    return problems


def _candidate_preceded_result(
    root: pathlib.Path,
    path: str,
    document: dict[str, Any],
    head: str,
) -> bool:
    result_commit = document["result"]["commit"]
    protocol = document["protocol"]
    history = _git(root, "rev-list", "--reverse", head, "--", path)
    if history.returncode != 0:
        return False
    for commit in history.stdout.splitlines():
        if commit == result_commit or not _is_ancestor(root, commit, result_commit):
            continue
        earlier = _json_at(root, commit, path)
        if earlier and earlier.get("stage") == "candidate" and earlier.get("protocol") == protocol:
            return True
    return False


def validate_lifecycle(
    root: pathlib.Path,
    relative_path: str,
    document: dict[str, Any],
    base: str,
    head: str,
) -> list[str]:
    label = relative_path
    problems: list[str] = []
    previous = _json_at(root, base, relative_path)
    if previous:
        if previous.get("stage") in {"canonical", "imported"} and previous != document:
            problems.append(f"{label}: closed records are immutable; create a new version")
        ranks = {"exploratory": 0, "candidate": 1, "canonical": 2, "imported": 2}
        old_stage, new_stage = previous.get("stage"), document.get("stage")
        if old_stage in ranks and new_stage in ranks and ranks[new_stage] < ranks[old_stage]:
            problems.append(f"{label}: lifecycle stage cannot move backward")
        if old_stage in {"canonical", "imported"} and new_stage != old_stage:
            problems.append(f"{label}: closed record class cannot change")

    if document.get("stage") == "canonical" and all(
        isinstance(document.get(name), dict) for name in ("protocol", "result", "manifest")
    ):
        protocol_commit = document["protocol"].get("commit")
        result_commit = document["result"].get("commit")
        if isinstance(protocol_commit, str) and isinstance(result_commit, str):
            if protocol_commit == result_commit or not _is_ancestor(root, protocol_commit, result_commit):
                problems.append(f"{label}: protocol commit must strictly precede result commit")
            if not _candidate_preceded_result(root, label, document, head):
                problems.append(f"{label}: canonical result requires a matching candidate record before result commit")
        manifest_commit = document["manifest"].get("commit")
        if isinstance(result_commit, str) and isinstance(manifest_commit, str):
            if result_commit != manifest_commit and not _is_ancestor(root, result_commit, manifest_commit):
                problems.append(f"{label}: manifest commit cannot precede result commit")
    return problems


def changed_paths(root: pathlib.Path, base: str, head: str) -> list[tuple[str, str]]:
    result = _git(root, "diff", "--name-status", f"{base}...{head}", "--")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    output: list[tuple[str, str]] = []
    for raw in result.stdout.splitlines():
        fields = raw.split("\t")
        if len(fields) >= 2:
            output.append((fields[0][0], fields[-1]))
    return output


def _added_canonical_ids(root: pathlib.Path, base: str, head: str) -> set[str]:
    result = _git(root, "diff", "--unified=0", f"{base}...{head}", "--", "CANONICAL-RECORDS.md")
    found: set[str] = set()
    for line in result.stdout.splitlines():
        if not line.startswith("+|") or line.startswith("+++|"):
            continue
        cells = [cell.strip() for cell in line[2:].split("|")]
        if cells and IDENTIFIER.fullmatch(cells[0]):
            found.add(cells[0])
    return found


def check(root: pathlib.Path, base: str, head: str) -> list[str]:
    changes = changed_paths(root, base, head)
    changed = {path for _, path in changes}
    problems: list[str] = []

    records: dict[str, dict[str, Any]] = {}
    record_root = root / RECORDS
    for path in sorted(record_root.glob("*.json")) if record_root.is_dir() else []:
        try:
            document = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            problems.append(f"{path.relative_to(root)}: malformed JSON: {exc}")
            continue
        if not isinstance(document, dict):
            problems.append(f"{path.relative_to(root)}: record must be an object")
            continue
        relative = path.relative_to(root).as_posix()
        records[str(document.get("id", path.stem))] = document
        problems.extend(validate_record(root, path, document, head))
        if relative in changed:
            problems.extend(validate_lifecycle(root, relative, document, base, head))

    if POLICY_PATHS & changed and INTEGRITY_TEST not in changed:
        problems.append(f"integrity policy changed without {INTEGRITY_TEST}")

    claim_indexes = {"CANONICAL-RECORDS.md", "PUBLIC-CLAIMS.md"}
    if claim_indexes & changed and "EVIDENCE-ALIGNMENT.md" not in changed:
        problems.append("public or canonical claims changed without EVIDENCE-ALIGNMENT.md")

    for identifier in sorted(_added_canonical_ids(root, base, head)):
        if identifier not in records:
            problems.append(f"CANONICAL-RECORDS.md adds {identifier} without research/records/{identifier}.json")

    added_result_dirs: set[str] = set()
    for status, path in changes:
        parts = pathlib.PurePosixPath(path).parts
        if status == "A" and len(parts) >= 3 and parts[0] == "results":
            directory = "/".join(parts[:2])
            if _git(root, "cat-file", "-e", f"{base}:{directory}").returncode != 0:
                added_result_dirs.add(directory)
    for directory in sorted(added_result_dirs):
        covered = any(
            record.get("stage") in {"canonical", "imported"}
            and any(str(artifact).startswith(directory + "/") for artifact in record.get("artifacts", []))
            for record in records.values()
        )
        if not covered:
            problems.append(f"new result directory {directory} lacks a canonical or imported research record")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="trusted comparison commit")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    try:
        problems = check(root, args.base, args.head)
    except RuntimeError as exc:
        print(f"Research-integrity check could not run: {exc}", file=sys.stderr)
        return 2
    if problems:
        print("Research-integrity check FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("Research-integrity check passed: graduated lifecycle and promotion boundaries hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
