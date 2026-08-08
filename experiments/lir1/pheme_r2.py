"""Select and normalize the preregistered disjoint PHEME-R2 holdout."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from .model import ClaimInstance, read_jsonl, write_jsonl
from .pheme import parse_thread


def case_set_digest(case_ids: set[str]) -> str:
    payload = ("\n".join(sorted(case_ids)) + "\n").encode()
    return hashlib.sha256(payload).hexdigest()


def normalize_disjoint(
    source: Path, *, cap: int, exclude_case_ids: set[str]
) -> tuple[list[ClaimInstance], dict[str, Any]]:
    threads = sorted(
        (path for path in source.glob("*-all-rnr-threads/rumours/*") if path.is_dir()),
        key=lambda path: str(path),
    )
    selected: list[ClaimInstance] = []
    skipped_for_cap = missing_tweets = invalid_threads = 0
    truth_counts = {"true": 0, "false": 0, "unresolved": 0}
    for thread in threads:
        case_id = f"pheme:{thread.name}"
        if case_id in exclude_case_ids:
            continue
        if not (thread / "annotation.json").exists() or not (thread / "structure.json").exists():
            invalid_threads += 1
            continue
        claims, missing = parse_thread(thread)
        claims = [replace(claim, split="confirmatory") for claim in claims]
        if len(selected) + len(claims) > cap:
            skipped_for_cap += 1
            continue
        selected.extend(claims)
        missing_tweets += missing
        truth_counts[claims[0].content_truth] += 1

    selected_case_ids = {claim.case_id for claim in selected}
    summary = {
        "schema": "minority-prophet.lir1-pheme-r2-inventory.v1",
        "status": "disjoint-holdout-inventory",
        "claimBoundary": "Recorded PHEME reply-tree structure; not causal evidence independence.",
        "source": {
            "article": "https://figshare.com/articles/dataset/PHEME_dataset_for_Rumour_Detection_and_Veracity_Classification/6392078",
            "fileId": 11767817,
            "suppliedMd5": "11530d4c0c7127fc78bbc1e46f2498f8",
            "rawSha256": "079f6ffdbc0b367399262f101774372e5d19dd8278c33d6c97a84461a9bc58dd",
        },
        "cap": cap,
        "availableRumorThreads": len(threads),
        "excludedCases": len(exclude_case_ids),
        "excludedCaseSetSha256": case_set_digest(exclude_case_ids),
        "eligibleRumorThreads": len(threads) - len(exclude_case_ids),
        "selectedCases": len(selected_case_ids),
        "selectedCaseSetSha256": case_set_digest(selected_case_ids),
        "selectedClaims": len(selected),
        "recordedEdges": sum(bool(claim.observed_parents) for claim in selected),
        "recordedRoots": len({claim.true_root_id for claim in selected}),
        "missingTweetFiles": missing_tweets,
        "invalidThreads": invalid_threads,
        "threadsSkippedForCap": skipped_for_cap,
        "selectedCaseTruth": truth_counts,
        "normalizedJsonlSha256": None,
        "redistribution": "Normalized tweet text remains local because Twitter retains content rights.",
    }
    return selected, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--exclude-from", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--cap", type=int, default=5000)
    args = parser.parse_args()
    excluded = {claim.case_id for claim in read_jsonl(args.exclude_from)}
    claims, summary = normalize_disjoint(args.source, cap=args.cap, exclude_case_ids=excluded)
    write_jsonl(args.output, claims)
    summary["normalizedJsonlSha256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
