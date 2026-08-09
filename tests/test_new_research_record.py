import hashlib
import json
import pathlib
import subprocess

import pytest

from scripts.new_research_record import (
    RecordError,
    create_candidate,
    create_exploratory,
    create_imported,
    promote_canonical,
)


def _git(root: pathlib.Path, *args: str) -> str:
    result = subprocess.run(
        ("git",) + args,
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write(path: pathlib.Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def _commit(root: pathlib.Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", message)
    return _git(root, "rev-parse", "HEAD")


def _repo(tmp_path: pathlib.Path) -> pathlib.Path:
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.test")
    _git(tmp_path, "config", "user.name", "test")
    _write(tmp_path / "README.md", "fixture\n")
    _commit(tmp_path, "base")
    return tmp_path


def test_creates_exploratory_record_without_promotion_fields(tmp_path):
    root = _repo(tmp_path)
    path = create_exploratory(root, "EX-101")
    document = json.loads(path.read_text())
    assert document["stage"] == "exploratory"
    assert document["authorityEffect"] == "none"
    assert document["protocol"] is None
    assert document["result"] is None


def test_candidate_pins_committed_protocol_content(tmp_path):
    root = _repo(tmp_path)
    protocol = root / "experiments/EX-102/PROTOCOL.md"
    _write(protocol, "frozen question\n")
    commit = _commit(root, "freeze protocol")
    path = create_candidate(root, "EX-102", "experiments/EX-102/PROTOCOL.md", commit)
    document = json.loads(path.read_text())
    assert document["stage"] == "candidate"
    assert document["protocol"]["commit"] == commit
    assert document["protocol"]["sha256"] == hashlib.sha256(protocol.read_bytes()).hexdigest()


def test_candidate_rejects_uncommitted_protocol(tmp_path):
    root = _repo(tmp_path)
    _write(root / "experiments/EX-103/PROTOCOL.md", "not committed\n")
    with pytest.raises(RecordError, match="commit it before creating the record"):
        create_candidate(root, "EX-103", "experiments/EX-103/PROTOCOL.md", "HEAD")


def test_canonical_requires_candidate_committed_before_result(tmp_path):
    root = _repo(tmp_path)
    protocol = "experiments/EX-104/PROTOCOL.md"
    _write(root / protocol, "frozen\n")
    protocol_commit = _commit(root, "freeze protocol")
    create_candidate(root, "EX-104", protocol, protocol_commit)
    _commit(root, "record candidate")

    result = "results/ex-104-v1/result.json"
    manifest = "results/ex-104-v1/manifest.json"
    _write(root / result, '{"outcome":"rejected"}\n')
    _write(root / manifest, '{"schema":"fixture"}\n')
    result_commit = _commit(root, "record result")

    path = promote_canonical(
        root,
        "EX-104",
        result,
        result_commit,
        manifest,
        result_commit,
        "rejected",
    )
    document = json.loads(path.read_text())
    assert document["stage"] == "canonical"
    assert document["verdict"] == "rejected"
    assert document["result"]["commit"] == result_commit


def test_canonical_refuses_result_that_predates_candidate_record(tmp_path):
    root = _repo(tmp_path)
    protocol = "experiments/EX-105/PROTOCOL.md"
    result = "results/ex-105-v1/result.json"
    manifest = "results/ex-105-v1/manifest.json"
    _write(root / protocol, "frozen\n")
    _write(root / result, "{}\n")
    _write(root / manifest, "{}\n")
    artifact_commit = _commit(root, "artifacts without candidate")
    create_candidate(root, "EX-105", protocol, artifact_commit)
    with pytest.raises(RecordError, match="candidate record was not committed before the result"):
        promote_canonical(
            root,
            "EX-105",
            result,
            artifact_commit,
            manifest,
            artifact_commit,
            "invalidated",
        )


def test_imported_record_declares_source_and_unknown_control(tmp_path):
    root = _repo(tmp_path)
    _write(root / "imports/EX-106/protocol.md", "protocol\n")
    _write(root / "imports/EX-106/result.json", "{}\n")
    _write(root / "imports/EX-106/manifest.json", "{}\n")
    path = create_imported(
        root,
        "EX-106",
        "imports/EX-106/protocol.md",
        "imports/EX-106/result.json",
        "imports/EX-106/manifest.json",
        "incomplete",
        "https://example.test/source.git",
        "a" * 40,
        "unknown",
    )
    document = json.loads(path.read_text())
    assert document["stage"] == "imported"
    assert document["origin"]["controlRelationship"] == "unknown"
    assert document["protocol"]["commit"] is None


def test_imported_record_requires_source_repository(tmp_path):
    root = _repo(tmp_path)
    _write(root / "imports/EX-108/protocol.md", "protocol\n")
    _write(root / "imports/EX-108/result.json", "{}\n")
    _write(root / "imports/EX-108/manifest.json", "{}\n")
    with pytest.raises(RecordError, match="source repository must identify"):
        create_imported(
            root,
            "EX-108",
            "imports/EX-108/protocol.md",
            "imports/EX-108/result.json",
            "imports/EX-108/manifest.json",
            "incomplete",
            "",
            "a" * 40,
            "unknown",
        )


def test_refuses_to_overwrite_existing_record(tmp_path):
    root = _repo(tmp_path)
    create_exploratory(root, "EX-107")
    with pytest.raises(RecordError, match="do not overwrite"):
        create_exploratory(root, "EX-107")
