"""Materialize disjoint PHEME splits with observable provenance features."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from experiments.lir1.model import ClaimInstance, read_jsonl, write_jsonl
from experiments.lir1.pheme import flatten_tree, parse_timestamp, truth_label, tweet_path
from experiments.lir1.pheme_r2 import case_set_digest


SPLIT_SALT = "minority-prophet-lir3-pheme-split-v1"
DEVELOPMENT_PERCENT = 25


def _author_id(tweet: dict[str, Any]) -> str | None:
    identifier = (tweet.get("user") or {}).get("id_str")
    return f"twitter:{identifier}" if identifier else None


def _entities(tweet: dict[str, Any]) -> dict[str, Any]:
    value = tweet.get("entities")
    return value if isinstance(value, dict) else {}


def _domains(tweet: dict[str, Any]) -> list[str]:
    domains: set[str] = set()
    for row in _entities(tweet).get("urls") or []:
        raw = row.get("expanded_url") or row.get("url")
        if not raw:
            continue
        host = (urlsplit(raw).hostname or "").lower().removeprefix("www.")
        if host:
            domains.add(host)
    return sorted(domains)


def _mentions(tweet: dict[str, Any]) -> list[str]:
    identifiers = {
        f"twitter:{row['id_str']}"
        for row in (_entities(tweet).get("user_mentions") or [])
        if row.get("id_str")
    }
    return sorted(identifiers)


def _hashtags(tweet: dict[str, Any]) -> list[str]:
    return sorted(
        {
            str(row["text"]).casefold()
            for row in (_entities(tweet).get("hashtags") or [])
            if row.get("text")
        }
    )


def parse_rich_thread(thread: Path, *, split: str) -> tuple[list[ClaimInstance], int]:
    """Parse labels plus provenance; never copy the exact parent into metadata."""
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
        reply_author = tweet.get("in_reply_to_user_id_str")
        claims.append(
            ClaimInstance(
                dataset="pheme_veracity_v1",
                case_id=f"pheme:{case_root_id}",
                claim_id=f"tweet:{tweet_id}",
                proposition_id=f"pheme-rumor:{case_root_id}",
                text=tweet.get("text"),
                timestamp=parse_timestamp(tweet.get("created_at")),
                author_id=_author_id(tweet),
                observed_parents=(f"tweet:{parent}",) if parent else (),
                content_truth=truth_label(annotation),
                independence_label="unknown",
                true_root_id=f"tweet:{component_root}",
                label_basis="explicit_edge",
                label_scope="record_root",
                split=split,
                channel_metadata={
                    "event": event,
                    "platform_relation": "reply_tree",
                    "reply_target_author_id": (
                        f"twitter:{reply_author}" if reply_author else None
                    ),
                    "mentioned_author_ids": _mentions(tweet),
                    "url_domains": _domains(tweet),
                    "hashtags": _hashtags(tweet),
                },
            )
        )
    return claims, missing


def split_for_case(case_id: str) -> str:
    digest = hashlib.sha256(f"{SPLIT_SALT}|{case_id}".encode()).digest()
    bucket = int.from_bytes(digest[:8], "big") % 100
    return "development" if bucket < DEVELOPMENT_PERCENT else "confirmatory"


def selection_key(case_id: str) -> str:
    return hashlib.sha256(f"{SPLIT_SALT}|selection|{case_id}".encode()).hexdigest()


def _select(
    threads: list[Path], *, split: str, cap: int
) -> tuple[list[ClaimInstance], dict[str, int]]:
    selected: list[ClaimInstance] = []
    missing_threads = invalid_threads = skipped_for_cap = 0
    ordered = sorted(threads, key=lambda path: selection_key(f"pheme:{path.name}"))
    for thread in ordered:
        if split_for_case(f"pheme:{thread.name}") != split:
            continue
        if not (thread / "annotation.json").exists() or not (thread / "structure.json").exists():
            invalid_threads += 1
            continue
        claims, missing = parse_rich_thread(thread, split=split)
        if missing:
            missing_threads += 1
            continue
        if len(selected) + len(claims) > cap:
            skipped_for_cap += 1
            continue
        selected.extend(claims)
    return selected, {
        "invalidThreads": invalid_threads,
        "threadsExcludedMissingTweets": missing_threads,
        "threadsSkippedForCap": skipped_for_cap,
    }


def materialize(
    source: Path,
    exclude_paths: list[Path],
    development_output: Path,
    confirmatory_output: Path,
    *,
    cap: int,
) -> dict[str, Any]:
    excluded = {
        claim.case_id for path in exclude_paths for claim in read_jsonl(path)
    }
    threads = [
        path
        for path in source.glob("*-all-rnr-threads/rumours/*")
        if path.is_dir() and f"pheme:{path.name}" not in excluded
    ]
    development, development_notes = _select(threads, split="development", cap=cap)
    confirmatory, confirmatory_notes = _select(threads, split="confirmatory", cap=cap)
    write_jsonl(development_output, development)
    write_jsonl(confirmatory_output, confirmatory)
    split_rows: dict[str, dict[str, Any]] = {}
    for name, rows, path, notes in (
        ("development", development, development_output, development_notes),
        ("confirmatory", confirmatory, confirmatory_output, confirmatory_notes),
    ):
        case_ids = {row.case_id for row in rows}
        split_rows[name] = {
            "cases": len(case_ids),
            "claims": len(rows),
            "recordedEdges": sum(bool(row.observed_parents) for row in rows),
            "recordedRoots": len({row.true_root_id for row in rows}),
            "caseSetSha256": case_set_digest(case_ids),
            "normalizedJsonlSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            **notes,
        }
    overlap = {
        row.case_id for row in development
    } & {row.case_id for row in confirmatory}
    if overlap:
        raise RuntimeError("development and confirmatory cases overlap")
    return {
        "schema": "minority-prophet.lir3-pheme-inventory.v1",
        "status": "sealed-disjoint-splits",
        "splitSaltSha256": hashlib.sha256(SPLIT_SALT.encode()).hexdigest(),
        "developmentPercent": DEVELOPMENT_PERCENT,
        "capPerSplit": cap,
        "availableUnusedThreadDirectories": len(threads),
        "excludedPriorCases": len(excluded),
        "excludedPriorCaseSetSha256": case_set_digest(excluded),
        "splits": split_rows,
        "caseOverlap": 0,
        "rawArchiveSha256": "079f6ffdbc0b367399262f101774372e5d19dd8278c33d6c97a84461a9bc58dd",
        "labelBoundary": "Recorded PHEME reply-tree roots; not causal evidence independence.",
        "redistribution": "Tweet text, author identifiers, and normalized rows remain local.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--exclude-from", required=True, nargs="+", type=Path)
    parser.add_argument("--development-output", required=True, type=Path)
    parser.add_argument("--confirmatory-output", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--cap", type=int, default=5000)
    args = parser.parse_args()
    inventory = materialize(
        args.source,
        args.exclude_from,
        args.development_output,
        args.confirmatory_output,
        cap=args.cap,
    )
    args.inventory.parent.mkdir(parents=True, exist_ok=True)
    args.inventory.write_text(json.dumps(inventory, sort_keys=True, indent=2) + "\n")
    print(json.dumps(inventory["splits"], sort_keys=True))


if __name__ == "__main__":
    main()
