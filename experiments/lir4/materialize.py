"""Seal a final PHEME holdout unused by LIR-1 through LIR-3."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from experiments.lir1.model import read_jsonl, write_jsonl
from experiments.lir1.pheme_r2 import case_set_digest
from experiments.lir3.pheme_provenance import parse_rich_thread


SELECTION_SALT = "minority-prophet-lir4-degradation-holdout-v1"


def selection_key(case_id: str) -> str:
    return hashlib.sha256(f"{SELECTION_SALT}|{case_id}".encode()).hexdigest()


def materialize(
    source: Path, exclude_paths: list[Path], output: Path, *, cap: int
) -> dict[str, Any]:
    excluded = {claim.case_id for path in exclude_paths for claim in read_jsonl(path)}
    threads = sorted(
        (
            path
            for path in source.glob("*-all-rnr-threads/rumours/*")
            if path.is_dir() and f"pheme:{path.name}" not in excluded
        ),
        key=lambda path: selection_key(f"pheme:{path.name}"),
    )
    selected = []
    missing_threads = invalid_threads = skipped_for_cap = 0
    for thread in threads:
        if not (thread / "annotation.json").exists() or not (thread / "structure.json").exists():
            invalid_threads += 1
            continue
        claims, missing = parse_rich_thread(thread, split="confirmatory")
        if missing:
            missing_threads += 1
            continue
        if len(selected) + len(claims) > cap:
            skipped_for_cap += 1
            continue
        selected.extend(claims)
    write_jsonl(output, selected)
    case_ids = {claim.case_id for claim in selected}
    roots_by_case: dict[str, set[str | None]] = defaultdict(set)
    for claim in selected:
        roots_by_case[claim.case_id].add(claim.true_root_id)
    return {
        "schema": "minority-prophet.lir4-pheme-inventory.v1",
        "status": "sealed-final-unused-holdout",
        "cap": cap,
        "availableRemainingThreadDirectories": len(threads),
        "excludedPriorCases": len(excluded),
        "excludedPriorCaseSetSha256": case_set_digest(excluded),
        "selectedCases": len(case_ids),
        "selectedClaims": len(selected),
        "recordedEdges": sum(bool(claim.observed_parents) for claim in selected),
        "recordedRoots": len({claim.true_root_id for claim in selected}),
        "multiRootCases": sum(len(roots) > 1 for roots in roots_by_case.values()),
        "selectedCaseSetSha256": case_set_digest(case_ids),
        "normalizedJsonlSha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "selectionSaltSha256": hashlib.sha256(SELECTION_SALT.encode()).hexdigest(),
        "invalidThreads": invalid_threads,
        "threadsExcludedMissingTweets": missing_threads,
        "threadsSkippedForCap": skipped_for_cap,
        "rawArchiveSha256": "079f6ffdbc0b367399262f101774372e5d19dd8278c33d6c97a84461a9bc58dd",
        "labelBoundary": "Recorded PHEME reply-tree roots; not causal evidence independence.",
        "redistribution": "Tweet text, author identifiers, and normalized rows remain local.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--exclude-from", required=True, nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--cap", type=int, default=5000)
    args = parser.parse_args()
    inventory = materialize(args.source, args.exclude_from, args.output, cap=args.cap)
    args.inventory.parent.mkdir(parents=True, exist_ok=True)
    args.inventory.write_text(json.dumps(inventory, sort_keys=True, indent=2) + "\n")
    print(json.dumps(inventory, sort_keys=True))


if __name__ == "__main__":
    main()
