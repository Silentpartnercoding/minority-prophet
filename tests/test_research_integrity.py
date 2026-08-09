import hashlib
import json
import pathlib
import subprocess

from scripts.check_research_integrity import (
    check,
    validate_agent_instruction_bridge,
    validate_record,
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


def _commit(root: pathlib.Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", message)
    return _git(root, "rev-parse", "HEAD")


def _write(path: pathlib.Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def _write_json(path: pathlib.Path, value: dict) -> None:
    _write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo(tmp_path: pathlib.Path) -> tuple[pathlib.Path, str]:
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.test")
    _git(tmp_path, "config", "user.name", "test")
    _write(tmp_path / "README.md", "fixture\n")
    return tmp_path, _commit(tmp_path, "base")


def _origin(mode: str = "repository-native") -> dict:
    return {
        "mode": mode,
        "controlRelationship": "same-control-domain",
        "sourceRepository": None,
        "sourceCommit": None,
    }


def _record(identifier: str, stage: str = "exploratory") -> dict:
    return {
        "schema": "minority-prophet.research-record.v1",
        "id": identifier,
        "stage": stage,
        "authorityEffect": "none",
        "origin": _origin(),
        "protocol": None,
        "result": None,
        "manifest": None,
        "verdict": None,
        "artifacts": [],
        "independenceClaims": [],
    }


def _artifact(root: pathlib.Path, relative: str, commit: str | None) -> dict:
    return {
        "path": relative,
        "sha256": _digest(root / relative),
        "commit": commit,
    }


def _canonical_repo(tmp_path: pathlib.Path) -> tuple[pathlib.Path, str, str, pathlib.Path]:
    root, base = _repo(tmp_path)
    protocol_path = "experiments/TEST-1/PROTOCOL.md"
    record_path = root / "research/records/TEST-1.json"
    _write(root / protocol_path, "frozen protocol\n")
    protocol_commit = _commit(root, "freeze protocol")

    candidate = _record("TEST-1", "candidate")
    candidate["protocol"] = _artifact(root, protocol_path, protocol_commit)
    _write_json(record_path, candidate)
    _commit(root, "record candidate")

    result_path = "results/test-1-v1/result.json"
    manifest_path = "results/test-1-v1/manifest.json"
    _write(root / result_path, '{"verdict":"rejected"}\n')
    _write(root / manifest_path, '{"schema":"fixture"}\n')
    result_commit = _commit(root, "record result artifacts")

    canonical = dict(candidate)
    canonical.update({
        "stage": "canonical",
        "result": _artifact(root, result_path, result_commit),
        "manifest": _artifact(root, manifest_path, result_commit),
        "verdict": "rejected",
        "artifacts": [protocol_path, result_path, manifest_path],
    })
    _write_json(record_path, canonical)
    head = _commit(root, "close rejected result")
    return root, base, head, record_path


def test_accepts_valid_exploratory_record(tmp_path):
    root, _ = _repo(tmp_path)
    path = root / "research/records/TEST-1.json"
    document = _record("TEST-1")
    _write_json(path, document)
    assert validate_record(root, path, document, "HEAD") == []


def test_accepts_flat_filename_for_slash_identifier(tmp_path):
    root, _ = _repo(tmp_path)
    path = root / "research/records/LIR-5--PHEME.json"
    document = _record("LIR-5/PHEME")
    _write_json(path, document)
    assert validate_record(root, path, document, "HEAD") == []


def test_rejects_candidate_without_frozen_protocol(tmp_path):
    root, _ = _repo(tmp_path)
    path = root / "research/records/TEST-1.json"
    document = _record("TEST-1", "candidate")
    _write_json(path, document)
    problems = validate_record(root, path, document, "HEAD")
    assert any("candidate requires a frozen protocol" in problem for problem in problems)


def test_rejects_authority_effect(tmp_path):
    root, _ = _repo(tmp_path)
    path = root / "research/records/TEST-1.json"
    document = _record("TEST-1")
    document["authorityEffect"] = "execute"
    _write_json(path, document)
    problems = validate_record(root, path, document, "HEAD")
    assert any("cannot grant an authority effect" in problem for problem in problems)


def test_rejects_independent_without_external_witness(tmp_path):
    root, _ = _repo(tmp_path)
    path = root / "research/records/TEST-1.json"
    document = _record("TEST-1")
    document["independenceClaims"] = [{
        "assessment": "independent",
        "witness": None,
        "witnessControlRelationship": "same-control-domain",
    }]
    _write_json(path, document)
    problems = validate_record(root, path, document, "HEAD")
    assert any("requires external-control witness" in problem for problem in problems)
    assert any("requires a content-bound witness" in problem for problem in problems)


def test_accepts_independent_with_bound_external_witness(tmp_path):
    root, _ = _repo(tmp_path)
    witness = "evidence/external-witness.json"
    _write(root / witness, '{"source":"external"}\n')
    _commit(root, "add witness")
    path = root / "research/records/TEST-1.json"
    document = _record("TEST-1")
    document["independenceClaims"] = [{
        "assessment": "independent",
        "witness": _artifact(root, witness, None),
        "witnessControlRelationship": "external-control",
    }]
    _write_json(path, document)
    assert validate_record(root, path, document, "HEAD") == []


def test_accepts_candidate_then_rejected_canonical_result(tmp_path):
    root, base, head, _ = _canonical_repo(tmp_path)
    assert check(root, base, head) == []


def test_rejects_canonical_without_prior_candidate_state(tmp_path):
    root, base = _repo(tmp_path)
    protocol = "experiments/TEST-1/PROTOCOL.md"
    result = "results/test-1-v1/result.json"
    manifest = "results/test-1-v1/manifest.json"
    _write(root / protocol, "protocol\n")
    _write(root / result, "{}\n")
    _write(root / manifest, "{}\n")
    one_commit = _commit(root, "add everything together")
    document = _record("TEST-1", "canonical")
    document.update({
        "protocol": _artifact(root, protocol, one_commit),
        "result": _artifact(root, result, one_commit),
        "manifest": _artifact(root, manifest, one_commit),
        "verdict": "rejected",
        "artifacts": [protocol, result, manifest],
    })
    record_path = root / "research/records/TEST-1.json"
    _write_json(record_path, document)
    head = _commit(root, "claim canonical")
    problems = check(root, base, head)
    assert any("strictly precede" in problem for problem in problems)
    assert any("requires a matching candidate" in problem for problem in problems)


def test_rejects_closed_record_mutation_and_downgrade(tmp_path):
    root, _, canonical_head, record_path = _canonical_repo(tmp_path)
    changed = json.loads(record_path.read_text())
    changed["stage"] = "exploratory"
    changed["protocol"] = None
    changed["result"] = None
    changed["manifest"] = None
    changed["verdict"] = None
    changed["artifacts"] = []
    _write_json(record_path, changed)
    head = _commit(root, "erase negative result")
    problems = check(root, canonical_head, head)
    assert any("closed records are immutable" in problem for problem in problems)
    assert any("cannot move backward" in problem for problem in problems)


def test_rejects_new_result_directory_without_record(tmp_path):
    root, base = _repo(tmp_path)
    _write(root / "results/unregistered-v1/result.json", "{}\n")
    head = _commit(root, "add unregistered result")
    problems = check(root, base, head)
    assert any("lacks a canonical or imported research record" in problem for problem in problems)


def test_rejects_new_canonical_index_row_without_record(tmp_path):
    root, _ = _repo(tmp_path)
    _write(root / "CANONICAL-RECORDS.md", "| Experiment | Status |\n| --- | --- |\n")
    _write(root / "EVIDENCE-ALIGNMENT.md", "# Evidence alignment\n")
    base = _commit(root, "add indexes")
    _write(
        root / "CANONICAL-RECORDS.md",
        "| Experiment | Status |\n| --- | --- |\n| TEST-2 | Canonical |\n",
    )
    _write(root / "EVIDENCE-ALIGNMENT.md", "# Evidence alignment\n\nTEST-2 pending.\n")
    head = _commit(root, "claim canonical without record")
    problems = check(root, base, head)
    assert any("adds TEST-2 without research/records/TEST-2.json" in problem for problem in problems)


def test_ignores_untouched_legacy_result_directory(tmp_path):
    root, _ = _repo(tmp_path)
    _write(root / "results/legacy-v1/result.json", "{}\n")
    base = _commit(root, "legacy result")
    _write(root / "notes.md", "ordinary documentation\n")
    head = _commit(root, "ordinary docs")
    assert check(root, base, head) == []


def test_policy_change_requires_integrity_test_change(tmp_path):
    root, base = _repo(tmp_path)
    _write(root / "AGENTS.md", "changed policy\n")
    head = _commit(root, "change policy without tests")
    problems = check(root, base, head)
    assert any("policy changed" in problem for problem in problems)


def test_accepts_claude_bridge_that_imports_agents(tmp_path):
    root, _ = _repo(tmp_path)
    _write(root / "AGENTS.md", "canonical instructions\n")
    _write(root / "CLAUDE.md", "# Claude Code instructions\n\n@AGENTS.md\n")
    assert validate_agent_instruction_bridge(root) == []


def test_rejects_claude_bridge_that_duplicates_or_drifts(tmp_path):
    root, _ = _repo(tmp_path)
    _write(root / "AGENTS.md", "canonical instructions\n")
    _write(root / "CLAUDE.md", "Copied rules that can drift.\n")
    problems = validate_agent_instruction_bridge(root)
    assert any("do not duplicate or fork" in problem for problem in problems)
