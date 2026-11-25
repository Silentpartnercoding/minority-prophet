"""Decision layer for the RH falsification pack.

No scores, weights or probabilities. Every action below is read off two
things: the count of distinct roots from the canonical ledger, and the
recorded outcome of verification steps (each a yes or no fact about a
calculation). The universal claim is settled only by
``aggregation.root_vote.asymmetric_verdict`` with ``claim_shape="universal"``,
the implementation of ``universalF`` in
``formal/lean/MinorityProphetCore/Asymmetric.lean``: one counterexample root
refutes, whatever the number of confirming roots, and the confirming roots
are never read (AC2).

A candidate report and a counterexample to the universal claim are different
propositions. A candidate becomes a counterexample root only when both of
these hold:

  1. its verification record is certified: level 6 (an outside,
     machine-checkable certificate), reproduced, numerically stable and
     internally consistent; and
  2. the tower has rechecked it itself, on its own machine with its own
     software and interval-arithmetic error bounds, producing a calculation
     of its own. That recheck is the counterexample root. It is issued
     through the registry under the tower's identity and the same cap.

A failed tower recheck rejects the whole candidate.

The pack stops at CANDIDATE_FALSIFIER. FALSIFIED is declared only by the
maintainer, by hand, outside this pack. Nothing automated emits it.

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
from rh_issuance import SYNTHETIC_T0, CalculationIssuer

from aggregation.root_vote import (  # noqa: E402
    AsymmetricOutcome,
    AsymmetricVerdict,
    asymmetric_verdict,
)
from provenance.graph import EvidenceGraph, EvidenceNode  # noqa: E402

ACTIONS = ("reject", "verify", "abstain", "escalate")

REPRODUCIBILITY = ("not_attempted", "reproduced", "failed", "partial")

# Level 6: a standalone outside verifier produced a machine-checkable
# certificate (experiment_spec.md, "Verification levels").
CERTIFIED_LEVEL = 6
# An anomaly counts as exhausted once rigorous arithmetic (level 4) has run.
ANOMALY_EXHAUSTED_LEVEL = 4

TOWER_IDENTITY = "tower"


@dataclass(frozen=True)
class TowerRecheck:
    """The tower's own recheck of a candidate. Facts only."""

    result_hash: str
    software: str
    machine: str
    interval_bounds: bool
    passed: bool

    def own_calculation(self, finder_hashes: Iterable[str], finder_methods: Iterable[str]) -> bool:
        """A recheck of its own: own machine, own software, interval bounds,
        and a result that is not a replay of any finder's calculation."""
        return bool(
            self.result_hash
            and self.software
            and self.machine
            and self.interval_bounds
            and self.result_hash not in set(finder_hashes)
            and self.software not in set(finder_methods)
        )


@dataclass(frozen=True)
class VerificationRecord:
    """What verification has established about one candidate. Facts only."""

    level: int
    reproducibility: str
    numerically_stable: bool
    internally_consistent: bool
    external_certificate: str = ""
    tower_recheck: Optional[TowerRecheck] = None

    def __post_init__(self) -> None:
        if not 0 <= self.level <= 6:
            raise ValueError("verification level must be 0..6")
        if self.reproducibility not in REPRODUCIBILITY:
            raise ValueError(f"unknown reproducibility {self.reproducibility!r}")

    @property
    def certified(self) -> bool:
        return (
            self.level >= CERTIFIED_LEVEL
            and bool(self.external_certificate)
            and self.reproducibility == "reproduced"
            and self.numerically_stable
            and self.internally_consistent
        )


class UniversalLedger:
    """Canonical graph for one universal claim ("every X in scope satisfies P").

    Counterexample roots (value False) are the tower's own rechecks, issued
    through the registry, and are the only roots ``universalF`` reads.
    Confirming roots (value True) are recorded as cited calculations and are
    never read (AC2), so they are not issued.
    Settlement is ``asymmetric_verdict(claim_shape="universal")``.
    """

    def __init__(self, proposition_id: str, issuer: Optional[CalculationIssuer] = None) -> None:
        self.proposition_id = proposition_id
        self.issuer = issuer if issuer is not None else CalculationIssuer()
        self.graph = EvidenceGraph(strict=True, root_authority=self.issuer)

    def add_confirmation(self, claim_id: str, result_hash: str) -> None:
        reference = f"{CALC_URN_PREFIX}hash:{result_hash}"
        self.graph.add(
            EvidenceNode(
                node_id=claim_id,
                proposition_id=self.proposition_id,
                value=True,
                observer_id=claim_id,
                source_id=claim_id,
                confidence=_UNREAD_REQUIRED_FIELD,
                evidence={"reference": reference},
                read_from=(reference,),
            )
        )

    def add_tower_recheck(self, recheck: TowerRecheck,
                          observed_at: int = SYNTHETIC_T0) -> Optional[str]:
        """Issue the tower's recheck as a counterexample root. None if over cap."""
        fingerprint = f"{CALC_URN_PREFIX}hash:{recheck.result_hash}"
        root_id = self.issuer.issue(
            identity=TOWER_IDENTITY,
            fingerprint=fingerprint,
            proposition_id=self.proposition_id,
            value=False,
            observed_at=observed_at,
        )
        if root_id is None:
            return None
        if root_id not in {n.node_id for n in self.graph.nodes()}:
            self.graph.add(
                EvidenceNode(
                    node_id=root_id,
                    proposition_id=self.proposition_id,
                    value=False,
                    observer_id=TOWER_IDENTITY,
                    source_id=recheck.software,
                    confidence=_UNREAD_REQUIRED_FIELD,
                    evidence={"calculation": fingerprint, "machine": recheck.machine},
                )
            )
        return root_id

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
        if self.next_state == "FALSIFIED":
            raise ValueError("only the maintainer declares FALSIFIED")


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
    4. A failed tower recheck rejects the whole candidate.
    5. An anomaly is never a counterexample. Abstain once verification is
       exhausted (level 4 or higher), otherwise keep verifying.
    6. A certified candidate (level 6) with a passed tower recheck of its own
       gets that recheck issued as a counterexample root. If the universal
       verdict is then REFUTED, escalate to CANDIDATE_FALSIFIER and stop.
       Without such a recheck, keep verifying.
    7. Otherwise keep verifying.
    """
    ids = list(claim_ids)
    cv = ledger.candidate_verdict(ids)
    roots = sorted(cv.support_true)
    n_roots = len(roots)
    raw = ledger.raw_support_count(ids)
    unattributed = ledger.unattributed_count(ids)
    entries = [ledger.get(c) for c in ids]

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

    tower = record.tower_recheck
    if not record.internally_consistent:
        return out("reject", "REJECTED_FALSE_POSITIVE", "record contradicts itself")
    if n_roots == 0:
        if unattributed and ledger.unattributed_policy == "abstain_if_decisive":
            return out("abstain", "ABSTAIN",
                       "only unattributed reports; withheld under abstain_if_decisive")
        return out("reject", "REJECTED_FALSE_POSITIVE", "no attributable calculation")
    if record.reproducibility == "failed":
        return out("reject", "REJECTED_FALSE_POSITIVE", "independent recheck failed")
    if tower is not None and not tower.passed:
        return out("reject", "REJECTED_FALSE_POSITIVE", "tower recheck failed")
    if claim_type == "anomaly":
        if record.level >= ANOMALY_EXHAUSTED_LEVEL:
            return out("abstain", "ABSTAIN", "anomaly unresolved after verification")
        return out("verify", "VERIFYING", "anomaly; verification incomplete")
    if record.certified:
        if tower is None:
            return out("verify", "VERIFYING", "certified; awaiting tower recheck")
        finder_hashes = [e.result_hash for e in entries if e.result_hash]
        finder_methods = [e.method for e in entries if e.method]
        if not tower.own_calculation(finder_hashes, finder_methods):
            return out("verify", "VERIFYING", "tower recheck is not a calculation of its own")
        observed_at = max(e.observed_at for e in entries)
        if universal.add_tower_recheck(tower, observed_at) is None:
            return out("verify", "VERIFYING", "tower issuance cap reached for this hour")
        if universal.settle().outcome is AsymmetricOutcome.REFUTED:
            return out("escalate", "CANDIDATE_FALSIFIER",
                       "tower recheck root refutes the universal claim; "
                       "the maintainer decides FALSIFIED")
    return out("verify", "VERIFYING", "verification incomplete")


def universal_with_confirmations(proposition_id: str, n: int, tag: str) -> UniversalLedger:
    """A universal ledger holding ``n`` confirming roots with distinct hashes."""
    u = UniversalLedger(proposition_id)
    for i in range(n):
        u.add_confirmation(f"conf_{tag}_{i}", f"conf_{tag}_{i}")
    return u


__all__: Tuple[str, ...] = (
    "ACTIONS",
    "ANOMALY_EXHAUSTED_LEVEL",
    "CERTIFIED_LEVEL",
    "TOWER_IDENTITY",
    "TowerRecheck",
    "Decision",
    "UniversalLedger",
    "VerificationRecord",
    "decide",
    "universal_with_confirmations",
)
