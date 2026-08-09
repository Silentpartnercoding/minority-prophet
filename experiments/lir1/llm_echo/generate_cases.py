"""Build sealed fictional cases for the registered LIR-1E experiment.

The generated material belongs under the Git-ignored artifacts boundary. The
command prints an inventory that commits to every output without printing the
seed or any label value.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import secrets
from pathlib import Path
from typing import Any, Iterable


SCHEMA_REQUEST = "minority-prophet.lir1e-request.v1"
SCHEMA_LABEL = "minority-prophet.lir1e-construction-label.v1"
SCHEMA_INVENTORY = "minority-prophet.lir1e-sealed-inventory.v1"
COUNTS = {"development": 12, "confirmatory": 36}
PRIVATE_KEYS = {
    "constructedTruth", "expectedAnswer", "sourcePolarity", "trueRootId",
    "directParent", "transformationId", "generatorSeed",
}
MUTATIONS = (
    "clause-reorder",
    "synonym-map",
    "wrapper-addition",
    "explanation-truncation",
    "punctuation-normalization",
    "synonym-and-wrapper",
)

_ADJECTIVES = (
    "amber", "brisk", "cobalt", "dappled", "ember", "fallow", "gentle",
    "hollow", "indigo", "jasper", "kindled", "lunar", "mellow", "narrow",
    "opal", "pearl", "quiet", "russet", "silver", "tidal", "umber",
    "velvet", "willow", "xenic", "young", "zephyr",
)
_NOUNS = (
    "archive", "beacon", "cairn", "delta", "estuary", "fountain", "grove",
    "harbor", "island", "junction", "keystone", "lantern", "meadow", "nexus",
    "orchard", "prairie", "quarry", "ridge", "sanctum", "terrace", "upland",
    "valley", "waypoint", "yard", "zenith",
)
_SOURCE_TEMPLATES = (
    "Field card {card} records that {entity}'s assigned signal is {value}.",
    "In registry leaf {card}, the signal paired with {entity} is written as {value}.",
    "Observer note {card} lists {value} beside the fictional site {entity}.",
    "The synthetic dispatch numbered {card} assigns {entity} the signal {value}.",
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rng(seed: bytes, split: str) -> random.Random:
    material = hashlib.sha256(seed + b"|" + split.encode()).digest()
    return random.Random(int.from_bytes(material, "big"))


def _token(rng: random.Random, prefix: str) -> str:
    return f"{prefix}-{rng.getrandbits(52):013x}"


def _write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        for record in records:
            handle.write(canonical(record))


def build(seed: bytes, split: str, count: int | None = None) -> tuple[list[dict], list[dict]]:
    if len(seed) < 32:
        raise ValueError("seed must contain at least 32 bytes")
    if split not in COUNTS:
        raise ValueError(f"unsupported split: {split}")
    expected = COUNTS[split]
    if count is not None and count != expected:
        raise ValueError(f"{split} count is frozen at {expected}")

    rng = _rng(seed, split)
    prompt = (Path(__file__).with_name("PROMPT.txt").read_text(encoding="utf-8").strip())
    requests: list[dict] = []
    labels: list[dict] = []

    for number in range(expected):
        case_id = f"lir1e-{split[:4]}-{number:03d}-{_token(rng, 'c')[-6:]}"
        entity = f"{rng.choice(_ADJECTIVES).title()} {rng.choice(_NOUNS).title()} {_token(rng, 'E')[-5:]}"
        truth = _token(rng, "sigil")
        falsehood = _token(rng, "sigil")
        while falsehood == truth:
            falsehood = _token(rng, "sigil")
        question = f"What signal token is assigned to {entity}?"

        packets: list[dict[str, str]] = []
        for packet_number, value in enumerate((truth, truth, truth, falsehood)):
            source_id = f"{case_id}-source-{packet_number}"
            source = _SOURCE_TEMPLATES[packet_number].format(
                card=_token(rng, "card"), entity=entity, value=value
            )
            packets.append({
                "sourceId": source_id,
                "sourcePacket": source,
                "sourceSha256": digest(source.encode()),
                "value": value,
                "polarity": "constructed-true" if value == truth else "constructed-false",
            })

        rng.shuffle(packets)
        true_packets = [p for p in packets if p["value"] == truth]
        false_packet = next(p for p in packets if p["value"] == falsehood)
        roles = (
            ("role-0", true_packets[0], "same_model_disjoint", "model-a"),
            ("role-1", true_packets[1], "same_model_disjoint", "model-a"),
            ("role-2", true_packets[2], "different_family_disjoint", "model-b"),
            ("role-3", false_packet, "same_model_same_source", "model-a"),
            ("role-4", false_packet, "same_model_same_source", "model-a"),
        )

        model_ids: list[str] = []
        for role_id, packet, cell, model_slot in roles:
            request_id = f"{case_id}-{role_id}"
            model_ids.append(request_id)
            requests.append({
                "schema": SCHEMA_REQUEST,
                "caseId": case_id,
                "split": split,
                "roleId": role_id,
                "requestId": request_id,
                "assignmentCell": cell,
                "modelSlot": model_slot,
                "sourceId": packet["sourceId"],
                "sourceSha256": packet["sourceSha256"],
                "question": question,
                "sourcePacket": packet["sourcePacket"],
                "prompt": prompt,
                "parameters": {"temperature": 0, "tools": False, "web": False, "memory": False},
            })
            labels.append({
                "schema": SCHEMA_LABEL,
                "caseId": case_id,
                "recordId": request_id,
                "recordKind": "model-response",
                "constructedTruth": truth,
                "expectedAnswer": packet["value"],
                "sourcePolarity": packet["polarity"],
                "trueRootId": packet["sourceId"],
                "directParent": None,
                "transformationId": None,
            })

        copy_id = f"{case_id}-exact-copy"
        labels.append({
            "schema": SCHEMA_LABEL,
            "caseId": case_id,
            "recordId": copy_id,
            "recordKind": "programmatic-copy",
            "constructedTruth": truth,
            "expectedAnswer": falsehood,
            "sourcePolarity": "constructed-false",
            "trueRootId": false_packet["sourceId"],
            "directParent": model_ids[3],
            "transformationId": "exact-copy",
        })
        for index, transformation in enumerate(MUTATIONS):
            labels.append({
                "schema": SCHEMA_LABEL,
                "caseId": case_id,
                "recordId": f"{case_id}-mutation-{index}",
                "recordKind": "programmatic-mutation",
                "constructedTruth": truth,
                "expectedAnswer": falsehood,
                "sourcePolarity": "constructed-false",
                "trueRootId": false_packet["sourceId"],
                "directParent": copy_id,
                "transformationId": transformation,
            })

    return requests, labels


def assert_boundary(requests: list[dict], labels: list[dict]) -> None:
    public_text = b"".join(canonical(record) for record in requests).decode()
    for key in PRIVATE_KEYS:
        if f'"{key}"' in public_text:
            raise ValueError(f"private key leaked into request view: {key}")
    request_ids = {record["requestId"] for record in requests}
    if len(request_ids) != len(requests):
        raise ValueError("request IDs are not unique")
    label_ids = {record["recordId"] for record in labels}
    if len(label_ids) != len(labels):
        raise ValueError("label record IDs are not unique")


def prepare(seed_path: Path, split: str, output: Path) -> dict[str, Any]:
    seed = seed_path.read_bytes()
    requests, labels = build(seed, split)
    assert_boundary(requests, labels)

    output.mkdir(parents=True, exist_ok=True)
    os.chmod(output, 0o700)
    public_path = output / "requests.jsonl"
    sealed_path = output / "construction-labels.jsonl"
    _write_jsonl(public_path, requests)
    _write_jsonl(sealed_path, labels)
    os.chmod(sealed_path, 0o600)

    root = Path(__file__).resolve().parents[3]
    files = {
        "requests.jsonl": digest(public_path.read_bytes()),
        "construction-labels.jsonl": digest(sealed_path.read_bytes()),
    }
    inventory = {
        "schema": SCHEMA_INVENTORY,
        "split": split,
        "caseCount": COUNTS[split],
        "requestCount": len(requests),
        "plannedRecordCount": len(labels),
        "seedSha256": digest(seed),
        "protocolSha256": digest((Path(__file__).with_name("PREREGISTRATION.md")).read_bytes()),
        "generatorSha256": digest(Path(__file__).read_bytes()),
        "promptSha256": digest(Path(__file__).with_name("PROMPT.txt").read_bytes()),
        "files": files,
    }
    inventory_path = output / "inventory.json"
    inventory_path.write_bytes(canonical(inventory))
    os.chmod(inventory_path, 0o600)
    return inventory


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    seed_parser = subparsers.add_parser("new-seed", help="create a private 256-bit seed")
    seed_parser.add_argument("path", type=Path)
    prepare_parser = subparsers.add_parser("prepare", help="build one frozen split")
    prepare_parser.add_argument("--seed-file", required=True, type=Path)
    prepare_parser.add_argument("--split", required=True, choices=tuple(COUNTS))
    prepare_parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.command == "new-seed":
        args.path.parent.mkdir(parents=True, exist_ok=True)
        if args.path.exists():
            raise SystemExit(f"refusing to overwrite seed: {args.path}")
        args.path.write_bytes(secrets.token_bytes(32))
        os.chmod(args.path, 0o600)
        print(json.dumps({"seedSha256": digest(args.path.read_bytes())}, sort_keys=True))
        return

    inventory = prepare(args.seed_file, args.split, args.output)
    print(json.dumps(inventory, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
