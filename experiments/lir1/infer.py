"""Transparent baseline for inferring record descent without label fields."""

from __future__ import annotations

import datetime as dt
import math
import re
from collections import defaultdict
from typing import Any, Iterable


TOKEN = re.compile(r"[a-z0-9]+")


def tokens(text: str | None) -> frozenset[str]:
    return frozenset(TOKEN.findall((text or "").lower()))


def jaccard(left: str | None, right: str | None) -> float:
    a, b = tokens(left), tokens(right)
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def timestamp_seconds(value: str | None) -> float | None:
    if value is None:
        return None
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def temporal_score(child: dict[str, Any], parent: dict[str, Any]) -> float:
    child_time, parent_time = timestamp_seconds(child["timestamp"]), timestamp_seconds(parent["timestamp"])
    if child_time is None or parent_time is None or parent_time >= child_time:
        return 0.0
    hours = (child_time - parent_time) / 3600.0
    return math.exp(-hours / 24.0)


def infer_parents(
    features: Iterable[dict[str, Any]], *, threshold: float = 0.58
) -> dict[str, str | None]:
    """Infer at most one parent per claim using only the feature projection."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for claim in features:
        grouped[(claim["dataset"], claim["case_id"])].append(claim)

    predictions: dict[str, str | None] = {}
    for claims in grouped.values():
        claims.sort(key=lambda item: (timestamp_seconds(item["timestamp"]) or float("-inf"), item["claim_id"]))
        seen: dict[str, dict[str, Any]] = {}
        for claim in claims:
            exposed = [parent for parent in claim["observed_parents"] if parent in seen]
            if exposed:
                predictions[claim["claim_id"]] = sorted(exposed)[0]
                seen[claim["claim_id"]] = claim
                continue

            best_parent: str | None = None
            best_score = -1.0
            child_tokens = tokens(claim["text"])
            for candidate_id, candidate in seen.items():
                if candidate["proposition_id"] != claim["proposition_id"]:
                    continue
                similarity = jaccard(claim["text"], candidate["text"])
                inherited_rare = len(
                    {token for token in child_tokens & tokens(candidate["text"]) if "marker" in token}
                )
                score = 0.82 * similarity + 0.16 * temporal_score(claim, candidate)
                score += min(0.02, inherited_rare * 0.02)
                if score > best_score or (score == best_score and candidate_id < (best_parent or "~")):
                    best_score, best_parent = score, candidate_id
            predictions[claim["claim_id"]] = best_parent if best_score >= threshold else None
            seen[claim["claim_id"]] = claim
    return predictions


def roots_from_parents(parents: dict[str, str | None]) -> dict[str, str]:
    roots: dict[str, str] = {}
    for claim_id in sorted(parents):
        path: list[str] = []
        current = claim_id
        while parents.get(current) is not None:
            if current in path:
                raise ValueError(f"predicted parent cycle includes {current}")
            path.append(current)
            current = parents[current]  # type: ignore[assignment]
        root = current
        roots[claim_id] = root
        for visited in path:
            roots[visited] = root
    return roots
