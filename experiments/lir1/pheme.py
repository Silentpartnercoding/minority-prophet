"""Normalize the locally acquired PHEME rumor corpus without publishing tweet text."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator

from .model import ClaimInstance, write_jsonl
from .synthetic_fixture import split_for


def flatten_tree(
    tree: dict[str, Any], parent: str | None = None, component_root: str | None = None
) -> Iterator[tuple[str, str | None, str]]:
    for node, children in tree.items():
        root = component_root or node
        yield node, parent, root
        if children == []:
            continue
        if not isinstance(children, dict):
            raise ValueError(f"children for {node} are not an object")
        yield from flatten_tree(children, node, root)


def parse_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    parsed = dt.datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")
    return parsed.isoformat()


def truth_label(annotation: dict[str, Any]) -> str:
    value = annotation.get("true")
    if str(value) == "1":
        return "true"
    if str(value) == "0":
        return "false"
    return "unresolved"


def tweet_path(thread: Path, tweet_id: str, root_id: str) -> Path:
    directory = "source-tweets" if tweet_id == root_id else "reactions"
    return thread / directory / f"{tweet_id}.json"


def parse_thread(thread: Path) -> tuple[list[ClaimInstance], int]:
    annotation = json.loads((thread / "annotation.json").read_text())
    structure = json.loads((thread / "structure.json").read_text())
    if not structure:
        raise ValueError(f"{thread}: empty platform structure")
    case_root_id = thread.name
    event = thread.parents[1].name.removesuffix("-all-rnr-threads")
    missing = 0
    claims: list[ClaimInstance] = []
    for tweet_id, parent, component_root in flatten_tree(structure):
        path = tweet_path(thread, tweet_id, case_root_id)
        if not path.exists():
            missing += 1
            continue
        tweet = json.loads(path.read_text())
        claims.append(ClaimInstance(
            dataset="pheme_veracity_v1",
            case_id=f"pheme:{case_root_id}",
            claim_id=f"tweet:{tweet_id}",
            proposition_id=f"pheme-rumor:{case_root_id}",
            text=tweet.get("text"),
            timestamp=parse_timestamp(tweet.get("created_at")),
            author_id=f"twitter:{tweet.get('user', {}).get('id_str')}" if tweet.get("user") else None,
            observed_parents=(f"tweet:{parent}",) if parent else (),
            content_truth=truth_label(annotation),
            independence_label="unknown",
            true_root_id=f"tweet:{component_root}",
            label_basis="explicit_edge",
            label_scope="record_root",
            split=split_for(f"pheme:{case_root_id}", "pheme_veracity_v1"),
            channel_metadata={"event": event, "platform_relation": "reply_tree"},
        ))
    return claims, missing


def normalize(source: Path, *, cap: int) -> tuple[list[ClaimInstance], dict[str, Any]]:
    threads = sorted(
        (path for path in source.glob("*-all-rnr-threads/rumours/*") if path.is_dir()),
        key=lambda path: str(path),
    )
    selected: list[ClaimInstance] = []
    missing_tweets = skipped_for_cap = invalid_threads = 0
    truth_counts = {"true": 0, "false": 0, "unresolved": 0}
    selected_cases = 0
    for thread in threads:
        if not (thread / "annotation.json").exists() or not (thread / "structure.json").exists():
            invalid_threads += 1
            continue
        claims, missing = parse_thread(thread)
        if len(selected) + len(claims) > cap:
            skipped_for_cap += 1
            continue
        selected.extend(claims)
        missing_tweets += missing
        selected_cases += 1
        truth_counts[claims[0].content_truth] += 1
    edge_count = sum(bool(claim.observed_parents) for claim in selected)
    split_claims = {
        split: sum(claim.split == split for claim in selected)
        for split in ("development", "confirmatory")
    }
    split_cases = {
        split: len({claim.case_id for claim in selected if claim.split == split})
        for split in ("development", "confirmatory")
    }
    summary = {
        "schema": "minority-prophet.lir1-pheme-inventory.v1",
        "status": "development-acquisition-inventory",
        "claimBoundary": "Recorded PHEME reply-tree structure; not causal evidence independence.",
        "source": {
            "article": "https://figshare.com/articles/dataset/PHEME_dataset_for_Rumour_Detection_and_Veracity_Classification/6392078",
            "fileId": 11767817,
            "suppliedMd5": "11530d4c0c7127fc78bbc1e46f2498f8",
            "rawSha256": "079f6ffdbc0b367399262f101774372e5d19dd8278c33d6c97a84461a9bc58dd"
        },
        "cap": cap,
        "availableRumorThreads": len(threads),
        "selectedCases": selected_cases,
        "selectedClaims": len(selected),
        "recordedEdges": edge_count,
        "recordedRoots": len({claim.true_root_id for claim in selected}),
        "splitClaims": split_claims,
        "splitCases": split_cases,
        "missingTweetFiles": missing_tweets,
        "invalidThreads": invalid_threads,
        "threadsSkippedForCap": skipped_for_cap,
        "selectedCaseTruth": truth_counts,
        "normalizedJsonlSha256": None,
        "redistribution": "Normalized tweet text remains local because Twitter retains content rights."
    }
    return selected, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--cap", type=int, default=5000)
    args = parser.parse_args()
    claims, summary = normalize(args.source, cap=args.cap)
    write_jsonl(args.output, claims)
    summary["normalizedJsonlSha256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
