#!/usr/bin/env python3
"""Validate the repository's canonical evidence-model registry.

The registry is a routing layer, not a new source of scientific results. This
checker resolves its references back to theorem and research authorities,
verifies declared immutable pins, and reconciles structured status banners on
documents that can otherwise be mistaken for current doctrine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_COLLECTIONS = ("layers", "terms", "mechanisms", "claimBindings", "artifacts")
DISPOSITIONS = {"current", "research_only", "rejected", "historical", "superseded"}
ARTIFACT_CLASSES = {"current", "historical_snapshot", "rejected_policy", "superseded"}
STATUS_RE = re.compile(r"<!--\s*mp-status:\s*(\{.*?\})\s*-->")


def _json(path: Path) -> Any:
    return json.loads(path.read_text())


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def _authority_ids(root: Path) -> tuple[set[str], dict[str, dict[str, Any]], list[str]]:
    problems: list[str] = []
    theorem_ids: set[str] = set()
    research: dict[str, dict[str, Any]] = {}

    theorem_path = root / "formal/THEOREM-LEDGER.json"
    try:
        theorem_ids = {entry["id"] for entry in _json(theorem_path)["claims"]}
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        problems.append(f"cannot load theorem authority {theorem_path}: {exc}")

    records_dir = root / "research/records"
    try:
        record_paths = sorted(records_dir.glob("*.json"))
    except OSError as exc:
        record_paths = []
        problems.append(f"cannot enumerate research authority {records_dir}: {exc}")
    for path in record_paths:
        try:
            record = _json(path)
            record_id = record["id"]
            if record_id in research:
                problems.append(f"duplicate research record id {record_id!r}")
            research[record_id] = record
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            problems.append(f"cannot load research authority {path}: {exc}")
    return theorem_ids, research, problems


def _check_refs(
    *,
    owner: str,
    entry: dict[str, Any],
    theorem_ids: set[str],
    research: dict[str, dict[str, Any]],
    problems: list[str],
) -> None:
    for theorem_id in entry.get("theorems", []):
        if theorem_id not in theorem_ids:
            problems.append(f"{owner}: unknown theorem id {theorem_id!r}")
    for record_id in entry.get("researchRecords", []):
        if record_id not in research:
            problems.append(f"{owner}: unknown research record id {record_id!r}")


def _check_path(root: Path, owner: str, value: str, problems: list[str]) -> Path:
    path = root / value
    if not path.is_file():
        problems.append(f"{owner}: missing artifact path {value!r}")
    return path


def _status_banner(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        prefix = "\n".join(path.read_text().splitlines()[:20])
    except OSError as exc:
        return None, str(exc)
    match = STATUS_RE.search(prefix)
    if match is None:
        return None, "missing mp-status JSON comment in first 20 lines"
    try:
        return json.loads(match.group(1)), None
    except json.JSONDecodeError as exc:
        return None, f"invalid mp-status JSON: {exc}"


def validate_registry_data(root: Path, model: dict[str, Any]) -> list[str]:
    """Return deterministic reconciliation problems for an already-loaded registry."""
    root = root.resolve()
    problems: list[str] = []
    if model.get("schemaVersion") != 1:
        problems.append("registry: schemaVersion must equal 1")
    for collection in REQUIRED_COLLECTIONS:
        if not isinstance(model.get(collection), list):
            problems.append(f"registry: {collection} must be a list")
    if problems:
        return sorted(problems)

    theorem_ids, research, authority_problems = _authority_ids(root)
    problems.extend(authority_problems)
    layer_ids = {entry.get("id") for entry in model["layers"] if isinstance(entry, dict)}

    all_ids: list[str] = []
    for collection in REQUIRED_COLLECTIONS:
        ids = [entry.get("id") for entry in model[collection] if isinstance(entry, dict)]
        for missing_index, entry_id in enumerate(ids):
            if not isinstance(entry_id, str) or not entry_id:
                problems.append(f"{collection}[{missing_index}]: non-empty string id required")
        for duplicate in _duplicates([entry_id for entry_id in ids if isinstance(entry_id, str)]):
            singular = {
                "layers": "layer",
                "terms": "term",
                "mechanisms": "mechanism",
                "claimBindings": "claim binding",
                "artifacts": "artifact",
            }[collection]
            problems.append(f"duplicate {singular} id {duplicate!r}")
        all_ids.extend(entry_id for entry_id in ids if isinstance(entry_id, str))
    for duplicate in _duplicates(all_ids):
        problems.append(f"id {duplicate!r} is reused across registry collections")

    labels = [entry.get("label", "").casefold() for entry in model["terms"]]
    for duplicate in _duplicates([label for label in labels if label]):
        problems.append(f"duplicate normative term label {duplicate!r}")

    for term in model["terms"]:
        owner = f"term {term.get('id', '<missing>')}"
        if term.get("layer") not in layer_ids:
            problems.append(f"{owner}: unknown layer {term.get('layer')!r}")
        for authority in term.get("authority", []):
            artifact = authority.get("artifact")
            if isinstance(artifact, str):
                _check_path(root, owner, artifact, problems)
            else:
                problems.append(f"{owner}: authority artifact must be a path")

    mechanism_ids = {entry.get("id") for entry in model["mechanisms"]}
    for mechanism in model["mechanisms"]:
        owner = f"mechanism {mechanism.get('id', '<missing>')}"
        if mechanism.get("layer") not in layer_ids:
            problems.append(f"{owner}: unknown layer {mechanism.get('layer')!r}")
        disposition = mechanism.get("disposition")
        if disposition not in DISPOSITIONS:
            problems.append(f"{owner}: unknown disposition {disposition!r}")
        replacement = mechanism.get("replacement")
        if replacement is not None and replacement not in mechanism_ids:
            problems.append(f"{owner}: unknown replacement {replacement!r}")
        _check_refs(
            owner=owner,
            entry=mechanism,
            theorem_ids=theorem_ids,
            research=research,
            problems=problems,
        )
        records = [research[record_id] for record_id in mechanism.get("researchRecords", [])
                   if record_id in research]
        if (disposition == "current" and not mechanism.get("theorems") and records
                and all(record.get("verdict") == "rejected" for record in records)):
            problems.append(f"{owner}: current mechanism is promoted by only rejected research records")
        for artifact in mechanism.get("artifacts", []):
            _check_path(root, owner, artifact, problems)
        for pin in mechanism.get("pins", []):
            manifest_rel = pin.get("manifest", "")
            pinned_rel = pin.get("path", "")
            manifest_path = _check_path(root, owner, manifest_rel, problems)
            pinned_path = root / pinned_rel
            if not manifest_path.is_file():
                continue
            try:
                manifest = _json(manifest_path)
                bound = manifest.get("files", {})
            except (OSError, TypeError, json.JSONDecodeError) as exc:
                problems.append(f"{owner}: cannot read manifest {manifest_rel!r}: {exc}")
                continue
            if pinned_rel not in bound:
                problems.append(f"{owner}: manifest {manifest_rel!r} does not bind {pinned_rel!r}")
                continue
            manifest_digest = bound[pinned_rel]
            declared_digest = pin.get("sha256")
            if declared_digest != manifest_digest:
                problems.append(
                    f"{owner}: declared digest for {pinned_rel!r} differs from manifest {manifest_rel!r}"
                )
            if not pinned_path.is_file():
                problems.append(f"{owner}: missing pinned artifact path {pinned_rel!r}")
            elif _digest(pinned_path) != manifest_digest:
                problems.append(
                    f"{owner}: working-tree digest for {pinned_rel!r} differs from manifest {manifest_rel!r}"
                )

    for binding in model["claimBindings"]:
        owner = f"claim binding {binding.get('id', '<missing>')}"
        _check_refs(
            owner=owner,
            entry=binding,
            theorem_ids=theorem_ids,
            research=research,
            problems=problems,
        )

    for artifact in model["artifacts"]:
        owner = f"artifact {artifact.get('id', '<missing>')}"
        artifact_class = artifact.get("class")
        if artifact_class not in ARTIFACT_CLASSES:
            problems.append(f"{owner}: unknown artifact class {artifact_class!r}")
        path_value = artifact.get("path", "")
        path = _check_path(root, owner, path_value, problems)
        _check_refs(
            owner=owner,
            entry=artifact,
            theorem_ids=theorem_ids,
            research=research,
            problems=problems,
        )
        if path.is_file() and artifact.get("statusBanner", True):
            banner, error = _status_banner(path)
            if error:
                problems.append(f"{owner}: status banner {error}")
            else:
                expected = {
                    "id": artifact.get("id"),
                    "class": artifact_class,
                    "asOf": artifact.get("asOf"),
                    "replacement": artifact.get("replacement"),
                    "immutable": artifact.get("immutable", False),
                }
                for key, expected_value in expected.items():
                    if banner.get(key) != expected_value:
                        problems.append(
                            f"{owner}: status banner {key!r} is {banner.get(key)!r}, "
                            f"registry requires {expected_value!r}"
                        )

    return sorted(set(problems))


def validate_repository(root: Path) -> list[str]:
    registry_path = root / "canon/model-registry.json"
    try:
        model = _json(registry_path)
    except (OSError, TypeError, json.JSONDecodeError) as exc:
        return [f"cannot load registry {registry_path}: {exc}"]
    return validate_registry_data(root, model)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    problems = validate_repository(root)
    if problems:
        print("Canonical model reconciliation FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    model = _json(root / "canon/model-registry.json")
    print(
        "Canonical model reconciled: "
        f"{len(model['terms'])} terms, {len(model['mechanisms'])} mechanisms, "
        f"{len(model['claimBindings'])} claim bindings, {len(model['artifacts'])} artifacts."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
