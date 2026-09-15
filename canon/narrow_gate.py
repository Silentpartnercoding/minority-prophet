"""Reference implementation of the MP Canon Narrow Gate.

SUPERSEDED AS A PROPOSAL 2026-09-08. See `canon/PLACEMENT.md`.

Deny-by-default, bounded undertaking, receipts and at-most-once effects are all
present in `minority-prophet-gate`'s `decide()` and `minority-prophet-border`'s
admission binding, in stronger form than here. Nothing in this module should be
ported.

It is retained as the executable form of the laws audited in `NOVELTY-AUDIT.md`
-- the record of how the rules were derived and which were rejected -- and not
as a component anyone should adopt.

Deliberately small and dependency-free. This is the executable form of the laws
audited in ``canon/NOVELTY-AUDIT.md``; it is a specification artifact, not a
production component, and nothing in production MP imports it.

Two design choices are load-bearing and both come from the audit:

* An **unauthenticated mandate cannot create a conflict** (L7). Deny-on-conflict
  is otherwise a denial-of-service primitive: anyone able to inject a mandate
  could halt the system by manufacturing disagreement.
* Every denial carries a machine-readable ``reason``. A gate that cannot say why
  it refused cannot be measured for ``FalseDenyRate``, and per the audit that is
  the metric preventing trivial success.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Hashable, Iterable


class Verdict:
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class Decision:
    verdict: str
    reason: str

    @property
    def allowed(self) -> bool:
        return self.verdict == Verdict.ALLOW


@dataclass(frozen=True)
class Effect:
    """A proposed change to the world."""

    name: str
    receipt_nonce: str | None = None
    max_loss: float | None = None
    max_cost: float | None = None
    scope: frozenset[str] = frozenset()
    reversibility: float = 0.0          # Rev(e) in [0, 1]
    tail_risk: float | None = None      # CVaR-style; see audit L2


@dataclass(frozen=True)
class Mandate:
    """A grant of authority. ``authenticated`` is not decoration -- see L7."""

    name: str
    permits: frozenset[str]
    forbids: frozenset[str] = frozenset()
    authenticated: bool = True


@dataclass
class Bounds:
    max_loss: float
    max_cost: float
    scope: frozenset[str]
    max_tail_risk: float


@dataclass
class NarrowGate:
    """Admits an effect only when membership in the gate is *proven*.

    ``authority_chain`` is ordered outermost-first: ``M_0, M_1, ... M_n``.
    """

    authority_chain: list[Mandate]
    bounds: Bounds
    in_viability: Callable[[Effect], bool] = lambda _e: True
    world_verified: bool = True
    resolver: Callable[[Mandate, Mandate], Mandate] | None = None
    _spent_nonces: set[str] = field(default_factory=set)

    # -- Law 1 -------------------------------------------------------------
    def surviving_authority(self) -> frozenset[str]:
        """Intersection over the chain. Non-expansion is enforced, not assumed."""
        authenticated = [m for m in self.authority_chain if m.authenticated]
        if not authenticated:
            return frozenset()
        surviving = authenticated[0].permits
        for mandate in authenticated[1:]:
            surviving = surviving & mandate.permits
        return surviving

    def authority_expanded(self) -> bool:
        """True if any step granted something its predecessor did not."""
        authenticated = [m for m in self.authority_chain if m.authenticated]
        return any(
            not later.permits <= earlier.permits
            for earlier, later in zip(authenticated, authenticated[1:])
        )

    # -- Law 7 -------------------------------------------------------------
    def _unresolved_conflict(self, effect: Effect) -> bool:
        """Only *authenticated* mandates are counterparties to a conflict."""
        permitting = [
            m for m in self.authority_chain
            if m.authenticated and effect.name in m.permits
        ]
        forbidding = [
            m for m in self.authority_chain
            if m.authenticated and effect.name in m.forbids
        ]
        if not (permitting and forbidding):
            return False
        return self.resolver is None

    # -- the gate ----------------------------------------------------------
    def decide(self, effect: Effect) -> Decision:
        if self.authority_expanded():
            return Decision(Verdict.DENY, "authority-expanded")

        # Capability is not permission. Absence of proof is denial.
        if effect.name not in self.surviving_authority():
            return Decision(Verdict.DENY, "outside-surviving-authority")

        if self._unresolved_conflict(effect):
            return Decision(Verdict.DENY, "unresolved-authority-conflict")

        if not self.world_verified:
            return Decision(Verdict.DENY, "world-state-unverified")

        # Law 8 -- no unbounded undertaking.
        if effect.max_loss is None or effect.max_cost is None:
            return Decision(Verdict.DENY, "unbounded-undertaking")
        if effect.max_loss > self.bounds.max_loss:
            return Decision(Verdict.DENY, "loss-bound-exceeded")
        if effect.max_cost > self.bounds.max_cost:
            return Decision(Verdict.DENY, "cost-bound-exceeded")
        if not effect.scope <= self.bounds.scope:
            return Decision(Verdict.DENY, "scope-bound-exceeded")

        # Law 2 -- reformulated: tail risk, not entropy. See audit L2.
        if effect.tail_risk is None:
            return Decision(Verdict.DENY, "uncertainty-unquantified")
        if effect.tail_risk > self.bounds.max_tail_risk:
            return Decision(Verdict.DENY, "tail-risk-exceeded")

        # Viability -- one-step containment (NarrowGate.gate_preserves_viability).
        if not self.in_viability(effect):
            return Decision(Verdict.DENY, "leaves-viability-region")

        # Law 10 / at-most-once: irreversible effects need a fresh receipt.
        if effect.reversibility < 1.0:
            if effect.receipt_nonce is None:
                return Decision(Verdict.DENY, "irreversible-without-receipt")
            if effect.receipt_nonce in self._spent_nonces:
                return Decision(Verdict.DENY, "receipt-replayed")

        return Decision(Verdict.ALLOW, "admitted")

    def execute(self, effect: Effect) -> Decision:
        decision = self.decide(effect)
        if decision.allowed and effect.receipt_nonce is not None:
            self._spent_nonces.add(effect.receipt_nonce)
        return decision


# -- Law 5 ----------------------------------------------------------------
def independent_lineages(
    sources: Iterable[Hashable],
    same_origin: Callable[[Hashable, Hashable], bool],
) -> int:
    """Effective evidence count under transitive closure of ``same_origin``.

    WARNING, and it is the whole point of audit item L5: real provenance
    similarity is **not transitive**. Taking the transitive closure -- which is
    what an equivalence relation requires -- collapses chains A~B, B~C, A/~C into
    a single lineage. This function will under-count on connected corpora; that
    is directional, not conservative (see ``canon/independent_set.py``). It is a
    lower bound and wrong as an estimate. Ledger item ``U1`` is closed; see
    ``canon/U1-PROXIMATE-ROOTS.md``.
    """
    items = list(sources)
    parent = list(range(len(items)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if same_origin(items[i], items[j]):
                parent[find(i)] = find(j)

    return len({find(i) for i in range(len(items))})
