"""Append-only evidence graph with ancestry, side and proposition validation.

The validation in `EvidenceGraph.add` is not defensive programming. It is the
enforcement point for R2 (side separation) from PROVENANCE-REQUIREMENTS.md,
which every theorem in formal/PROOFS.md assumes and which nothing in this
codebase checked before 2026-08.

Formal correspondence (formal/lean/MinorityProphetCore/):
  a node with empty `copied_from` AND empty `read_from` -> a member of `rootSet`
  `roots(node_id)` walks `copied_from` and materialized `read_from` parents
                                           -> `rootsOf`
  the invariant enforced by `add`          -> `SideConsistent`
  the invariant enforced by `acyclic`      -> `World.acyclic`

Lean has no `read_from`. This module materialises each cited source as a
parentless `source:{canonical}` node so the DAG Lean sees is still parent
edges. `_roots()` must walk those edges. Updating `is_root` without updating
the walk inverts `independent()`.

What this module does NOT do, and no theorem covers (see formal/CLAIM-SCOPE.md):
  * decide whether two distinct `node_id`s denote the same underlying
    observation. Root identity is supplied by the caller and is inside the
    trusted base.
  * detect that a claim entered without `copied_from` is in fact a copy. An
    undetected copy is indistinguishable from an original observation here, and
    is governed by the margin theorems, not by copy invariance.
"""

from __future__ import annotations

import re
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


_RESOLVABLE_FORMS: tuple[tuple[str, "re.Pattern[str]"], ...] = (
    ("doi", re.compile(r"^(https?://(dx\.)?doi\.org/)?10\.\d{4,9}/\S+$", re.I)),
    ("url", re.compile(r"^https?://\S+\.\S+", re.I)),
    ("hash", re.compile(r"^[0-9a-f]{32,128}$", re.I)),
    ("arxiv", re.compile(r"^(arxiv:)?\d{4}\.\d{4,5}(v\d+)?$", re.I)),
    ("urn", re.compile(r"^urn:[a-z0-9][a-z0-9-]{0,31}:\S+$", re.I)),
)


WARRANT_KEY = "claim_warrant"

_DOI_PREFIX = re.compile(
    r"^(?:https?://(?:dx\.)?doi\.org/|doi:)?(10\.\d{4,9}/\S+)$", re.I
)
_ARXIV = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5}(?:v\d+)?)$", re.I)
_URL = re.compile(r"^(https?://)([^/]+)(/.*)?$", re.I)


def canonical_reference(reference: str) -> str:
    """One identity per cited object, so DOI aliases collapse to one source node.

    Shape only: this does not check that the DOI exists. Empty and whitespace
    become the empty string. DOI resolver prefixes and a leading `doi:` are
    stripped; the remaining `10.xxxx/...` body is lowercased (Crossref
    practice). Bare http(s) URLs keep path case and drop a trailing slash.
    """
    raw = (reference or "").strip()
    if not raw:
        return ""
    doi = _DOI_PREFIX.match(raw)
    if doi:
        return doi.group(1).rstrip("/").lower()
    arxiv = _ARXIV.match(raw)
    if arxiv:
        return arxiv.group(1).lower()
    url = _URL.match(raw)
    if url:
        path = url.group(3) or ""
        return url.group(1).lower() + url.group(2).lower() + path.rstrip("/")
    return raw


def resolvable_reference(evidence: dict[str, Any]) -> str | None:
    """The first value in `evidence` that has the FORM of a dereferenceable reference.

    Returns the matched form name, or None.

    This checks SHAPE, NOT EXISTENCE. A well-formed DOI that was never
    registered passes. Verifying that a reference resolves requires a network
    call at ingest, which is a different trade-off and is not made here. The
    guarantee is narrow and deliberate: the claim named something that could in
    principle be checked, rather than prose that could not.

    The reserved `claim_warrant` key is skipped. A warrant describes how a claim
    could be checked; it is not itself evidence that the claim named anything,
    and its `source_digest` is a hex string matching the `hash` form. Letting it
    satisfy this function would move `UnattributedRootError` as a side effect of
    attaching metadata. Nested dicts are already skipped by the isinstance guard,
    so this is explicit rather than load-bearing today -- it keeps the guarantee
    if this function ever learns to recurse.
    """
    for key, value in evidence.items():
        if key == WARRANT_KEY:
            continue
        if not isinstance(value, str):
            continue
        candidate = value.strip()
        for name, pattern in _RESOLVABLE_FORMS:
            if pattern.match(candidate):
                return name
    return None


class UnattributedRootError(ValueError):
    """A parentless claim that names no checkable evidence.

    A claim with no recorded ancestry is an evidence ROOT, and roots are what
    `margin` counts. A claim that also carries no evidence therefore contributes
    full evidential weight while identifying nothing -- it is indistinguishable
    from an independent observation, which is CE-01 in
    formal/COUNTEREXAMPLES.md.

    KL-014's pilot measured this on real published claims: 5 of 9 (56%) cited no
    resolvable primary source. By contrast the bundled-artifact regimes that
    KL-014 v0.4 was written to address are roughly 2% of the literature. The
    attribution gap is the larger problem by more than an order of magnitude,
    which is why this gate exists and the unit rule was deprioritised.

    ON BY DEFAULT since 2026-08-13. Pass `require_root_evidence=False` to admit
    unattributed roots, which is what every version before this did.

    The gate requires a reference with the FORM of something dereferenceable --
    a DOI, URL, content hash, arXiv id or URN. `{"source": "trust me"}` is
    refused; `{"source": "10.1038/nature12373"}` is admitted. See
    `resolvable_reference` for what that does and does not guarantee.
    """


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
    read_from: tuple[str, ...] = ()
    """External sources this claimant **read**, as dereferenceable identifiers.

    Distinct from `evidence`, and the distinction is the whole point. `evidence`
    backs an observation the claimant made: a capture, a log, a receipt. This
    field names what the claimant *consulted*, which makes them a descendant of
    it rather than an independent witness to it.

    Both used to land in `evidence`, so five people who read one paper and cited
    it honestly were recorded as five independent roots. Nobody lied and every
    gate passed; the two meanings simply had one field between them. See
    `research/adversarial-weighting/citation_is_not_ancestry.py`.

    A node that names a source here is never a root. The graph materialises the
    external source as a node and makes this claim its child, so every reader of
    one source collapses onto it, which is what the copy machinery already does
    correctly once the edge exists.
    """
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
        """True when no ancestry is recorded, declared or cited.

        Naming a source in `read_from` is recorded ancestry: the claimant said
        where they got it. It is not an admission of guilt, it is the ordinary
        honest case, and it is what stops one paper becoming as many roots as it
        has readers.

        WARNING: this means "no ancestry RECORDED", not "independently
        observed". The distinction is the entire undetected-copy threat.
        """
        return not self.copied_from and not self.read_from


@dataclass(frozen=True)
class GateReport:
    """What the root-evidence gate admitted and turned away.

    A gate nobody reads is a gate nobody can tune. `refusal_rate` is the number
    to watch, and BOTH directions are informative:

      rate ~ 0.0   Either the incoming evidence genuinely carries references, or
                   the gate is not wired up. Check `roots_admitted` is non-zero
                   before concluding the first.
      rate rising  Something upstream changed. Read `refused_by_reason` and a
                   sample of `refused` before assuming the source got worse --
                   the usual cause is a legitimate reference format that
                   `resolvable_reference` does not recognise, which is a gap in
                   the recogniser rather than in the data.
      rate ~ 1.0   The graph is being starved. Almost certainly a format
                   mismatch, not an attack.

    There is no "correct" rate. On the corpus KL-014 measured, roughly 46% of
    indexed journal articles record no ancestry at all, so a high rate on real
    published material is expected rather than alarming. What matters is that
    the number is SEEN, and that a change in it is noticed.
    """

    roots_offered: int
    """Every parentless claim passed to `add`, whatever happened next."""
    roots_refused: int
    """Those the gate rejected. In strict mode they are absent from the graph;
    in permissive mode they are PRESENT but flagged, and `immunity_applicable`
    is False. The count is the same either way, which is the point."""
    refused_by_reason: dict[str, int]
    refused: tuple[str, ...]

    @property
    def roots_admitted(self) -> int:
        """Roots the gate would let through. In permissive mode the graph also
        contains the refused ones; this is the number that passed on merit."""
        return self.roots_offered - self.roots_refused

    @property
    def refusal_rate(self) -> float:
        """Refused roots as a fraction of roots offered. 0.0 if none offered."""
        return self.roots_refused / self.roots_offered if self.roots_offered else 0.0

    def summary(self) -> str:
        """One line, suitable for a log."""
        if not self.roots_offered:
            return "root gate: no roots offered"
        reasons = ", ".join(f"{k}={v}" for k, v in sorted(self.refused_by_reason.items()))
        return (f"root gate: {self.roots_offered} offered, {self.roots_refused} refused "
                f"({self.refusal_rate:.1%})" + (f" [{reasons}]" if reasons else ""))


@dataclass(frozen=True)
class Violation:
    """A rejected-or-recorded integrity failure, kept for audit."""

    kind: str
    node_id: str
    parent_id: str
    detail: str


def _source_node_id(reference: str) -> str:
    """One node per external source, so every reader of it shares one parent."""
    return f"source:{canonical_reference(reference) or reference.strip()}"


def _parent_ids(node: "EvidenceNode") -> tuple[str, ...]:
    """Every recorded ancestor: copy edges and materialized citation edges."""
    sources = tuple(
        _source_node_id(ref) for ref in node.read_from if canonical_reference(ref) or ref.strip()
    )
    return tuple(node.copied_from) + sources


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

    def __init__(self, *, strict: bool = True, root_authority: RootAuthority | None = None,
                 require_root_evidence: bool = True) -> None:
        self._nodes: dict[str, EvidenceNode] = {}
        self._violations: list[Violation] = []
        self._strict = strict
        self._root_authority = root_authority
        self._require_root_evidence = require_root_evidence
        self._roots_offered = 0

    # ------------------------------------------------------------------ ingest

    def _materialise_source(self, reference: str, child: EvidenceNode) -> None:
        """Ensure the external source exists as a node, once, shared by all readers.

        The source itself is a root: it is the thing that was read, and nothing in
        the graph stands behind it. It carries the canonical reference as its own
        evidence. This path used to skip `require_root_evidence`, so
        `read_from=("trust me",)` minted a parentless node the bare-root gate
        would have refused.

        Created on the side the first reader asserts. A later reader asserting the
        opposite side hits the ordinary side-consistency check rather than a
        special case, which is correct: two readers of one source who disagree
        about what it says is a real conflict and not something to paper over.

        Materialised sources are identity-by-canonical-reference, not registry
        minted IDs. `root_authority` is not consulted here; junk citations are
        stopped by the resolvable-form gate instead.
        """
        canon = canonical_reference(reference)
        offered = {"reference": canon or (reference or "").strip()}
        if not canon or (
            self._require_root_evidence and resolvable_reference(offered) is None
        ):
            detail = (
                "empty read_from"
                if not canon
                else f"read_from {reference!r} names nothing dereferenceable"
            )
            self._reject(
                UnattributedRootError,
                Violation(
                    "unattributed_root",
                    child.node_id,
                    "",
                    f"{detail}, so it would mint a parentless source that "
                    "identifies nothing",
                ),
            )
            # Never mint the refused source, including in diagnostic mode.
            # Two empty citations sharing `source:` would be a dependence
            # claim the record does not support.
            return
        node_id = _source_node_id(reference)
        if node_id in self._nodes:
            return
        self._nodes[node_id] = EvidenceNode(
            node_id=node_id,
            proposition_id=child.proposition_id,
            value=child.value,
            observer_id=node_id,
            source_id=node_id,
            confidence=child.confidence,
            evidence={"reference": canon or (reference or "").strip()},
        )
        self._roots_offered += 1

    def add(self, node: EvidenceNode) -> None:
        if node.node_id in self._nodes:
            raise ValueError(f"duplicate node: {node.node_id}")

        for reference in node.read_from:
            self._materialise_source(reference, node)

        parents = tuple(node.copied_from) + tuple(
            _source_node_id(ref)
            for ref in node.read_from
            if _source_node_id(ref) in self._nodes
        )
        missing = [parent for parent in node.copied_from if parent not in self._nodes]
        if missing:
            raise ValueError(f"unknown ancestors: {', '.join(missing)}")

        if node.is_root and self._root_authority is not None:
            if node.node_id not in self._root_authority.active_roots():
                raise RootAuthorizationError(
                    f"root {node.node_id!r} is not active in the configured authority"
                )

        if node.is_root:
            self._roots_offered += 1

        if node.is_root and self._require_root_evidence:
            if resolvable_reference(node.evidence) is None:
                detail = ("carries no evidence at all" if not node.evidence
                          else f"evidence {sorted(node.evidence)} names nothing "
                               "dereferenceable (expected a DOI, URL, hash, arXiv id or URN)")
                self._reject(
                    UnattributedRootError,
                    Violation(
                        "unattributed_root",
                        node.node_id,
                        "",
                        f"parentless claim {detail}, so it would count as an "
                        "independent observation while identifying nothing",
                    ),
                )

        for parent_id in parents:
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

    def gate_report(self) -> GateReport:
        """Admitted-vs-refused counts for the root-evidence gate.

        Populated in BOTH modes: strict raises after recording, permissive
        records and continues. A caller that lets the exception escape should
        still hold the graph long enough to read this, or the refusal is
        invisible -- which is the failure this method exists to prevent.
        """
        refused = [v for v in self._violations if v.kind == "unattributed_root"]
        by_reason: dict[str, int] = {}
        for violation in refused:
            key = "no_evidence" if "no evidence at all" in violation.detail else "unresolvable_reference"
            by_reason[key] = by_reason.get(key, 0) + 1
        return GateReport(
            roots_offered=self._roots_offered,
            roots_refused=len(refused),
            refused_by_reason=by_reason,
            refused=tuple(v.node_id for v in refused),
        )

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
            for parent in _parent_ids(node):
                if parent not in self._nodes:
                    continue
                found |= self._roots(parent, cache, stack + (node_id,))
            result = frozenset(found)
        cache[node_id] = result
        return result

    def independent(self, left: str, right: str) -> bool:
        """No shared recorded ancestry.

        This is ALL-OR-NOTHING disjointness. Two claims sharing some but not all
        roots are reported as dependent. Graded independence is not modelled and
        no theorem covers it.

        Empty ancestor sets do not count as independent. That was the
        `read_from` query hole: two honest readers kept `copied_from=()` so
        both walks were empty and `isdisjoint` was True. "No dependence
        trace" is not a positive independence claim (ASSAYER A5).
        """
        left_roots = self.roots(left)
        right_roots = self.roots(right)
        if not left_roots or not right_roots:
            return False
        return left_roots.isdisjoint(right_roots)

    def root_set(self) -> frozenset[str]:
        """Every parentless claim in the graph (the `rootSet` of the theorems)."""
        return frozenset(nid for nid, node in self._nodes.items() if node.is_root)

    def nodes(self) -> tuple[EvidenceNode, ...]:
        return tuple(self._nodes.values())

    # ------------------------------------------------------------- (de)serialise

    def to_dict(self) -> dict[str, object]:
        return {
            "version": "0.3",
            "strict": self._strict,
            "require_root_evidence": self._require_root_evidence,
            "nodes": [vars(node) for node in self._nodes.values()],
        }

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
        *,
        strict: bool | None = None,
        require_root_evidence: bool | None = None,
    ) -> "EvidenceGraph":
        """Validating loader.

        Deserialisation previously had no counterpart to `add`, so a payload
        could reintroduce every invariant violation the ingest path rejects.
        This loader replays nodes through `add` in dependency order.

        The caller's `strict` / `require_root_evidence` are a floor, not a
        default the payload may lower. `from_dict(untrusted, strict=True)`
        stays strict even if the file says `"strict": false`. Omit the
        argument to honour the payload. A payload may only raise the floor.

        `read_from` is restored (v0.2 dropped it in `_node_from_raw`, so five
        honest readers became six roots after a roundtrip). Materialised
        `source:` nodes already present from a reader are not added twice.
        `source:` ids from older payloads are rewritten to the canonical form
        so a DOI stored under `https://doi.org/...` merges with `10.xxxx/...`.
        """
        payload_strict = bool(payload.get("strict", True))
        payload_require = bool(payload.get("require_root_evidence", True))
        graph = cls(
            strict=payload_strict if strict is None else (strict or payload_strict),
            require_root_evidence=(
                payload_require
                if require_root_evidence is None
                else (require_root_evidence or payload_require)
            ),
        )
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
                original_id = raw["node_id"]
                node = _node_from_raw(raw)
                if node.node_id in graph._nodes:
                    placed.add(original_id)
                    placed.add(node.node_id)
                    del pending[original_id]
                    continue
                graph.add(node)
                placed.add(original_id)
                placed.add(node.node_id)
                del pending[original_id]
        return graph


def _node_from_raw(raw: dict[str, Any]) -> EvidenceNode:
    node_id = raw["node_id"]
    if isinstance(node_id, str) and node_id.startswith("source:"):
        node_id = _source_node_id(node_id[len("source:"):])
    return EvidenceNode(
        node_id=node_id,
        proposition_id=raw["proposition_id"],
        value=bool(raw["value"]),
        observer_id=raw["observer_id"],
        source_id=raw["source_id"],
        confidence=float(raw["confidence"]),
        evidence=dict(raw.get("evidence") or {}),
        copied_from=tuple(raw.get("copied_from") or ()),
        read_from=tuple(raw.get("read_from") or ()),
        transformations=tuple(raw.get("transformations") or ()),
        signature=raw.get("signature"),
        timestamp=raw["timestamp"],
    )


def build(nodes: Iterable[EvidenceNode], *, strict: bool = True,
          require_root_evidence: bool = True) -> EvidenceGraph:
    """Convenience constructor; nodes must arrive in dependency order."""
    graph = EvidenceGraph(strict=strict, require_root_evidence=require_root_evidence)
    for node in nodes:
        graph.add(node)
    return graph
