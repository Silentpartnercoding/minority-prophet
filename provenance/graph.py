"""Minimal append-only evidence graph with ancestry validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class EvidenceNode:
    node_id: str
    proposition_id: str
    value: bool
    observer_id: str
    source_id: str
    confidence: float
    evidence: dict[str, Any]
    copied_from: tuple[str, ...] = ()
    transformations: tuple[str, ...] = ()
    signature: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if not self.observer_id or not self.source_id:
            raise ValueError("observer and source are required")


class EvidenceGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, EvidenceNode] = {}

    def add(self, node: EvidenceNode) -> None:
        if node.node_id in self._nodes:
            raise ValueError(f"duplicate node: {node.node_id}")
        missing = [parent for parent in node.copied_from if parent not in self._nodes]
        if missing:
            raise ValueError(f"unknown ancestors: {', '.join(missing)}")
        self._nodes[node.node_id] = node

    def roots(self, node_id: str) -> frozenset[str]:
        if node_id not in self._nodes:
            raise KeyError(node_id)
        node = self._nodes[node_id]
        if not node.copied_from:
            return frozenset({node_id})
        roots: set[str] = set()
        for parent in node.copied_from:
            roots.update(self.roots(parent))
        return frozenset(roots)

    def independent(self, left: str, right: str) -> bool:
        return self.roots(left).isdisjoint(self.roots(right))

    def to_dict(self) -> dict[str, object]:
        return {
            "version": "0.1",
            "nodes": [vars(node) for node in self._nodes.values()],
        }
