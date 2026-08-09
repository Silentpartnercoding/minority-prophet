"""Direct root grouping from observable claim features."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Any, Iterable

from experiments.lir1.infer import jaccard, temporal_score, timestamp_seconds


class UnionFind:
    def __init__(self, identifiers: Iterable[str]) -> None:
        self.parent = {identifier: identifier for identifier in identifiers}

    def find(self, identifier: str) -> str:
        while self.parent[identifier] != identifier:
            self.parent[identifier] = self.parent[self.parent[identifier]]
            identifier = self.parent[identifier]
        return identifier

    def union(self, left: str, right: str) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root == right_root:
            return
        first, second = sorted((left_root, right_root))
        self.parent[second] = first


def pair_score(left: dict[str, Any], right: dict[str, Any]) -> float:
    left_time = timestamp_seconds(left["timestamp"])
    right_time = timestamp_seconds(right["timestamp"])
    left_key = (left_time if left_time is not None else float("inf"), left["claim_id"])
    right_key = (right_time if right_time is not None else float("inf"), right["claim_id"])
    earlier, later = (left, right) if left_key <= right_key else (right, left)
    return 0.82 * jaccard(left["text"], right["text"]) + 0.16 * temporal_score(later, earlier)


def infer_roots(features: Iterable[dict[str, Any]], *, threshold: float) -> dict[str, str]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for feature in features:
        grouped[(feature["dataset"], feature["case_id"])].append(feature)
    roots: dict[str, str] = {}
    for rows in grouped.values():
        by_id = {row["claim_id"]: row for row in rows}
        forest = UnionFind(by_id)
        for row in rows:
            for parent in row["observed_parents"]:
                if parent in by_id:
                    forest.union(row["claim_id"], parent)
        for left, right in combinations(rows, 2):
            if left["proposition_id"] != right["proposition_id"]:
                continue
            if pair_score(left, right) >= threshold:
                forest.union(left["claim_id"], right["claim_id"])
        components: dict[str, list[str]] = defaultdict(list)
        for identifier in by_id:
            components[forest.find(identifier)].append(identifier)
        for identifiers in components.values():
            canonical = min(identifiers)
            for identifier in identifiers:
                roots[identifier] = canonical
    return roots

