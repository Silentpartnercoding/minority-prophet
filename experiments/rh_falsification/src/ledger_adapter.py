"""Ledger for the RH falsification pack, stored in the canonical evidence graph.

Storage is ``provenance.graph.EvidenceGraph`` (strict, root-evidence gate on).
Counting is ``aggregation.root_vote.verdict``: the unweighted F the compiled
theorems are about. Nothing in this module computes a score, a weight or a
probability. The only number it produces is a count of distinct roots.

Root identity (see ROOT-IDENTITY.md): a root is a finished calculation. A
report that carries a computation fingerprint (``result_hash``, or
``method`` plus ``candidate_key``) is recorded as reading that calculation,
so the graph materialises one ``source:urn:rh-calc:...`` node per distinct
calculation and every report of it becomes a child of that node. Twenty
reports with one hash and no declared parents therefore count as one root
(CE-01 on this wire). Three reports with three hashes count as three.

A report that declares a parent is a recorded copy. Its own fingerprint is
kept on the record but does not add a root, which is what copy invariance
says a recorded copy must do.

A parentless report with no fingerprint names nothing checkable. The
canonical graph refuses it (``UnattributedRootError``). What happens next is
``unattributed_policy``:

  quarantine           (default) it is kept on the report log but never
                       enters the graph, so it adds zero roots.
  abstain_if_decisive  as quarantine, and it is passed to ``root_vote`` as an
                       unattributed claim, so a decision that it could change
                       is withheld (root_vote's own default).
  treat_as_root        explicit opt-in: the graph is built with the evidence
                       gate off and each such report is its own root.

Mapping onto the canonical node (``provenance/evidence-lineage.schema.json``):

  claim_id            -> node_id
  agent_id            -> observer_id
  method              -> source_id (agent_id when method is empty)
  parent_evidence_ids -> copied_from
  fingerprint         -> read_from = ("urn:rh-calc:...",)
  result_hash, candidate_key, method, claim_type, claim_state -> evidence

``agent_id`` is never a root. Declared ``independent_of`` is a claim to
check, never a fact, and is not read here.

Not wired here, on purpose: Gate ``decide()`` and ``TrustAllVerifier``.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Optional, Set

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from aggregation.root_vote import RootVerdict, verdict  # noqa: E402
from provenance.graph import EvidenceGraph, EvidenceNode  # noqa: E402

CLAIM_STATES = (
    "SUPPORTED",
    "UNSUPPORTED",
    "ANOMALY",
    "CANDIDATE_FALSIFIER",
    "VERIFYING",
    "REPRODUCED",
    "REJECTED_FALSE_POSITIVE",
    "ABSTAIN",
    "FALSIFIED",
)

# ANOMALY may never transition directly to FALSIFIED (experiment_spec.md).
FORBIDDEN_TRANSITIONS = {("ANOMALY", "FALSIFIED")}

UNATTRIBUTED_POLICIES = ("quarantine", "abstain_if_decisive", "treat_as_root")

# The candidate ledger records reports that a specific candidate is real.
# Confirmations of the universal claim are a different proposition and are
# recorded in the universal ledger (rh_decision.UniversalLedger).
CANDIDATE_CLAIM_TYPES = ("candidate_counterexample", "counterexample", "anomaly")

CALC_URN_PREFIX = "urn:rh-calc:"

# ``EvidenceNode`` requires a field named ``confidence``. Nothing in this pack
# or in ``root_vote`` reads it, and no verdict depends on it. It is filled with
# one constant so the canonical constructor accepts the node.
_UNREAD_REQUIRED_FIELD = 1.0

# root_vote's name for "drop unattributed claims" is "ignore".
_ROOT_VOTE_POLICY = {
    "quarantine": "ignore",
    "abstain_if_decisive": "abstain_if_decisive",
    "treat_as_root": "treat_as_root",
}


@dataclass(frozen=True)
class LedgerEntry:
    """One append-only report.

    ``parent_evidence_ids`` are declared parents (untrusted). ``result_hash``
    or ``method`` plus ``candidate_key`` form the computation fingerprint.
    """

    claim_id: str
    agent_id: str
    claim_type: str
    parent_evidence_ids: FrozenSet[str] = field(default_factory=frozenset)
    method: str = ""
    claim_state: str = "ANOMALY"
    result_hash: str = ""
    candidate_key: str = ""

    def fingerprint(self) -> Optional[str]:
        """Identity of the finished calculation, or None if it cannot be told."""
        if self.result_hash:
            return f"hash:{self.result_hash}"
        if self.candidate_key and self.method:
            return f"cand:{self.method}:{self.candidate_key}"
        return None

    def calc_reference(self) -> Optional[str]:
        fp = self.fingerprint()
        if fp is None:
            return None
        if any(ch.isspace() for ch in fp):
            raise ValueError(f"fingerprint for {self.claim_id!r} contains whitespace")
        return CALC_URN_PREFIX + fp


@dataclass(frozen=True)
class _RootClaim:
    """One root behind the selected reports, as a root_vote RootedClaim."""

    value: bool
    root_id: Optional[str]
    independence_basis: Optional[str] = None
    witness_depth: Optional[str] = None
    attestation: Optional[str] = None
    witness_identity: Optional[str] = None
    depth_basis: Optional[str] = None


class KnowledgeLedger:
    """Append-only report log over one canonical evidence graph.

    The report log holds every report, including quarantined ones, so the
    claim-state machine and the append-only rule cover them too. Only the
    graph is counted.
    """

    def __init__(
        self,
        unattributed_policy: str = "quarantine",
        *,
        proposition_id: str = "rh:candidate",
        root_authority=None,
    ) -> None:
        if unattributed_policy not in UNATTRIBUTED_POLICIES:
            raise ValueError(
                f"unknown unattributed_policy {unattributed_policy!r}; "
                f"want one of {UNATTRIBUTED_POLICIES}"
            )
        self.unattributed_policy = unattributed_policy
        self.proposition_id = proposition_id
        # root_authority is passed straight to the canonical graph. None means
        # no issuance cap is enforced (see ROOT-IDENTITY.md, "Cap").
        self.graph = EvidenceGraph(
            strict=True,
            root_authority=root_authority,
            require_root_evidence=unattributed_policy != "treat_as_root",
        )
        self._entries: Dict[str, LedgerEntry] = {}
        self._order: List[str] = []
        self._quarantined: Set[str] = set()

    # ------------------------------------------------------------- ingest

    def append(self, entry: LedgerEntry) -> None:
        if entry.claim_id in self._entries:
            raise ValueError(
                f"append-only violation: claim_id {entry.claim_id!r} already exists"
            )
        for parent in entry.parent_evidence_ids:
            if parent not in self._entries:
                raise ValueError(
                    f"unknown parent {parent!r} for claim {entry.claim_id!r}; "
                    "parents must be appended before children"
                )
        if entry.claim_state not in CLAIM_STATES:
            raise ValueError(f"unknown claim_state {entry.claim_state!r}")
        if entry.claim_type not in CANDIDATE_CLAIM_TYPES:
            raise ValueError(
                f"claim_type {entry.claim_type!r} is not a report about a candidate; "
                "confirmations and counterexamples are different propositions"
            )

        node = self._node_for(entry)
        if node is not None:
            self.graph.add(node)
        else:
            self._quarantined.add(entry.claim_id)
        self._entries[entry.claim_id] = entry
        self._order.append(entry.claim_id)

    def _node_for(self, entry: LedgerEntry) -> Optional[EvidenceNode]:
        """The canonical node for a report, or None when it is quarantined."""
        admitted_parents = tuple(
            sorted(p for p in entry.parent_evidence_ids if p not in self._quarantined)
        )
        calc = entry.calc_reference()
        evidence = {
            "claim_type": entry.claim_type,
            "claim_state": entry.claim_state,
        }
        if entry.method:
            evidence["method"] = entry.method
        if entry.result_hash:
            evidence["result_hash"] = entry.result_hash
        if entry.candidate_key:
            evidence["candidate_key"] = entry.candidate_key

        if admitted_parents:
            # Recorded copy: descends from its parents only.
            read_from: tuple = ()
        elif calc is not None:
            read_from = (calc,)
        elif self.unattributed_policy == "treat_as_root":
            read_from = ()
        else:
            return None

        return EvidenceNode(
            node_id=entry.claim_id,
            proposition_id=self.proposition_id,
            value=True,
            observer_id=entry.agent_id,
            source_id=entry.method or entry.agent_id,
            confidence=_UNREAD_REQUIRED_FIELD,
            evidence=evidence,
            copied_from=admitted_parents,
            read_from=read_from,
        )

    # ------------------------------------------------------------ queries

    def get(self, claim_id: str) -> LedgerEntry:
        return self._entries[claim_id]

    def __len__(self) -> int:
        return len(self._entries)

    def is_quarantined(self, claim_id: str) -> bool:
        return claim_id in self._quarantined

    def provenance_roots(self, claim_id: str) -> FrozenSet[str]:
        """Canonical graph roots behind one report. Empty when quarantined."""
        if claim_id in self._quarantined:
            return frozenset()
        return self.graph.roots(claim_id)

    def unattributed_count(self, claim_ids: Iterable[str]) -> int:
        """Selected reports that reach no root (quarantined)."""
        return sum(1 for c in claim_ids if c in self._quarantined)

    def raw_support_count(self, claim_ids: Iterable[str]) -> int:
        """Number of reports. Never evidence by itself."""
        return len(list(claim_ids))

    def candidate_verdict(self, claim_ids: Iterable[str]) -> RootVerdict:
        """root_vote.verdict over the distinct roots behind the reports.

        Every root here asserts the candidate, so the margin is the number of
        distinct roots. Quarantined reports are passed as unattributed claims
        and root_vote applies the policy.
        """
        ids = list(claim_ids)
        roots: Set[str] = set()
        for claim_id in ids:
            roots |= self.provenance_roots(claim_id)
        claims: List[_RootClaim] = [_RootClaim(True, r) for r in sorted(roots)]
        claims += [
            _RootClaim(True, None) for c in ids if c in self._quarantined
        ]
        return verdict(
            claims,
            unattributed_policy=_ROOT_VOTE_POLICY[self.unattributed_policy],
            claim_shape="symmetric",
        )

    def independent_support_count(self, claim_ids: Iterable[str]) -> int:
        """Number of distinct roots behind the reports, from root_vote."""
        return len(self.candidate_verdict(claim_ids).support_true)

    def transition(self, claim_id: str, new_state: str) -> LedgerEntry:
        """Append a state-transition record. Earlier records never change."""
        current = self._entries[claim_id]
        if new_state not in CLAIM_STATES:
            raise ValueError(f"unknown claim_state {new_state!r}")
        if (current.claim_state, new_state) in FORBIDDEN_TRANSITIONS:
            raise ValueError(
                f"forbidden transition {current.claim_state} -> {new_state}: "
                "a raw anomaly must pass through verification before FALSIFIED"
            )
        successor = LedgerEntry(
            claim_id=f"{claim_id}::state::{new_state}::{len(self._order)}",
            agent_id="ledger",
            claim_type=current.claim_type,
            parent_evidence_ids=frozenset({claim_id}),
            method=current.method,
            claim_state=new_state,
            result_hash=current.result_hash,
            candidate_key=current.candidate_key,
        )
        self.append(successor)
        return successor


def _entry_from_report(report: dict) -> LedgerEntry:
    if "raw_result_hash" in report:
        raise ValueError(
            "raw_result_hash is not a field of this schema; use result_hash"
        )
    return LedgerEntry(
        claim_id=report["claim_id"],
        agent_id=report["agent_id"],
        claim_type=report["claim_type"],
        parent_evidence_ids=frozenset(report.get("parent_evidence_ids", [])),
        method=report.get("method") or "",
        claim_state=report.get("claim_state", "ANOMALY"),
        result_hash=report.get("result_hash") or "",
        candidate_key=report.get("candidate_key") or "",
    )


def build_ledger_from_reports(
    reports: List[dict],
    unattributed_policy: str = "quarantine",
    **kwargs,
) -> KnowledgeLedger:
    """Convenience constructor used by tests and the harness.

    Each report needs claim_id, agent_id, claim_type; optional
    parent_evidence_ids, method, claim_state, result_hash, candidate_key.
    Reports must arrive parents first.
    """
    ledger = KnowledgeLedger(unattributed_policy=unattributed_policy, **kwargs)
    for report in reports:
        ledger.append(_entry_from_report(report))
    return ledger
