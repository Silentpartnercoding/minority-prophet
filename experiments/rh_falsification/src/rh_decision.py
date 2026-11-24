"""Decision layer for the RH falsification pack.

No scores, weights or probabilities. Every action below is read off two
things: the count of distinct roots from the canonical ledger, and the
recorded outcome of verification steps (each a yes or no fact about a
calculation). The universal claim is settled only by
``aggregation.root_vote.asymmetric_verdict`` with ``claim_shape="universal"``,
the implementation of ``universalF`` in
``formal/lean/MinorityProphetCore/Asymmetric.lean``: one verified
counterexample root refutes, whatever the number of confirming roots, and
the confirming roots are never read (AC2).

A candidate report and a counterexample to the universal claim are different
propositions. A candidate enters the universal ledger as a counterexample
root only after its verification record is certified (level 4 or higher,
reproduced, numerically stable, internally consistent).

``NOT_REFUTED`` is not "proved". There is no state for a proved RH and none
can be produced here.

Not wired here, on purpose: Gate ``decide()`` and ``TrustAllVerifier``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from ledger_adapter import (  # noqa: I001  (also puts the repo root on sys.path)
    CALC_URN_PREFIX,
    CLAIM_STATES,
    KnowledgeLedger,
    _UNREAD_REQUIRED_FIELD,
)

from aggregation.root_vote import (  # noqa: E402
    AsymmetricOutcome,
    AsymmetricVerdict,
    asymmetric_verdict,
)
from provenance.graph import EvidenceGraph, EvidenceNode  # noqa: E402

ACTIONS = ("reject", "verify", "abstain", "escalate")

REPRODUCIBILITY = ("not_attempted", "reproduced", "failed", "partial")

# Level at which a candidate can become a counterexample root: certified zero
# and a certified real-part interval excluding 1/2 (experiment_spec.md).
CERTIFIED_LEVEL = 4


@dataclass(frozen=True)
class VerificationRecord:
    """What verification has established about one candidate. Facts only."""

    level: int
    reproducibility: str
    numerically_stable: bool
    internally_consistent: bool

    def __post_init__(self) -> None:
        if not 0 <= self.level <= 6:
            raise ValueError("verification level must be 0..6")
        if self.reproducibility not in REPRODUCIBILITY:
            raise ValueError(f"unknown reproducibility {self.reproducibility!r}")

    @property
    def certified(self) -> bool:
        return (
            self.level >= CERTIFIED_LEVEL
            and self.reproducibility == "reproduced"
            and self.numerically_stable
            and self.internally_consistent
        )


class UniversalLedger:
    """Canonical graph for one universal claim ("every X in scope satisfies P").

    Confirming roots assert True. Verified counterexample roots assert False.
    Settlement is ``asymmetric_verdict(claim_shape="universal")``.
    """

    def __init__(self, proposition_id: str) -> None:
        self.proposition_id = proposition_id
        self.graph = EvidenceGraph(strict=True)

    def _add(self, node_id: str, value: bool, reference: str, observer: str) -> None:
        self.graph.add(
            EvidenceNode(
                node_id=node_id,
                proposition_id=self.proposition_id,
                value=value,
                observer_id=observer,
                source_id=observer,
                confidence=_UNREAD_REQUIRED_FIELD,
                evidence={"reference": reference},
                read_from=(reference,),
            )
        )

    def add_confirmation(self, claim_id: str, result_hash: str) -> None:
        self._add(claim_id, True, f"{CALC_URN_PREFIX}hash:{result_hash}", claim_id)

    def add_verified_counterexample(self, root_id: str) -> None:
        """``root_id`` is a candidate-ledger root (``source:urn:rh-calc:...``)."""
        reference = root_id[len("source:"):] if root_id.startswith("source:") else root_id
        self._add(f"verified::{root_id}", False, reference, "verifier")

    def settle(self) -> AsymmetricVerdict:
        roots = self.graph.root_set()
        claims = [
            _Root(node.value, node.node_id)
            for node in self.graph.nodes()
            if node.node_id in roots
        ]
        return asymmetric_verdict(claims, claim_shape="universal")


@dataclass(frozen=True)
class _Root:
    value: bool
    root_id: Optional[str]
    independence_basis: Optional[str] = None
    witness_depth: Optional[str] = None
    attestation: Optional[str] = None
    witness_identity: Optional[str] = None
    depth_basis: Optional[str] = None


@dataclass(frozen=True)
class Decision:
    action: str
    next_state: str
    reason: str
    independent_roots: int
    raw_reports: int
    unattributed: int
    universal_outcome: str
    decisive_roots: int
    ignored_confirming_roots: int

    def __post_init__(self) -> None:
        if self.action not in ACTIONS:
            raise ValueError(self.action)
        if self.next_state not in CLAIM_STATES:
            raise ValueError(self.next_state)


def decide(
    ledger: KnowledgeLedger,
    claim_ids: Iterable[str],
    *,
    claim_type: str,
    record: VerificationRecord,
    universal: UniversalLedger,
) -> Decision:
    """Route one candidate. Order of the rules is the rule.

    1. A record that contradicts itself is rejected.
    2. No attributable root: reject under quarantine and treat_as_root;
       abstain under abstain_if_decisive when unattributed reports exist.
    3. A failed independent recheck rejects the candidate.
    4. An anomaly is never a counterexample. Abstain once verification is
       exhausted (level 4 or higher), otherwise keep verifying.
    5. A certified candidate enters the universal ledger as a counterexample
       root. If the universal verdict is then REFUTED, escalate.
    6. Otherwise keep verifying.
    """
    ids = list(claim_ids)
    cv = ledger.candidate_verdict(ids)
    roots = sorted(cv.support_true)
    n_roots = len(roots)
    raw = ledger.raw_support_count(ids)
    unattributed = ledger.unattributed_count(ids)

    def out(action: str, state: str, reason: str) -> Decision:
        settled = universal.settle()
        return Decision(
            action=action,
            next_state=state,
            reason=reason,
            independent_roots=n_roots,
            raw_reports=raw,
            unattributed=unattributed,
            universal_outcome=settled.outcome.value,
            decisive_roots=len(settled.decisive_roots),
            ignored_confirming_roots=settled.ignored_root_count,
        )

    if not record.internally_consistent:
        return out("reject", "REJECTED_FALSE_POSITIVE", "record contradicts itself")
    if n_roots == 0:
        if unattributed and ledger.unattributed_policy == "abstain_if_decisive":
            return out("abstain", "ABSTAIN",
                       "only unattributed reports; withheld under abstain_if_decisive")
        return out("reject", "REJECTED_FALSE_POSITIVE", "no attributable calculation")
    if record.reproducibility == "failed":
        return out("reject", "REJECTED_FALSE_POSITIVE", "independent recheck failed")
    if claim_type == "anomaly":
        if record.level >= CERTIFIED_LEVEL:
            return out("abstain", "ABSTAIN", "anomaly unresolved after verification")
        return out("verify", "VERIFYING", "anomaly; verification incomplete")
    if record.certified:
        for root in roots:
            universal.add_verified_counterexample(root)
        if universal.settle().outcome is AsymmetricOutcome.REFUTED:
            return out("escalate", "CANDIDATE_FALSIFIER",
                       "certified counterexample root; universal claim refuted")
    return out("verify", "VERIFYING", "verification incomplete")


def universal_with_confirmations(proposition_id: str, n: int, tag: str) -> UniversalLedger:
    """A universal ledger holding ``n`` confirming roots with distinct hashes."""
    u = UniversalLedger(proposition_id)
    for i in range(n):
        u.add_confirmation(f"conf_{tag}_{i}", f"conf_{tag}_{i}")
    return u


__all__: Tuple[str, ...] = (
    "ACTIONS",
    "CERTIFIED_LEVEL",
    "Decision",
    "UniversalLedger",
    "VerificationRecord",
    "decide",
    "universal_with_confirmations",
)
