"""Append-only evidence graph with ancestry, side and proposition validation.

The validation in `EvidenceGraph.add` is not defensive programming. It is the
enforcement point for R2 (side separation) from PROVENANCE-REQUIREMENTS.md,
which every theorem in formal/PROOFS.md assumes and which nothing in this
codebase checked before 2026-08.

Formal correspondence (formal/lean/MinorityProphetCore/):
  a node with empty `copied_from`      -> a member of `rootSet`
  `roots(node_id)`                     -> `rootsOf`
  the invariant enforced by `add`      -> `SideConsistent`
  the invariant enforced by `acyclic`  -> `World.acyclic`

What this module does NOT do, and no theorem covers (see formal/CLAIM-SCOPE.md):
  * decide whether two distinct `node_id`s denote the same underlying
    observation. Root identity is supplied by the caller and is inside the
    trusted base.
  * detect that a claim entered without `copied_from` is in fact a copy. An
    undetected copy is indistinguishable from an original observation here, and
    is governed by the margin theorems, not by copy invariance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Protocol


class SideConsistencyError(ValueError):
    """A derivation edge whose endpoints assert opposite values.

    Rejecting this is R2. Lemma 1 (side-locality) fails without it, and its
    failure mode is not graceful: in every non-side-consistent world tested
    (44,450/44,450 at n<=6) the literal S_a places some root on BOTH sides, so
    the two "independent evidence counts" stop counting disjoint evidence.
    """


class PropositionMismatchError(ValueError):
    """A derivation edge between claims about different propositions.

    Every theorem is stated for a single proposition. The graph is global, so
    without this check subject substitution is unconstrained at the data layer.
    """


class CycleError(ValueError):
    """A derivation cycle. `rootsOf` is only well defined on a DAG."""


class RootAuthorizationError(ValueError):
    """A parentless claim was not minted by the configured root authority."""


class RootAuthority(Protocol):
    def active_roots(self) -> frozenset[str]: ...


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

    @property
    def is_root(self) -> bool:
        """True when no ancestry is recorded.

        WARNING: this means "no ancestry RECORDED", not "independently
        observed". The distinction is the entire undetected-copy threat.
        """
        return not self.copied_from


@dataclass(frozen=True)
class Violation:
    """A rejected-or-recorded integrity failure, kept for audit."""

    kind: str
    node_id: str
    parent_id: str
    detail: str


class EvidenceGraph:
    """Append-only evidence DAG.

    Acyclicity is structural: `add` requires every ancestor to exist already, so
    an edge can only ever point backwards in insertion order. `roots()` still
    carries an explicit cycle guard, because `to_dict`/`from_dict` and any
    future mutating API are paths that do not go through `add`.

    Parameters
    ----------
    strict:
        True (default) rejects R2 and proposition violations at ingest -- fail
        closed. False accepts them but records them in `violations`, so a
        pipeline that must ingest dirty data still fails LOUDLY rather than
        silently. `immunity_applicable` is False whenever violations exist, and
        no theorem in formal/PROOFS.md applies to such a graph.
    """

    def __init__(self, *, strict: bool = True, root_authority: RootAuthority | None = None) -> None:
        self._nodes: dict[str, EvidenceNode] = {}
        self._violations: list[Violation] = []
        self._strict = strict
        self._root_authority = root_authority

    # ------------------------------------------------------------------ ingest

    def add(self, node: EvidenceNode) -> None:
        if node.node_id in self._nodes:
            raise ValueError(f"duplicate node: {node.node_id}")

        missing = [parent for parent in node.copied_from if parent not in self._nodes]
        if missing:
            raise ValueError(f"unknown ancestors: {', '.join(missing)}")

        if node.is_root and self._root_authority is not None:
            if node.node_id not in self._root_authority.active_roots():
                raise RootAuthorizationError(
                    f"root {node.node_id!r} is not active in the configured authority"
                )

        for parent_id in node.copied_from:
            parent = self._nodes[parent_id]
            if parent.proposition_id != node.proposition_id:
                self._reject(
                    PropositionMismatchError,
                    Violation(
                        "proposition_mismatch",
                        node.node_id,
                        parent_id,
                        f"{node.proposition_id!r} derived from {parent.proposition_id!r}",
                    ),
                )
            if parent.value != node.value:
                self._reject(
                    SideConsistencyError,
                    Violation(
                        "side_inconsistent_edge",
                        node.node_id,
                        parent_id,
                        f"value {node.value} derived from value {parent.value}",
                    ),
                )

        self._nodes[node.node_id] = node

    def _reject(self, error: type[ValueError], violation: Violation) -> None:
        self._violations.append(violation)
        if self._strict:
            raise error(
                f"{violation.kind}: {violation.node_id} <- {violation.parent_id} "
                f"({violation.detail})"
            )

    # ------------------------------------------------------------------ queries

    @property
    def violations(self) -> tuple[Violation, ...]:
        return tuple(self._violations)

    @property
    def immunity_applicable(self) -> bool:
        """Whether the R2 precondition of Theorem 1 holds for this graph.

        False means the immunity theorem says nothing about this graph. It does
        not mean the verdict is wrong; it means there is no guarantee.
        """
        return not self._violations

    def roots(self, node_id: str) -> frozenset[str]:
        """Parentless ancestors of `node_id`. Memoised, cycle-guarded."""
        if node_id not in self._nodes:
            raise KeyError(node_id)
        cache: dict[str, frozenset[str]] = {}
        return self._roots(node_id, cache, ())

    def _roots(
        self, node_id: str, cache: dict[str, frozenset[str]], stack: tuple[str, ...]
    ) -> frozenset[str]:
        if node_id in cache:
            return cache[node_id]
        if node_id in stack:
            raise CycleError(
                "derivation cycle: " + " -> ".join(stack[stack.index(node_id) :] + (node_id,))
            )
        node = self._nodes[node_id]
        if node.is_root:
            result = frozenset({node_id})
        else:
            found: set[str] = set()
            for parent in node.copied_from:
                found |= self._roots(parent, cache, stack + (node_id,))
            result = frozenset(found)
        cache[node_id] = result
        return result

    def independent(self, left: str, right: str) -> bool:
        """No shared recorded ancestry.

        This is ALL-OR-NOTHING disjointness. Two claims sharing some but not all
        roots are reported as dependent. Graded independence is not modelled and
        no theorem covers it.
        """
        return self.roots(left).isdisjoint(self.roots(right))

    def root_set(self) -> frozenset[str]:
        """Every parentless claim in the graph (the `rootSet` of the theorems)."""
        return frozenset(nid for nid, node in self._nodes.items() if node.is_root)

    def nodes(self) -> tuple[EvidenceNode, ...]:
        return tuple(self._nodes.values())

    # ------------------------------------------------------------- (de)serialise

    def to_dict(self) -> dict[str, object]:
        return {
            "version": "0.2",
            "strict": self._strict,
            "nodes": [vars(node) for node in self._nodes.values()],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any], *, strict: bool = True) -> "EvidenceGraph":
        """Validating loader.

        Deserialisation previously had no counterpart to `add`, so a payload
        could reintroduce every invariant violation the ingest path rejects.
        This loader replays nodes through `add` in dependency order.
        """
        graph = cls(strict=strict)
        pending = {n["node_id"]: n for n in payload.get("nodes", [])}
        placed: set[str] = set()
        while pending:
            ready = [
                n
                for n in pending.values()
                if all(p in placed for p in tuple(n.get("copied_from", ()) or ()))
            ]
            if not ready:
                raise CycleError(
                    "unresolvable ancestry among: " + ", ".join(sorted(pending))
                )
            for raw in ready:
                graph.add(_node_from_raw(raw))
                placed.add(raw["node_id"])
                del pending[raw["node_id"]]
        return graph


def _node_from_raw(raw: dict[str, Any]) -> EvidenceNode:
    return EvidenceNode(
        node_id=raw["node_id"],
        proposition_id=raw["proposition_id"],
        value=bool(raw["value"]),
        observer_id=raw["observer_id"],
        source_id=raw["source_id"],
        confidence=float(raw["confidence"]),
        evidence=dict(raw.get("evidence") or {}),
        copied_from=tuple(raw.get("copied_from") or ()),
        transformations=tuple(raw.get("transformations") or ()),
        signature=raw.get("signature"),
        timestamp=raw["timestamp"],
    )


def build(nodes: Iterable[EvidenceNode], *, strict: bool = True) -> EvidenceGraph:
    """Convenience constructor; nodes must arrive in dependency order."""
    graph = EvidenceGraph(strict=strict)
    for node in nodes:
        graph.add(node)
    return graph
