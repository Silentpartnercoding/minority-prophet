#!/usr/bin/env python3
"""Run fixed baselines and the pinned canonical Minority Prophet root vote.

The runner imports repository-native files only after verifying that their
bytes still match the pinned canonical commit. It does not reimplement or
approximate Minority Prophet here.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace


PINNED_COMMIT = "41911af5b372dbeec8513581d6970abcda4dd166"
ROOT_VOTE_SHA256 = "74ccf33aafc6de3281dee253558934a47f338e254c6a2e4b322556ff0db4328e"
BASELINES_SHA256 = "c80ea6579d7bbe6061dd73b1d03666c175241d80eac38447aca11c0e3d34e3dd"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_canonical_repo(repo: Path) -> dict[str, str]:
    root_vote = repo / "aggregation" / "root_vote.py"
    baselines = repo / "experiments" / "exp008_shootout.py"
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True
    ).strip()
    observed = {"root_vote": sha256(root_vote), "baselines": sha256(baselines)}
    subprocess.run(
        ["git", "cat-file", "-e", f"{PINNED_COMMIT}^{{commit}}"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    if observed != {"root_vote": ROOT_VOTE_SHA256, "baselines": BASELINES_SHA256}:
        raise RuntimeError(f"canonical source hash mismatch: {observed}")
    return {"commit": PINNED_COMMIT, "checkout_commit": head, **observed}


def map_binary(values: list[int]) -> list[str]:
    return ["A" if value else "B" for value in values]


def head_majority(records: list[dict], propositions: int) -> list[str]:
    answers: list[str] = []
    for proposition in range(propositions):
        a = sum(record["answers"][proposition] == "A" for record in records)
        b = len(records) - a
        answers.append("ABSTAIN" if a == b else ("A" if a > b else "B"))
    return answers


def confidence_weighted(records: list[dict], propositions: int) -> list[str]:
    answers: list[str] = []
    for proposition in range(propositions):
        a = sum(record["confidence"] for record in records if record["answers"][proposition] == "A")
        b = sum(record["confidence"] for record in records if record["answers"][proposition] == "B")
        answers.append("ABSTAIN" if a == b else ("A" if a > b else "B"))
    return answers


def run_case(packet: dict, root_vote, baseline_module) -> dict:
    records = packet["records"]
    propositions = len(packet["proposition_ids"])
    # The archived reference baselines expose their task count as module-level K.
    # Set it to this frozen packet's task count before invoking them.
    baseline_module.K = propositions
    by_id = {record["record_id"]: record for record in records}
    roots: dict[str, str] = {}

    def resolve_root(record_id: str, visiting: frozenset[str] = frozenset()) -> str:
        if record_id in roots:
            return roots[record_id]
        if record_id in visiting:
            raise RuntimeError(f"cycle in fixed lineage at {record_id}")
        record = by_id.get(record_id)
        if record is None:
            raise RuntimeError(f"missing fixed lineage parent {record_id}")
        parent = record["parent_record_id"]
        root = record_id if parent is None else resolve_root(parent, visiting | {record_id})
        roots[record_id] = root
        return root

    index_by_id = {record["record_id"]: index for index, record in enumerate(records)}
    source_rows = [
        {
            "id": index,
            "t": float(record["sequence"]),
            "ans": [1 if answer == "A" else 0 for answer in record["answers"]],
            "cite": None if record["parent_record_id"] is None else index_by_id[record["parent_record_id"]],
        }
        for index, record in enumerate(records)
    ]

    methods = {
        "standard_head_majority": lambda: head_majority(records, propositions),
        "standard_confidence_weighted": lambda: confidence_weighted(records, propositions),
        "standard_dawid_skene": lambda: map_binary(baseline_module.dawid_skene(source_rows)),
        "standard_truthfinder": lambda: map_binary(baseline_module.truthfinder(source_rows)),
        "standard_accu_lite": lambda: map_binary(baseline_module.accu_lite(source_rows)),
        "standard_cluster_vote": lambda: map_binary(baseline_module.cluster_vote(source_rows)),
    }

    def canonical_root_vote() -> list[str]:
        output: list[str] = []
        for proposition in range(propositions):
            claims = [
                SimpleNamespace(
                    root_id=resolve_root(record["record_id"]),
                    value=record["answers"][proposition] == "A",
                )
                for record in records
            ]
            result = root_vote.verdict(claims, unattributed_policy="abstain_if_decisive")
            output.append(
                "A" if result.verdict.value == "true" else
                "B" if result.verdict.value == "false" else
                "ABSTAIN"
            )
        return output

    methods["minority_prophet_root_vote"] = canonical_root_vote
    results = {}
    for name, function in methods.items():
        started = time.perf_counter_ns()
        answers = function()
        results[name] = {
            "answers": answers,
            "elapsed_ns": time.perf_counter_ns() - started,
        }
    return {"case_id": packet["case_id"], "packet_hash": packet["packet_hash"], "methods": results}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--canonical-repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    provenance = verify_canonical_repo(args.canonical_repo)
    root_vote = load_module("pinned_root_vote", args.canonical_repo / "aggregation" / "root_vote.py")
    baselines = load_module("pinned_exp008", args.canonical_repo / "experiments" / "exp008_shootout.py")
    packets = json.loads(args.input.read_text())
    print(json.dumps({
        "canonical_provenance": provenance,
        "cases": [run_case(packet, root_vote, baselines) for packet in packets],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
